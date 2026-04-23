#!/usr/bin/env python3
"""Combine all travel plan markdown files into a single Korean HTML file."""

import os
import re

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(WORKSPACE, "busan_travel.html")

FILES = [
    ("00_input.md",                "여행 입력 정보",    "✈️"),
    ("01_destination_analysis.md", "목적지 분석",       "🗺️"),
    ("02_itinerary.md",            "여행 일정표",       "📅"),
    ("03_accommodation.md",        "숙소 가이드",       "🏨"),
    ("04_budget.md",               "예산 계획서",       "💰"),
    ("05_local_guide.md",          "현지 정보 가이드",  "🧭"),
]


def inline(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out = []
    in_table = in_ul = in_ol = in_code = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>"); in_ul = False
        if in_ol:
            out.append("</ol>"); in_ol = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>"); in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            if not in_code:
                close_lists(); close_table()
                lang = line.strip()[3:].strip()
                out.append(f'<pre><code class="language-{lang}">')
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            i += 1; continue

        if in_code:
            out.append(line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
            i += 1; continue

        # table row
        if line.strip().startswith("|") and "|" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                close_lists()
                out.append('<table>')
                out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                in_table = True
                i += 1
                if i < len(lines) and re.match(r"^\|[\s|:-]+\|$", lines[i].strip()):
                    i += 1
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            continue
        else:
            close_table()

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            close_lists()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1; continue

        # hr
        if re.match(r"^---+$", line.strip()):
            close_lists()
            out.append("<hr>")
            i += 1; continue

        # unordered list
        m = re.match(r"^(\s*)[-*+]\s+(.*)", line)
        if m:
            if not in_ul:
                if in_ol: out.append("</ol>"); in_ol = False
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(m.group(2))}</li>")
            i += 1; continue

        # ordered list
        m = re.match(r"^\d+\.\s+(.*)", line)
        if m:
            if not in_ol:
                if in_ul: out.append("</ul>"); in_ul = False
                out.append("<ol>"); in_ol = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1; continue

        close_lists()

        if line.strip() == "":
            out.append("<div class='spacer'></div>")
            i += 1; continue

        out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_lists(); close_table()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>부산 여행 계획서 (2026.07.29 ~ 08.01)</title>
<style>
/* ── Google Fonts: Noto Sans KR ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

:root {
  --primary:   #1a3a5c;
  --secondary: #2c5f8a;
  --accent:    #3a7abf;
  --light-bg:  #f5f8fc;
  --border:    #d0dce8;
  --text:      #222;
  --muted:     #666;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
  background: #f0f4f8;
}

/* ── Nav sidebar ── */
#toc {
  position: fixed;
  top: 0; left: 0;
  width: 220px;
  height: 100vh;
  background: var(--primary);
  color: #cde;
  padding: 24px 0;
  overflow-y: auto;
  z-index: 100;
}
#toc h2 {
  font-size: 13px;
  letter-spacing: 1px;
  color: #aac;
  padding: 0 20px 12px;
  border-bottom: 1px solid #2a4f72;
  margin-bottom: 8px;
}
#toc a {
  display: block;
  padding: 8px 20px;
  color: #cde;
  text-decoration: none;
  font-size: 13px;
  transition: background .15s;
}
#toc a:hover { background: #2c5f8a; color: #fff; }
#toc .toc-icon { margin-right: 6px; }

/* ── Main content ── */
#main {
  margin-left: 220px;
  padding: 40px 48px;
  max-width: 960px;
}

/* ── Cover banner ── */
.cover {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  color: white;
  border-radius: 12px;
  padding: 48px 40px;
  margin-bottom: 40px;
  text-align: center;
}
.cover h1 { font-size: 30px; font-weight: 700; margin-bottom: 10px; }
.cover .subtitle { font-size: 16px; opacity: .85; }
.cover .meta { margin-top: 20px; font-size: 14px; opacity: .75; }

/* ── Chapter sections ── */
.chapter {
  background: white;
  border-radius: 10px;
  padding: 36px 40px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,.07);
}
.chapter-header {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--primary);
  color: white;
  border-radius: 8px;
  padding: 14px 20px;
  margin: -36px -40px 28px;
}
.chapter-header .icon { font-size: 22px; }
.chapter-header h2 { font-size: 18px; font-weight: 700; }

