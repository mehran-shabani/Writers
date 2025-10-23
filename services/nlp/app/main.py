import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .schemas import UploadResponse, JobStatus
from .models import SessionLocal, Job
from .storage import upload_bytes, presign
from .celery_app import run_pipeline_task

app = FastAPI(title="NLP/Orchestrator Service")

# Max file size: 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(default=...)):
    """Upload audio file for processing."""
    db = SessionLocal()
    try:
        # Validate file size
        data = await file.read()
        if len(data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_FILE_SIZE} bytes)"
            )
        
        job = Job()
        db.add(job)
        db.commit()
        
        key = f"jobs/{job.id}/audio/{file.filename}"
        upload_bytes(key, data, file.content_type or "application/octet-stream")
        job.audio_key = key
        db.commit()
        
        run_pipeline_task.delay(job.id)
        return UploadResponse(job_id=job.id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        db.close()


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str):
    """Get job processing status and output URLs."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return JSONResponse({"detail": "not found"}, status_code=404)
        
        md_url = presign(job.md_key) if job.md_key else None
        pdf_url = presign(job.pdf_key) if job.pdf_key else None
        
        return JobStatus(
            job_id=job.id,
            status=job.status,
            error=job.error,
            md_key=job.md_key,
            pdf_key=job.pdf_key,
            md_url=md_url,
            pdf_url=pdf_url
        )
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=False)
