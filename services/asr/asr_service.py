import os
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

app = FastAPI(title="ASR Service")

# Load model at startup
model = WhisperModel(
    os.getenv("WHISPER_MODEL", "large-v3"),
    device="cuda",
    compute_type="float16"
)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(default=...)):
    """Transcribe audio file to text using Whisper."""
    temp_path = None
    try:
        suffix = os.path.splitext(file.filename or "")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        segments, info = model.transcribe(
            temp_path,
            beam_size=5,
            vad_filter=True,
            word_timestamps=True
        )
        
        out = {
            "language": info.language,
            "duration": info.duration,
            "segments": [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "words": [
                        {"start": w.start, "end": w.end, "word": w.word}
                        for w in (s.words or [])
                    ]
                }
                for s in segments
            ]
        }
        return out
    except Exception as e:
        logger.exception(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")


@app.get("/health")
def health():
    return {"ok": True, "model": os.getenv("WHISPER_MODEL", "large-v3")}
