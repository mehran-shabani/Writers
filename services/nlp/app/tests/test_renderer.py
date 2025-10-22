from app.renderers import build_markdown

def test_md_build():
    md = build_markdown("# عنوان\nمتن")
    assert md.strip().startswith("# عنوان")
