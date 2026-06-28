from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from sqlmodel import Session, select
import os
from pydantic import BaseModel

from ..db import get_db
from ..models import User, Resume, CoverLetter, InterviewSession
from ..dependencies.auth_dependency import get_current_user
from ..auth import verify_password, hash_password
from ..schemas.auth_schema import UserProfileUpdateRequest
from ..schemas.response_schema import ApiResponse

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.get("")
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resumes = db.exec(
        select(Resume).where(Resume.user_id == user.id)
    ).all()
    cover_letters = db.exec(
        select(CoverLetter).where(CoverLetter.user_id == user.id)
    ).all()
    interviews = db.exec(
        select(InterviewSession).where(InterviewSession.user_id == user.id)
    ).all()

    return ApiResponse(
        success=True,
        message="Profile details fetched successfully",
        data={
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at.isoformat()
            },
            "resumes": [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "created_at": r.created_at.isoformat()
                } for r in resumes
            ],
            "cover_letters": [
                {
                    "id": c.id,
                    "job_description": c.job_description,
                    "tone": c.tone,
                    "cover_text": c.cover_text,
                    "created_at": c.created_at.isoformat()
                } for c in cover_letters
            ],
            "interviews": [
                {
                    "id": i.id,
                    "target_role": i.target_role,
                    "created_at": i.created_at.isoformat()
                } for i in interviews
            ]
        }
    )

@router.put("")
def update_profile(
    data: UserProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user.full_name = data.full_name
    user.phone_number = data.phone_number
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(
        success=True,
        message="Profile updated successfully",
        data={
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

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, or JPEG images are allowed"
        )

    os.makedirs("./uploads", exist_ok=True)
    content = await file.read()

    # Create filename
    filename = f"avatar_{user.id}_{os.path.basename(file.filename)}"
    path = f"./uploads/{filename}"

    with open(path, "wb") as f:
        f.write(content)

    user.profile_picture = f"/uploads/{filename}"
    db.add(user)
    db.commit()
    db.refresh(user)

    return ApiResponse(
        success=True,
        message="Profile picture updated successfully",
        data={"profile_picture": user.profile_picture}
    )

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect current password"
        )
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    db.commit()
    return ApiResponse(
        success=True,
        message="Password updated successfully"
    )
