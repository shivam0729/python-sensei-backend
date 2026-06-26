from pydantic import BaseModel, EmailStr


# -------------------------
# REQUEST SCHEMAS
# -------------------------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# RESPONSE SCHEMAS
# -------------------------

class UserResponse(BaseModel):
    id: int
    email: str


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse