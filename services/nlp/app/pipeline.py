import io, requests
from .chunker import chunk_by_length
from .summarizer import summarize
from .renderers import build_markdown, markdown_to_pdf_bytes

def run_pipeline(audio_bytes: bytes, asr_url: str) -> (str, bytes):
    # 1) ASR
    files = {"file": ("audio.m4a", io.BytesIO(audio_bytes), "audio/mp4")}
    r = requests.post(asr_url, files=files, timeout=600)
    r.raise_for_status()
    data = r.json()
    txt = "\n".join([s["text"].strip() for s in data.get("segments",[])])
    # 2) Chunk + Summarize (ساده: همهٔ متن یکجا)
    # اگر خواستی: برای هر chunk خلاصهٔ جدا تولید کن و merge کن.
    out = summarize(txt)
    md = build_markdown(out["raw"])
    pdf = markdown_to_pdf_bytes(md)
    return md, pdf
