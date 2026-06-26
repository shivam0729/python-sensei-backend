import os

from fastapi import (
    UploadFile,
    HTTPException,
    BackgroundTasks,
)

from sqlmodel import Session

from ..models import (
    Resume,
    ResumeSuggestion,
)
from ..core.logger import logger

from ..celery_tasks import process_resume_task

# -----------------------------------
# BACKGROUND AI PROCESSING
# -----------------------------------


# -----------------------------------
# UPLOAD RESUME SERVICE
# -----------------------------------

async def upload_resume_service(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    user,
    db: Session,
):

    # Validate file
    if not file.filename.endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are allowed"
        )

    # Create uploads folder
    os.makedirs("./uploads", exist_ok=True)

    # Read uploaded file
    content = await file.read()

    # Create file path
    path = f"./uploads/{user.id}_{file.filename}"

    # Save file locally
    with open(path, "wb") as f:
        f.write(content)

    # Save resume record
    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        path=path,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # -----------------------------------
    # START BACKGROUND AI TASK
    # -----------------------------------

    process_resume_task.delay(
    resume.id,
    user.id,
    )

    return {
        "success": True,
        "message": "Resume uploaded. AI analysis started.",
        "data": {
            "resume_id": resume.id
        }
    }