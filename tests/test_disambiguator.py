from datetime import datetime
import unittest

from hood_pipeline.domain.models import FetchedArticle
from hood_pipeline.infrastructure.extraction.hood_disambiguator import HoodDisambiguator


class HoodDisambiguatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.disambiguator = HoodDisambiguator()

    def test_accepts_hood_news_article(self) -> None:
        article = FetchedArticle(
            source_id="hood_news",
            url="https://www.hood.edu/news/example-story",
            title="Hood College welcomes new students",
            published_at=None,
            fetched_at=datetime.now(),
            body="Hood College in Frederick, Maryland celebrated new students.",
            content_hash="abc",
            is_relevant=False,
            relevance_reason="",
        )
        accepted, reason = self.disambiguator.evaluate(article)
        self.assertTrue(accepted)
        self.assertIn("Hood College News", reason)

    def test_rejects_negative_marker(self) -> None:
        article = FetchedArticle(
            source_id="other",
            url="https://example.com/hood-story",
            title="A different Hood story",
            published_at=None,
            fetched_at=datetime.now(),
            body="This article is about Hood Theological Seminary.",
            content_hash="abc",
            is_relevant=False,
            relevance_reason="",
        )
        accepted, reason = self.disambiguator.evaluate(article)
        self.assertFalse(accepted)
        self.assertIn("negative marker", reason)

    def test_accepts_official_hood_story(self) -> None:
        article = FetchedArticle(
            source_id="hood_stories",
            url="https://www.hood.edu/discover/stories/student-spotlight",
            title="Student Spotlight",
            published_at=None,
            fetched_at=datetime.now(),
            body="A closer look at a Hood student's academic path.",
            content_hash="abc",
            is_relevant=False,
            relevance_reason="",
        )
        accepted, reason = self.disambiguator.evaluate(article)
        self.assertTrue(accepted)
        self.assertIn("official Hood College Stories", reason)


if __name__ == "__main__":
    unittest.main()
