from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import FetchedArticle, PersonMention, WeeklyConnection


class MarkdownDiscoveryWriter:
    def __init__(self, discoveries_dir: Path) -> None:
        self.discoveries_dir = discoveries_dir

    def write_daily_story(
        self,
        run_date: date,
        articles: list[FetchedArticle],
        mentions: list[PersonMention],
    ) -> str:
        self.discoveries_dir.mkdir(parents=True, exist_ok=True)
        path = self.discoveries_dir / f"{run_date.isoformat()}.md"
        merged_mentions = self._merge_mentions(mentions)
        top_names = Counter(
            {name: item["article_count"] for name, item in merged_mentions.items()}
        ).most_common(6)
        name_list = ", ".join(name for name, _ in top_names)
        if articles:
            opening = (
                f"On {run_date.isoformat()}, Hood College coverage focused on {len(articles)} "
                f"article(s), with people such as {name_list or 'no clearly extractable names'} "
                "appearing across campus news and athletics updates."
            )
        else:
            opening = (
                f"On {run_date.isoformat()}, the pipeline did not store any new relevant Hood College "
                "articles worth turning into a discovery story."
            )

        lines = [
            f"# Hood College Discovery for {run_date.isoformat()}",
            "",
            opening,
            "",
            "## Sources",
            "",
        ]
        if articles:
            for article in articles:
                lines.append(f"- [{article.title}]({article.url})")
        else:
            lines.append("- No new relevant sources were stored.")

        lines.extend(["", "## People Observed", ""])
        if merged_mentions:
            for name, item in merged_mentions.items():
                article_label = "article" if item["article_count"] == 1 else "articles"
                lines.append(
                    f"- **{name}** ({item['role_category']}, {item['article_count']} {article_label}) - "
                    f"{item['context'][:220]}"
                )
        else:
            lines.append("- No people were extracted for this day.")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _merge_mentions(self, mentions: list[PersonMention]) -> dict[str, dict[str, object]]:
        merged: dict[str, dict[str, object]] = {}
        for mention in sorted(mentions, key=lambda item: (item.name.lower(), -item.confidence)):
            current = merged.get(mention.name)
            if current is None:
                merged[mention.name] = {
                    "role_category": mention.role_category,
                    "context": mention.context,
                    "article_urls": {mention.article_url},
                    "best_confidence": mention.confidence,
                }
                continue

            current["article_urls"].add(mention.article_url)
            if mention.confidence > current["best_confidence"]:
                current["best_confidence"] = mention.confidence
                current["context"] = mention.context
                current["role_category"] = mention.role_category

        for item in merged.values():
            item["article_count"] = len(item["article_urls"])
        return merged


class MarkdownConnectionWriter:
    def __init__(self, connections_dir: Path) -> None:
        self.connections_dir = connections_dir

    def write_weekly_report(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
    ) -> str:
        self.connections_dir.mkdir(parents=True, exist_ok=True)
        path = self.connections_dir / f"{run_date.isoformat()}.md"
        nodes = sorted({connection.left_name for connection in connections} | {connection.right_name for connection in connections})
        hub_counts = Counter()
        adjacency: dict[str, set[str]] = {}
        for connection in connections:
            hub_counts[connection.left_name] += 1
            hub_counts[connection.right_name] += 1
            adjacency.setdefault(connection.left_name, set()).add(connection.right_name)
            adjacency.setdefault(connection.right_name, set()).add(connection.left_name)
        components = self._components(adjacency)
        lines = [
            f"# Hood College Cumulative Connections for {run_date.isoformat()}",
            "",
            (
                f"As of {run_date.isoformat()}, the cumulative Hood College network links "
                f"{len(nodes)} people through {len(connections)} evidence-backed co-mention connection(s)."
                if connections
                else f"As of {run_date.isoformat()}, the pipeline has not yet derived any cumulative people connections."
            ),
            "",
            "## Network Snapshot",
            "",
        ]
        if connections:
            lines.extend(
                [
                    f"- People in network: {len(nodes)}",
                    f"- Connections in network: {len(connections)}",
                    f"- Connected groups: {len(components)}",
                ]
            )
        else:
            lines.append("- No cumulative connections are available yet.")

        lines.extend(["", "## Strongest Co-Mentions", ""])
        if connections:
            for connection in connections:
                lines.append(
                    f"- **{connection.left_name}** and **{connection.right_name}** "
                    f"appeared together in {connection.supporting_article_count} article(s)."
                )
        else:
            lines.append("- No cumulative connections were derived.")

        lines.extend(["", "## Network Hubs", ""])
        if hub_counts:
            for name, degree in hub_counts.most_common(10):
                people_label = "person" if degree == 1 else "people"
                lines.append(f"- **{name}** is directly connected to {degree} {people_label}.")
        else:
            lines.append("- No network hubs are available yet.")

        lines.extend(["", "## Connected Groups", ""])
        if components:
            for index, component in enumerate(sorted(components, key=lambda item: (-len(item), item)), start=1):
                preview = ", ".join(component[:10])
                suffix = "" if len(component) <= 10 else ", ..."
                lines.append(f"- Group {index} ({len(component)} people): {preview}{suffix}")
        else:
            lines.append("- No connected groups were derived.")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _components(self, adjacency: dict[str, set[str]]) -> list[list[str]]:
        visited: set[str] = set()
        components: list[list[str]] = []
        for start in sorted(adjacency):
            if start in visited:
                continue
            stack = [start]
            component: list[str] = []
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                stack.extend(sorted(adjacency.get(current, set()) - visited, reverse=True))
            components.append(sorted(component))
        return components
