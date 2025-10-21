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
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)
