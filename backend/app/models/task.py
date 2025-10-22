from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Enum as SQLAlchemyEnum


class TaskStatus(str, Enum):
    """Enumeration for the status of a task."""
    PENDING = "pending"
    PROCESSING = "processing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(SQLModel, table=True):
    """Represents a task in the database.

    Attributes:
        id (UUID): The unique identifier for the task.
        title (str): The title of the task.
        description (Optional[str]): A description of the task.
        status (TaskStatus): The current status of the task.
        user_id (UUID): The ID of the user who owns the task.
        file_path (Optional[str]): The path to a file associated with the task.
        result_path (Optional[str]): The path to the result of the task.
        due_date (Optional[datetime]): The due date for the task.
        completed_at (Optional[datetime]): The timestamp when the task was completed.
        created_at (datetime): The timestamp when the task was created.
        updated_at (datetime): The timestamp when the task was last updated.
    """
    __tablename__ = "tasks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(
        sa_column=Column(SQLAlchemyEnum(TaskStatus), default=TaskStatus.PENDING)
    )
    user_id: UUID = Field(foreign_key="users.id", index=True)
    file_path: Optional[str] = Field(default=None, max_length=500)
    result_path: Optional[str] = Field(default=None, max_length=500)
    due_date: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
