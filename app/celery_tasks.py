from sqlmodel import Session

from .celery_worker import celery_app

from .db import engine

from .models import (
    Resume,
    ResumeSuggestion,
)

from .tasks import (
    process_resume_and_generate_suggestions
)

from .core.logger import logger

import asyncio

from .websocket_manager import manager


@celery_app.task(
    name="app.celery_tasks.process_resume_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_resume_task(
    self,
    resume_id: int,
    user_id: int,
):

    db = Session(engine)

    try:

        resume = db.get(
            Resume,
            resume_id
        )

        if resume:

            resume.processing_status = "processing"

            db.add(resume)
            db.commit()

            # Send realtime update
            asyncio.run(
                manager.send_message(
                    user_id,
                    {
                        "status": "processing",
                        "resume_id": resume_id,
                    }
                )
            )

        # AI processing
        result = process_resume_and_generate_suggestions(
            resume_id
        )

        suggestion = ResumeSuggestion(
            user_id=user_id,
            resume_id=resume_id,
            parsed_text=result["parsed_text"],
            suggestions=result["suggestions"],
        )

        db.add(suggestion)

        if resume:

            resume.processing_status = "completed"

            resume.processing_error = None

            db.add(resume)

        db.commit()

        # Send realtime completed update
        asyncio.run(
            manager.send_message(
                user_id,
                {
                    "status": "completed",
                    "resume_id": resume_id,
                }
            )
        )

        logger.info(
            f"Celery AI processing completed "
            f"for resume_id={resume_id}"
        )

    except Exception as e:

        logger.exception(
            f"Celery AI processing failed: {str(e)}"
        )

        resume = db.get(
            Resume,
            resume_id
        )

        # Mark failed only after retries exhausted
        if self.request.retries >= 3:

            if resume:

                resume.processing_status = "failed"

                resume.processing_error = str(e)

                db.add(resume)

                db.commit()

                # Send realtime failed update
                asyncio.run(
                    manager.send_message(
                        user_id,
                        {
                            "status": "failed",
                            "resume_id": resume_id,
                            "error": str(e),
                        }
                    )
                )

        raise self.retry(exc=e)

    finally:

        db.close()