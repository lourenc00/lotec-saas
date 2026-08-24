from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    status: str
    is_super_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
