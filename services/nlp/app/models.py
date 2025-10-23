import os
import uuid
import datetime as dt
from sqlalchemy import create_engine, Column, String, DateTime, Text, Index, Enum
from sqlalchemy.orm import declarative_base, sessionmaker

DSN = os.getenv("POSTGRES_DSN")
engine = create_engine(DSN, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(
        Enum("queued", "processing", "done", "error", name="job_status"),
        default="queued",
        nullable=False
    )
    error = Column(Text, nullable=True)
    audio_key = Column(String, nullable=True)
    md_key = Column(String, nullable=True)
    pdf_key = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.timezone.utc),
        onupdate=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False
    )
