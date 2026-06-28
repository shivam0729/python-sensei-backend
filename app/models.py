# backend/app/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    full_name: str = Field(default="")
    phone_number: Optional[str] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Resume(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    user_id: int

    filename: str

    path: str

    created_at: datetime = Field(
    default_factory=datetime.utcnow
)

    processing_status: str = Field(
        default="pending"
    )

    processing_error: str | None = Field(
        default=None
    )

class ResumeSuggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    resume_id: int
    suggestions: Optional[str] = None
    parsed_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobOptimization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    resume_id: int
    job_description: Optional[str] = None
    ats_score: Optional[float] = None
    missing_keywords: Optional[str] = None
    improved_bullets: Optional[str] = None
    tailored_summary: Optional[str] = None
    raw_output: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CoverLetter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    resume_id: Optional[int] = None
    job_description: Optional[str] = None
    tone: Optional[str] = None
    cover_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewSession(SQLModel, table=True):
    """
    One mock interview session: linked to user & resume.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    resume_id: Optional[int] = None
    job_description: Optional[str] = None
    target_role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewQnA(SQLModel, table=True):
    """
    Individual question + answer + AI feedback within a session.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int
    question_index: int
    question_text: str
    user_answer: Optional[str] = None
    ai_feedback: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    role: str      # "user" / "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
