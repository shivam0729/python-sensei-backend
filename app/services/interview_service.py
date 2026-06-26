import json

from fastapi import HTTPException

from sqlmodel import (
    Session,
    select,
)

from ..models import (
    Resume,
    ResumeSuggestion,
    InterviewSession,
    InterviewQnA,
)

from ..llm_client import (
    call_openai,
)


# -----------------------------------
# GENERATE INTERVIEW SESSION
# -----------------------------------

def generate_interview_service(
    resume_id: int,
    job_description: str,
    target_role: str,
    num_questions: int,
    user,
    db: Session,
):

    resume = db.get(
        Resume,
        resume_id
    )

    if not resume or resume.user_id != user.id:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    suggestion = db.exec(
        select(ResumeSuggestion).where(
            ResumeSuggestion.resume_id == resume_id
        )
    ).first()

    parsed_text = ""

    if suggestion:

        parsed_text = (
            suggestion.parsed_text or ""
        )

    prompt = f"""
Generate {num_questions} interview questions
for the role: {target_role}

Return ONLY JSON:

{{"questions":["Question 1","Question 2"]}}

Resume:
{parsed_text}

Job Description:
{job_description}
"""

    ai_response = call_openai(
        prompt
    ).strip()

    try:

        data = json.loads(
            ai_response
        )

        questions = data.get(
            "questions",
            []
        )

    except Exception:

        questions = [
            q.strip("- ").strip()
            for q in ai_response.splitlines()
            if q.strip()
        ]

    if not questions:

        questions = [
            "Tell me about yourself.",
            "Explain a challenging project."
        ]

    session_obj = InterviewSession(
        user_id=user.id,
        resume_id=resume_id,
        job_description=job_description,
        target_role=target_role,
    )

    db.add(
        session_obj
    )

    db.commit()

    db.refresh(
        session_obj
    )

    for i, question in enumerate(
        questions
    ):

        db.add(
            InterviewQnA(
                session_id=session_obj.id,
                question_index=i,
                question_text=question,
            )
        )

    db.commit()

    return {
        "session_id": session_obj.id,
        "questions": [
            {
                "question": q
            }
            for q in questions
        ]
    }


# -----------------------------------
# SUBMIT ANSWER
# -----------------------------------

# -----------------------------------
# SUBMIT ANSWER
# -----------------------------------

def submit_answer_service(
    session_id: int,
    question_index: int,
    answer: str,
    db: Session,
):

    qa = db.exec(
        select(InterviewQnA).where(
            InterviewQnA.session_id == session_id,
            InterviewQnA.question_index == question_index,
        )
    ).first()

    if not qa:

        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    feedback = call_openai(
        f"""
Evaluate this interview answer professionally.

Question:
{qa.question_text}

Answer:
{answer}

Return EXACTLY in this format:

SCORE: <number between 0 and 10>

STRENGTHS:
<strengths>

WEAKNESSES:
<weaknesses>

IMPROVEMENTS:
<improvement suggestions>
"""
    )

    score = 0

    try:

        first_line = (
            feedback.splitlines()[0]
        )

        if "SCORE:" in first_line:

            score = float(
                first_line.replace(
                    "SCORE:",
                    ""
                ).strip()
            )

    except Exception:

        score = 0

    qa.user_answer = answer

    qa.ai_feedback = feedback

    qa.score = score

    db.add(
        qa
    )

    db.commit()

    return {
        "feedback": feedback,
        "score": score
    }
    
    # -----------------------------------
# INTERVIEW SUMMARY
# -----------------------------------

def get_interview_summary_service(
    session_id: int,
    db: Session,
):

    qnas = db.exec(
        select(InterviewQnA).where(
            InterviewQnA.session_id == session_id
        )
    ).all()

    if not qnas:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    scores = [
        q.score
        for q in qnas
        if q.score is not None
    ]

    total_questions = len(qnas)

    answered_questions = len(
        [
            q
            for q in qnas
            if q.user_answer
        ]
    )

    average_score = (
        round(
            sum(scores) / len(scores),
            2
        )
        if scores
        else 0
    )

    highest_score = (
        max(scores)
        if scores
        else 0
    )

    lowest_score = (
        min(scores)
        if scores
        else 0
    )

    return {
        "session_id": session_id,
        "questions_total": total_questions,
        "questions_answered": answered_questions,
        "average_score": average_score,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
    }