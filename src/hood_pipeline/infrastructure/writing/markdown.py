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
        top_names = Counter(mention.name for mention in mentions).most_common(6)
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
        if mentions:
            for mention in mentions:
                lines.append(
                    f"- **{mention.name}** ({mention.role_category}) - {mention.context[:180]}"
                )
        else:
            lines.append("- No people were extracted for this day.")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)


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
        lines = [
            f"# Hood College Weekly Connections for {run_date.isoformat()}",
            "",
            "## Strongest Co-Mentions",
            "",
        ]
        if connections:
            for connection in connections:
                lines.append(
                    f"- **{connection.left_name}** and **{connection.right_name}** "
                    f"appeared together in {connection.supporting_article_count} article(s)."
                )
        else:
            lines.append("- No weekly connections were derived.")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)
