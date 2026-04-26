from __future__ import annotations

from collections import Counter
from datetime import date
from itertools import combinations
from typing import Iterable

from hood_pipeline.domain.models import WeeklyConnection


def build_cumulative_connections(rows: Iterable[object], run_date: date) -> list[WeeklyConnection]:
    grouped: dict[str, set[str]] = {}
    for row in rows:
        article_url = str(row["article_url"])
        name = str(row["name"])
        grouped.setdefault(article_url, set()).add(name)

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
            shared_context=f"Observed in the same article across cumulative coverage through {run_date.isoformat()}.",
        )
        for (left, right), count in pairs.items()
        if count >= 1
    ]
    connections.sort(
        key=lambda item: (-item.supporting_article_count, item.left_name, item.right_name)
    )
    return connections
