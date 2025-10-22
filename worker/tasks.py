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
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
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

# =============================================================================
# Model Configuration (Singleton Pattern for Warm Start Optimization)
# =============================================================================
# تنظیمات مدل برای بهینه‌سازی warm start و مدیریت حافظه

# Model configuration from environment variables
MODEL_DEVICE = os.getenv("MODEL_DEVICE", "cuda")  # cuda, cpu
MODEL_DEVICE_INDEX = int(os.getenv("MODEL_DEVICE_INDEX", "0"))  # GPU index (0, 1, 2, ...)
MODEL_COMPUTE_TYPE = os.getenv("MODEL_COMPUTE_TYPE", "float16")  # float16, int8, float32
MODEL_NAME = os.getenv("MODEL_NAME", "base")  # tiny, base, small, medium, large

# Resource monitoring configuration
VRAM_WARNING_THRESHOLD = float(os.getenv("VRAM_WARNING_THRESHOLD", "0.85"))  # 85% usage
RAM_WARNING_THRESHOLD = float(os.getenv("RAM_WARNING_THRESHOLD", "0.90"))  # 90% usage
ENABLE_RESOURCE_MONITORING = os.getenv("ENABLE_RESOURCE_MONITORING", "true").lower() == "true"


class ModelSingleton:
    """Manages the lifecycle of a transcription model to optimize performance.

    This class implements the singleton pattern to ensure that the transcription
    model is loaded into memory only once. This approach significantly reduces
    the overhead of model initialization for subsequent tasks, leading to
    faster "warm start" times.

    The model's configuration, such as the device (CPU/GPU), compute type, and
    model size, is determined by environment variables.

    Attributes:
        _instance: The single instance of the ModelSingleton class.
        _lock: A thread lock to ensure thread-safe initialization.
        _model: The loaded transcription model.
    """
    
    _instance = None
    _lock = threading.Lock()
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self):
        """Retrieves the transcription model, initializing it if necessary.

        Returns:
            The transcription model instance.
        """
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._initialize_model()
        return self._model
    
    def _initialize_model(self):
        """Initializes the transcription model based on environment settings."""
        logger.info(
            f"Initializing transcription model: {MODEL_NAME} on "
            f"{MODEL_DEVICE}:{MODEL_DEVICE_INDEX} with {MODEL_COMPUTE_TYPE}"
        )
        
        try:
            # Check available resources before loading model
            check_available_resources()
            
            # For production, uncomment and use actual Whisper model:
            # import whisper
            # self._model = whisper.load_model(
            #     MODEL_NAME,
            #     device=f"{MODEL_DEVICE}:{MODEL_DEVICE_INDEX}",
            #     download_root=os.path.join(STORAGE_ROOT, "models"),
            # )
            
            # Mock model for development
            self._model = {
                "name": MODEL_NAME,
                "device": MODEL_DEVICE,
                "device_index": MODEL_DEVICE_INDEX,
                "compute_type": MODEL_COMPUTE_TYPE,
                "initialized_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Model initialized successfully")
            log_resource_usage("After model initialization")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}", exc_info=True)
            raise


# Global model singleton instance
model_singleton = ModelSingleton()


# =============================================================================
# Resource Monitoring Functions
# =============================================================================

