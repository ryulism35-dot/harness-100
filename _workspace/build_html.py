import markdown
import os

WORKSPACE = "/workspaces/harness-100/_workspace"

files = [
    ("00_input.md",              "조사 입력 — 사업 개요"),
    ("01_industry_analysis.md",  "산업 분석"),
    ("02_competitor_analysis.md","경쟁자 분석"),
    ("03_consumer_analysis.md",  "소비자 분석"),
    ("04_trend_analysis.md",     "트렌드 분석"),
    ("05_research_report.md",    "통합 시장조사 보고서"),
]

md = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br", "sane_lists"])

sections_html = []
toc_items = []

for idx, (fname, label) in enumerate(files):
    path = os.path.join(WORKSPACE, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    md.reset()
    body = md.convert(content)
    section_id = f"section-{idx:02d}"
    toc_items.append(f'<li><a href="#{section_id}"><span class="toc-num">{idx:02d}</span>{label}</a></li>')
    sections_html.append(f'<section id="{section_id}" class="report-section">\n{body}\n</section>')

toc_html = "\n".join(toc_items)
content_html = "\n".join(sections_html)

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>한국 산업단지 신규 전력사업 — 통합 시장조사 보고서</title>
  <style>
    /* ── 기본 리셋 & 폰트 ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    :root {{
      --primary:   #1a3a5c;
      --secondary: #2c5f8a;
      --accent:    #e8a020;
      --bg:        #f4f7fb;
      --surface:   #ffffff;
      --text:      #1e1e1e;
      --muted:     #6b7280;
      --border:    #d1dae8;
      --sidebar-w: 280px;
    }}

    html {{ scroll-behavior: smooth; }}

    body {{
      font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
      background: var(--bg);
      color: var(--text);
      font-size: 14px;
      line-height: 1.85;
      display: flex;
    }}

    /* ── 사이드바 ── */
    #sidebar {{
      position: fixed;
      top: 0; left: 0;
      width: var(--sidebar-w);
      height: 100vh;
      background: var(--primary);
      color: #fff;
      overflow-y: auto;
      z-index: 100;
      display: flex;
      flex-direction: column;
    }}

    #sidebar .sidebar-header {{
      padding: 28px 20px 20px;
      border-bottom: 1px solid rgba(255,255,255,0.15);
    }}

    #sidebar .sidebar-header .report-badge {{
      font-size: 10px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 8px;
    }}

    #sidebar .sidebar-header h2 {{
      font-size: 14px;
      font-weight: 700;
      line-height: 1.5;
      color: #fff;
      border: none;
    }}

    #sidebar .sidebar-header .meta {{
      margin-top: 10px;
      font-size: 11px;
      color: rgba(255,255,255,0.55);
    }}

    #sidebar nav ul {{
      list-style: none;
      padding: 12px 0;
    }}

    #sidebar nav ul li a {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 11px 20px;
      color: rgba(255,255,255,0.75);
      text-decoration: none;
      font-size: 13px;
      transition: background 0.15s, color 0.15s;
    }}

    #sidebar nav ul li a:hover {{
      background: rgba(255,255,255,0.1);
      color: #fff;
    }}

    #sidebar nav ul li a .toc-num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px; height: 24px;
      border-radius: 50%;
      background: rgba(255,255,255,0.15);
      font-size: 11px;
      font-weight: 700;
      flex-shrink: 0;
    }}

    /* ── 메인 콘텐츠 ── */
    #main {{
      margin-left: var(--sidebar-w);
      flex: 1;
      min-height: 100vh;
    }}

    /* ── 상단 헤더 ── */
    #hero {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
      color: #fff;
      padding: 60px 60px 50px;
    }}

    #hero .badge {{
      display: inline-block;
      background: var(--accent);
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 4px 12px;
      border-radius: 20px;
      margin-bottom: 18px;
    }}

    #hero h1 {{
      font-size: 30px;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 14px;
      color: #fff;
      border: none;
    }}

    #hero .subtitle {{
      font-size: 15px;
      color: rgba(255,255,255,0.75);
      margin-bottom: 30px;
    }}

    #hero .stats {{
      display: flex;
      gap: 32px;
      flex-wrap: wrap;
    }}

    #hero .stat {{
      text-align: center;
    }}

    #hero .stat .val {{
      font-size: 24px;
      font-weight: 700;
      color: var(--accent);
    }}

    #hero .stat .lbl {{
      font-size: 11px;
      color: rgba(255,255,255,0.65);
      margin-top: 2px;
    }}

    /* ── 섹션 공통 ── */
    .report-section {{
      background: var(--surface);
      margin: 28px 40px;
      border-radius: 12px;
      padding: 40px 48px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
      border-top: 4px solid var(--primary);
    }}

    .report-section:first-of-type {{
      margin-top: 28px;
    }}

    /* ── 섹션 번호 뱃지 ── */
    .report-section::before {{
      content: attr(data-label);
    }}

    /* ── 타이포그래피 ── */
    .report-section h1 {{
      font-size: 22px;
      color: var(--primary);
      border-bottom: 2px solid var(--primary);
      padding-bottom: 10px;
      margin-bottom: 20px;
      margin-top: 0;
    }}

    .report-section h2 {{
      font-size: 17px;
      color: var(--primary);
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
      margin-top: 32px;
      margin-bottom: 14px;
    }}

    .report-section h3 {{
      font-size: 14px;
      color: var(--secondary);
      margin-top: 22px;
      margin-bottom: 10px;
      font-weight: 700;
    }}

    .report-section h4 {{
      font-size: 13px;
      color: #444;
      margin-top: 16px;
      margin-bottom: 8px;
      font-weight: 700;
    }}

    .report-section p {{
      margin-bottom: 12px;
    }}

    .report-section ul, .report-section ol {{
      padding-left: 22px;
      margin-bottom: 12px;
    }}

    .report-section li {{
      margin-bottom: 5px;
    }}

    .report-section strong {{
      color: var(--primary);
      font-weight: 700;
    }}

    .report-section em {{
      color: var(--secondary);
    }}

    .report-section blockquote {{
      border-left: 4px solid var(--accent);
      margin: 14px 0;
      padding: 10px 18px;
      background: #fff8ed;
      color: #444;
      border-radius: 0 6px 6px 0;
    }}

    .report-section hr {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 24px 0;
    }}

    /* ── 코드 블록 ── */
    .report-section code {{
      background: #eef2f7;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
      font-family: 'Courier New', Consolas, monospace;
      color: #c0392b;
    }}

    .report-section pre {{
      background: #f0f4f8;
      border-left: 4px solid var(--secondary);
      border-radius: 6px;
      padding: 16px 18px;
      overflow-x: auto;
      font-size: 12px;
      margin: 14px 0;
      line-height: 1.6;
    }}

    .report-section pre code {{
      background: none;
      padding: 0;
      color: inherit;
      font-size: inherit;
    }}

    /* ── 테이블 ── */
    .report-section table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 13px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }}

    .report-section thead th {{
      background: var(--primary);
      color: #fff;
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
      font-size: 12px;
    }}

    .report-section tbody td {{
      padding: 9px 14px;
      border-bottom: 1px solid var(--border);
    }}

    .report-section tbody tr:nth-child(even) td {{
      background: #f5f8fc;
    }}

    .report-section tbody tr:hover td {{
      background: #eaf1fb;
    }}

    /* ── 푸터 ── */
    #footer {{
      text-align: center;
      padding: 30px;
      color: var(--muted);
      font-size: 12px;
      margin: 0 40px 40px;
    }}

    /* ── 반응형 ── */
    @media (max-width: 900px) {{
      :root {{ --sidebar-w: 0px; }}
      #sidebar {{ display: none; }}
      #main {{ margin-left: 0; }}
      .report-section {{ margin: 16px 12px; padding: 24px 20px; }}
      #hero {{ padding: 36px 24px; }}
    }}
  </style>
