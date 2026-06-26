from sqlmodel import Session, select

from ..models import (
    ResumeSuggestion,
    CoverLetter,
)

from ..llm_client import (
    call_openai,
)


def generate_cover_letter_service(
    resume_id: int,
    user_id: int,
    job_description: str,
    tone: str,
    db: Session,
):

    suggestion = db.exec(
        select(ResumeSuggestion).where(
            ResumeSuggestion.resume_id == resume_id
        )
    ).first()

    if not suggestion:

        return {
            "success": False,
            "message": "Resume not found"
        }

    parsed_text = (
        suggestion.parsed_text or ""
    )

    print("\n")
    print("========================================")
    print("COVER LETTER DEBUG")
    print("RESUME ID:", resume_id)
    print("USER ID:", user_id)
    print("PARSED TEXT PREVIEW:")
    print(parsed_text[:2000])
    print("========================================")
    print("\n")

    prompt = f"""
You are an expert recruiter and resume reviewer.

Create a professional cover letter.

Job Description:
{job_description}

Candidate Resume:
{parsed_text}

Strict Rules:

1. Use ONLY information found in the resume.
2. Mention at least two projects from the resume.
3. Mention relevant technologies from the resume.
4. Mention internship/work experience if present.
5. Do NOT invent project names.
6. Do NOT invent companies.
7. Do NOT invent achievements.
8. Do NOT invent contact information.
9. Tailor the letter to the job description.
10. Tone should be {tone}.

Return ONLY the cover letter.
"""

    cover_text = call_openai(
        prompt
    )

    cover = CoverLetter(
        user_id=user_id,
        resume_id=resume_id,
        job_description=job_description,
        tone=tone,
        cover_text=cover_text,
    )

    db.add(
        cover
    )

    db.commit()

    db.refresh(
        cover
    )

    return {
        "success": True,
        "message": "Cover letter generated",
        "data": {
            "cover_letter_id": cover.id,
            "cover_text": cover_text,
        }
    }