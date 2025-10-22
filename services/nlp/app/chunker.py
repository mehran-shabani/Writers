def chunk_by_length(text: str, max_chars=1800):
    text = text.strip()
    if not text: return []
    parts, buf = [], []
    cur = 0
    for para in text.split("\n"):
        if len("\n".join(buf + [para])) > max_chars:
            parts.append("\n".join(buf).strip())
            buf = [para]
        else:
            buf.append(para)
    if buf: parts.append("\n".join(buf).strip())
    return parts
