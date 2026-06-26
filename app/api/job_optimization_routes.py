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

from ..services.job_optimization_service import (
    optimize_resume_service
)

router = APIRouter(
    prefix="",
    tags=["ATS Optimization"]
)


@router.post("/optimize_resume")
def optimize_resume(
    resume_id: int,
    job_description: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return optimize_resume_service(
        resume_id=resume_id,
        user_id=user.id,
        job_description=job_description,
        db=db,
    )