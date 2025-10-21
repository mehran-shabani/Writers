from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..models.task import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new task with file upload"""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    user_id: UUID
    file_path: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Schema for task list response"""
    tasks: list[TaskResponse]
    total: int
