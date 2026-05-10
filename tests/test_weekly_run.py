import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from hood_pipeline.application.weekly_run import WeeklyRunService
from hood_pipeline.domain.models import FetchedArticle, PersonMention
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore
from hood_pipeline.infrastructure.writing.markdown import MarkdownConnectionWriter


class _WeeklyServices:
    def __init__(self, root: Path) -> None:
        self.sqlite = SQLiteStore(root / "test.db")
        self.sqlite.initialize()
        self.connection_writer = MarkdownConnectionWriter(root / "connections")
        self.social_network_writer = _FakeSocialNetworkWriter(root / "summary")


class _FakeSocialNetworkWriter:
    def __init__(self, summary_dir: Path) -> None:
        self.summary_dir = summary_dir

    def write_report(self, report):
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.summary_dir / "social-network-analysis.md"
        json_path = self.summary_dir / "social-network-analysis.json"
        markdown_path.write_text("# sna\n", encoding="utf-8")
        json_path.write_text("{}\n", encoding="utf-8")
        return str(markdown_path), str(json_path)


class WeeklyRunTest(unittest.TestCase):
    def test_weekly_run_builds_cumulative_connections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            services = _WeeklyServices(root)
            self._store_article(
                services.sqlite,
                url="https://example.com/article-1",
                fetched_at=datetime(2026, 4, 10, 12, 0, 0),
                seen_at=date(2026, 4, 10),
                mentions=[
                    self._mention("Alice Carter", "student", "Alice Carter was featured."),
                    self._mention("Bob Smith", "faculty", "Bob Smith was featured."),
                ],
            )
            self._store_article(
                services.sqlite,
                url="https://example.com/article-2",
                fetched_at=datetime(2026, 4, 24, 12, 0, 0),
                seen_at=date(2026, 4, 24),
                mentions=[
                    self._mention("Bob Smith", "faculty", "Bob Smith appeared again."),
                    self._mention("Carol Jones", "staff", "Carol Jones appeared again."),
                ],
            )

            result = WeeklyRunService(services).run(date(2026, 4, 25))

            pairs = {(item.left_name, item.right_name): item.supporting_article_count for item in result.connections}
            self.assertEqual(pairs[("Alice Carter", "Bob Smith")], 1)
            self.assertEqual(pairs[("Bob Smith", "Carol Jones")], 1)
            self.assertNotIn(("Alice Carter", "Carol Jones"), pairs)
            self.assertTrue(result.report_path.endswith("2026-04-25.md"))

    def _store_article(
        self,
        store: SQLiteStore,
        url: str,
        fetched_at: datetime,
        seen_at: date,
        mentions: list[PersonMention],
    ) -> None:
        article_id = store.upsert_article(
            FetchedArticle(
                source_id="test",
                url=url,
                title=url,
                published_at=None,
                published_at_source="unknown",
                fetched_at=fetched_at,
                body="Body",
                content_hash=url,
                is_relevant=True,
                relevance_reason="accepted",
            )
        )
        store.replace_article_mentions(article_id, mentions, seen_at)

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
