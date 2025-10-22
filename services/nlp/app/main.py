import os, uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from .schemas import UploadResponse, JobStatus
from .models import SessionLocal, Job, engine
from .storage import upload_bytes, presign
from .celery_app import run_pipeline_task

app = FastAPI(title="NLP/Orchestrator Service")

@app.get("/health")
def health(): return {"ok": True}

@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    db = SessionLocal()
    try:
        job = Job()
        db.add(job); db.commit()
        key = f"jobs/{job.id}/audio/{file.filename}"
        data = await file.read()
        upload_bytes(key, data, file.content_type or "application/octet-stream")
        job.audio_key = key; db.commit()
        run_pipeline_task.delay(job.id)
        return UploadResponse(job_id=job.id)
    finally:
        db.close()

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return JSONResponse({"detail":"not found"}, status_code=404)
        md_url = presign(job.md_key) if job.md_key else None
        pdf_url = presign(job.pdf_key) if job.pdf_key else None
        return JobStatus(job_id=job.id, status=job.status, error=job.error,
                         md_key=job.md_key, pdf_key=job.pdf_key, md_url=md_url, pdf_url=pdf_url)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=False)
