from sqlmodel import Session, select

from ..models import (
    Resume,
    JobOptimization,
    InterviewSession,
    CoverLetter,
)


def get_dashboard_stats_service(
    user_id: int,
    db: Session,
):

    total_resumes = len(
        db.exec(
            select(Resume).where(
                Resume.user_id == user_id
            )
        ).all()
    )

    total_ats_runs = len(
        db.exec(
            select(JobOptimization).where(
                JobOptimization.user_id == user_id
            )
        ).all()
    )

    total_interviews = len(
        db.exec(
            select(InterviewSession).where(
                InterviewSession.user_id == user_id
            )
        ).all()
    )

    total_cover_letters = len(
        db.exec(
            select(CoverLetter).where(
                CoverLetter.user_id == user_id
            )
        ).all()
    )

    return {
        "success": True,
        "data": {
            "total_resumes": total_resumes,
            "total_ats_runs": total_ats_runs,
            "total_interviews": total_interviews,
            "total_cover_letters": total_cover_letters,
        }
    }