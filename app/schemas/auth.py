import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.common import ORMModel


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    institution: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    institution: str | None = Field(default=None, max_length=255)


class UserResponse(ORMModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    institution: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendVerificationOTPRequest(BaseModel):
    email: EmailStr


class RegistrationMessage(BaseModel):
    message: str


