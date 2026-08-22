from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    payload = {"sub": subject, "type": token_type, "exp": datetime.now(UTC) + expires_delta}
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token(user_id, "access", timedelta(minutes=get_settings().access_token_expire_minutes))


def create_refresh_token(user_id: str) -> str:
    return _create_token(user_id, "refresh", timedelta(days=get_settings().refresh_token_expire_days))


def decode_token(token: str, expected_type: str) -> str:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type or not payload.get("sub"):
            raise ValueError("Invalid token type")
        return str(payload["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
