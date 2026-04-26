from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import shutil


@dataclass(frozen=True)
class SummaryTable:
    headers: list[str]
    rows: list[list[str]]


class GitHubPagesSiteWriter:
    def __init__(self, repo_name: str, summary_dir: Path) -> None:
        self.repo_name = repo_name
        self.summary_dir = summary_dir

    def build_site(self, output_dir: Path) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_names = [
            "connection-network.html",
            "connection-network.svg",
            "discovery-growth.svg",
            "discovery-summary.md",
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

        summary_text = source_paths["discovery-summary.md"].read_text(encoding="utf-8")
        table = self._parse_summary_table(summary_text)
        index_path = output_dir / "index.html"
        index_html = self._render_index(table)
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

    def _render_index(self, table: SummaryTable) -> str:
        latest_date = table.rows[-1][0] if table.rows else "No data yet"
        latest_total = table.rows[-1][-1] if table.rows else "0"
        table_html = self._render_table(table)
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
