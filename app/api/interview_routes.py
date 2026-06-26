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

from ..services.interview_service import (
    generate_interview_service,
    submit_answer_service,
    get_interview_summary_service,
)

router = APIRouter(
    prefix="",
    tags=["Interview"]
)


# -----------------------------------
# GENERATE SESSION
# -----------------------------------

@router.post("/generate_interview_session")
def generate_interview_session(
    resume_id: int,
    job_description: str = "",
    target_role: str = "General",
    num_questions: int = 5,

    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_interview_service(
        resume_id=resume_id,
        job_description=job_description,
        target_role=target_role,
        num_questions=num_questions,
        user=user,
        db=db,
    )


# -----------------------------------
# SUBMIT ANSWER
# -----------------------------------

@router.post("/interview_answer")
def interview_answer(
    session_id: int,
    question_index: int,
    answer: str,

    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return submit_answer_service(
        session_id=session_id,
        question_index=question_index,
        answer=answer,
        db=db,
    )
    
    # -----------------------------------
# INTERVIEW SUMMARY
# -----------------------------------

@router.get("/interview_summary/{session_id}")
def interview_summary(
    session_id: int,
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    return get_interview_summary_service(
        session_id=session_id,
        db=db,
    )