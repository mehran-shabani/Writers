# Writers Notetaker (ASR → NLP → MD/PDF)

## Run
```bash
cp .env.example .env
make build
make up
make migrate
make init-bucket
```

## Use
- Upload:
```bash
curl -F "file=@sample.m4a" http://localhost:8001/api/upload
```

- Status:
```bash
curl http://localhost:8001/api/jobs/<job_id>
```
