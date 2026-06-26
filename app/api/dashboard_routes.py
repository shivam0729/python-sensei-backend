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

from ..services.dashboard_service import (
    get_dashboard_stats_service
)

router = APIRouter(
    prefix="",
    tags=["Dashboard"]
)


@router.get("/dashboard_stats")
def dashboard_stats(
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    return get_dashboard_stats_service(
        user_id=user.id,
        db=db,
    )