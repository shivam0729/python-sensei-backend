from fastapi import HTTPException
from sqlmodel import Session, select

from ..models import User

from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
)


# -------------------------
# SIGNUP SERVICE
# -------------------------

def signup_user(
    email: str,
    password: str,
    db: Session,
):
    existing_user = db.exec(
        select(User).where(
            User.email == email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        email=email,
        hashed_password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email
        }
    }


# -------------------------
# LOGIN SERVICE
# -------------------------

def login_user(
    email: str,
    password: str,
    db: Session,
):
    user = db.exec(
        select(User).where(
            User.email == email
        )
    ).first()

    if not user or not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email
        }
    }