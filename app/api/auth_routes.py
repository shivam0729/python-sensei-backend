from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlmodel import (
    Session,
    select,
)

from ..db import get_db

from ..models import User

from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
)

from ..schemas.auth_schema import (
    SignupRequest,
    LoginRequest,
)

from ..schemas.response_schema import (
    ApiResponse,
)

router = APIRouter(
    prefix="",
    tags=["Authentication"]
)


# -------------------------
# SIGNUP
# -------------------------

@router.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.exec(
        select(User).where(
            User.email == data.email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(
            data.password
        )
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return ApiResponse(
        success=True,
        message="Signup successful",
        data={
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email
            }
        }
    )
# -------------------------
# LOGIN
# -------------------------

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.exec(
        select(User).where(
            User.email == data.email
        )
    ).first()

    if not user or not verify_password(
        data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return ApiResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email
            }
        }
    )