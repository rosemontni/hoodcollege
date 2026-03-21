from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from hood_pipeline.domain.models import FetchedArticle, PersonMention, SummaryPoint, WeeklyConnection


class SQLiteStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def session(self):
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.session() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    published_at TEXT,
                    fetched_at TEXT NOT NULL,
                    body TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    is_relevant INTEGER NOT NULL,
                    relevance_reason TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    role_category TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS article_people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    article_url TEXT NOT NULL,
                    seen_date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role_category TEXT NOT NULL,
                    role_text TEXT NOT NULL,
                    context TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    inclusion_note TEXT NOT NULL,
                    FOREIGN KEY(article_id) REFERENCES articles(id)
                );

                CREATE TABLE IF NOT EXISTS weekly_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_start TEXT NOT NULL,
                    left_name TEXT NOT NULL,
                    right_name TEXT NOT NULL,
                    connection_type TEXT NOT NULL,
                    supporting_article_count INTEGER NOT NULL,
                    shared_context TEXT NOT NULL
                );
                """
            )

    def has_article(self, url: str, content_hash: str | None = None) -> bool:
        with self.session() as connection:
            if content_hash is None:
                row = connection.execute("SELECT 1 FROM articles WHERE url = ?", (url,)).fetchone()
            else:
                row = connection.execute(
                    "SELECT 1 FROM articles WHERE url = ? AND content_hash = ?",
                    (url, content_hash),
                ).fetchone()
        return row is not None

    def upsert_article(self, article: FetchedArticle) -> int:
        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO articles (
                    source_id, url, title, published_at, fetched_at, body, content_hash, is_relevant, relevance_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    source_id=excluded.source_id,
                    title=excluded.title,
                    published_at=excluded.published_at,
                    fetched_at=excluded.fetched_at,
                    body=excluded.body,
                    content_hash=excluded.content_hash,
                    is_relevant=excluded.is_relevant,
                    relevance_reason=excluded.relevance_reason
                """,
                (
                    article.source_id,
                    article.url,
                    article.title,
                    _iso(article.published_at),
                    _iso(article.fetched_at),
                    article.body,
                    article.content_hash,
                    int(article.is_relevant),
                    article.relevance_reason,
                ),
            )
            row = connection.execute("SELECT id FROM articles WHERE url = ?", (article.url,)).fetchone()
            if row is None:
                raise RuntimeError(f"Failed to look up article id for {article.url}")
            return int(row["id"])

    def replace_article_mentions(self, article_id: int, mentions: list[PersonMention], seen_at: date) -> None:
        with self.session() as connection:
            article_url_row = connection.execute(
                "SELECT url FROM articles WHERE id = ?",
                (article_id,),
            ).fetchone()
            if article_url_row is None:
                raise RuntimeError(f"Unknown article id {article_id}")
            article_url = str(article_url_row["url"])
            connection.execute("DELETE FROM article_people WHERE article_id = ?", (article_id,))
            for mention in mentions:
                connection.execute(
                    """
                    INSERT INTO article_people (
                        article_id, article_url, seen_date, name, role_category, role_text, context, confidence, inclusion_note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article_id,
                        article_url,
                        seen_at.isoformat(),
                        mention.name,
                        mention.role_category,
                        mention.role_text,
                        mention.context,
                        mention.confidence,
                        mention.inclusion_note,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO people (name, role_category, first_seen, last_seen)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO NOTHING
                    """,
                    (mention.name, mention.role_category, seen_at.isoformat(), seen_at.isoformat()),
                )
                existing = connection.execute(
                    "SELECT role_category, first_seen FROM people WHERE name = ?",
                    (mention.name,),
                ).fetchone()
                if existing is None:
                    continue
                preferred_role = _preferred_role(existing["role_category"], mention.role_category)
                connection.execute(
                    """
                    UPDATE people
                    SET role_category = ?, first_seen = ?, last_seen = ?
                    WHERE name = ?
                    """,
                    (
                        preferred_role,
                        existing["first_seen"],
                        seen_at.isoformat(),
                        mention.name,
                    ),
                )

    def mentions_for_date(self, run_date: date) -> list[PersonMention]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT article_url, name, role_category, role_text, context, confidence, inclusion_note
                FROM article_people
                WHERE seen_date = ?
                ORDER BY name
                """,
                (run_date.isoformat(),),
            ).fetchall()
        return [PersonMention(**dict(row)) for row in rows]

    def weekly_mentions(self, week_start: date, week_end: date) -> list[sqlite3.Row]:
        with self.session() as connection:
            return connection.execute(
                """
                SELECT article_url, name
                FROM article_people
                WHERE seen_date BETWEEN ? AND ?
                ORDER BY article_url, name
                """,
                (week_start.isoformat(), week_end.isoformat()),
            ).fetchall()

    def replace_weekly_connections(self, week_start: date, connections: list[WeeklyConnection]) -> None:
        with self.session() as connection:
            connection.execute(
                "DELETE FROM weekly_connections WHERE week_start = ?",
                (week_start.isoformat(),),
            )
            for connection_row in connections:
                connection.execute(
                    """
                    INSERT INTO weekly_connections (
                        week_start, left_name, right_name, connection_type, supporting_article_count, shared_context
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        week_start.isoformat(),
                        connection_row.left_name,
                        connection_row.right_name,
                        connection_row.connection_type,
                        connection_row.supporting_article_count,
                        connection_row.shared_context,
                    ),
                )

    def relevant_articles_for_date(self, run_date: date) -> list[FetchedArticle]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT source_id, url, title, published_at, fetched_at, body, content_hash, is_relevant, relevance_reason
                FROM articles
                WHERE DATE(fetched_at) = ? AND is_relevant = 1
                ORDER BY title
                """,
                (run_date.isoformat(),),
            ).fetchall()
        return [
            FetchedArticle(
                source_id=row["source_id"],
                url=row["url"],
                title=row["title"],
                published_at=_parse_datetime(row["published_at"]),
                fetched_at=_parse_datetime(row["fetched_at"]) or datetime.utcnow(),
                body=row["body"],
                content_hash=row["content_hash"],
                is_relevant=bool(row["is_relevant"]),
                relevance_reason=row["relevance_reason"],
            )
            for row in rows
        ]

    def cumulative_people_summary(self) -> list[SummaryPoint]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT first_seen, role_category, COUNT(*) AS discovered_count
                FROM people
                GROUP BY first_seen, role_category
                ORDER BY first_seen, role_category
                """
            ).fetchall()
        by_date: dict[date, dict[str, int]] = {}
        for row in rows:
            run_date = date.fromisoformat(row["first_seen"])
            role_category = str(row["role_category"])
            count = int(row["discovered_count"])
            by_date.setdefault(run_date, {})[role_category] = count

        cumulative: dict[str, int] = {}
        points: list[SummaryPoint] = []
        for run_date in sorted(by_date):
            for role_category, count in by_date[run_date].items():
                cumulative[role_category] = cumulative.get(role_category, 0) + count
            points.append(
                SummaryPoint(
                    run_date=run_date,
                    counts_by_role=dict(sorted(cumulative.items())),
                    total=sum(cumulative.values()),
                )
            )
        return points


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


ROLE_PRIORITY = {
    "person": 0,
    "student": 1,
    "student-athlete": 2,
    "alumni": 2,
    "staff": 3,
    "faculty": 4,
    "coach": 4,
    "administrator": 5,
}


def _preferred_role(current_role: str, new_role: str) -> str:
    current_priority = ROLE_PRIORITY.get(current_role, 0)
    new_priority = ROLE_PRIORITY.get(new_role, 0)
    if new_priority >= current_priority:
        return new_role
    return current_role
