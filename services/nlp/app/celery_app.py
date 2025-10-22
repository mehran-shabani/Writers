import os, requests
from celery import Celery
from .models import SessionLocal, Job
from .storage import upload_bytes
from .pipeline import run_pipeline

celery = Celery(__name__, broker=os.getenv("REDIS_URL","redis://redis:6379/0"))
celery.conf.update(result_backend=os.getenv("REDIS_URL","redis://redis:6379/0"))

@celery.task(name="run_pipeline_task", queue="default")
def run_pipeline_task(job_id: str):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job: return
        job.status = "processing"; db.commit()
        from .storage import download_to_bytes
        audio = download_to_bytes(job.audio_key)
        md, pdf = run_pipeline(audio_bytes=audio, asr_url=os.getenv("ASR_URL","http://asr:7000/transcribe"))
        md_key = f"jobs/{job_id}/output.md"
        pdf_key = f"jobs/{job_id}/output.pdf"
        upload_bytes(md_key, md.encode("utf-8"), "text/markdown")
        upload_bytes(pdf_key, pdf, "application/pdf")
        job.md_key, job.pdf_key, job.status = md_key, pdf_key, "done"
        db.commit()
    except Exception as e:
        job = db.get(Job, job_id)
        if job:
            job.status = "error"; job.error = str(e)
            db.commit()
    finally:
        db.close()
