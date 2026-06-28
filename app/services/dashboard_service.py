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

    resumes = db.exec(
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .limit(5)
    ).all()
    total_resumes = len(
        db.exec(
            select(Resume).where(
                Resume.user_id == user_id
            )
        ).all()
    )

    ats_runs = db.exec(
        select(JobOptimization)
        .where(JobOptimization.user_id == user_id)
        .order_by(JobOptimization.created_at.desc())
        .limit(5)
    ).all()
    total_ats_runs = len(
        db.exec(
            select(JobOptimization).where(
                JobOptimization.user_id == user_id
            )
        ).all()
    )
    
    # Calculate average ATS score
    all_runs = db.exec(
        select(JobOptimization).where(
            JobOptimization.user_id == user_id
        )
    ).all()
    scores = [run.ats_score for run in all_runs if run.ats_score is not None]
    average_ats_score = round(sum(scores) / len(scores), 1) if scores else 0

    interviews = db.exec(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
        .limit(5)
    ).all()
    total_interviews = len(
        db.exec(
            select(InterviewSession).where(
                InterviewSession.user_id == user_id
            )
        ).all()
    )

    cover_letters = db.exec(
        select(CoverLetter)
        .where(CoverLetter.user_id == user_id)
        .order_by(CoverLetter.created_at.desc())
        .limit(5)
    ).all()
    total_cover_letters = len(
        db.exec(
            select(CoverLetter).where(
                CoverLetter.user_id == user_id
            )
        ).all()
    )

    # Compile recent activity feed
    activities = []
    
    for r in resumes:
        activities.append({
            "type": "resume_upload",
            "title": "Uploaded Resume",
            "description": f"Uploaded resume '{r.filename}'",
            "created_at": r.created_at
        })
        
    for o in ats_runs:
        score_info = f" (Score: {int(o.ats_score)}%)" if o.ats_score is not None else ""
        activities.append({
            "type": "ats_optimize",
            "title": "Optimized Resume",
            "description": f"Analyzed resume matching gaps{score_info}",
            "created_at": o.created_at
        })
        
    for c in cover_letters:
        activities.append({
            "type": "cover_letter",
            "title": "Generated Cover Letter",
            "description": f"Drafted tailored cover letter with {c.tone} tone",
            "created_at": c.created_at
        })
        
    for i in interviews:
        activities.append({
            "type": "mock_interview",
            "title": "Started Mock Interview",
            "description": f"Practice mock interview for '{i.target_role}' role",
            "created_at": i.created_at
        })
        
    # Sort and keep top 5
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    recent_activities = []
    for act in activities[:5]:
        recent_activities.append({
            "type": act["type"],
            "title": act["title"],
            "description": act["description"],
            "created_at": act["created_at"].isoformat()
        })

    return {
        "success": True,
        "data": {
            "total_resumes": total_resumes,
            "total_ats_runs": total_ats_runs,
            "total_interviews": total_interviews,
            "total_cover_letters": total_cover_letters,
            "average_ats_score": average_ats_score,
            "recent_activities": recent_activities,
        }
    }