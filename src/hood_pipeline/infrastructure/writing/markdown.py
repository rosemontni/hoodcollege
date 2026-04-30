from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import FacultyStaffRecord, FetchedArticle, PersonMention, WeeklyConnection


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
        articles_by_url = {article.url: article for article in articles}
        merged_mentions = self._merge_mentions(mentions, articles_by_url)
        top_names = Counter(
            {name: item["article_count"] for name, item in merged_mentions.items()}
        ).most_common(6)
        name_list = ", ".join(name for name, _ in top_names)
        story_dates = sorted(
            {
                article.published_at.date().isoformat()
                for article in articles
                if article.published_at is not None
            }
        )
        date_span = self._date_span_label(story_dates)
        if articles:
            opening = (
                f"During the collection run on {run_date.isoformat()}, the pipeline stored {len(articles)} "
                f"Hood College article(s) spanning story dates {date_span}, with people such as "
                f"{name_list or 'no clearly extractable names'} appearing across campus news and athletics updates."
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
            for article in sorted(
                articles,
                key=lambda item: (
                    item.published_at or item.fetched_at,
                    item.title.lower(),
                ),
                reverse=True,
            ):
                lines.append(
                    f"- {self._story_date_label(article)} - [{article.title}]({article.url}) "
                    f"({article.source_id}, date source: {article.published_at_source})"
                )
        else:
            lines.append("- No new relevant sources were stored.")

        lines.extend(["", "## People Observed", ""])
        if merged_mentions:
            for name, item in merged_mentions.items():
                article_label = "article" if item["article_count"] == 1 else "articles"
                lines.append(
                    f"- **{name}** ({item['role_category']}, {item['article_count']} {article_label}) - "
                    f"stories dated {item['story_dates_label']}; {item['context'][:220]}"
                )
        else:
            lines.append("- No people were extracted for this day.")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _merge_mentions(
        self,
        mentions: list[PersonMention],
        articles_by_url: dict[str, FetchedArticle],
    ) -> dict[str, dict[str, object]]:
        merged: dict[str, dict[str, object]] = {}
        for mention in sorted(mentions, key=lambda item: (item.name.lower(), -item.confidence)):
            current = merged.get(mention.name)
            article = articles_by_url.get(mention.article_url)
            story_date = article.published_at.date().isoformat() if article and article.published_at else "date unavailable"
            if current is None:
                merged[mention.name] = {
                    "role_category": mention.role_category,
                    "context": mention.context,
                    "article_urls": {mention.article_url},
                    "story_dates": {story_date},
                    "best_confidence": mention.confidence,
                }
                continue

            current["article_urls"].add(mention.article_url)
            current["story_dates"].add(story_date)
            if mention.confidence > current["best_confidence"]:
                current["best_confidence"] = mention.confidence
                current["context"] = mention.context
                current["role_category"] = mention.role_category

        for item in merged.values():
            item["article_count"] = len(item["article_urls"])
            item["story_dates_label"] = self._date_span_label(sorted(item["story_dates"]))
        return merged

    def _story_date_label(self, article: FetchedArticle) -> str:
        if article.published_at is None:
            return "date unavailable"
        return article.published_at.date().isoformat()

    def _date_span_label(self, dates: list[str]) -> str:
        cleaned = [value for value in dates if value]
        if not cleaned:
            return "date unavailable"
        if len(cleaned) == 1:
            return cleaned[0]
        return f"{cleaned[0]} to {cleaned[-1]}"


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


class MarkdownDirectoryWriter:
    def __init__(self, directory_dir: Path) -> None:
        self.directory_dir = directory_dir

    def write_faculty_staff_directory(
        self,
        run_date: date,
        source_url: str,
        records: list[FacultyStaffRecord],
    ) -> str:
        self.directory_dir.mkdir(parents=True, exist_ok=True)
        path = self.directory_dir / "faculty-staff-directory.md"
        counts_by_role = Counter(record.role_category for record in records)
        active_count = sum(1 for record in records if record.active)
        inactive_count = len(records) - active_count
        lines = [
            "# Hood College Faculty and Staff Directory",
            "",
            f"Imported on {run_date.isoformat()} from [{source_url}]({source_url}).",
            "",
            "## Snapshot",
            "",
            f"- Directory records: {len(records)}",
            f"- Active records: {active_count}",
            f"- Inactive retained records: {inactive_count}",
        ]
        for role, count in sorted(counts_by_role.items()):
            lines.append(f"- {role.title()}: {count}")
        lines.extend(
            [
                "",
                "## Records",
                "",
                "| Name | Role | Active | Last Seen In Directory | Faculty Type | Titles | Email | Phone | Profile |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for record in sorted(records, key=lambda item: (not item.active, item.name.lower())):
            profile = f"[Profile]({record.profile_url})" if record.profile_url else ""
            lines.append(
                "| "
                + " | ".join(
                    [
                        self._escape_table(record.name),
                        self._escape_table(record.role_category),
                        "yes" if record.active else "no",
                        record.last_seen_in_directory.isoformat(),
                        self._escape_table(", ".join(record.faculty_types)),
                        self._escape_table("; ".join(record.titles)),
                        self._escape_table(record.email),
                        self._escape_table(record.phone),
                        profile,
                    ]
                )
                + " |"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _escape_table(self, value: str) -> str:
        return value.replace("|", "\\|")


class MarkdownMonthlyWriter:
    def __init__(self, monthly_reports_dir: Path) -> None:
        self.monthly_reports_dir = monthly_reports_dir

    def write_monthly_report(
        self,
        run_date: date,
        period_start: date,
        period_end: date,
        articles: list[FetchedArticle],
        mentions: list[PersonMention],
    ) -> str:
        self.monthly_reports_dir.mkdir(parents=True, exist_ok=True)
        path = self.monthly_reports_dir / f"{period_start.strftime('%Y-%m')}.md"
        article_urls_by_person, role_by_person = self._roll_up_people(mentions)

        source_counts = Counter(article.source_id for article in articles)
        distinct_people = len(article_urls_by_person)
        narrative_paragraphs = self._build_narrative_essay(
            period_start,
            period_end,
            articles,
        )

        lines = [
            f"# Hood College Monthly Report for {period_start.strftime('%B %Y')}",
            "",
            (
                f"Published on {run_date.isoformat()}, this report covers Hood College stories dated "
                f"from {period_start.isoformat()} through {period_end.isoformat()}."
            ),
            "",
            "## Narrative Essay",
            "",
        ]
        lines.extend(narrative_paragraphs)
        if articles:
            lines.extend(
                [
                    "",
                    "## Reporting Appendix",
                    "",
                    "## Snapshot",
                    "",
                    f"- Dated relevant stories: {len(articles)}",
                    f"- Distinct people mentioned: {distinct_people}",
                    f"- Sources represented: {len(source_counts)}",
                ]
            )
            if source_counts:
                source_summary = ", ".join(
                    f"{source_id} ({count})"
                    for source_id, count in source_counts.most_common(5)
                )
                lines.append(f"- Source mix: {source_summary}")
        else:
            lines.extend(
                [
                    "",
                    "## Reporting Appendix",
                    "",
                    "No dated Hood College stories were available for this monthly window.",
                    "",
                    "## Snapshot",
                    "",
                    "- Dated relevant stories: 0",
                    "- Distinct people mentioned: 0",
                ]
            )

        lines.extend(["", "## Story Timeline", ""])
        if articles:
            for article in articles:
                lines.append(
                    f"- {article.published_at.date().isoformat() if article.published_at else 'date unavailable'} - "
                    f"[{article.title}]({article.url}) ({article.source_id}, date source: {article.published_at_source})"
                )
        else:
            lines.append("- No dated stories were available to summarize.")

        lines.extend(["", "## People In Focus", ""])
        if article_urls_by_person:
            ranked_people = sorted(
                article_urls_by_person.items(),
                key=lambda item: (-len(item[1]), item[0].lower()),
            )
            for name, article_urls in ranked_people[:15]:
                article_count = len(article_urls)
                article_label = "story" if article_count == 1 else "stories"
                role = role_by_person.get(name, "person")
                lines.append(f"- **{name}** ({role}) appeared in {article_count} dated {article_label}.")
        else:
            lines.append("- No people were extracted from dated stories in this month.")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _roll_up_people(
        self,
        mentions: list[PersonMention],
    ) -> tuple[dict[str, set[str]], dict[str, str]]:
        article_urls_by_person: dict[str, set[str]] = {}
        role_by_person: dict[str, str] = {}
        for mention in mentions:
            article_urls_by_person.setdefault(mention.name, set()).add(mention.article_url)
            existing_role = role_by_person.get(mention.name, "person")
            role_by_person[mention.name] = self._preferred_role(existing_role, mention.role_category)
        return article_urls_by_person, role_by_person

    def _build_narrative_essay(
        self,
        period_start: date,
        period_end: date,
        articles: list[FetchedArticle],
    ) -> list[str]:
        month_label = period_start.strftime("%B %Y")
        if not articles:
            return [
                (
                    f"Hood College had no dated public stories available for {month_label}, leaving too little "
                    "confirmed material for a local monthly essay."
                )
            ]

        month_name = period_start.strftime("%B")
        themes = self._theme_labels(articles)
        theme_text = self._natural_join(themes[:4])

        lead = (
            f"In {month_name}, Hood College's public story was one of steady campus motion. "
            f"The month brought attention to {theme_text or 'academic life, student experience, athletics, and community-facing work'}, "
            "with the college presenting itself as both a residential campus and a civic neighbor in Frederick."
        )
        campus_paragraph = (
            "Academic and graduate education remained a central thread. Stories from classrooms, laboratories, professional programs, "
            "and faculty work pointed to a college trying to make learning visible beyond course catalogs and commencement speeches. "
            "The strongest impression was of an institution using practical examples to show how study at Hood connects to work, service, and public life."
        )
        community_paragraph = (
            "The month also had a broader community rhythm. Public events, athletics updates, and feature stories added texture to the campus calendar, "
            "showing a small college balancing daily operations with moments meant for alumni, neighbors, families, and prospective students. "
            f"Taken together, the public record suggests Hood spent {month_name} reinforcing its role as a compact but active part of Frederick's educational and cultural landscape."
        )
        return [lead, "", campus_paragraph, "", community_paragraph]

    def _preferred_role(self, current_role: str, new_role: str) -> str:
        priority = {
            "person": 0,
            "student": 1,
            "student-athlete": 2,
            "alumni": 2,
            "staff": 3,
            "faculty": 4,
            "coach": 4,
            "administrator": 5,
        }
        if priority.get(new_role, 0) >= priority.get(current_role, 0):
            return new_role
        return current_role

    def _theme_labels(self, articles: list[FetchedArticle]) -> list[str]:
        text = " ".join(f"{article.title} {article.body[:600]}" for article in articles).lower()
        theme_rules = [
            (
                "classroom and laboratory work",
                ["biology", "laboratory", "research", "classroom", "faculty", "education", "program"],
            ),
            (
                "graduate and professional study",
                ["graduate", "mba", "counseling", "professional", "student spotlight"],
            ),
            (
                "arts and public events",
                ["concert", "jazz", "exhibit", "lecture", "gallery", "performance"],
            ),
            (
                "athletics and team operations",
                ["athletics", "lacrosse", "swimming", "coach", "basketball", "volleyball", "soccer"],
            ),
            (
                "alumni and community service",
                ["alumni", "community", "service", "partnership", "frederick", "nonprofit", "teacher"],
            ),
        ]
        themes = [label for label, keywords in theme_rules if any(keyword in text for keyword in keywords)]
        return themes or ["campus life"]

    def _natural_join(self, items: list[str]) -> str:
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return f"{', '.join(items[:-1])}, and {items[-1]}"
