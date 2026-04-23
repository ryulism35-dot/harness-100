import markdown
import os
from weasyprint import HTML, CSS

WORKSPACE = "/workspaces/harness-100/_workspace"

CSS_STYLE = CSS(string="""
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

@page {
    margin: 2cm 2.2cm;
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-size: 10px;
        color: #888;
    }
}

body {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 13px;
    line-height: 1.8;
    color: #222;
}

h1 {
    font-size: 22px;
    color: #1a3a5c;
    border-bottom: 3px solid #1a3a5c;
    padding-bottom: 8px;
    margin-top: 30px;
}

h2 {
    font-size: 17px;
    color: #1a3a5c;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 24px;
}

h3 {
    font-size: 14px;
    color: #2c5f8a;
    margin-top: 18px;
}

h4 {
    font-size: 13px;
    color: #444;
    margin-top: 14px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 12px;
}

th {
    background-color: #1a3a5c;
    color: white;
    padding: 7px 10px;
    text-align: left;
}

td {
    padding: 6px 10px;
    border: 1px solid #ddd;
}

tr:nth-child(even) td {
    background-color: #f5f8fc;
}

code {
    background-color: #f0f4f8;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 11px;
    font-family: 'Courier New', monospace;
}

pre {
    background-color: #f0f4f8;
    padding: 12px;
    border-radius: 5px;
    border-left: 4px solid #1a3a5c;
    font-size: 11px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

blockquote {
    border-left: 4px solid #2c5f8a;
    margin: 10px 0;
    padding: 8px 16px;
    background-color: #eef4fb;
    color: #333;
}

ul, ol {
    padding-left: 22px;
}

li {
    margin-bottom: 4px;
}

strong {
    color: #1a3a5c;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 20px 0;
}

.page-break {
    page-break-after: always;
}
""")

files = [
    "00_input.md",
    "01_industry_analysis.md",
    "02_competitor_analysis.md",
    "03_consumer_analysis.md",
    "04_trend_analysis.md",
    "05_research_report.md",
]

md = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br", "sane_lists"])

for fname in files:
    md_path = os.path.join(WORKSPACE, fname)
    pdf_path = os.path.join(WORKSPACE, fname.replace(".md", ".pdf"))

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    md.reset()
    html_body = md.convert(content)

    html_full = f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>{fname}</title></head>
<body>{html_body}</body>
</html>"""

    HTML(string=html_full).write_pdf(pdf_path, stylesheets=[CSS_STYLE])
    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"✓ {fname} → {fname.replace('.md', '.pdf')} ({size_kb} KB)")

print("\n모든 PDF 변환 완료.")
