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
    published_at_source: str
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
    connection_graph_path: str
    connection_graph_html_path: str
    monthly_report_path: str | None = None


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
class MonthlyRunResult:
    run_date: date
    period_start: date
    period_end: date
    articles: list[FetchedArticle]
    report_path: str


@dataclass(frozen=True)
class FacultyStaffRecord:
    name: str
    role_category: str
    faculty_types: list[str]
    titles: list[str]
    phone: str
    email: str
    profile_url: str
    source_url: str
    imported_at: date
    last_seen_in_directory: date
    active: bool


@dataclass(frozen=True)
class FacultyStaffImportResult:
    run_date: date
    source_url: str
    records: list[FacultyStaffRecord]
    report_path: str


@dataclass(frozen=True)
class SummaryPoint:
    run_date: date
    counts_by_role: dict[str, int]
    total: int


@dataclass(frozen=True)
class StoredArticleMetadata:
    url: str
    content_hash: str
    published_at: datetime | None
    published_at_source: str
