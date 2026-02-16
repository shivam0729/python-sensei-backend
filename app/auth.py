# backend/app/auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET", "mysecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# 🔥 Use pbkdf2_sha256 — clean, stable, long-password support.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def normalize_password(password):
    if password is None:
        return ""
    if not isinstance(password, str):
        password = str(password)
    return password.strip()

def hash_password(password: str):
    password = normalize_password(password)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    plain_password = normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
