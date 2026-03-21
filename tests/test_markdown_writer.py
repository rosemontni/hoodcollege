import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from hood_pipeline.domain.models import FetchedArticle, PersonMention, WeeklyConnection
from hood_pipeline.infrastructure.writing.markdown import (
    MarkdownConnectionWriter,
    MarkdownDiscoveryWriter,
)


class MarkdownWriterTest(unittest.TestCase):
    def test_daily_writer_merges_duplicate_people(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownDiscoveryWriter(Path(tmpdir))
            path = writer.write_daily_story(
                run_date=date(2026, 3, 20),
                articles=[
                    FetchedArticle(
                        source_id="hood_news",
                        url="https://www.hood.edu/news/example",
                        title="Example story",
                        published_at=None,
                        fetched_at=datetime.now(),
                        body="Body",
                        content_hash="hash",
                        is_relevant=True,
                        relevance_reason="accepted",
                    )
                    ,
                    FetchedArticle(
                        source_id="hood_news",
                        url="https://www.hood.edu/news/example-2",
                        title="Example story 2",
                        published_at=None,
                        fetched_at=datetime.now(),
                        body="Body",
                        content_hash="hash-2",
                        is_relevant=True,
                        relevance_reason="accepted",
                    )
                ],
                mentions=[
                    PersonMention(
                        article_url="https://www.hood.edu/news/example",
                        name="Debbie Ricker",
                        role_category="administrator",
                        role_text="President",
                        context="Debbie Ricker spoke about the partnership.",
                        confidence=0.9,
                        inclusion_note="Named in article context.",
                    ),
                    PersonMention(
                        article_url="https://www.hood.edu/news/example-2",
                        name="Debbie Ricker",
                        role_category="person",
                        role_text="",
                        context="Debbie Ricker later discussed the grant award.",
                        confidence=0.7,
                        inclusion_note="Named in article context.",
                    )
                ],
            )
            text = Path(path).read_text(encoding="utf-8")
            self.assertEqual(text.count("**Debbie Ricker**"), 1)
            self.assertIn("(administrator, 2 articles)", text)
            self.assertIn("Example story", text)

    def test_weekly_writer_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownConnectionWriter(Path(tmpdir))
            path = writer.write_weekly_report(
                run_date=date(2026, 3, 20),
                connections=[
                    WeeklyConnection(
                        left_name="Debbie Ricker",
                        right_name="Melissa Muntz",
                        connection_type="co_mention",
                        supporting_article_count=2,
                        shared_context="Observed together in partnership coverage.",
                    )
                ],
            )
            text = Path(path).read_text(encoding="utf-8")
            self.assertIn("Melissa Muntz", text)
            self.assertIn("2 article", text)


if __name__ == "__main__":
    unittest.main()
