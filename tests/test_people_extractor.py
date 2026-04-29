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
            published_at_source="unknown",
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

    def test_blocks_academic_program_phrases(self) -> None:
        article = FetchedArticle(
            source_id="hood_stories",
            url="https://www.hood.edu/discover/stories/example",
            title="Graduate Student Spotlight",
            published_at=None,
            published_at_source="unknown",
            fetched_at=datetime.now(),
            body=(
                "Autumn Smith is a graduate student in the Interdisciplinary Studies program. "
                "The Graduate School highlighted Autumn Smith for her work."
            ),
            content_hash="def",
            is_relevant=True,
            relevance_reason="accepted",
        )
        mentions = self.extractor.extract(article)
        names = {mention.name for mention in mentions}
        self.assertIn("Autumn Smith", names)
        self.assertNotIn("Interdisciplinary Studies", names)
        self.assertNotIn("Graduate School", names)


if __name__ == "__main__":
    unittest.main()
