import os, tempfile
from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel

app = FastAPI(title="ASR Service")
model = WhisperModel(os.getenv("WHISPER_MODEL","large-v3"), device="cuda", compute_type="float16")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    segments, info = model.transcribe(path, beam_size=5, vad_filter=True, word_timestamps=True)
    out = {
        "language": info.language,
        "duration": info.duration,
        "segments": [{
            "start": s.start, "end": s.end, "text": s.text,
            "words": [{"start": w.start, "end": w.end, "word": w.word} for w in (s.words or [])]
        } for s in segments]
    }
    try: os.unlink(path)
    except: pass
    return out

@app.get("/health")
def health(): return {"ok": True}
