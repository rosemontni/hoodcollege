from __future__ import annotations

from datetime import date
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from hood_pipeline.domain.models import SummaryPoint, WeeklyConnection


ROLE_LABELS = {
    "administrator": "Administrators",
    "faculty": "Faculty",
    "staff": "Staff",
    "alumni": "Alumni",
    "student": "Students",
    "student-athlete": "Student-Athletes",
    "coach": "Coaches",
    "guest": "Guests / External Partners",
    "person": "Unclassified People",
}

ROLE_ORDER = [
    "student",
    "student-athlete",
    "faculty",
    "staff",
    "administrator",
    "alumni",
    "coach",
    "guest",
    "person",
]

PALETTE = [
    "#0f766e",
    "#2563eb",
    "#dc2626",
    "#d97706",
    "#7c3aed",
    "#059669",
    "#db2777",
    "#4b5563",
]


class SummaryArtifactsWriter:
    def __init__(self, summary_dir: Path) -> None:
        self.summary_dir = summary_dir

    def write_summary(
        self,
        points: list[SummaryPoint],
        connection_graph_name: str | None = None,
        connection_graph_html_name: str | None = None,
    ) -> tuple[str, str]:
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.summary_dir / "discovery-summary.md"
        graph_path = self.summary_dir / "discovery-growth.svg"
        roles = self._ordered_roles(points)
        markdown_path.write_text(
            self._render_markdown(
                points,
                roles,
                graph_path.name,
                connection_graph_name,
                connection_graph_html_name,
            ),
            encoding="utf-8",
        )
        graph_path.write_text(
            self._render_svg(points, roles),
            encoding="utf-8",
        )
        return str(markdown_path), str(graph_path)

    def write_connection_network_graph(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int = 25,
    ) -> str:
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        graph_path = self.summary_dir / "connection-network.svg"
        graph_path.write_text(
            self._render_connection_network_svg(run_date, connections, max_people=max_people),
            encoding="utf-8",
        )
        return str(graph_path)

    def write_connection_network_html(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int = 25,
    ) -> str:
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        html_path = self.summary_dir / "connection-network.html"
        html_path.write_text(
            self._render_connection_network_html(run_date, connections, max_people=max_people),
            encoding="utf-8",
        )
        return str(html_path)

    def _ordered_roles(self, points: list[SummaryPoint]) -> list[str]:
        present = {role for point in points for role in point.counts_by_role}
        ordered = [role for role in ROLE_ORDER if role in present]
        ordered.extend(sorted(role for role in present if role not in ordered))
        return ordered

    def _render_markdown(
        self,
        points: list[SummaryPoint],
        roles: list[str],
        graph_name: str,
        connection_graph_name: str | None,
        connection_graph_html_name: str | None,
    ) -> str:
        lines = [
            "# Discovery Summary",
            "",
            "This table shows cumulative distinct people discovered by first-seen date.",
            "",
            f"![Discovery growth]({graph_name})",
            "",
        ]
        if connection_graph_name:
            lines.extend(
                [
                    "## Connection Network",
                    "",
                    "This graph shows the top 25 people with the highest cumulative connection degree.",
                    "",
                    f"![Connection network]({connection_graph_name})",
                    "",
                ]
            )
            if connection_graph_html_name:
                lines.extend(
                    [
                        f"Interactive file: `{connection_graph_html_name}`",
                        "",
                    ]
                )
        headers = ["Date"] + [ROLE_LABELS.get(role, role.title()) for role in roles] + ["Total"]
        separator = ["---"] * len(headers)
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(separator) + " |")

        if not points:
            lines.append("| No data yet |" + " |".join("" for _ in headers[1:]))
            return "\n".join(lines) + "\n"

        for point in points:
            row = [point.run_date.isoformat()]
            for role in roles:
                row.append(str(point.counts_by_role.get(role, 0)))
            row.append(str(point.total))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _render_svg(self, points: list[SummaryPoint], roles: list[str]) -> str:
        width = 1100
        height = 600
        left = 80
        right = 210
        top = 50
        bottom = 80
        plot_width = width - left - right
        plot_height = height - top - bottom
        all_roles = ["total"] + roles
        max_value = max([point.total for point in points] + [1]) if points else 1
        tick_count = min(5, max_value)
        tick_values = sorted(set(int(round(max_value * step / max(tick_count, 1))) for step in range(tick_count + 1)))
        tick_values[0] = 0

        def x_for(index: int) -> float:
            if len(points) <= 1:
                return left + plot_width / 2
            return left + (plot_width * index / (len(points) - 1))

        def y_for(value: int) -> float:
            return top + plot_height - ((value / max_value) * plot_height)

        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            '<text x="80" y="28" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="700" fill="#111827">Discovery Growth</text>',
            '<text x="80" y="46" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6b7280">Cumulative distinct people discovered by role over time</text>',
        ]

        for value in tick_values:
            y = y_for(value)
            lines.append(
                f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>'
            )
            lines.append(
                f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#6b7280">{value}</text>'
            )

        lines.append(
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5"/>'
        )
        lines.append(
            f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5"/>'
        )

        for index, point in enumerate(points):
            x = x_for(index)
            lines.append(
                f'<text x="{x:.1f}" y="{top + plot_height + 20}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#6b7280">{point.run_date.isoformat()}</text>'
            )

        series = []
        for role in all_roles:
            values = [point.total if role == "total" else point.counts_by_role.get(role, 0) for point in points]
            series.append((role, values))

        for index, (role, values) in enumerate(series):
            color = "#111827" if role == "total" else PALETTE[(index - 1) % len(PALETTE)]
            points_attr = " ".join(
                f"{x_for(i):.1f},{y_for(value):.1f}" for i, value in enumerate(values)
            )
            if points_attr:
                lines.append(
                    f'<polyline fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" points="{points_attr}"/>'
                )
            for i, value in enumerate(values):
                lines.append(
                    f'<circle cx="{x_for(i):.1f}" cy="{y_for(value):.1f}" r="3.5" fill="{color}"/>'
                )

        legend_x = left + plot_width + 24
        legend_y = top + 24
        for index, role in enumerate(all_roles):
            color = "#111827" if role == "total" else PALETTE[(index - 1) % len(PALETTE)]
            y = legend_y + index * 22
            label = "Total" if role == "total" else ROLE_LABELS.get(role, role.title())
            lines.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 18}" y2="{y}" stroke="{color}" stroke-width="3"/>')
            lines.append(
                f'<text x="{legend_x + 26}" y="{y + 4}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#111827">{label}</text>'
            )

        lines.append("</svg>")
        return "\n".join(lines) + "\n"

    def _render_connection_network_svg(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int,
    ) -> str:
        model = self._connection_network_model(run_date, connections, max_people)
        width = 1200
        height = 900
        padding = 85
        network_width = width - padding * 2
        network_height = height - padding * 2 - 60

        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            '<text x="80" y="32" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="700" fill="#111827">Connection Network</text>',
            (
                f'<text x="80" y="52" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6b7280">'
                f'Top {model["shown_count"]} people by cumulative connection degree through {run_date.isoformat()}'
                "</text>"
            ),
        ]

        if not model["nodes"]:
            lines.extend(
                [
                    '<text x="80" y="120" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#6b7280">No cumulative people connections are available yet.</text>',
                    "</svg>",
                ]
            )
            return "\n".join(lines) + "\n"

        lines.append(
            f'<rect x="{padding - 20}" y="{padding + 20}" width="{network_width + 40}" height="{network_height + 40}" rx="24" fill="#f8fafc" stroke="#e5e7eb"/>'
        )

        for edge in model["edges"]:
            lines.append(
                f'<line x1="{edge["x1"]:.1f}" y1="{edge["y1"]:.1f}" x2="{edge["x2"]:.1f}" y2="{edge["y2"]:.1f}" '
                f'stroke="#94a3b8" stroke-width="{edge["stroke_width"]:.2f}" stroke-linecap="round" opacity="{edge["opacity"]:.2f}"/>'
            )

        center_x = width / 2
        for node in model["nodes"]:
            x = float(node["x"])
            y = float(node["y"])
            radius = float(node["radius"])
            fill = str(node["color"])
            lines.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="#ffffff" stroke-width="2"/>'
            )
            anchor = "start" if x <= center_x else "end"
            label_x = x + radius + 8 if anchor == "start" else x - radius - 8
            lines.append(
                f'<text x="{label_x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" '
                f'font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#111827">{self._escape_xml(str(node["id"]))}</text>'
            )

        legend_x = width - 300
        legend_y = 120
        lines.extend(
            [
                f'<text x="{legend_x}" y="{legend_y}" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">Legend</text>',
                f'<text x="{legend_x}" y="{legend_y + 24}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6b7280">Node size = cumulative degree</text>',
                f'<text x="{legend_x}" y="{legend_y + 42}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6b7280">Edge width = shared-article count</text>',
                f'<text x="{legend_x}" y="{legend_y + 60}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6b7280">Only top {model["shown_count"]} people are shown</text>',
            ]
        )

        lines.append("</svg>")
        return "\n".join(lines) + "\n"

    def _render_connection_network_html(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int,
    ) -> str:
        model = self._connection_network_model(run_date, connections, max_people)
        data_json = json.dumps(model, ensure_ascii=True)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hood College Connection Network</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --card: #ffffff;
      --ink: #111827;
      --muted: #6b7280;
      --line: #cbd5e1;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
      color: var(--ink);
    }}
    .page {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 24px;
    }}
    .header {{
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      padding: 20px 22px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.06);
      margin-bottom: 18px;
    }}
    .header h1 {{
      margin: 0 0 6px 0;
      font-size: 28px;
    }}
    .header p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 280px;
      gap: 18px;
    }}
    .card {{
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.06);
      overflow: hidden;
    }}
    .canvas-wrap {{
      padding: 14px;
    }}
    svg {{
      width: 100%;
      height: auto;
      display: block;
      background: #ffffff;
      border-radius: 14px;
      border: 1px solid #e5e7eb;
      touch-action: none;
      user-select: none;
    }}
    .sidebar {{
      padding: 18px;
    }}
    .sidebar h2 {{
      margin: 0 0 12px 0;
      font-size: 16px;
    }}
    .sidebar p {{
      margin: 0 0 10px 0;
      color: var(--muted);
      line-height: 1.5;
      font-size: 13px;
    }}
    .meta {{
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }}
    .meta-item {{
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 10px 12px;
    }}
    .meta-item strong {{
      display: block;
      font-size: 14px;
      margin-bottom: 4px;
    }}
    .meta-item span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .hint {{
      margin-top: 16px;
      padding: 10px 12px;
      border-radius: 12px;
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      color: #3730a3;
      font-size: 12px;
      line-height: 1.5;
    }}
    .edge {{
      stroke: #94a3b8;
      stroke-linecap: round;
    }}
    .node circle {{
      stroke: #ffffff;
      stroke-width: 2;
      cursor: grab;
    }}
    .node.dragging circle {{
      cursor: grabbing;
      stroke: #111827;
      stroke-width: 3;
    }}
    .node text {{
      font-size: 12px;
      fill: #111827;
      pointer-events: none;
    }}
    @media (max-width: 980px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="header">
      <h1>Hood College Connection Network</h1>
      <p>Top {model["shown_count"]} people by cumulative connection degree through {run_date.isoformat()}. Drag nodes to rearrange the network and inspect crowded areas.</p>
    </div>
    <div class="layout">
      <div class="card canvas-wrap">
        <svg id="network" viewBox="0 0 1200 900" aria-label="Draggable connection network"></svg>
      </div>
      <div class="card sidebar">
        <h2>How to Read This</h2>
        <p>Node size shows how many cumulative connections a person has. Edge thickness shows how many shared articles support that connection.</p>
        <div class="meta">
          <div class="meta-item">
            <strong>{model["shown_count"]} people shown</strong>
            <span>Limited to the highest-degree nodes for readability</span>
          </div>
          <div class="meta-item">
            <strong>{len(model["edges"])} edges shown</strong>
            <span>Only edges between the displayed top-degree people are drawn</span>
          </div>
          <div class="meta-item">
            <strong>{run_date.isoformat()}</strong>
            <span>Cumulative network snapshot date</span>
          </div>
        </div>
        <div class="hint">GitHub's normal repository file view may not execute this interactive page. The file itself is self-contained and works in a browser or any static host that serves HTML, CSS, and JavaScript.</div>
      </div>
    </div>
  </div>
  <script>
    const model = {data_json};
    const svg = document.getElementById("network");
    const edgeLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const nodeLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.appendChild(edgeLayer);
    svg.appendChild(nodeLayer);

    const nodes = new Map(model.nodes.map((node) => [node.id, {{ ...node }}]));
    const edges = model.edges.map((edge) => ({{ ...edge }}));
    const nodeGroups = new Map();
    const edgeEls = [];

    for (const edge of edges) {{
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("class", "edge");
      line.setAttribute("stroke-width", edge.stroke_width.toFixed(2));
      line.setAttribute("opacity", edge.opacity.toFixed(2));
      edgeLayer.appendChild(line);
      edgeEls.push({{ edge, line }});
    }}

    for (const node of nodes.values()) {{
      const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
      group.setAttribute("class", "node");
      group.dataset.nodeId = node.id;

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("r", node.radius.toFixed(1));
      circle.setAttribute("fill", node.color);

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.textContent = node.id;

      group.appendChild(circle);
      group.appendChild(label);
      nodeLayer.appendChild(group);
      nodeGroups.set(node.id, {{ group, circle, label }});
    }}

    function render() {{
      for (const {{ edge, line }} of edgeEls) {{
        const left = nodes.get(edge.source);
        const right = nodes.get(edge.target);
        line.setAttribute("x1", left.x.toFixed(1));
        line.setAttribute("y1", left.y.toFixed(1));
        line.setAttribute("x2", right.x.toFixed(1));
        line.setAttribute("y2", right.y.toFixed(1));
      }}

      for (const node of nodes.values()) {{
        const {{ group, circle, label }} = nodeGroups.get(node.id);
        group.setAttribute("transform", `translate(${{node.x.toFixed(1)}}, ${{node.y.toFixed(1)}})`);
        const anchor = node.x <= 600 ? "start" : "end";
        const labelX = anchor === "start" ? node.radius + 8 : -node.radius - 8;
        label.setAttribute("x", labelX.toFixed(1));
        label.setAttribute("y", "4");
        label.setAttribute("text-anchor", anchor);
        circle.setAttribute("cx", "0");
        circle.setAttribute("cy", "0");
      }}
    }}

    function clamp(value, min, max) {{
      return Math.max(min, Math.min(max, value));
    }}

    function svgPoint(event) {{
      const point = svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      return point.matrixTransform(svg.getScreenCTM().inverse());
    }}

    let dragging = null;

    nodeLayer.addEventListener("pointerdown", (event) => {{
      const group = event.target.closest(".node");
      if (!group) {{
        return;
      }}
      const node = nodes.get(group.dataset.nodeId);
      if (!node) {{
        return;
      }}
      dragging = node;
      group.classList.add("dragging");
      group.setPointerCapture(event.pointerId);
      event.preventDefault();
    }});

    nodeLayer.addEventListener("pointermove", (event) => {{
      if (!dragging) {{
        return;
      }}
      const point = svgPoint(event);
      dragging.x = clamp(point.x, 95, 1105);
      dragging.y = clamp(point.y, 125, 805);
      render();
    }});

    function releaseDrag(event) {{
      if (!dragging) {{
        return;
      }}
      const meta = nodeGroups.get(dragging.id);
      if (meta) {{
        meta.group.classList.remove("dragging");
        if (event) {{
          meta.group.releasePointerCapture(event.pointerId);
        }}
      }}
      dragging = null;
    }}

    nodeLayer.addEventListener("pointerup", releaseDrag);
    nodeLayer.addEventListener("pointercancel", releaseDrag);
    nodeLayer.addEventListener("lostpointercapture", releaseDrag);

    render();
  </script>
</body>
</html>
"""

    def _connection_network_model(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int,
    ) -> dict[str, Any]:
        degree_by_name: dict[str, int] = {}
        for connection in connections:
            degree_by_name[connection.left_name] = degree_by_name.get(connection.left_name, 0) + 1
            degree_by_name[connection.right_name] = degree_by_name.get(connection.right_name, 0) + 1

        selected_names = [
            name
            for name, _ in sorted(
                degree_by_name.items(),
                key=lambda item: (-item[1], item[0]),
            )[:max_people]
        ]
        selected_set = set(selected_names)
        selected_connections = [
            connection
            for connection in connections
            if connection.left_name in selected_set and connection.right_name in selected_set
        ]

        positions = self._force_layout(
            selected_names,
            selected_connections,
            1200 - 85 * 2,
            900 - 85 * 2 - 60,
            85,
            85 + 40,
        ) if selected_names else {}

        max_degree = max([degree_by_name[name] for name in selected_names] + [1])
        max_weight = max([item.supporting_article_count for item in selected_connections] + [1])

        nodes = []
        for index, name in enumerate(selected_names):
            degree = degree_by_name[name]
            radius = 8 + (18 * degree / max_degree)
            x, y = positions[name]
            nodes.append(
                {
                    "id": name,
                    "degree": degree,
                    "radius": round(radius, 2),
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "color": PALETTE[index % len(PALETTE)],
                }
            )

        edges = []
        for connection in selected_connections:
            left_x, left_y = positions[connection.left_name]
            right_x, right_y = positions[connection.right_name]
            edges.append(
                {
                    "source": connection.left_name,
                    "target": connection.right_name,
                    "weight": connection.supporting_article_count,
                    "stroke_width": round(1.2 + (2.8 * connection.supporting_article_count / max_weight), 2),
                    "opacity": round(0.22 + (0.38 * connection.supporting_article_count / max_weight), 2),
                    "x1": round(left_x, 2),
                    "y1": round(left_y, 2),
                    "x2": round(right_x, 2),
                    "y2": round(right_y, 2),
                }
            )

        return {
            "run_date": run_date.isoformat(),
            "max_people": max_people,
            "shown_count": len(selected_names),
            "nodes": nodes,
            "edges": edges,
        }

    def _force_layout(
        self,
        names: list[str],
        connections: list[WeeklyConnection],
        width: float,
        height: float,
        offset_x: float,
        offset_y: float,
    ) -> dict[str, tuple[float, float]]:
        positions: dict[str, list[float]] = {}
        center_x = offset_x + width / 2
        center_y = offset_y + height / 2
        radius = min(width, height) * 0.34
        count = max(len(names), 1)

        for index, name in enumerate(names):
            angle = (2 * math.pi * index / count) + self._angle_jitter(name)
            positions[name] = [
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle),
            ]

        edges = [(connection.left_name, connection.right_name, max(connection.supporting_article_count, 1)) for connection in connections]
        area = width * height
        ideal_length = math.sqrt(area / max(len(names), 1)) * 0.62
        temperature = min(width, height) * 0.11

        for _ in range(90):
            disp = {name: [0.0, 0.0] for name in names}

            for index, left in enumerate(names):
                for right in names[index + 1 :]:
                    delta_x = positions[left][0] - positions[right][0]
                    delta_y = positions[left][1] - positions[right][1]
                    distance = math.hypot(delta_x, delta_y) or 0.01
                    force = (ideal_length * ideal_length) / distance
                    move_x = delta_x / distance * force
                    move_y = delta_y / distance * force
                    disp[left][0] += move_x
                    disp[left][1] += move_y
                    disp[right][0] -= move_x
                    disp[right][1] -= move_y

            for left, right, weight in edges:
                delta_x = positions[left][0] - positions[right][0]
                delta_y = positions[left][1] - positions[right][1]
                distance = math.hypot(delta_x, delta_y) or 0.01
                force = (distance * distance) / ideal_length
                force *= 0.18 + (0.12 * weight)
                move_x = delta_x / distance * force
                move_y = delta_y / distance * force
                disp[left][0] -= move_x
                disp[left][1] -= move_y
                disp[right][0] += move_x
                disp[right][1] += move_y

            for name in names:
                delta_x, delta_y = disp[name]
                distance = math.hypot(delta_x, delta_y) or 0.01
                limited = min(distance, temperature)
                positions[name][0] += delta_x / distance * limited
                positions[name][1] += delta_y / distance * limited
                positions[name][0] = min(offset_x + width - 30, max(offset_x + 30, positions[name][0]))
                positions[name][1] = min(offset_y + height - 30, max(offset_y + 30, positions[name][1]))

            temperature *= 0.95

        return {name: (positions[name][0], positions[name][1]) for name in names}

    def _angle_jitter(self, name: str) -> float:
        digest = hashlib.sha1(name.encode("utf-8")).hexdigest()
        return (int(digest[:6], 16) / 0xFFFFFF - 0.5) * 0.22

    def _escape_xml(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
