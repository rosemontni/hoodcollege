from __future__ import annotations

from datetime import date
from typing import Protocol

from hood_pipeline.domain.models import FetchedArticle, PersonMention, WeeklyConnection
from hood_pipeline.domain.models import SummaryPoint


class ArticleRepository(Protocol):
    def upsert_article(self, article: FetchedArticle) -> int:
        ...

    def has_article(self, url: str, content_hash: str | None = None) -> bool:
        ...

    def relevant_articles_for_date(self, run_date: date) -> list[FetchedArticle]:
        ...


class PersonRepository(Protocol):
    def replace_article_mentions(self, article_id: int, mentions: list[PersonMention], seen_at: date) -> None:
        ...

    def mentions_for_date(self, run_date: date) -> list[PersonMention]:
        ...


class ConnectionRepository(Protocol):
    def replace_weekly_connections(self, week_start: date, connections: list[WeeklyConnection]) -> None:
        ...

    def mentions_through_date(self, run_date: date):
        ...


class SummaryRepository(Protocol):
    def cumulative_people_summary(self) -> list[SummaryPoint]:
        ...
