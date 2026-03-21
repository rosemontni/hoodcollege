from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    name: str
    reader: str
    url: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceItem:
    source_id: str
    source_name: str
    url: str
    title: str
    published_at: datetime | None
    summary: str


@dataclass(frozen=True)
class FetchedArticle:
    source_id: str
    url: str
    title: str
    published_at: datetime | None
    fetched_at: datetime
    body: str
    content_hash: str
    is_relevant: bool
    relevance_reason: str


@dataclass(frozen=True)
class PersonMention:
    article_url: str
    name: str
    role_category: str
    role_text: str
    context: str
    confidence: float
    inclusion_note: str


@dataclass(frozen=True)
class DailyRunResult:
    run_date: date
    articles_seen: int
    articles_stored: int
    relevant_articles: list[FetchedArticle]
    mentions: list[PersonMention]
    discovery_path: str
    summary_path: str
    summary_graph_path: str


@dataclass(frozen=True)
class WeeklyConnection:
    left_name: str
    right_name: str
    connection_type: str
    supporting_article_count: int
    shared_context: str


@dataclass(frozen=True)
class WeeklyRunResult:
    run_date: date
    connections: list[WeeklyConnection]
    report_path: str


@dataclass(frozen=True)
class SummaryPoint:
    run_date: date
    counts_by_role: dict[str, int]
    total: int
