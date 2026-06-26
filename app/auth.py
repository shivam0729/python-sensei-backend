from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from .core.config import settings


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

ALGORITHM = "HS256"


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):

    return pwd_context.verify(
        password,
        hashed
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=ALGORITHM
    )

    return encoded_jwt