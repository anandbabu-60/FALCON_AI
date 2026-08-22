from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DBSession
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenPair, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def tokens_for(user: User) -> TokenPair:
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: DBSession):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, institution=payload.institution, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: DBSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return tokens_for(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshTokenRequest, db: DBSession):
    import uuid
    try: user_id = uuid.UUID(decode_token(payload.refresh_token, "refresh"))
    except ValueError as exc: raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Account is unavailable")
    return tokens_for(user)
