from .parse_resume import (extract_text_from_resume)
from .llm_client import call_openai
from .models import Resume
from .db import get_db


def process_resume_and_generate_suggestions(
    resume_id: int
):
    """
    Process uploaded resume
    and generate AI suggestions.
    """

    db = next(get_db())

    resume = db.get(
        Resume,
        resume_id
    )

    if not resume:

        return {
            "parsed_text": "",
            "suggestions":
                "Resume not found."
        }

    parsed_text = (
        extract_text_from_resume(
            resume.path
        )
    )

    # Prevent token limit issues
    MAX_CHARS = 4000

    if len(parsed_text) > MAX_CHARS:

        parsed_text = (
            parsed_text[:MAX_CHARS]
        )

    prompt = f"""
Analyze this resume.

Provide:

1. ATS improvement suggestions

2. Missing skills

3. Resume formatting improvements

4. Professional recommendations

Keep the response concise and practical.

Resume:

{parsed_text}
"""

    suggestions = call_openai(
        prompt
    )

    return {
        "parsed_text":
            parsed_text,

        "suggestions":
            suggestions,
    }