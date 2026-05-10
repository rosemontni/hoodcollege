from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hood_pipeline.application.social_network_analysis import SocialNetworkAnalysisReport


class SocialNetworkAnalysisWriter:
    def __init__(self, summary_dir: Path) -> None:
        self.summary_dir = summary_dir

    def write_report(self, report: SocialNetworkAnalysisReport) -> tuple[str, str]:
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.summary_dir / "social-network-analysis.md"
        json_path = self.summary_dir / "social-network-analysis.json"
        markdown_path.write_text(self._render_markdown(report), encoding="utf-8")
        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return str(markdown_path), str(json_path)

    def _render_markdown(self, report: SocialNetworkAnalysisReport) -> str:
        lines = [
            f"# Hood College Social Network Analysis for {report.run_date.isoformat()}",
            "",
            report.narratives["scope"],
            "",
            "## Network Overview",
            "",
            report.narratives["overview"],
            "",
            *self._overview_lines(report.overview),
            "",
            "## Strongest Public Co-Mention Bonds",
            "",
            report.narratives["strongest_bonds"],
            "",
            self._bond_table(report.strongest_bonds),
            "",
            "## Most Connected People By Role",
            "",
            report.narratives["role_leaders"],
            "",
        ]
        for role, people in report.role_leaders.items():
            lines.extend(
                [
                    f"### {self._role_label_from_people(role, people)}",
                    "",
                    self._person_table(people, include_recent=False),
                    "",
                ]
            )

        lines.extend(
            [
                "## Faculty Public Visibility",
                "",
                report.narratives["faculty_visibility"],
                "",
                self._person_table(report.faculty_visibility, include_recent=False),
                "",
                "## Faculty-Administration Connectors",
                "",
                report.narratives["faculty_administration_connectors"],
                "",
                self._person_table(report.faculty_administration_connectors, include_bridge=True),
                "",
                "## Brokerage And Critical Persons",
                "",
                report.narratives["brokers"],
                "",
                self._person_table(report.brokers, include_recent=False),
                "",
                "## Articulation People",
                "",
                report.narratives["articulation_people"],
                "",
                self._person_table(report.articulation_people, include_recent=False),
                "",
                "## Local Bridge Bonds",
                "",
                report.narratives["local_bridges"],
                "",
                self._local_bridge_table(report.local_bridges),
                "",
                "## Role Mixing",
                "",
                report.narratives["role_mixing"],
                "",
                self._role_mixing_table(report.role_mixing),
                "",
                "## Emerging People In The Last 30 Days",
                "",
                report.narratives["emerging_people"],
                "",
                self._person_table(report.emerging_people, include_recent=True),
                "",
                "## Connected Communities",
                "",
                report.narratives["communities"],
                "",
                self._community_table(report.communities),
                "",
                "## Data Notes",
                "",
                "- A bond is created when two names are observed in the same stored article or source item.",
                "- Edge weight is the number of distinct stored articles supporting that co-mention.",
                "- Degree counts distinct neighbors; weighted degree sums repeated co-mentions.",
                "- Betweenness and articulation metrics are structural signals from the public evidence graph, not claims of private influence.",
                "- Recent metrics use the pipeline's seen date over the last 30 days.",
            ]
        )
        return "\n".join(lines) + "\n"

    def _overview_lines(self, overview: dict[str, Any]) -> list[str]:
        lines = [
            f"- People in graph: {overview['people']}",
            f"- Co-mention connections: {overview['connections']}",
            f"- Source articles/items: {overview['articles']}",
            f"- Source families represented: {overview['sources']}",
            f"- Density: {overview['density']}",
            f"- Connected groups: {overview['connected_groups']}",
            f"- Largest connected group: {overview['largest_group_size']} people",
        ]
        for role in overview.get("roles", []):
            lines.append(f"- {role['label']}: {role['count']}")
        return lines

    def _bond_table(self, bonds: list[dict[str, Any]]) -> str:
        if not bonds:
            return "_No repeated public co-mention bonds are available yet._"
        lines = [
            "| Rank | People | Roles | Shared Articles | Jaccard | Sources |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for index, bond in enumerate(bonds, start=1):
            people = f"{bond['left']} and {bond['right']}"
            roles = f"{self._role_label(bond['left_role'])} / {self._role_label(bond['right_role'])}"
            sources = ", ".join(bond.get("sources", []))
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(index),
                        self._escape_table(people),
                        self._escape_table(roles),
                        str(bond["shared_article_count"]),
                        f"{float(bond['jaccard']):.3f}",
                        self._escape_table(sources),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _person_table(
        self,
        people: list[dict[str, Any]],
        include_recent: bool = False,
        include_bridge: bool = False,
    ) -> str:
        if not people:
            return "_No qualifying people are available yet._"
        headers = ["Rank", "Name", "Role", "Degree", "Weighted Degree", "Mentions", "Sources", "Betweenness", "PageRank"]
        if include_bridge:
            headers.extend(["Faculty Neighbors", "Administrator Neighbors", "Bridge Score"])
        if include_recent:
            headers.extend(["Recent Mentions", "Recent Degree"])
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for index, person in enumerate(people, start=1):
            row = [
                str(index),
                self._escape_table(person["name"]),
                self._escape_table(person["role_label"]),
                str(person["degree"]),
                str(person["weighted_degree"]),
                str(person["mention_count"]),
                str(person["source_count"]),
                f"{float(person['betweenness']):.5f}",
                f"{float(person['pagerank']):.6f}",
            ]
            if include_bridge:
                row.extend(
                    [
                        str(person["faculty_neighbor_count"]),
                        str(person["administrator_neighbor_count"]),
                        str(person["faculty_admin_bridge_score"]),
                    ]
                )
            if include_recent:
                row.extend([str(person["recent_mentions"]), str(person["recent_degree"])])
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)

    def _local_bridge_table(self, bridges: list[dict[str, Any]]) -> str:
        if not bridges:
            return "_No local bridge bonds are available yet._"
        lines = [
            "| Rank | People | Roles | Shared Articles | Endpoint Degrees |",
            "| --- | --- | --- | --- | --- |",
        ]
        for index, bridge in enumerate(bridges, start=1):
            people = f"{bridge['left']} and {bridge['right']}"
            roles = f"{self._role_label(bridge['left_role'])} / {self._role_label(bridge['right_role'])}"
            degrees = f"{bridge['left_degree']} / {bridge['right_degree']}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(index),
                        self._escape_table(people),
                        self._escape_table(roles),
                        str(bridge["shared_article_count"]),
                        degrees,
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _role_mixing_table(self, role_mixing: list[dict[str, Any]]) -> str:
        if not role_mixing:
            return "_No cross-role mixing is available yet._"
        lines = [
            "| Rank | Role Pair | Distinct Edges | Weighted Co-Mentions |",
            "| --- | --- | --- | --- |",
        ]
        for index, item in enumerate(role_mixing, start=1):
            pair = f"{item['left_role_label']} / {item['right_role_label']}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(index),
                        self._escape_table(pair),
                        str(item["edge_count"]),
                        str(item["weighted_count"]),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _community_table(self, communities: list[dict[str, Any]]) -> str:
        if not communities:
            return "_No connected communities are available yet._"
        lines = [
            "| Group | Size | Dominant Roles | Top People |",
            "| --- | --- | --- | --- |",
        ]
        for community in communities:
            roles = ", ".join(
                f"{role['label']} ({role['count']})"
                for role in community.get("role_mix", [])[:4]
            )
            top_people = ", ".join(community.get("top_people", []))
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(community["group"]),
                        str(community["size"]),
                        self._escape_table(roles),
                        self._escape_table(top_people),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _role_label_from_people(self, role: str, people: list[dict[str, Any]]) -> str:
        if people:
            return str(people[0]["role_label"])
        return self._role_label(role)

    @staticmethod
    def _role_label(role: str) -> str:
        labels = {
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
        return labels.get(role, role.replace("-", " ").title())

    @staticmethod
    def _escape_table(value: str) -> str:
        return value.replace("|", "\\|")
