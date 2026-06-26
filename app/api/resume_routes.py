from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    BackgroundTasks,
    HTTPException,
)

from sqlmodel import Session, select

from ..db import get_db

from ..models import (
    User,
    Resume,
    ResumeSuggestion,
)

from ..dependencies.auth_dependency import (
    get_current_user
)

from ..services.resume_service import (
    upload_resume_service
)

router = APIRouter(
    prefix="",
    tags=["Resume"]
)

# -------------------------
# UPLOAD RESUME
# -------------------------

@router.post("/upload_resume")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await upload_resume_service(
        background_tasks=background_tasks,
        file=file,
        user=user,
        db=db,
    )


# -------------------------
# MY RESUMES
# -------------------------

@router.get("/my_resumes")
def my_resumes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = db.exec(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.created_at.desc())
    ).all()

    output = []

    for resume in resumes:

        suggestion = db.exec(
            select(ResumeSuggestion).where(
                ResumeSuggestion.resume_id == resume.id
            )
        ).first()

        output.append({
            "resume_id": resume.id,
            "filename": resume.filename,
            "uploaded_at": resume.created_at.isoformat(),

            "parsed_text":
                suggestion.parsed_text
                if suggestion else None,

            "suggestions":
                suggestion.suggestions
                if suggestion else None,
        })

    return {
        "resumes": output
    }


# -------------------------
# RESUME STATUS
# -------------------------

@router.get("/resume_status/{resume_id}")
def get_resume_status(
    resume_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    resume = db.get(
        Resume,
        resume_id
    )

    if not resume or resume.user_id != user.id:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return {
        "success": True,
        "message": "Resume status fetched",
        "data": {
            "resume_id": resume.id,
            "status": resume.processing_status,
            "error": resume.processing_error,
        }
    }


# -------------------------
# RESUME RESULT
# -------------------------

@router.get("/resume_result/{resume_id}")
def get_resume_result(
    resume_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    resume = db.get(
        Resume,
        resume_id
    )

    if not resume or resume.user_id != user.id:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    suggestion = db.exec(
        select(ResumeSuggestion).where(
            ResumeSuggestion.resume_id == resume_id
        )
    ).first()

    if not suggestion:

        raise HTTPException(
            status_code=404,
            detail="Resume result not found"
        )

    return {
        "success": True,
        "message": "Resume result fetched",
        "data": {
            "resume_id": resume_id,
            "parsed_text": suggestion.parsed_text,
            "suggestions": suggestion.suggestions,
        }
    }