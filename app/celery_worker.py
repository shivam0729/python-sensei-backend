from celery import Celery

celery_app = Celery(
    "python_sensei",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_track_started=True,
)

# IMPORTANT
import app.celery_tasks