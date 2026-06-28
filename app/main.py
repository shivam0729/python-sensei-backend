# backend/app/main.py
from .core.config import settings
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
import os, json, re
from .api.auth_routes import router as auth_router
from .api.user_routes import router as user_router

from .db import get_db
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
from .schemas.auth_schema import (
    SignupRequest,
    LoginRequest,
    AuthResponse
)
from .services.resume_service import (
    upload_resume_service
)
from .api.resume_routes import (
    router as resume_router
)

from .dependencies.auth_dependency import (
    get_current_user
)

from .api.interview_routes import (
    router as interview_router
)

from .api.job_optimization_routes import (
    router as job_optimization_router
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

from .core.middleware import (
    RequestLoggingMiddleware
)

from .api.cover_letter_routes import (
    router as cover_letter_router
)

from fastapi import WebSocket

from .websocket_manager import manager

import asyncio
from fastapi import WebSocketDisconnect

from .api.dashboard_routes import (
    router as dashboard_router
)
from .db import create_db_and_tables

app = FastAPI(title="Python Sensei API")
# Create uploads directory before mounting
os.makedirs("./uploads", exist_ok=True)

# Mount uploads folder
app.mount(
    "/uploads",
    StaticFiles(directory="./uploads"),
    name="uploads",
)


app.add_middleware(
    RequestLoggingMiddleware
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Python Sensei API Running Successfully",
        "status": "healthy"
    }



@app.on_event("startup")
def on_startup():
    os.makedirs("./uploads", exist_ok=True)
    create_db_and_tables()

print(settings.ENVIRONMENT)



@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:

        manager.disconnect(
            user_id
        )
# ---------------------------
# Auth
# ---------------------------
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(job_optimization_router)
app.include_router(cover_letter_router)
app.include_router(dashboard_router)