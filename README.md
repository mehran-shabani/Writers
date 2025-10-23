# Writers Notetaker (ASR → NLP → MD/PDF)

Multi-service pipeline for converting audio lectures to structured Persian notes with Markdown and PDF output.

## Quick Start

```bash
cp .env.example .env
make build
make up
make migrate
make init-bucket
```

## Usage

**Upload audio file:**

```bash
curl -F "file=@sample.m4a" http://localhost:8001/api/upload
```

**Check job status:**

```bash
curl http://localhost:8001/api/jobs/<job_id>
```

## Services

- **ASR**: Whisper (GPU) - audio transcription
- **NLP**: FastAPI orchestrator + Celery workers
- **Storage**: MinIO (S3-compatible)
- **Database**: PostgreSQL
- **Queue**: Redis + Celery

## Requirements

- Docker + Docker Compose
- NVIDIA GPU + nvidia-container-toolkit (for ASR)
- 16GB+ RAM recommended
