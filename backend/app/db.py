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
    """Initializes and returns the database engine.

    The engine is created with a connection pool and pre-ping to ensure
    database connectivity. It is initialized lazily to prevent import errors
    when database drivers are not installed.

    Returns:
        Engine: The SQLAlchemy engine instance.
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
    """Creates and returns a session factory for generating database sessions.

    The session factory is configured to not autocommit or autoflush, and is
    bound to the database engine.

    Returns:
        sessionmaker: The session factory instance.
    """
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
    """Provides a database session for a single request.

    This function is a FastAPI dependency that yields a database session and
    ensures that the session is closed after the request is complete.

    Yields:
        Generator[Session, None, None]: A generator that yields a database session.
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables():
    """Creates all database tables defined by the SQLModel metadata.

    This function is intended for development and testing purposes. In a
    production environment, database migrations with Alembic should be used.
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(get_engine())
