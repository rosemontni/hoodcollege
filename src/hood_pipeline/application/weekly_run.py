from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from itertools import combinations

from hood_pipeline.domain.models import WeeklyConnection, WeeklyRunResult


class WeeklyRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> WeeklyRunResult:
        week_start = run_date - timedelta(days=6)
        rows = self.services.sqlite.weekly_mentions(week_start, run_date)
        grouped: dict[str, set[str]] = {}
        for row in rows:
            grouped.setdefault(row["article_url"], set()).add(row["name"])

        pairs: Counter[tuple[str, str]] = Counter()
        for names in grouped.values():
            for left, right in combinations(sorted(names), 2):
                pairs[(left, right)] += 1

        connections = [
            WeeklyConnection(
                left_name=left,
                right_name=right,
                connection_type="co_mention",
                supporting_article_count=count,
                shared_context="Observed in the same article during the weekly window.",
            )
            for (left, right), count in pairs.items()
            if count >= 1
        ]
        connections.sort(
            key=lambda item: (-item.supporting_article_count, item.left_name, item.right_name)
        )
        self.services.sqlite.replace_weekly_connections(week_start, connections)
        report_path = self.services.connection_writer.write_weekly_report(run_date, connections)
        return WeeklyRunResult(run_date=run_date, connections=connections, report_path=report_path)
