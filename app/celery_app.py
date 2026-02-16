# backend/app/celery_app.py

from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis is optional — if not running Redis, Celery won't start,
# but backend can still run because tasks are delayed (not executed).
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)
