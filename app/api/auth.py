import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DBSession
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.models.registration import PendingRegistration
from app.schemas.auth import RegistrationMessage, RefreshTokenRequest, ResendVerificationOTPRequest, TokenPair, UserLogin, UserRegister, UserResponse, VerifyEmailRequest
from app.services.email import send_verification_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])


def tokens_for(user: User) -> TokenPair:
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/register", response_model=RegistrationMessage, status_code=status.HTTP_202_ACCEPTED)
def register(payload: UserRegister, db: DBSession):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="An account with this email already exists. Please sign in.")
    email = payload.email.lower()
    pending = db.scalar(select(PendingRegistration).where(PendingRegistration.email == email))
    if pending:
        raise HTTPException(status_code=409, detail="A verification is already pending for this email. Request a new code after the cooldown.")
    code = f"{secrets.randbelow(1_000_000):06d}"
    now = datetime.now(UTC)
    pending = PendingRegistration(email=email, full_name=payload.full_name, institution=payload.institution, password_hash=hash_password(payload.password), otp_hash=hash_password(code), expires_at=now + timedelta(minutes=5), resend_available_at=now + timedelta(seconds=60))
    db.add(pending)
    try:
        send_verification_otp(email, code)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Email verification is not configured. Please contact the administrator.") from exc
    return {"message": "Verification code sent to your email."}


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: DBSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return tokens_for(user)


@router.post("/verify-email", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def verify_email(payload: VerifyEmailRequest, db: DBSession):
    pending = db.scalar(select(PendingRegistration).where(PendingRegistration.email == payload.email.lower()))
    if not pending or pending.is_used:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    now = datetime.now(UTC)
    if pending.expires_at < now:
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new OTP.")
    if pending.attempts >= pending.max_attempts:
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. Please request a new OTP.")
    if not verify_password(payload.code, pending.otp_hash):
        pending.attempts += 1
        db.commit()
        if pending.attempts >= pending.max_attempts:
            raise HTTPException(status_code=400, detail="Too many incorrect attempts. Please request a new OTP.")
        raise HTTPException(status_code=400, detail="OTP verification failed. Please enter the correct OTP.")
    user = User(email=pending.email, full_name=pending.full_name, institution=pending.institution, password_hash=pending.password_hash)
    db.add(user)
    pending.is_used = True
    db.delete(pending)
    db.commit(); db.refresh(user)
    return user


@router.post("/resend-verification-otp", response_model=RegistrationMessage)
def resend_verification_otp(payload: ResendVerificationOTPRequest, db: DBSession):
    pending = db.scalar(select(PendingRegistration).where(PendingRegistration.email == payload.email.lower()))
    if not pending:
        raise HTTPException(status_code=404, detail="No pending registration found for this email.")
    now = datetime.now(UTC)
    if pending.resend_available_at > now:
        raise HTTPException(status_code=429, detail="Please wait before requesting another OTP.")
    code = f"{secrets.randbelow(1_000_000):06d}"
    pending.otp_hash = hash_password(code)
    pending.expires_at = now + timedelta(minutes=5)
    pending.resend_available_at = now + timedelta(seconds=60)
    pending.attempts = 0
    try:
        send_verification_otp(pending.email, code)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Email verification is not configured. Please contact the administrator.") from exc
    return {"message": "New OTP sent successfully."}


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshTokenRequest, db: DBSession):
    try: user_id = uuid.UUID(decode_token(payload.refresh_token, "refresh"))
    except ValueError as exc: raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Account is unavailable")
    return tokens_for(user)
