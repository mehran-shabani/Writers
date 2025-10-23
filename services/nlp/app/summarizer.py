import os
import requests

LOCAL_MODEL = os.getenv("LOCAL_MODEL", "local-model")
VLLM_URL_DEFAULT = os.getenv("VLLM_URL", "http://vllm:8000/v1")

SYSTEM_PROMPT = """تو یک دستیار متخصص خلاصه‌سازی در حوزهٔ پزشکی هستی.
خروجی کاملاً فارسی باشد و کلمات انگلیسی فقط در پرانتز بیایند.
ساختار خروجی:
- عنوان جلسه
- سرفصل‌ها: هر سرفصل شامل خلاصه، نکات طلایی و دام‌های تستی
- در انتها: ۳ تا ۱۰ سوال چهارگزینه‌ای با کلید و "منطق پاسخ"
- یک بخش "خلاصه شب امتحان" موجز و خطی
"""

# ruff: noqa: RUF001
def _to_messages(text: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"متن زیر را به قالب خواسته‌شده تبدیل کن:\n{text}"}
    ]

def call_local(text: str) -> dict:
    vllm_url = os.getenv("VLLM_URL", VLLM_URL_DEFAULT)
    payload = {
        "model": LOCAL_MODEL,
        "messages": _to_messages(text),
        "temperature": 0.2,
        "max_tokens": 2048
    }
    r = requests.post(f"{vllm_url}/chat/completions", json=payload, timeout=180)
    r.raise_for_status()
    try:
        data = r.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise RuntimeError(
            f"Malformed local response: {r.text[:500]}"
        ) from e
    return {"raw": content}

def call_openai(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for OpenAI backend")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4.1-mini",
        "messages": _to_messages(text),
        "temperature": 0.2,
        "max_tokens": 2048
    }
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=180
    )
    r.raise_for_status()
    try:
        data = r.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise RuntimeError(
            f"Malformed OpenAI response: {r.text[:500]}"
        ) from e
    return {"raw": content}

def summarize(text: str) -> dict:
    """Summarize text using configured backend (local or openai).
    
    Note: For medical data, ensure proper anonymization before calling.
    """
    backend = os.getenv("SUMMARIZER_BACKEND", "local")
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if backend == "openai" and api_key:
        return call_openai(text)
    return call_local(text)
