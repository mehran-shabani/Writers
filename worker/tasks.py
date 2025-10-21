"""
Audio transcription worker tasks.

This module implements the transcribe_audio task that:
1. Updates database status to PROCESSING
2. Reads audio file from /storage/uploads/
3. Processes the audio (transcription)
4. Saves result to /storage/results/
5. Updates database with result_path, completed_at, and status=COMPLETED
6. On error, sets status=FAILED and logs appropriately
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

# Add backend to Python path to access shared code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.celery_app import celery_app
from app.db import get_session_local
from app.models.task import Task, TaskStatus
from sqlmodel import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "/storage")
UPLOADS_DIR = os.path.join(STORAGE_ROOT, "uploads")
RESULTS_DIR = os.path.join(STORAGE_ROOT, "results")

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def update_task_in_db(task_id: UUID, **fields) -> bool:
    """
    Update task fields in database.
    
    Args:
        task_id: UUID of the task
        **fields: Fields to update (status, result_path, completed_at, etc.)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        SessionLocal = get_session_local()
        session = SessionLocal()
        
        try:
            statement = select(Task).where(Task.id == task_id)
            task = session.exec(statement).first()
            
            if task:
                for key, value in fields.items():
                    setattr(task, key, value)
                
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                logger.info(f"Task {task_id} updated successfully: {fields}")
                return True
            else:
                logger.error(f"Task {task_id} not found in database")
                return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {str(e)}", exc_info=True)
        return False


def process_audio_transcription(audio_path: str) -> Dict[str, Any]:
    """
    Process audio file and perform transcription.
    
    In production, this would integrate with services like:
    - OpenAI Whisper API
    - Google Speech-to-Text
    - AWS Transcribe
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        dict: Transcription result with metadata
    """
    # For now, this is a mock implementation
    # In production, replace this with actual transcription service
    
    logger.info(f"Processing audio file: {audio_path}")
    
    # Simulate processing
    import time
    time.sleep(2)
    
    # Mock transcription result
    result = {
        "transcription": "این یک متن نمونه از رونویسی صوتی است",
        "language": "fa",
        "duration": 120,
        "confidence": 0.95,
        "timestamp": datetime.utcnow().isoformat(),
        "source_file": os.path.basename(audio_path)
    }
    
    return result


@celery_app.task(name="transcribe_audio", bind=True)
def transcribe_audio(self, task_id: str, audio_file_path: str) -> Dict[str, Any]:
    """
    Transcribe audio file to text.
    
    This task:
    1. Updates database status to PROCESSING
    2. Reads the audio file from /storage/uploads/
    3. Performs transcription
    4. Saves output to /storage/results/
    5. Updates result_path, completed_at, and status=COMPLETED
    6. On error, sets status=FAILED and logs appropriately
    
    Args:
        task_id: UUID of the task as string
        audio_file_path: Relative path to the audio file in uploads directory
        
    Returns:
        dict: Result of transcription with status and metadata
    """
    task_uuid = UUID(task_id)
    logger.info(f"Starting audio transcription for task {task_id}")
    
    try:
        # Step 1: Update status to PROCESSING
        logger.info(f"Updating task {task_id} status to PROCESSING")
        if not update_task_in_db(task_uuid, status=TaskStatus.PROCESSING):
            raise Exception("Failed to update task status to PROCESSING")
        
        # Step 2: Read file from /storage/uploads/
        # Handle both absolute and relative paths
        if os.path.isabs(audio_file_path):
            full_audio_path = audio_file_path
        else:
            full_audio_path = os.path.join(UPLOADS_DIR, audio_file_path)
        
        logger.info(f"Reading audio file from: {full_audio_path}")
        
        if not os.path.exists(full_audio_path):
            raise FileNotFoundError(f"Audio file not found: {full_audio_path}")
        
        # Step 3: Process audio transcription
        logger.info(f"Processing audio transcription for: {full_audio_path}")
        transcription_result = process_audio_transcription(full_audio_path)
        
        # Step 4: Save output to /storage/results/
        result_filename = f"{task_id}_transcription.json"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        
        logger.info(f"Saving transcription result to: {result_path}")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(transcription_result, f, ensure_ascii=False, indent=2)
        
        # Step 5: Update database with success status
        logger.info(f"Updating task {task_id} with completion data")
        update_task_in_db(
            task_uuid,
            status=TaskStatus.COMPLETED,
            result_path=result_path,
            completed_at=datetime.utcnow()
        )
        
        logger.info(f"Audio transcription completed successfully for task {task_id}")
        
        return {
            "status": "success",
            "task_id": task_id,
            "result_path": result_path,
            "transcription": transcription_result
        }
        
    except Exception as e:
        # Step 6: On error, set status to FAILED and log
        logger.error(
            f"Audio transcription failed for task {task_id}: {str(e)}",
            exc_info=True
        )
        
        # Update task status to FAILED
        update_task_in_db(task_uuid, status=TaskStatus.FAILED)
        
        return {
            "status": "error",
            "task_id": task_id,
            "error": str(e),
            "error_type": type(e).__name__
        }
