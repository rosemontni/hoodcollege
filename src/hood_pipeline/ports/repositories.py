from __future__ import annotations

from datetime import date
from typing import Protocol

from hood_pipeline.domain.models import FetchedArticle, PersonMention, StoredArticleMetadata, WeeklyConnection
from hood_pipeline.domain.models import SummaryPoint


class ArticleRepository(Protocol):
    def upsert_article(self, article: FetchedArticle) -> int:
        ...

    def has_article(self, url: str, content_hash: str | None = None) -> bool:
        ...

    def relevant_articles_for_date(self, run_date: date) -> list[FetchedArticle]:
        ...

    def relevant_articles_for_seen_date(self, run_date: date) -> list[FetchedArticle]:
        ...

    def relevant_articles_published_between(self, start_date: date, end_date: date) -> list[FetchedArticle]:
        ...

    def stored_article(self, url: str) -> StoredArticleMetadata | None:
        ...

    def update_article_story_date(
        self,
        url: str,
        published_at,
        published_at_source: str,
    ) -> None:
        ...


class PersonRepository(Protocol):
    def replace_article_mentions(self, article_id: int, mentions: list[PersonMention], seen_at: date) -> None:
        ...

    def mentions_for_date(self, run_date: date) -> list[PersonMention]:
        ...

    def mentions_for_article_urls(self, article_urls: list[str]) -> list[PersonMention]:
        ...


class ConnectionRepository(Protocol):
    def replace_weekly_connections(self, week_start: date, connections: list[WeeklyConnection]) -> None:
        ...

    def mentions_through_date(self, run_date: date):
        ...


class SummaryRepository(Protocol):
    def cumulative_people_summary(self) -> list[SummaryPoint]:
        ...
