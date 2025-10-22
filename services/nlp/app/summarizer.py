import os, requests
from typing import Dict

BACKEND = os.getenv("SUMMARIZER_BACKEND","local")
VLLM_URL = os.getenv("VLLM_URL","http://vllm:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")

SYSTEM_PROMPT = """تو یک دستیار متخصص خلاصه‌سازی در حوزهٔ پزشکی هستی.
خروجی کاملاً فارسی باشد و کلمات انگلیسی فقط در پرانتز بیایند.
ساختار خروجی:
- عنوان جلسه
- سرفصل‌ها: هر سرفصل شامل خلاصه، نکات طلایی و دام‌های تستی
- در انتها: ۳ تا ۱۰ سوال چهارگزینه‌ای با کلید و "منطق پاسخ"
- یک بخش "خلاصه شب امتحان" موجز و خطی
"""

def _to_messages(text: str):
    return [
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": f"متن زیر را به قالب خواسته‌شده تبدیل کن:\n{text}"}
    ]

def call_local(text: str) -> Dict:
    payload = {"model":"local-model","messages":_to_messages(text), "temperature":0.2, "max_tokens":2048}
    r = requests.post(f"{VLLM_URL}/chat/completions", json=payload, timeout=180)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return {"raw": content}

def call_openai(text: str) -> Dict:
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {"model":"gpt-4o-mini", "messages":_to_messages(text), "temperature":0.2, "max_tokens":2048}
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return {"raw": content}

def summarize(text: str) -> Dict:
    if BACKEND == "openai" and OPENAI_API_KEY:
        return call_openai(text)
    return call_local(text)
