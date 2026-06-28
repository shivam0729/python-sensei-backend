from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlmodel import (
    Session,
    select,
)

from jose import jwt, JWTError
from ..db import get_db
from ..models import User

from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    ALGORITHM,
)

from ..core.config import settings

from ..schemas.auth_schema import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
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
        full_name=data.full_name,
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
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at.isoformat()
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
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at.isoformat()
            }
        }
    )


# -------------------------
# FORGOT PASSWORD
# -------------------------

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Email address not found"
        )

    token = create_password_reset_token(user.email)
    reset_link = f"http://localhost:5173/reset-password?token={token}"

    # Print to console in dev mode
    print("\n" + "=" * 60)
    print(f"PASSWORD RESET LINK GENERATED FOR: {user.email}")
    print(reset_link)
    print("=" * 60 + "\n")

    return ApiResponse(
        success=True,
        message="Password reset link sent to your email",
        data={"reset_link": reset_link}
    )


# -------------------------
# RESET PASSWORD
# -------------------------

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            data.token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM]
        )
        email = payload.get("sub")
        token_type = payload.get("type")
        if not email or token_type != "password_reset":
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="The password reset token is expired or invalid"
        )

    user = db.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User account not found"
        )

    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    db.commit()

    return ApiResponse(
        success=True,
        message="Password reset successfully"
    )