</head>
<body>

<!-- 사이드바 -->
<aside id="sidebar">
  <div class="sidebar-header">
    <div class="report-badge">Market Research Report</div>
    <h2>한국 산업단지<br>신규 전력사업<br>시장조사</h2>
    <div class="meta">열병합/SMR + 직접 PPA<br>2026년 4월 19일</div>
  </div>
  <nav>
    <ul>
      {toc_html}
    </ul>
  </nav>
</aside>

<!-- 메인 -->
<div id="main">

  <!-- 히어로 -->
  <header id="hero">
    <div class="badge">44번 하네스 — Market Research Agent Team</div>
    <h1>한국 산업단지 신규 전력사업<br>통합 시장조사 보고서</h1>
    <p class="subtitle">열병합발전(CHP, 500MW+) · SMR · 직접 PPA — Longlist → Shortlist → Top 10 산단 + 마스터플랜</p>
    <div class="stats">
      <div class="stat"><div class="val">TAM 32조</div><div class="lbl">원/년 — 산업용 전력 시장</div></div>
      <div class="stat"><div class="val">SAM 7.6조</div><div class="lbl">원/년 — 직접 PPA 전환 가능</div></div>
      <div class="stat"><div class="val">Top 10</div><div class="lbl">산단 최종 선정</div></div>
      <div class="stat"><div class="val">IRR 12~15%</div><div class="lbl">기본 시나리오</div></div>
      <div class="stat"><div class="val">5개 에이전트</div><div class="lbl">industry / competitor / consumer / trend / reviewer</div></div>
    </div>
  </header>

  <!-- 보고서 섹션 -->
  {content_html}

  <footer id="footer">
    본 보고서는 44번 하네스(Market Research Agent Team)의 5개 전문 에이전트가 생성하였습니다.<br>
    industry-analyst · competitor-analyst · consumer-analyst · trend-analyst · research-reviewer<br>
    © 2026 | 한국 산업단지 신규 전력사업 시장조사
  </footer>

</div>
</body>
</html>"""

out_path = os.path.join(WORKSPACE, "final_report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(out_path) // 1024
print(f"완료: final_report.html ({size_kb} KB)")