def get_gpu_memory_info() -> Optional[Dict[str, Any]]:
    """Retrieves GPU memory and utilization information.

    This function uses the `nvidia-smi` command to query the memory usage and
    utilization of a specific GPU.

    Returns:
        A dictionary containing GPU memory and utilization details, or None if
        the information cannot be retrieved.
    """
    try:
        import subprocess
        result = subprocess.run(
            [
                'nvidia-smi',
                '--query-gpu=memory.total,memory.used,memory.free,utilization.gpu',
                '--format=csv,noheader,nounits',
                f'--id={MODEL_DEVICE_INDEX}'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            total, used, free, util = result.stdout.strip().split(',')
            return {
                'total_mb': float(total),
                'used_mb': float(used),
                'free_mb': float(free),
                'utilization_percent': float(util),
                'usage_ratio': float(used) / float(total) if float(total) > 0 else 0
            }
    except Exception as e:
        logger.debug(f"Could not get GPU memory info: {str(e)}")
    
    return None


def get_ram_memory_info() -> Dict[str, Any]:
    """Retrieves system RAM information.

    Returns:
        A dictionary containing details about the system's RAM usage.
    """
    mem = psutil.virtual_memory()
    info: Dict[str, Any] = {
        'total_mb': mem.total / (1024 * 1024),
        'used_mb': mem.used / (1024 * 1024),
        'available_mb': mem.available / (1024 * 1024),
        'percent': mem.percent,
        'usage_ratio': mem.percent / 100.0
    }
    return info


def log_resource_usage(context: str = ""):
    """Logs the current VRAM and RAM usage.

    Args:
        context (str): A string indicating the context in which the resource
                       usage is being logged.
    """
    if not ENABLE_RESOURCE_MONITORING:
        return
    
    try:
        # Log RAM usage
        ram_info = get_ram_memory_info()
        logger.info(
            f"[{context}] RAM: {ram_info['used_mb']:.0f}MB / "
            f"{ram_info['total_mb']:.0f}MB ({ram_info['percent']:.1f}%)"
        )
        
        # Log GPU memory usage if available
        gpu_info = get_gpu_memory_info()
        if gpu_info:
            logger.info(
                f"[{context}] VRAM (GPU {MODEL_DEVICE_INDEX}): "
                f"{gpu_info['used_mb']:.0f}MB / {gpu_info['total_mb']:.0f}MB "
                f"({gpu_info['usage_ratio']*100:.1f}%) | "
                f"GPU Utilization: {gpu_info['utilization_percent']:.1f}%"
            )
    except Exception as e:
        logger.warning(f"Failed to log resource usage: {str(e)}")


def check_available_resources():
    """Checks for sufficient system resources to prevent OOM errors.

    This function logs a warning if RAM or VRAM usage exceeds predefined
    thresholds, indicating a risk of an Out Of Memory (OOM) error.
    """
    if not ENABLE_RESOURCE_MONITORING:
        return
    
    # Check RAM
    ram_info = get_ram_memory_info()
    if ram_info['usage_ratio'] > RAM_WARNING_THRESHOLD:
        warning_msg = (
            f"High RAM usage detected: {ram_info['percent']:.1f}% "
            f"(threshold: {RAM_WARNING_THRESHOLD*100}%). "
            f"Risk of OOM!"
        )
        logger.warning(warning_msg)
        # Note: We log warning but don't raise to allow graceful degradation
    
    # Check VRAM if GPU is available
    gpu_info = get_gpu_memory_info()
    if gpu_info and gpu_info['usage_ratio'] > VRAM_WARNING_THRESHOLD:
        warning_msg = (
            f"High VRAM usage detected on GPU {MODEL_DEVICE_INDEX}: "
            f"{gpu_info['usage_ratio']*100:.1f}% "
            f"(threshold: {VRAM_WARNING_THRESHOLD*100}%). "
            f"Risk of OOM!"
        )
        logger.warning(warning_msg)
        # Note: We log warning but don't raise to allow graceful degradation


def update_task_in_db(task_id: UUID, **fields) -> bool:
    """Updates a task's information in the database.

    Args:
        task_id (UUID): The ID of the task to update.
        **fields: The fields of the task to update.

    Returns:
        bool: True if the update was successful, otherwise False.
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
    """Transcribes an audio file using the singleton model.

    This function simulates the audio transcription process. In a production
    environment, it would use a speech-to-text model like OpenAI's Whisper.

    Args:
        audio_path (str): The path to the audio file.

    Returns:
        Dict[str, Any]: A dictionary containing the transcription result.
    """
    logger.info(f"Processing audio file: {audio_path}")
    
    # Check resources before processing
    log_resource_usage("Before transcription")
    check_available_resources()
    
    # Get singleton model instance (warm start optimization)
    model = model_singleton.get_model()
    logger.info(f"Using model: {model}")
    
    # For now, this is a mock implementation
    # In production, uncomment below to use actual Whisper transcription:
    #
    # result = model.transcribe(
    #     audio_path,
    #     language="fa",  # or auto-detect
    #     task="transcribe",
    #     fp16=(MODEL_COMPUTE_TYPE == "float16"),
    # )
    # 
    # return {
    #     "transcription": result["text"],
    #     "language": result.get("language", "fa"),
    #     "duration": result.get("duration", 0),
    #     "segments": result.get("segments", []),
    #     "timestamp": datetime.utcnow().isoformat(),
    #     "source_file": os.path.basename(audio_path),
    #     "model_config": {
    #         "name": MODEL_NAME,
    #         "device": MODEL_DEVICE,
    #         "compute_type": MODEL_COMPUTE_TYPE
    #     }
    # }
    
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
        "source_file": os.path.basename(audio_path),
        "model_config": {
            "name": MODEL_NAME,
            "device": MODEL_DEVICE,
            "device_index": MODEL_DEVICE_INDEX,
            "compute_type": MODEL_COMPUTE_TYPE
        }
    }
    
    # Log resources after processing
    log_resource_usage("After transcription")
    
    return result


@celery_app.task(name="transcribe_audio", bind=True)
def transcribe_audio(self, task_id: str, audio_file_path: str) -> Dict[str, Any]:
    """Celery task for transcribing audio files.

    This task orchestrates the audio transcription process. It updates the task
    status in the database, processes the audio file, saves the result, and
    handles any errors that occur.

    Args:
        task_id (str): The ID of the task.
        audio_file_path (str): The path to the audio file to be transcribed.

    Returns:
        Dict[str, Any]: A dictionary with the result of the transcription.
    """
    task_uuid = UUID(task_id)
    logger.info(f"Starting audio transcription for task {task_id}")
    
    # Log initial resource usage
    log_resource_usage("Task start")
    
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
        
        # Log final resource usage
        log_resource_usage("Task completed successfully")
        
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
        
        # Log resource usage on error (may help diagnose OOM issues)
        log_resource_usage("Task failed with error")
        
        # Update task status to FAILED
        update_task_in_db(task_uuid, status=TaskStatus.FAILED)
        
        return {
            "status": "error",
            "task_id": task_id,
            "error": str(e),
            "error_type": type(e).__name__
        }
