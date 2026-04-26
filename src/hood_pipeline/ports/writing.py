from __future__ import annotations

from datetime import date
from pathlib import Path
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
        connection_graph_name: str | None = None,
        connection_graph_html_name: str | None = None,
    ) -> tuple[str, str]:
        ...

    def write_connection_network_graph(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int = 25,
    ) -> str:
        ...


class PagesWriter(Protocol):
    def build_site(self, output_dir: Path) -> str:
        ...

    def write_connection_network_html(
        self,
        run_date: date,
        connections: list[WeeklyConnection],
        max_people: int = 25,
    ) -> str:
        ...
