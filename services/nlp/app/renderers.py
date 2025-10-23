from markdown import markdown as md_to_html
from weasyprint import HTML, default_url_fetcher
from urllib.parse import urlparse

# RTL CSS for Persian/Arabic content
RTL_CSS = """
body {
    direction: rtl;
    text-align: right;
    font-family: 'Vazir', 'Tahoma', 'Arial', sans-serif;
    line-height: 1.8;
}
"""


def _safe_url_fetcher(url: str):
    """Restrict external resource fetching to prevent SSRF/local file reads."""
    parsed = urlparse(url)
    # Only allow safe schemes (data URIs and about:blank)
    if parsed.scheme in ("about", "data"):
        return default_url_fetcher(url)
    raise ValueError(f"Blocked external resource: {url}")


def build_markdown(structured_text: str) -> str:
    """Build markdown output, preserving leading whitespace but trimming trailing."""
    # ورودی: متن خروجی LLM به‌صورت Markdown یا شبه-markdown
    return structured_text.rstrip() + "\n"


def markdown_to_pdf_bytes(md_text: str) -> bytes:
    """Convert markdown to PDF with RTL support and SSRF protection."""
    html = md_to_html(md_text, output_format="xhtml")
    # Inject RTL CSS
    html_with_style = f"<style>{RTL_CSS}</style>{html}"
    pdf_bytes = HTML(
        string=html_with_style,
        base_url="about:blank",
        url_fetcher=_safe_url_fetcher
    ).write_pdf()
    return pdf_bytes
