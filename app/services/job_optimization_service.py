from sqlmodel import Session

from ..models import (
    Resume,
    ResumeSuggestion,
    JobOptimization,
)

from ..tasks import (
    extract_text_from_resume,
)

from ..llm_client import (
    call_openai,
)


def optimize_resume_service(
    resume_id: int,
    user_id: int,
    job_description: str,
    db: Session,
):

    resume = db.get(
        Resume,
        resume_id
    )

    if not resume:

        return {
            "success": False,
            "message": "Resume not found"
        }

    parsed_text = extract_text_from_resume(
        resume.path
    )

    prompt = f"""
You are an ATS expert.

Compare this resume against the provided job description.

Return your response in exactly this format:

ATS_SCORE:
<number between 0 and 100>

MISSING_KEYWORDS:
<comma separated keywords>

IMPROVED_BULLETS:
<improved resume bullet points>

TAILORED_SUMMARY:
<professional summary tailored to the role>

JOB DESCRIPTION:

{job_description}

RESUME:

{parsed_text}
"""

    result = call_openai(
        prompt
    )

    optimization = JobOptimization(
        user_id=user_id,
        resume_id=resume_id,
        job_description=job_description,
        raw_output=result,
    )

    db.add(
        optimization
    )

    db.commit()

    db.refresh(
        optimization
    )

    return {
        "success": True,
        "message": "Resume optimized successfully",
        "data": {
            "optimization_id": optimization.id,
            "result": result,
        }
    }