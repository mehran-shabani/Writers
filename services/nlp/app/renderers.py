from markdown import markdown as md_to_html
from weasyprint import HTML

def build_markdown(structured_text: str) -> str:
    # ورودی: متن خروجی LLM به‌صورت Markdown یا شبه-markdown
    return structured_text.strip() + "\n"

def markdown_to_pdf_bytes(md_text: str) -> bytes:
    html = md_to_html(md_text, output_format="xhtml")
    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
