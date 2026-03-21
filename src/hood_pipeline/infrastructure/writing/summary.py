from __future__ import annotations

from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import SummaryPoint


ROLE_LABELS = {
    "administrator": "Administrators",
    "faculty": "Faculty",
    "staff": "Staff",
    "alumni": "Alumni",
    "student": "Students",
    "student-athlete": "Student-Athletes",
    "coach": "Coaches",
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

    def write_summary(self, points: list[SummaryPoint]) -> tuple[str, str]:
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.summary_dir / "discovery-summary.md"
        graph_path = self.summary_dir / "discovery-growth.svg"
        roles = self._ordered_roles(points)
        markdown_path.write_text(
            self._render_markdown(points, roles, graph_path.name),
            encoding="utf-8",
        )
        graph_path.write_text(
            self._render_svg(points, roles),
            encoding="utf-8",
        )
        return str(markdown_path), str(graph_path)

    def _ordered_roles(self, points: list[SummaryPoint]) -> list[str]:
        present = {role for point in points for role in point.counts_by_role}
        ordered = [role for role in ROLE_ORDER if role in present]
        ordered.extend(sorted(role for role in present if role not in ordered))
        return ordered

    def _render_markdown(self, points: list[SummaryPoint], roles: list[str], graph_name: str) -> str:
        lines = [
            "# Discovery Summary",
            "",
            "This table shows cumulative distinct people discovered by first-seen date.",
            "",
            f"![Discovery growth]({graph_name})",
            "",
        ]
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
