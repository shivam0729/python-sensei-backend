# backend/app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import os, json, re

from .db import create_db_and_tables, get_db
from .models import (
    User,
    Resume,
    ResumeSuggestion,
    JobOptimization,
    CoverLetter,
    InterviewSession,
    InterviewQnA,
)
from .auth import hash_password, verify_password, create_access_token
from .tasks import process_resume_and_generate_suggestions
from .llm_client import call_openai

app = FastAPI(title="Python Sensei API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    os.makedirs("./uploads", exist_ok=True)

# ---------------------------
# Auth
# ---------------------------
@app.post("/signup")
def signup(email: str, password: str, db: Session = Depends(get_db)):
    if db.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user": {"id": user.id, "email": user.email}}

@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user": {"id": user.id, "email": user.email}}

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        token = authorization.split(" ")[1]
        from jose import jwt

        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET", "mysecretkey123"),
            algorithms=["HS256"],
        )
        user = db.get(User, int(payload["sub"]))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---------------------------
# Upload Resume
# ---------------------------
@app.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    path = f"./uploads/{user.id}_{file.filename}"

    with open(path, "wb") as f:
        f.write(content)

    resume = Resume(user_id=user.id, filename=file.filename, path=path)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    result = process_resume_and_generate_suggestions(resume.id)

    suggestion = ResumeSuggestion(
        user_id=user.id,
        resume_id=resume.id,
        parsed_text=result["parsed_text"],
        suggestions=result["suggestions"],
    )
    db.add(suggestion)
    db.commit()

    return {"status": "success", "resume_id": resume.id}

@app.get("/my_resumes")
def my_resumes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = db.exec(
        select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    ).all()

    out = []
    for r in resumes:
        s = db.exec(
            select(ResumeSuggestion).where(ResumeSuggestion.resume_id == r.id)
        ).first()
        out.append({
            "resume_id": r.id,
            "filename": r.filename,
            "uploaded_at": r.created_at.isoformat(),
            "parsed_text": s.parsed_text if s else None,
            "suggestions": s.suggestions if s else None,
        })

    return {"resumes": out}

# ---------------------------
# Mock Interview — Generate
# ---------------------------
@app.post("/generate_interview_session")
def generate_interview_session(
    resume_id: int,
    job_description: str = "",
    target_role: str = "General",
    num_questions: int = 8,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    parsed_text = resume.parsed_text or ""

    prompt = f"""
Generate {num_questions} interview questions for the role: {target_role}.
Return ONLY JSON:

{{ "questions": ["Question 1", "Question 2"] }}

Resume:
{parsed_text}

Job Description:
{job_description}
"""

    ai = call_openai(prompt).strip()

    try:
        data = json.loads(ai)
        questions = data.get("questions", [])
    except:
        questions = [q.strip("- ").strip() for q in ai.splitlines() if q.strip()]

    if not questions:
        questions = ["Tell me about yourself.", "Explain a challenging project."]

    session_obj = InterviewSession(
        user_id=user.id,
        resume_id=resume_id,
        job_description=job_description,
        target_role=target_role,
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    for i, q in enumerate(questions):
        db.add(InterviewQnA(
            session_id=session_obj.id,
            question_index=i,
            question_text=q
        ))
    db.commit()

    return {
        "session_id": session_obj.id,
        "questions": [{"question": q} for q in questions],
    }

# ---------------------------
# Mock Interview — Answer
# ---------------------------
@app.post("/interview_answer")
def interview_answer(
    session_id: int,
    question_index: int,
    answer: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    qa = db.exec(
        select(InterviewQnA).where(
            InterviewQnA.session_id == session_id,
            InterviewQnA.question_index == question_index,
        )
    ).first()

    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")

    feedback = call_openai(
        f"Evaluate this answer:\nQuestion: {qa.question_text}\nAnswer: {answer}"
    )

    qa.user_answer = answer
    qa.ai_feedback = feedback
    db.add(qa)
    db.commit()

    return {"score": None, "feedback": feedback}

# ---------------------------
# Mock Interview: summary
# ---------------------------
@app.get("/interview_summary/{session_id}")
def interview_summary(
    session_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    inter = session.get(InterviewSession, session_id)
    if not inter or inter.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview session not found")

    qas = session.exec(
        select(InterviewQnA).where(InterviewQnA.session_id == session_id)
    ).all()

    if not qas:
        raise HTTPException(status_code=400, detail="No answers found")

    scores = [qa.score for qa in qas if qa.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    # Simple verdict logic
    if avg_score >= 80:
        verdict = "Strong Hire Potential"
    elif avg_score >= 60:
        verdict = "Moderate – Needs Improvement"
    else:
        verdict = "Not Ready Yet"

    # Generate strengths & improvements using LLM
    combined_feedback = "\n".join([qa.ai_feedback for qa in qas if qa.ai_feedback])

    prompt = f"""
You are an interview coach.

Based on the following interview feedback, summarize:

1) Key strengths (bullet points)
2) Areas for improvement (bullet points)
3) Suggested topics to practice (bullet points)

Feedback:
{combined_feedback}

Respond in clear plain text with section headers.
"""

    try:
        summary_text = call_openai(prompt)
    except Exception as e:
        summary_text = "Summary generation failed."

    return {
        "session_id": session_id,
        "average_score": avg_score,
        "verdict": verdict,
        "summary": summary_text,
    }
