from fastapi import (
    APIRouter,
    Depends,
)

from sqlmodel import Session

from ..db import get_db

from ..models import User

from ..dependencies.auth_dependency import (
    get_current_user
)

from ..services.cover_letter_service import (
    generate_cover_letter_service
)

router = APIRouter(
    prefix="",
    tags=["Cover Letter"]
)


@router.post("/generate_cover_letter")
def generate_cover_letter(
    resume_id: int,
    job_description: str,
    tone: str = "Professional",

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    return generate_cover_letter_service(
        resume_id=resume_id,
        user_id=user.id,
        job_description=job_description,
        tone=tone,
        db=db,
    )