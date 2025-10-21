from typing import Generator, Optional
from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/writers_db")

# Engine will be created lazily
_engine: Optional[Engine] = None
_SessionLocal = None


def get_engine() -> Engine:
    """
    Get or create the database engine.
    Lazy initialization to avoid import errors when psycopg2 is not installed.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            echo=True,  # Set to False in production
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def get_session_local():
    """Get or create session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
            class_=Session,
        )
    return _SessionLocal


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            ...
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables():
    """
    Create all tables in the database.
    This is mainly for development/testing.
    In production, use Alembic migrations.
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(get_engine())
