from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from hood_pipeline.domain.models import FetchedArticle, PersonMention
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore


class SQLiteRolePrecedenceTest(unittest.TestCase):
    def test_specific_role_wins_over_generic_person(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            store = SQLiteStore(db_path)
            store.initialize()
            article = FetchedArticle(
                source_id="hood_news",
                url="https://www.hood.edu/news/example",
                title="Example",
                published_at=None,
                fetched_at=datetime(2026, 3, 20, 12, 0, 0),
                body="Body",
                content_hash="hash",
                is_relevant=True,
                relevance_reason="accepted",
            )
            article_id = store.upsert_article(article)
            store.replace_article_mentions(
                article_id,
                [
                    PersonMention(
                        article_url=article.url,
                        name="Debbie Ricker",
                        role_category="person",
                        role_text="",
                        context="Debbie Ricker",
                        confidence=0.7,
                        inclusion_note="generic",
                    )
                ],
                date(2026, 3, 20),
            )
            store.replace_article_mentions(
                article_id,
                [
                    PersonMention(
                        article_url=article.url,
                        name="Debbie Ricker",
                        role_category="administrator",
                        role_text="President",
                        context="Debbie Ricker, president of Hood College",
                        confidence=0.9,
                        inclusion_note="specific",
                    )
                ],
                date(2026, 3, 21),
            )
            with store.session() as connection:
                row = connection.execute(
                    "SELECT role_category, first_seen, last_seen FROM people WHERE name = ?",
                    ("Debbie Ricker",),
                ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["role_category"], "administrator")
            self.assertEqual(row["first_seen"], "2026-03-20")
            self.assertEqual(row["last_seen"], "2026-03-21")


if __name__ == "__main__":
    unittest.main()
