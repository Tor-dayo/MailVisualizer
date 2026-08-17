from html import escape


def _text(value) -> str:
    return escape(str(value or ""))


def export_print_html(mails, filename):
    total = len(mails)
    sections = []

    for index, mail in enumerate(mails, start=1):
        sections.append(
            f"""
<article class="mail-report">
  <header>
    <div>
      <p class="eyebrow">MAIL REVIEW REPORT</p>
      <h1>{_text(mail.subject)}</h1>
    </div>
    <div class="report-number">管理No. {_text(mail.no)}<br><span>{index} / {total}</span></div>
  </header>

  <table class="metadata">
    <tr><th>送信日時</th><td>{_text(mail.date)}</td></tr>
    <tr><th>差出人</th><td>{_text(mail.sender)}</td></tr>
    <tr><th>宛先</th><td>{_text(mail.to)}</td></tr>
    <tr><th>Message-ID</th><td class="machine-text">{_text(mail.message_id)}</td></tr>
  </table>

  <section class="body-section">
    <h2>本文</h2>
    <pre>{_text(mail.body) or "本文なし"}</pre>
  </section>

  <footer>Mail Visualizer · 管理No. {_text(mail.no)}</footer>
</article>"""
        )

    html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mail Visualizer 印刷用レポート</title>
<style>
:root {{ color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #e9edf1;
  color: #17202a;
  font-family: "Yu Gothic UI", "Meiryo", sans-serif;
}}
.toolbar {{
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  color: white;
  background: #17324d;
}}
.toolbar p {{ margin: 0; }}
.toolbar button {{
  border: 0;
  border-radius: 6px;
  padding: 9px 20px;
  color: #17324d;
  background: white;
  font-weight: 700;
  cursor: pointer;
}}
.mail-report {{
  position: relative;
  width: 190mm;
  min-height: 267mm;
  margin: 12mm auto;
  padding: 14mm 14mm 18mm;
  background: white;
  box-shadow: 0 3px 18px rgba(23, 50, 77, .15);
  overflow-wrap: anywhere;
  break-after: page;
  page-break-after: always;
}}
.mail-report:last-child {{ break-after: auto; page-break-after: auto; }}
header {{
  display: flex;
  justify-content: space-between;
  gap: 16mm;
  padding-bottom: 7mm;
  border-bottom: 2px solid #17324d;
}}
.eyebrow {{ margin: 0 0 2mm; color: #58728b; font-size: 8pt; letter-spacing: .12em; }}
h1 {{ margin: 0; font-size: 17pt; line-height: 1.4; }}
.report-number {{ flex: 0 0 auto; text-align: right; font-size: 10pt; font-weight: 700; }}
.report-number span {{ color: #58728b; font-size: 8.5pt; font-weight: 400; }}
.metadata {{ width: 100%; margin: 7mm 0; border-collapse: collapse; table-layout: fixed; font-size: 9.5pt; }}
.metadata th, .metadata td {{ padding: 3mm; border: 1px solid #cbd5df; vertical-align: top; }}
.metadata th {{ width: 28mm; background: #eef3f7; text-align: left; white-space: nowrap; }}
.machine-text {{ font-family: Consolas, monospace; font-size: 8.5pt; }}
.body-section h2 {{ margin: 0 0 4mm; font-size: 12pt; color: #17324d; }}
pre {{
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  font: 10pt/1.75 "Yu Gothic UI", "Meiryo", sans-serif;
}}
footer {{
  position: absolute;
  right: 14mm;
  bottom: 8mm;
  left: 14mm;
  padding-top: 2mm;
  border-top: 1px solid #cbd5df;
  color: #657789;
  font-size: 8pt;
  text-align: right;
}}
@page {{ size: A4 portrait; margin: 10mm; }}
@media print {{
  body {{ background: white; }}
  .toolbar {{ display: none; }}
  .mail-report {{ width: auto; min-height: 277mm; margin: 0; box-shadow: none; }}
}}
</style>
</head>
<body>
<div class="toolbar">
  <p>印刷用レポート：{total}件</p>
  <button type="button" onclick="window.print()">印刷する</button>
</div>
{''.join(sections)}
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)
