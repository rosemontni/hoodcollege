import unittest
from datetime import datetime

from hood_pipeline.domain.models import FetchedArticle
from hood_pipeline.infrastructure.extraction.heuristic_people_extractor import HeuristicPeopleExtractor


class HeuristicPeopleExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = HeuristicPeopleExtractor()

    def test_extracts_staff_and_student_athlete(self) -> None:
        article = FetchedArticle(
            source_id="hood_athletics_general",
            url="https://hoodathletics.com/news/example",
            title="Example athletics story",
            published_at=None,
            fetched_at=datetime.now(),
            body=(
                "Head coach Chad Dickman praised Jake Dallas after the freshman guard scored 12 points. "
                "Assistant director Matthew Gelhard said the team showed resilience."
            ),
            content_hash="abc",
            is_relevant=True,
            relevance_reason="accepted",
        )
        mentions = self.extractor.extract(article)
        names = {mention.name: mention.role_category for mention in mentions}
        self.assertEqual(names["Chad Dickman"], "coach")
        self.assertIn(names["Jake Dallas"], {"student", "student-athlete"})


if __name__ == "__main__":
    unittest.main()
