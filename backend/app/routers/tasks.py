import os
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from datetime import datetime

from ..db import get_session
from ..models.task import Task, TaskStatus
from ..auth.dependencies import get_current_user
from ..models.user import User
from .schemas import TaskCreate, TaskResponse, TaskListResponse
from ..tasks import process_task_file

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# Get storage root from environment
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "/var/app/storage")


@router.post("", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task with optional file upload.
    
    Args:
        title: Task title
        description: Task description (optional)
        due_date: Task due date (optional)
        file: Uploaded file (optional)
        session: Database session
        current_user: Authenticated user
    
    Returns:
        TaskResponse with 202 Accepted status
    """
    # Handle file upload if provided
    file_path = None
    if file:
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(STORAGE_ROOT, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    # Create task in database
    new_task = Task(
        title=title,
        description=description,
        status=TaskStatus.PENDING,
        user_id=current_user.id,
        file_path=file_path,
        due_date=due_date,
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    
    # Queue Celery task for background processing
    if file_path:
        process_task_file.delay(str(new_task.id), file_path)
        # Update status to IN_PROGRESS
        new_task.status = TaskStatus.IN_PROGRESS
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
    
    return TaskResponse.model_validate(new_task)


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TaskStatus] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of tasks for the current user.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status_filter: Filter by task status (optional)
        session: Database session
        current_user: Authenticated user
    
    Returns:
        TaskListResponse with list of tasks and total count
    """
    # Build query
    statement = select(Task).where(Task.user_id == current_user.id)
    
    if status_filter:
        statement = statement.where(Task.status == status_filter)
    
    # Get total count
    count_statement = select(Task).where(Task.user_id == current_user.id)
    if status_filter:
        count_statement = count_statement.where(Task.status == status_filter)
    
    total = len(session.exec(count_statement).all())
    
    # Apply pagination and ordering
    statement = statement.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    
    tasks = session.exec(statement).all()
    
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    
    Args:
        task_id: UUID of the task
        session: Database session
        current_user: Authenticated user
    
    Returns:
        TaskResponse
    
    Raises:
        HTTPException: If task not found or user doesn't have access
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this task"
        )
    
    return TaskResponse.model_validate(task)


@router.get("/{task_id}/result")
async def get_task_result(
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the transcription result for a specific task.
    
    Args:
        task_id: UUID of the task
        session: Database session
        current_user: Authenticated user
    
    Returns:
        JSON with transcription result
    
    Raises:
        HTTPException: If task not found, user doesn't have access, or result not ready
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this task"
        )
    
    # Check if task is completed and has a result
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is not completed yet. Current status: {task.status}"
        )
    
    if not task.result_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result file not found for this task"
        )
    
    # Read and return the result file
    try:
        if os.path.exists(task.result_path):
            with open(task.result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            return result_data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result file not found on disk"
            )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse result file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading result file: {str(e)}"
        )