/* ── Headings inside chapters ── */
h1 { font-size: 20px; color: var(--primary); margin: 24px 0 10px; padding-bottom: 6px; border-bottom: 2px solid var(--primary); }
h2 { font-size: 16px; color: var(--secondary); margin: 20px 0 8px; padding-left: 10px; border-left: 4px solid var(--secondary); }
h3 { font-size: 14px; color: var(--accent); margin: 16px 0 6px; }
h4 { font-size: 13px; color: var(--muted); margin: 12px 0 4px; }
h5, h6 { font-size: 12px; color: var(--muted); margin: 10px 0 4px; }

p { margin: 4px 0 6px; }
.spacer { height: 6px; }

/* ── Tables ── */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 18px;
  font-size: 13px;
  overflow-x: auto;
  display: block;
}
th {
  background: var(--secondary);
  color: white;
  padding: 8px 10px;
  text-align: left;
  font-weight: 700;
  white-space: nowrap;
}
td {
  padding: 6px 10px;
  border: 1px solid var(--border);
  vertical-align: top;
}
tr:nth-child(even) td { background: var(--light-bg); }
tr:hover td { background: #e8f0f8; }

/* ── Lists ── */
ul, ol { margin: 6px 0 10px 22px; }
li { margin: 3px 0; }

/* ── Inline ── */
strong { font-weight: 700; color: var(--primary); }
em { font-style: italic; color: var(--secondary); }
code {
  background: #eef2f7;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  font-family: 'Noto Sans KR', monospace;
}
pre {
  background: #eef2f7;
  padding: 14px 16px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 10px 0;
}

hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

/* ── Responsive ── */
@media (max-width: 768px) {
  #toc { display: none; }
  #main { margin-left: 0; padding: 20px 16px; }
  .chapter { padding: 24px 18px; }
  .chapter-header { margin: -24px -18px 20px; }
}
</style>
</head>
<body>

<nav id="toc">
  <h2>목차</h2>
  {TOC}
</nav>

<div id="main">
  <div class="cover">
    <h1>🌊 부산 여행 계획서</h1>
    <div class="subtitle">2026년 7월 29일 (수) ~ 8월 1일 (토) · 3박 4일</div>
    <div class="meta">성인 5명 + 아이 4명 (만 2~12세) · 한국인 4명 + 일본인 5명</div>
  </div>
  {CHAPTERS}
</div>

<script>
// Highlight active TOC link on scroll
const chapters = document.querySelectorAll('.chapter');
const links = document.querySelectorAll('#toc a');
window.addEventListener('scroll', () => {
  let current = '';
  chapters.forEach(c => { if (window.scrollY >= c.offsetTop - 80) current = c.id; });
  links.forEach(a => {
    a.style.background = a.getAttribute('href') === '#' + current ? '#2c5f8a' : '';
    a.style.color = a.getAttribute('href') === '#' + current ? '#fff' : '';
  });
});
</script>
</body>
</html>
"""


def main():
    toc_items = []
    chapter_items = []

    for filename, title, icon in FILES:
        path = os.path.join(WORKSPACE, filename)
        if not os.path.exists(path):
            print(f"  [건너뜀] {filename} 없음")
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()

        slug = filename.replace(".md", "").replace("_", "-")
        body = md_to_html(content)

        toc_items.append(
            f'<a href="#{slug}"><span class="toc-icon">{icon}</span>{title}</a>'
        )
        chapter_items.append(
            f'<section class="chapter" id="{slug}">'
            f'<div class="chapter-header"><span class="icon">{icon}</span><h2>{title}</h2></div>'
            f'{body}'
            f'</section>'
        )

    html = HTML_TEMPLATE.replace("{TOC}", "\n  ".join(toc_items))
    html = html.replace("{CHAPTERS}", "\n  ".join(chapter_items))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT) // 1024
    print(f"완료: {OUTPUT} ({size_kb} KB)")


if __name__ == "__main__":
    main()
