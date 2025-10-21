from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/writers_db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            ...
    """
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
    SQLModel.metadata.create_all(engine)
