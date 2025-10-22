from app.chunker import chunk_by_length

def test_chunker_basic():
    text = ("الف\n"*200) + "پایان"
    parts = chunk_by_length(text, max_chars=100)
    assert len(parts) > 1
    assert any("پایان" in p for p in parts)
