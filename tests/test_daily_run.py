from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from hood_pipeline.application.daily_run import DailyRunService
from hood_pipeline.domain.models import PersonMention, SourceItem
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore


class _FakeConfig:
    def __init__(self, db_path: Path, discoveries_dir: Path, metadata: dict | None = None) -> None:
        self.database_path = db_path
        self.discoveries_dir = discoveries_dir
        self.metadata = metadata or {}

    def load_source_definitions(self):
        return [
            {
                "source_id": "hood_news",
                "name": "Hood College News",
                "reader": "fake",
                "url": "https://www.hood.edu/news",
                "enabled": True,
                "metadata": self.metadata,
            }
        ]


class _FakeReader:
    def read(self, definition):
        return [
            SourceItem(
                source_id="hood_news",
                source_name="Hood College News",
                url="https://www.hood.edu/news/failing",
                title="Failing article",
                published_at=None,
                summary="",
            ),
            SourceItem(
                source_id="hood_news",
                source_name="Hood College News",
                url="https://www.hood.edu/news/working",
                title="Hood College Working article",
                published_at=None,
                summary="",
            ),
        ]


class _FakeFetcher:
    def fetch_article(self, url: str, fallback_published_at=None):
        if url.endswith("/failing"):
            raise RuntimeError("boom")
        return (
            "Debbie Ricker, Ph.D., president of Hood College, said the partnership matters.",
            datetime(2026, 3, 18, 12, 0, 0),
            "meta",
        )


class _FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 3, 20, 12, 0, 0)


class _FakeDisambiguator:
    def evaluate(self, article):
        return True, "accepted"


class _FakeExtractor:
    def extract(self, article):
        return [
            PersonMention(
                article_url=article.url,
                name="Debbie Ricker",
                role_category="administrator",
                role_text="President",
                context="Debbie Ricker, Ph.D., president of Hood College, said the partnership matters.",
                confidence=0.9,
                inclusion_note="Named with title.",
            )
        ]


class _FakeWriter:
    def __init__(self, discoveries_dir: Path) -> None:
        self.discoveries_dir = discoveries_dir

    def write_daily_story(self, run_date, articles, mentions):
        path = self.discoveries_dir / f"{run_date.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# test\n", encoding="utf-8")
        return str(path)


class _FakeSummaryWriter:
    def __init__(self, summary_dir: Path) -> None:
        self.summary_dir = summary_dir

    def write_summary(self, points, connection_graph_name=None, connection_graph_html_name=None):
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.summary_dir / "discovery-summary.md"
        graph_path = self.summary_dir / "discovery-growth.svg"
        markdown_path.write_text("# summary\n", encoding="utf-8")
        graph_path.write_text("<svg></svg>\n", encoding="utf-8")
        return str(markdown_path), str(graph_path)

    def write_connection_network_graph(self, run_date, connections, max_people=25):
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        graph_path = self.summary_dir / "connection-network.svg"
        graph_path.write_text("<svg></svg>\n", encoding="utf-8")
        return str(graph_path)

    def write_connection_network_html(self, run_date, connections, max_people=25):
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        html_path = self.summary_dir / "connection-network.html"
        html_path.write_text("<!DOCTYPE html>\n", encoding="utf-8")
        return str(html_path)


class _FakeMonthlyWriter:
    def __init__(self, monthly_dir: Path) -> None:
        self.monthly_dir = monthly_dir

    def write_monthly_report(self, run_date, period_start, period_end, articles, mentions):
        self.monthly_dir.mkdir(parents=True, exist_ok=True)
        path = self.monthly_dir / f"{period_start.strftime('%Y-%m')}.md"
        path.write_text("# monthly\n", encoding="utf-8")
        return str(path)


class _FakeServices:
    def __init__(self, db_path: Path, discoveries_dir: Path, metadata: dict | None = None) -> None:
        self.config = _FakeConfig(db_path, discoveries_dir, metadata=metadata)
        self.clock = _FakeClock()
        self.fetcher = _FakeFetcher()
        self.disambiguator = _FakeDisambiguator()
        self.extractor = _FakeExtractor()
        self.sqlite = SQLiteStore(db_path)
        self.sqlite.initialize()
        self.discovery_writer = _FakeWriter(discoveries_dir)
        self.summary_writer = _FakeSummaryWriter(discoveries_dir.parent / "summary")
        self.monthly_writer = _FakeMonthlyWriter(discoveries_dir.parent / "monthly")
        self.source_readers = {"fake": _FakeReader()}


class DailyRunTest(unittest.TestCase):
    def test_daily_run_skips_failed_fetch_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            services = _FakeServices(root / "test.db", root / "discoveries")
            result = DailyRunService(services).run(date(2026, 3, 20))
            self.assertEqual(result.articles_seen, 2)
            self.assertEqual(result.articles_stored, 1)
            self.assertEqual(len(result.mentions), 1)
            self.assertTrue(result.summary_path.endswith("discovery-summary.md"))
            self.assertTrue(result.connection_graph_path.endswith("connection-network.svg"))
            self.assertTrue(result.connection_graph_html_path.endswith("connection-network.html"))
            self.assertIsNone(result.monthly_report_path)

    def test_daily_run_prefetch_keywords_skip_unmatched_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            services = _FakeServices(
                root / "test.db",
                root / "discoveries",
                metadata={"prefetch_keywords_any": ["hood college"]},
            )
            result = DailyRunService(services).run(date(2026, 3, 20))
            self.assertEqual(result.articles_seen, 2)
            self.assertEqual(result.articles_stored, 1)
            self.assertEqual(len(result.mentions), 1)

    def test_daily_run_publishes_monthly_report_on_first_day(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            services = _FakeServices(root / "test.db", root / "discoveries")
            result = DailyRunService(services).run(date(2026, 4, 1))
            self.assertTrue(result.monthly_report_path.endswith("2026-03.md"))


if __name__ == "__main__":
    unittest.main()
