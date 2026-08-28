import secrets
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select

from app.api.deps import DBSession
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.models.registration import PendingRegistration
from app.models.password_reset import PasswordResetToken
from app.schemas.auth import ForgotPasswordRequest, RegistrationMessage, ResetPasswordRequest, RefreshTokenRequest, ResendVerificationOTPRequest, TokenPair, UserLogin, UserRegister, UserResponse, VerifyEmailRequest
from app.services.email import send_password_reset_otp, send_verification_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _oauth_error_redirect(message: str) -> RedirectResponse:
    """Send browser-based OAuth failures back to the frontend without exposing provider details."""
    settings = get_settings()
    target = f"{settings.frontend_url.rstrip('/')}/oauth/callback?{urlencode({'error': message})}"
    return RedirectResponse(target, status_code=status.HTTP_302_FOUND)


def tokens_for(user: User) -> TokenPair:
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.get("/google/login", include_in_schema=True)
def google_login() -> RedirectResponse:
    """Start Google OpenID Connect login and retain a short-lived CSRF state cookie."""
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        return _oauth_error_redirect("Google OAuth is not configured on the server yet.")
    state = secrets.token_urlsafe(32)
    query = urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state,
    })
    response = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}", status_code=status.HTTP_302_FOUND)
    response.set_cookie("google_oauth_state", state, max_age=600, httponly=True, samesite="lax", secure=settings.environment == "production")
    return response


@router.get("/google/callback", include_in_schema=True)
def google_callback(request: Request, db: DBSession, code: str | None = None, state: str | None = None, error: str | None = None) -> RedirectResponse:
    """Exchange Google's authorization code, provision/find the user, and issue this API's JWT pair."""
    if error or not code:
        return _oauth_error_redirect("Google sign-in was cancelled.")
    expected_state = request.cookies.get("google_oauth_state")
    if not state or not expected_state or not secrets.compare_digest(state, expected_state):
        return _oauth_error_redirect("Google sign-in could not be verified. Please try again.")

    settings = get_settings()
    try:
        with httpx.Client(timeout=10.0) as client:
            token_response = client.post("https://oauth2.googleapis.com/token", data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            })
            token_response.raise_for_status()
            google_access_token = token_response.json().get("access_token")
            if not google_access_token:
                return _oauth_error_redirect("Google did not return an access token.")
            profile_response = client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {google_access_token}"})
            profile_response.raise_for_status()
            profile = profile_response.json()
    except (httpx.HTTPError, ValueError, KeyError):
        return _oauth_error_redirect("Google sign-in could not be completed. Please try again.")

    email = str(profile.get("email", "")).strip().lower()
    if not email or profile.get("email_verified") is not True:
        return _oauth_error_redirect("Google did not provide a verified email address.")
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email))
    if not user:
        # Do not silently create accounts from an OAuth button. Let the user explicitly
        # complete the normal registration + email OTP verification flow instead.
        display_name = str(profile.get("name") or email.split("@", 1)[0])[:150]
        target = f"{settings.frontend_url.rstrip('/')}/oauth/callback?{urlencode({'needs_registration': '1', 'email': email, 'name': display_name})}"
        response = RedirectResponse(target, status_code=status.HTTP_302_FOUND)
        response.delete_cookie("google_oauth_state")
        return response
    if not user.is_active:
        return _oauth_error_redirect("This account is disabled. Contact the administrator.")

    pair = tokens_for(user)
    # Keep bearer tokens out of the callback URL query string (and therefore
    # out of common server/proxy query logs and Referer headers). The frontend
    # consumes the fragment and immediately stores the pair locally.
    target = f"{settings.frontend_url.rstrip('/')}/oauth/callback#{urlencode({'access_token': pair.access_token, 'refresh_token': pair.refresh_token})}"
    response = RedirectResponse(target, status_code=status.HTTP_302_FOUND)
    response.delete_cookie("google_oauth_state")
    return response


@router.post("/register", response_model=RegistrationMessage, status_code=status.HTTP_202_ACCEPTED)
def register(payload: UserRegister, db: DBSession):
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(func.lower(func.trim(User.email)) == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists. Please sign in.")
    pending = db.scalar(select(PendingRegistration).where(func.lower(func.trim(PendingRegistration.email)) == email))
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
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return tokens_for(user)


@router.post("/verify-email", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def verify_email(payload: VerifyEmailRequest, db: DBSession):
    pending = db.scalar(select(PendingRegistration).where(func.lower(func.trim(PendingRegistration.email)) == payload.email.strip().lower()))
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
    pending = db.scalar(select(PendingRegistration).where(func.lower(func.trim(PendingRegistration.email)) == payload.email.strip().lower()))
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


@router.post("/forgot-password", response_model=RegistrationMessage, status_code=status.HTTP_202_ACCEPTED)
def forgot_password(payload: ForgotPasswordRequest, db: DBSession):
    """Send a time-limited reset code. The response is intentionally generic."""
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email))
    if user:
        previous = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id, PasswordResetToken.is_used.is_(False)).order_by(PasswordResetToken.created_at.desc()))
        now = datetime.now(UTC)
        if previous and previous.resend_available_at > now:
            raise HTTPException(status_code=429, detail="Please wait before requesting another reset code.")
        code = f"{secrets.randbelow(1_000_000):06d}"
        token = PasswordResetToken(user_id=user.id, otp_hash=hash_password(code), expires_at=now + timedelta(minutes=10), resend_available_at=now + timedelta(seconds=60))
        db.add(token)
        try:
            send_password_reset_otp(email, code)
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=503, detail="Password reset email could not be sent. Contact the administrator.") from exc
    return {"message": "If an account exists for that email, a password reset code has been sent."}


@router.post("/reset-password", response_model=RegistrationMessage)
def reset_password(payload: ResetPasswordRequest, db: DBSession):
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code.")
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id, PasswordResetToken.is_used.is_(False)).order_by(PasswordResetToken.created_at.desc()))
    now = datetime.now(UTC)
    if not token or token.expires_at < now:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code.")
    if token.attempts >= token.max_attempts:
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. Request a new reset code.")
    if not verify_password(payload.code, token.otp_hash):
        token.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Reset code is incorrect.")
    user.password_hash = hash_password(payload.new_password)
    token.is_used = True
    db.commit()
    return {"message": "Password reset successfully. You can now sign in."}


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshTokenRequest, db: DBSession):
    try: user_id = uuid.UUID(decode_token(payload.refresh_token, "refresh"))
    except ValueError as exc: raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Account is unavailable")
    return tokens_for(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> Response:
    """End the client session.

    JWTs are stateless in this deployment, so the browser must discard both
    tokens. Immediate server-side revocation can be added later with Redis;
    this endpoint keeps logout consistent across clients today.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
