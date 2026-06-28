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

    import re
    
    ats_score = None
    missing_keywords = None
    improved_bullets = None
    tailored_summary = None

    # Parse result
    score_match = re.search(r"ATS_SCORE:\s*(\d+)", result)
    if score_match:
        ats_score = float(score_match.group(1))

    keyword_match = re.search(r"MISSING_KEYWORDS:(.*?)IMPROVED_BULLETS:", result, re.DOTALL)
    if keyword_match:
        missing_keywords = keyword_match.group(1).strip()

    bullet_match = re.search(r"IMPROVED_BULLETS:(.*?)TAILORED_SUMMARY:", result, re.DOTALL)
    if bullet_match:
        improved_bullets = bullet_match.group(1).strip()

    summary_match = re.search(r"TAILORED_SUMMARY:(.*)", result, re.DOTALL)
    if summary_match:
        tailored_summary = summary_match.group(1).strip()

    optimization = JobOptimization(
        user_id=user_id,
        resume_id=resume_id,
        job_description=job_description,
        ats_score=ats_score,
        missing_keywords=missing_keywords,
        improved_bullets=improved_bullets,
        tailored_summary=tailored_summary,
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