from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import shutil


@dataclass(frozen=True)
class SummaryTable:
    headers: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class MonthlyReportEntry:
    title: str
    markdown_name: str
    html_name: str
    intro: str
    preview: str
    bullet_points: list[str]


class GitHubPagesSiteWriter:
    def __init__(self, repo_name: str, summary_dir: Path, monthly_reports_dir: Path) -> None:
        self.repo_name = repo_name
        self.summary_dir = summary_dir
        self.monthly_reports_dir = monthly_reports_dir

    def build_site(self, output_dir: Path) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_names = [
            "connection-network.html",
            "connection-network.svg",
            "discovery-growth.svg",
            "discovery-summary.md",
        ]
        optional_artifact_names = [
            "social-network-analysis.md",
            "social-network-analysis.json",
        ]
        source_paths = {name: self.summary_dir / name for name in artifact_names}
        missing = [name for name, path in source_paths.items() if not path.exists()]
        if missing:
            joined = ", ".join(missing)
            raise FileNotFoundError(
                f"Cannot build the GitHub Pages site because these summary artifacts are missing: {joined}"
            )

        for name, source_path in source_paths.items():
            shutil.copyfile(source_path, output_dir / name)
        optional_source_paths = {
            name: self.summary_dir / name
            for name in optional_artifact_names
            if (self.summary_dir / name).exists()
        }
        for name, source_path in optional_source_paths.items():
            shutil.copyfile(source_path, output_dir / name)

        summary_text = source_paths["discovery-summary.md"].read_text(encoding="utf-8")
        social_network_text = ""
        social_network_path = optional_source_paths.get("social-network-analysis.md")
        if social_network_path is not None:
            social_network_text = social_network_path.read_text(encoding="utf-8")
        table = self._parse_summary_table(summary_text)
        monthly_reports = self._build_monthly_reports(output_dir)
        index_path = output_dir / "index.html"
        index_html = self._render_index(table, monthly_reports, social_network_text)
        index_path.write_text(index_html, encoding="utf-8")
        (output_dir / "404.html").write_text(index_html, encoding="utf-8")
        (output_dir / ".nojekyll").write_text("", encoding="utf-8")
        return str(index_path)

    def _parse_summary_table(self, markdown_text: str) -> SummaryTable:
        table_lines = [line.strip() for line in markdown_text.splitlines() if line.strip().startswith("|")]
        if len(table_lines) < 2:
            return SummaryTable(headers=[], rows=[])

        headers = self._split_row(table_lines[0])
        rows = []
        for line in table_lines[2:]:
            cells = self._split_row(line)
            if len(cells) == len(headers):
                rows.append(cells)
        return SummaryTable(headers=headers, rows=rows)

    @staticmethod
    def _split_row(row: str) -> list[str]:
        return [cell.strip() for cell in row.strip().strip("|").split("|")]

    def _render_index(
        self,
        table: SummaryTable,
        monthly_reports: list[MonthlyReportEntry],
        social_network_text: str,
    ) -> str:
        latest_date = table.rows[-1][0] if table.rows else "No data yet"
        latest_total = table.rows[-1][-1] if table.rows else "0"
        table_html = self._render_table(table)
        latest_monthly_html = self._render_latest_monthly(monthly_reports[0]) if monthly_reports else self._render_empty_monthly()
        archive_html = self._render_monthly_archive(monthly_reports)
        social_network_html = self._render_social_network_card(social_network_text)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hood College Signal Atlas</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #10213a;
      --muted: #5f6b7c;
      --line: #d7dee8;
      --paper: rgba(255, 255, 255, 0.92);
      --wash: #f5f7fb;
      --accent: #0f766e;
      --accent-2: #1d4ed8;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(29, 78, 216, 0.13), transparent 28%),
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.14), transparent 24%),
        linear-gradient(180deg, #edf4ff 0%, #f8fafc 45%, #eef6f2 100%);
    }}
    a {{
      color: var(--accent-2);
    }}
    .page {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 28px 22px 40px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(255,255,255,0.86));
      border: 1px solid rgba(215, 222, 232, 0.95);
      border-radius: 24px;
      padding: 28px 30px;
      box-shadow: 0 28px 60px rgba(16, 33, 58, 0.08);
      margin-bottom: 18px;
    }}
    .eyebrow {{
      margin: 0 0 8px 0;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0 0 10px 0;
      font-size: 34px;
      line-height: 1.1;
    }}
    .hero p {{
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      line-height: 1.6;
    }}
    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .pill {{
      border-radius: 999px;
      border: 1px solid #dbe4ee;
      background: #ffffff;
      padding: 9px 14px;
      font-size: 13px;
      color: var(--ink);
      text-decoration: none;
    }}
    .pill strong {{
      font-weight: 700;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
      gap: 18px;
      align-items: start;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid rgba(215, 222, 232, 0.95);
      border-radius: 22px;
      box-shadow: 0 24px 50px rgba(16, 33, 58, 0.07);
      overflow: hidden;
    }}
    .card-body {{
      padding: 20px;
    }}
    .card h2 {{
      margin: 0 0 10px 0;
      font-size: 19px;
    }}
    .card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }}
    iframe {{
      width: 100%;
      min-height: 980px;
      border: 0;
      background: #ffffff;
      display: block;
    }}
    .stack {{
      display: grid;
      gap: 18px;
    }}
    .image-frame {{
      padding: 18px;
    }}
    .image-frame img {{
      width: 100%;
      height: auto;
      display: block;
      border-radius: 16px;
      border: 1px solid #e5e7eb;
      background: #ffffff;
    }}
    .table-wrap {{
      overflow-x: auto;
      margin-top: 14px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: #ffffff;
      border-radius: 14px;
      overflow: hidden;
    }}
    th,
    td {{
      padding: 10px 12px;
      border-bottom: 1px solid #e5e7eb;
      text-align: left;
      white-space: nowrap;
    }}
    th {{
      background: #f8fafc;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    tr:last-child td {{
      border-bottom: 0;
      font-weight: 700;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    .footnote {{
      margin-top: 14px;
      font-size: 12px;
      color: var(--muted);
    }}
    .report-list {{
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }}
    .report-item {{
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      background: #ffffff;
      padding: 12px 14px;
    }}
    .report-item h3 {{
      margin: 0 0 6px 0;
      font-size: 15px;
    }}
    .report-item p {{
      margin: 0 0 10px 0;
      font-size: 13px;
    }}
    .report-item ul {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 13px;
    }}
    .report-item li + li {{
      margin-top: 4px;
    }}
    @media (max-width: 1100px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      iframe {{
        min-height: 760px;
      }}
    }}
    @media (max-width: 720px) {{
      .page {{
        padding: 18px 14px 28px;
      }}
      .hero,
      .card-body,
      .image-frame {{
        padding: 16px;
      }}
      h1 {{
        font-size: 28px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <p class="eyebrow">Hood College Signal Atlas</p>
      <h1>Interactive People Network for Hood College</h1>
      <p>
        This GitHub Pages site publishes the cumulative Hood College discovery outputs from the repository’s daily pipeline.
        The network below is limited to the top 25 people by cumulative connection degree so the graph stays readable while the database grows over time.
      </p>
      <div class="hero-meta">
        <span class="pill"><strong>Last snapshot:</strong> {escape(latest_date)}</span>
        <span class="pill"><strong>Cumulative people:</strong> {escape(latest_total)}</span>
        <a class="pill" href="connection-network.html">Open interactive graph only</a>
        <a class="pill" href="connection-network.svg">Open static SVG</a>
        <a class="pill" href="discovery-summary.md">Open summary markdown</a>
      </div>
    </section>

    <div class="layout">
      <section class="card">
        <iframe src="connection-network.html" title="Interactive Hood College people network"></iframe>
      </section>

      <div class="stack">
        <section class="card">
          <div class="card-body">
            <h2>Discovery Growth</h2>
            <p>The daily cumulative count of distinct people discovered by role.</p>
          </div>
          <div class="image-frame">
            <img src="discovery-growth.svg" alt="Discovery growth line graph">
          </div>
        </section>

        <section class="card">
          <div class="card-body">
            <h2>Cumulative Discovery Table</h2>
            <p>Each row is a cumulative snapshot by first-seen date, so the totals only move upward as coverage expands.</p>
            <div class="table-wrap">
              {table_html}
            </div>
            <div class="links">
              <a href="discovery-summary.md">Markdown source</a>
              <a href="https://github.com/rosemontni/{escape(self.repo_name)}">Repository</a>
            </div>
            <p class="footnote">The interactive graph supports drag-and-reposition directly in the browser. GitHub Pages serves the HTML, CSS, and JavaScript as a normal static site, so you can inspect crowded neighborhoods more easily than in the repository file view.</p>
          </div>
        </section>

        {social_network_html}

        <section class="card">
          <div class="card-body">
            <h2>Monthly Report</h2>
            <p>On the first day of each month, the pipeline publishes a dated report covering the month that just ended.</p>
            {latest_monthly_html}
            <div class="report-list">
              {archive_html}
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</body>
</html>
"""

    def _render_table(self, table: SummaryTable) -> str:
        if not table.headers:
            return "<p>No summary data has been generated yet.</p>"

        header_html = "".join(f"<th>{escape(cell)}</th>" for cell in table.headers)
        row_html = []
        for row in table.rows:
            cells = "".join(f"<td>{escape(cell)}</td>" for cell in row)
            row_html.append(f"<tr>{cells}</tr>")
        return (
            "<table>"
            f"<thead><tr>{header_html}</tr></thead>"
            f"<tbody>{''.join(row_html)}</tbody>"
            "</table>"
        )

    def _render_social_network_card(self, markdown_text: str) -> str:
        if not markdown_text:
            return (
                '<section class="card">'
                '<div class="card-body">'
                '<h2>Social Network Analysis</h2>'
                '<p>The social network report will appear after the next daily or weekly pipeline run.</p>'
                '</div>'
                '</section>'
            )
        title = "Social Network Analysis"
        preview = ""
        for line in markdown_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                continue
            if stripped and not stripped.startswith("#") and not stripped.startswith("|") and not stripped.startswith("- "):
                preview = stripped
                break
        return (
            '<section class="card">'
            '<div class="card-body">'
            f'<h2>{escape(title)}</h2>'
            f'<p>{self._render_inline_markdown(preview)}</p>'
            '<div class="links">'
            '<a href="social-network-analysis.md">Open narrated report</a>'
            '<a href="social-network-analysis.json">Open JSON data</a>'
            '</div>'
            '<p class="footnote">The SNA layer is evidence-based: links mean public co-mentions in stored sources, not private relationships.</p>'
            '</div>'
            '</section>'
        )

    def _build_monthly_reports(self, output_dir: Path) -> list[MonthlyReportEntry]:
        monthly_output_dir = output_dir / "monthly"
        monthly_output_dir.mkdir(parents=True, exist_ok=True)
        entries: list[MonthlyReportEntry] = []
        for markdown_path in sorted(self.monthly_reports_dir.glob("*.md"), reverse=True):
            markdown_text = markdown_path.read_text(encoding="utf-8")
            html_name = f"{markdown_path.stem}.html"
            entry = self._parse_monthly_report(markdown_path.name, html_name, markdown_text)
            (monthly_output_dir / markdown_path.name).write_text(markdown_text, encoding="utf-8")
            (monthly_output_dir / html_name).write_text(
                self._render_markdown_page(entry.title, markdown_text),
                encoding="utf-8",
            )
            entries.append(entry)
        return entries

    def _parse_monthly_report(
        self,
        markdown_name: str,
        html_name: str,
        markdown_text: str,
    ) -> MonthlyReportEntry:
        lines = [line.rstrip() for line in markdown_text.splitlines()]
        title = "Monthly Report"
        intro = ""
        preview = ""
        bullet_points: list[str] = []
        current_section = ""
        current_paragraph: list[str] = []
        essay_paragraphs: list[str] = []
        for line in lines:
            stripped = line.strip()
            if line.startswith("# ") and title == "Monthly Report":
                title = line[2:].strip()
                continue
            if line.startswith("## "):
                if current_section == "Narrative Essay" and current_paragraph:
                    essay_paragraphs.append(" ".join(current_paragraph))
                    current_paragraph.clear()
                current_section = line[3:].strip()
                continue
            if current_section == "Narrative Essay":
                if not stripped:
                    if current_paragraph:
                        essay_paragraphs.append(" ".join(current_paragraph))
                        current_paragraph.clear()
                    continue
                if not stripped.startswith("- "):
                    current_paragraph.append(stripped)
                continue
            if not intro and stripped and not stripped.startswith("#") and not stripped.startswith("- "):
                intro = stripped
                continue
            if current_section == "Snapshot" and stripped.startswith("- ") and len(bullet_points) < 3:
                bullet_points.append(stripped[2:].strip())
        if current_section == "Narrative Essay" and current_paragraph:
            essay_paragraphs.append(" ".join(current_paragraph))
        preview = essay_paragraphs[0] if essay_paragraphs else intro
        return MonthlyReportEntry(
            title=title,
            markdown_name=markdown_name,
            html_name=html_name,
            intro=intro,
            preview=preview,
            bullet_points=bullet_points,
        )

    def _render_latest_monthly(self, report: MonthlyReportEntry) -> str:
        bullets = "".join(f"<li>{self._render_inline_markdown(item)}</li>" for item in report.bullet_points)
        bullet_html = f"<ul>{bullets}</ul>" if bullets else ""
        return (
            '<div class="report-item">'
            f'<h3><a href="monthly/{escape(report.html_name)}">{escape(report.title)}</a></h3>'
            f"<p>{self._render_inline_markdown(report.preview)}</p>"
            f"{bullet_html}"
            f'<p><a href="monthly/{escape(report.markdown_name)}">Markdown</a></p>'
            "</div>"
        )

    def _render_empty_monthly(self) -> str:
        return (
            '<div class="report-item">'
            "<h3>No monthly report yet</h3>"
            "<p>The first report will appear once the pipeline completes a first-of-month publishing run.</p>"
            "</div>"
        )

    def _render_monthly_archive(self, monthly_reports: list[MonthlyReportEntry]) -> str:
        if not monthly_reports:
            return ""
        items = []
        for report in monthly_reports[:12]:
            items.append(
                '<div class="report-item">'
                f'<h3><a href="monthly/{escape(report.html_name)}">{escape(report.title)}</a></h3>'
                f'<p><a href="monthly/{escape(report.markdown_name)}">Markdown</a></p>'
                "</div>"
            )
        return "".join(items)

    def _render_markdown_page(self, title: str, markdown_text: str) -> str:
        body_html = self._render_markdown_blocks(markdown_text)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      color: #10213a;
      background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    }}
    .page {{
      max-width: 900px;
      margin: 0 auto;
      padding: 28px 18px 48px;
    }}
    .card {{
      background: rgba(255,255,255,0.94);
      border: 1px solid #e5e7eb;
      border-radius: 22px;
      padding: 26px;
      box-shadow: 0 24px 50px rgba(16, 33, 58, 0.08);
    }}
    h1, h2 {{
      line-height: 1.2;
    }}
    p, li {{
      line-height: 1.65;
    }}
    a {{
      color: #1d4ed8;
    }}
    ul {{
      padding-left: 22px;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="card">
      {body_html}
    </div>
  </div>
</body>
</html>
"""

    def _render_markdown_blocks(self, markdown_text: str) -> str:
        html_parts: list[str] = []
        list_items: list[str] = []
        paragraph_lines: list[str] = []

        def flush_paragraph() -> None:
            if not paragraph_lines:
                return
            html_parts.append(f"<p>{self._render_inline_markdown(' '.join(paragraph_lines))}</p>")
            paragraph_lines.clear()

        def flush_list() -> None:
            if not list_items:
                return
            html_parts.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")
            list_items.clear()

        for raw_line in markdown_text.splitlines():
            line = raw_line.strip()
            if not line:
                flush_paragraph()
                flush_list()
                continue
            if line.startswith("# "):
                flush_paragraph()
                flush_list()
                html_parts.append(f"<h1>{self._render_inline_markdown(line[2:].strip())}</h1>")
                continue
            if line.startswith("## "):
                flush_paragraph()
                flush_list()
                html_parts.append(f"<h2>{self._render_inline_markdown(line[3:].strip())}</h2>")
                continue
            if line.startswith("- "):
                flush_paragraph()
                list_items.append(self._render_inline_markdown(line[2:].strip()))
                continue
            flush_list()
            paragraph_lines.append(line)

        flush_paragraph()
        flush_list()
        return "".join(html_parts)

    def _render_inline_markdown(self, text: str) -> str:
        rendered = escape(text)
        rendered = rendered.replace("`", "")
        rendered = rendered.replace("**", "<strong>", 1).replace("**", "</strong>", 1) if rendered.count("**") >= 2 else rendered
        rendered = self._replace_links(rendered)
        return rendered

    def _replace_links(self, text: str) -> str:
        result = []
        cursor = 0
        while True:
            start = text.find("[", cursor)
            if start == -1:
                result.append(text[cursor:])
                break
            middle = text.find("](", start)
            end = text.find(")", middle + 2) if middle != -1 else -1
            if middle == -1 or end == -1:
                result.append(text[cursor:])
                break
            result.append(text[cursor:start])
            label = text[start + 1 : middle]
            href = text[middle + 2 : end]
            result.append(f'<a href="{href}">{label}</a>')
            cursor = end + 1
        return "".join(result)
