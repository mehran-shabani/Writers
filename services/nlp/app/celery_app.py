import os
import logging
from celery import Celery
from .models import SessionLocal, Job
from .storage import upload_bytes, download_to_bytes
from .pipeline import run_pipeline

logger = logging.getLogger(__name__)

celery = Celery(__name__, broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))
celery.conf.update(
    result_backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
)


@celery.task(name="run_pipeline_task", queue="default", bind=True)
def run_pipeline_task(self, job_id: str):
    """Process audio file through ASR and NLP pipeline."""
    db = SessionLocal()
    job = None
    
    try:
        job = db.get(Job, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        job.status = "processing"
        db.commit()
        
        # Download audio
        audio = download_to_bytes(job.audio_key)
        
        # Run pipeline
        asr_url = os.getenv("ASR_URL", "http://asr:7000/transcribe")
        md, pdf = run_pipeline(audio_bytes=audio, asr_url=asr_url)
        
        # Upload outputs
        md_key = f"jobs/{job_id}/output.md"
        pdf_key = f"jobs/{job_id}/output.pdf"
        upload_bytes(md_key, md.encode("utf-8"), "text/markdown")
        upload_bytes(pdf_key, pdf, "application/pdf")
        
        # Update job
        job.md_key = md_key
        job.pdf_key = pdf_key
        job.status = "done"
        db.commit()
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.exception(f"Job {job_id} failed: {e}")
        if job:
            job.status = "error"
            job.error = str(e)[:1000]  # Truncate long errors
            db.commit()
        raise
    finally:
        db.close()
