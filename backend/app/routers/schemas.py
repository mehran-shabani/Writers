from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..models.task import TaskStatus


class TaskCreate(BaseModel):
    """Defines the schema for creating a new task.

    Attributes:
        title (str): The title of the task.
        description (Optional[str]): A description of the task.
        due_date (Optional[datetime]): The due date for the task.
    """
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Defines the schema for a task response.

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
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    user_id: UUID
    file_path: Optional[str]
    result_path: Optional[str]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Defines the schema for a list of tasks.

    Attributes:
        tasks (list[TaskResponse]): A list of tasks.
        total (int): The total number of tasks.
    """
    tasks: list[TaskResponse]
    total: int
