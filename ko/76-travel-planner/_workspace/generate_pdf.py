#!/usr/bin/env python3
"""Generate a combined Korean PDF from all travel plan markdown files."""

import os
import re
from weasyprint import HTML, CSS

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/tmp/korean-fonts"

FILES = [
    ("00_input.md", "여행 입력 정보"),
    ("01_destination_analysis.md", "목적지 분석"),
    ("02_itinerary.md", "여행 일정표"),
    ("03_accommodation.md", "숙소 가이드"),
    ("04_budget.md", "예산 계획서"),
    ("05_local_guide.md", "현지 정보 가이드"),
]

OUTPUT = os.path.join(WORKSPACE, "busan_travel_plan.pdf")


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML conversion (tables, headings, bold, lists)."""
    lines = text.split("\n")
    html_lines = []
    in_table = False
    in_ul = False
    in_ol = False
    in_code = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    def inline(s: str) -> str:
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        return s

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.strip().startswith("```"):
            if not in_code:
                close_lists()
                if in_table:
                    html_lines.append("</table>")
                    in_table = False
                html_lines.append("<pre><code>")
                in_code = True
            else:
                html_lines.append("</code></pre>")
                in_code = False
            i += 1
            continue

        if in_code:
            html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            i += 1
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                close_lists()
                html_lines.append('<table class="md-table">')
                in_table = True
                # header row
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                html_lines.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                i += 1
                # skip separator row
                if i < len(lines) and re.match(r"^\|[-| :]+\|$", lines[i].strip()):
                    i += 1
            else:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                html_lines.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            continue
        elif in_table:
            html_lines.append("</tbody></table>")
            in_table = False

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            close_lists()
            level = len(m.group(1))
            html_lines.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # HR
        if re.match(r"^---+$", line.strip()):
            close_lists()
            html_lines.append("<hr>")
            i += 1
            continue

        # Unordered list
        m = re.match(r"^(\s*)[-*+]\s+(.*)", line)
        if m:
            if not in_ul:
                in_ul = True
                html_lines.append("<ul>")
            html_lines.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue

        # Ordered list
        m = re.match(r"^\d+\.\s+(.*)", line)
        if m:
            if not in_ol:
                in_ol = True
                html_lines.append("<ol>")
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        close_lists()

        # Blank line → paragraph break
        if line.strip() == "":
            html_lines.append("<br>")
            i += 1
            continue

        # Normal paragraph line
        html_lines.append(f"<p>{inline(line)}</p>")
        i += 1

    close_lists()
    if in_table:
        html_lines.append("</tbody></table>")
    if in_code:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


CSS_STYLE = f"""
@font-face {{
    font-family: 'NotoSansKR';
    src: url('file://{FONT_DIR}/NotoSansKR-Regular.otf') format('opentype');
    font-weight: normal;
}}
@font-face {{
    font-family: 'NotoSansKR';
    src: url('file://{FONT_DIR}/NotoSansKR-Bold.otf') format('opentype');
    font-weight: bold;
}}

@page {{
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
    @bottom-right {{
        content: counter(page);
        font-family: 'NotoSansKR', sans-serif;
        font-size: 9pt;
        color: #888;
    }}
}}

* {{
    font-family: 'NotoSansKR', sans-serif;
    box-sizing: border-box;
}}

body {{
    font-size: 10pt;
    line-height: 1.7;
    color: #222;
}}

.chapter-title {{
    page-break-before: always;
    background: #1a3a5c;
    color: white;
    padding: 18px 24px;
    border-radius: 6px;
    margin-bottom: 24px;
    font-size: 18pt;
    font-weight: bold;
}}

.chapter-title:first-child {{
    page-break-before: avoid;
}}

h1 {{ font-size: 16pt; color: #1a3a5c; margin: 20px 0 10px; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; }}
h2 {{ font-size: 13pt; color: #2c5f8a; margin: 16px 0 8px; border-left: 4px solid #2c5f8a; padding-left: 10px; }}
h3 {{ font-size: 11pt; color: #3a7abf; margin: 12px 0 6px; }}
h4 {{ font-size: 10pt; color: #555; margin: 10px 0 4px; }}
h5, h6 {{ font-size: 10pt; color: #666; margin: 8px 0 4px; }}

p {{ margin: 4px 0; }}
br {{ display: block; margin: 4px 0; }}

table.md-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px;
    font-size: 9pt;
    page-break-inside: auto;
}}
table.md-table th {{
    background: #2c5f8a;
    color: white;
    padding: 6px 8px;
    text-align: left;
    font-weight: bold;
}}
table.md-table td {{
    padding: 5px 8px;
    border: 1px solid #ddd;
    vertical-align: top;
}}
table.md-table tr:nth-child(even) td {{
    background: #f5f8fc;
}}

ul, ol {{
    margin: 4px 0 8px 18px;
    padding: 0;
}}
li {{ margin: 2px 0; }}

code {{
    background: #f0f4f8;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 8.5pt;
    font-family: monospace;
}}
pre {{
    background: #f0f4f8;
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 8pt;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}}

hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 14px 0;
}}

strong {{ font-weight: bold; }}
em {{ font-style: italic; }}
"""


def build_html() -> str:
    sections = []
    for filename, title in FILES:
        path = os.path.join(WORKSPACE, filename)
        if not os.path.exists(path):
            print(f"  [건너뜀] {filename} 없음")
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        body = md_to_html(content)
        sections.append(f'<div class="chapter-title">{title}</div>\n{body}')

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>부산 여행 계획서</title>
</head>
<body>
{"<div class='page-break'></div>".join(sections)}
</body>
</html>"""


def main():
    print("HTML 변환 중...")
    html = build_html()

    print("PDF 생성 중... (한글 폰트 렌더링)")
    doc = HTML(string=html, base_url=WORKSPACE)
    css = CSS(string=CSS_STYLE)
    doc.write_pdf(OUTPUT, stylesheets=[css])
    size_kb = os.path.getsize(OUTPUT) // 1024
    print(f"완료: {OUTPUT} ({size_kb} KB)")


if __name__ == "__main__":
    main()
