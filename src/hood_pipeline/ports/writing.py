from __future__ import annotations

from datetime import date
from typing import Protocol

from hood_pipeline.domain.models import FetchedArticle, PersonMention, WeeklyConnection
from hood_pipeline.domain.models import SummaryPoint


class DiscoveryWriter(Protocol):
    def write_daily_story(
        self,
        run_date: date,
        articles: list[FetchedArticle],
        mentions: list[PersonMention],
    ) -> str:
        ...


class ConnectionWriter(Protocol):
    def write_weekly_report(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
    ) -> str:
        ...


class SummaryWriter(Protocol):
    def write_summary(
        self,
        points: list[SummaryPoint],
    ) -> tuple[str, str]:
        ...
