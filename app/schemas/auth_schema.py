from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# -------------------------
# REQUEST SCHEMAS
# -------------------------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserProfileUpdateRequest(BaseModel):
    full_name: str
    phone_number: Optional[str] = None


# -------------------------
# RESPONSE SCHEMAS
# -------------------------

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse