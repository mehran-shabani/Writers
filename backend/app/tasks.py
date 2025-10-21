import os
import time
from uuid import UUID
from .celery_app import celery_app
from .db import get_session_local
from .models.task import Task, TaskStatus
from sqlmodel import select


@celery_app.task(name="process_task_file")
def process_task_file(task_id: str, file_path: str):
    """
    Process uploaded file for a task.
    
    This is a background task that processes the uploaded file.
    In a real application, this could perform various operations like:
    - File validation
    - Virus scanning
    - Format conversion
    - Data extraction
    - AI processing
    
    Args:
        task_id: UUID of the task as string
        file_path: Path to the uploaded file
    
    Returns:
        dict: Result of processing
    """
    try:
        # Simulate file processing
        time.sleep(2)  # Simulate some processing time
        
        # Update task status in database
        SessionLocal = get_session_local()
        session = SessionLocal()
        
        try:
            task_uuid = UUID(task_id)
            statement = select(Task).where(Task.id == task_uuid)
            task = session.exec(statement).first()
            
            if task:
                task.status = TaskStatus.COMPLETED
                session.add(task)
                session.commit()
                session.refresh(task)
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "file_path": file_path,
                    "message": "File processed successfully"
                }
            else:
                return {
                    "status": "error",
                    "task_id": task_id,
                    "message": "Task not found"
                }
        finally:
            session.close()
            
    except Exception as e:
        # Update task status to cancelled on error
        SessionLocal = get_session_local()
        session = SessionLocal()
        
        try:
            task_uuid = UUID(task_id)
            statement = select(Task).where(Task.id == task_uuid)
            task = session.exec(statement).first()
            
            if task:
                task.status = TaskStatus.CANCELLED
                session.add(task)
                session.commit()
        finally:
            session.close()
        
        return {
            "status": "error",
            "task_id": task_id,
            "message": str(e)
        }
