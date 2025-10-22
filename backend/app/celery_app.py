"""Celery application configuration for the Writers API.

This module initializes and configures the Celery application, which is used for
running background tasks asynchronously. It sets up the message broker and
result backend using Redis, and defines various task execution settings,
including serialization, time limits, and task routing.

The Celery app instance created here is used by both the FastAPI application to
send tasks and by the Celery workers to execute them.
"""
import os
from celery import Celery

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_QUEUE_DB = os.getenv("REDIS_QUEUE_DB", "2")

# Construct broker and backend URLs
broker_url = f"{REDIS_URL}/{REDIS_QUEUE_DB}"
result_backend = f"{REDIS_URL}/{REDIS_QUEUE_DB}"

# Create Celery app
celery_app = Celery(
    "writers_tasks",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks", "worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Serialization settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone settings (matching database UTC timezone)
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,  # Store results persistently in Redis
    
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task routing
    task_routes={
        'app.tasks.process_task_file': {'queue': 'default'},
        'app.tasks.transcribe_audio': {'queue': 'media'},
        'app.tasks.process_video': {'queue': 'media'},
        'app.tasks.analyze_text': {'queue': 'default'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
