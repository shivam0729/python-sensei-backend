# backend/app/tasks.py

from .parse_resume import parse_resume_file
from .llm_client import call_openai
from .db import engine
from sqlmodel import Session
from .models import Resume

def process_resume_and_generate_suggestions(resume_id: int):
    """
    Reads the resume → parses it → sends to LLM → returns suggestions.
    Synchronous version (no Celery).
    """

    with Session(engine) as session:
        resume = session.get(Resume, resume_id)

        if not resume:
            return {"error": "Resume not found"}

        # Parse text from uploaded PDF/DOCX
        parsed_text = parse_resume_file(resume.path)
        resume.parsed_text = parsed_text
        session.add(resume)
        session.commit()
        session.refresh(resume)

        # Build prompt for the AI
        prompt = f"""
You are an expert career coach.

Analyze this resume text and provide:

1) A 2-line summary
2) Top 5 skills extracted
3) 5 improved resume bullet points with action verbs
4) 5 probable interview questions

Respond in plain text (you can include JSON-like sections).
Resume:
{parsed_text}
"""

        # Get AI suggestions
        suggestions = call_openai(prompt)

        return {
            "resume_id": resume.id,
            "parsed_text": parsed_text,
            "suggestions": suggestions
        }
