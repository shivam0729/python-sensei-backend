# backend/app/db.py

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./sensei.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def get_db():
    """
    FastAPI dependency that provides a DB session
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
