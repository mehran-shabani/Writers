def chunk_by_length(text: str, max_chars: int = 1800) -> list[str]:
    """Split text into chunks by paragraph, respecting max_chars limit."""
    text = text.strip()
    if not text:
        return []
    
    parts: list[str] = []
    buf: list[str] = []
    
    for para in text.split("\n"):
        combined = "\n".join([*buf, para])
        if len(combined) > max_chars and buf:
            parts.append("\n".join(buf).strip())
            buf = [para]
        else:
            buf.append(para)
    
    if buf:
        parts.append("\n".join(buf).strip())
    
    return parts
