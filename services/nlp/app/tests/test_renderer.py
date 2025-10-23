from app.renderers import build_markdown


def test_md_build():
    src = "# عنوان\nمتن"
    md = build_markdown(src)
    # Heading should be untouched
    assert md.startswith("# عنوان")
    # Should end with exactly one newline
    assert md.endswith("\n")
    assert not md.endswith("\n\n")


def test_md_build_preserves_leading_whitespace():
    src = "  # عنوان با فاصله\nمتن"
    md = build_markdown(src)
    # Leading spaces should be preserved
    assert md.startswith("  #")
    assert md.endswith("\n")
