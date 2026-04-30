from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from hood_pipeline.application.monthly_run import MonthlyRunService
from hood_pipeline.domain.models import FetchedArticle, PersonMention
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore
from hood_pipeline.infrastructure.writing.markdown import MarkdownMonthlyWriter


class _MonthlyServices:
    def __init__(self, root: Path) -> None:
        self.sqlite = SQLiteStore(root / "test.db")
        self.sqlite.initialize()
        self.monthly_writer = MarkdownMonthlyWriter(root / "monthly")


class MonthlyRunTest(unittest.TestCase):
    def test_monthly_run_uses_story_dates_not_fetch_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            services = _MonthlyServices(root)
            self._store_article(
                services.sqlite,
                url="https://example.com/april-story",
                fetched_at=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
                published_at=datetime(2026, 4, 28, 10, 0, tzinfo=timezone.utc),
                mentions=[self._mention("Debbie Ricker", "administrator", "Debbie Ricker was mentioned.")],
            )
            self._store_article(
                services.sqlite,
                url="https://example.com/march-story",
                fetched_at=datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc),
                published_at=datetime(2026, 3, 15, 10, 0, tzinfo=timezone.utc),
                mentions=[self._mention("Melissa Muntz", "staff", "Melissa Muntz was mentioned.")],
            )

            result = MonthlyRunService(services).run(date(2026, 5, 1))

            self.assertEqual(result.period_start, date(2026, 4, 1))
            self.assertEqual(result.period_end, date(2026, 4, 30))
            self.assertEqual([article.url for article in result.articles], ["https://example.com/april-story"])
            report_text = Path(result.report_path).read_text(encoding="utf-8")
            narrative_text = report_text.split("## Narrative Essay", 1)[1].split("## Reporting Appendix", 1)[0]
            self.assertIn("## Narrative Essay", report_text)
            self.assertIn("Hood College's public story", narrative_text)
            self.assertNotIn("Debbie Ricker", narrative_text)
            self.assertNotIn("connection", narrative_text.lower())
            self.assertNotIn("network", narrative_text.lower())
            self.assertNotIn("pipeline", narrative_text.lower())
            self.assertIn("2026-04-28 - [https://example.com/april-story]", report_text)
            self.assertNotIn("https://example.com/march-story", report_text)

    def _store_article(
        self,
        store: SQLiteStore,
        url: str,
        fetched_at: datetime,
        published_at: datetime,
        mentions: list[PersonMention],
    ) -> None:
        article_id = store.upsert_article(
            FetchedArticle(
                source_id="test",
                url=url,
                title=url,
                published_at=published_at,
                published_at_source="meta",
                fetched_at=fetched_at,
                body="Body",
                content_hash=url,
                is_relevant=True,
                relevance_reason="accepted",
            )
        )
        store.replace_article_mentions(article_id, mentions, fetched_at.date())

    def _mention(self, name: str, role_category: str, context: str) -> PersonMention:
        return PersonMention(
            article_url="https://example.com/placeholder",
            name=name,
            role_category=role_category,
            role_text=role_category,
            context=context,
            confidence=0.9,
            inclusion_note="test",
        )


if __name__ == "__main__":
    unittest.main()
