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

    def test_blocks_known_non_person_false_positives(self) -> None:
        false_positive_phrases = {
            "Work Search",
            "Your Future",
            "Teacher Collaboration",
            "Student Research",
            "Student Life",
            "Student English",
            "Save Living",
            "Scholarships Undergraduate",
            "School Biomedical",
            "Residence Life",
            "Publishes Research",
            "On November",
            "Memorial Hall",
            "Marymount University",
            "Monocacy Elementary",
            "National Association",
            "Navy Commander",
            "Task Force",
            "Towson University",
            "Tri-State Association",
            "Virgin Islands",
            "Watershed Studies",
            "Archaeology English",
            "Army Reserve",
            "Blazer Radio",
            "Brodbeck Hall",
            "Coffman Chapel",
            "Colburn School",
            "Creative Writing",
            "Delaplaine School",
            "Different Type",
            "Enhance Pre",
            "Fall Festival",
            "Family Farmer",
            "Following Move-In",
            "Honors Partner",
            "Integrating Art",
            "Leading Colleges",
            "Look Back",
            "Ripley Person",
            "Shrove Tuesday",
            "Souder Named",
            "Students Write",
            "Wisteria Magazine",
        }
        article = FetchedArticle(
            source_id="hood_stories",
            url="https://www.hood.edu/discover/stories/false-positives",
            title="False positive examples",
            published_at=None,
            published_at_source="unknown",
            fetched_at=datetime.now(),
            body=(
                "Autumn Smith is a graduate student whose story appeared near Work Search, Your Future, "
                "Teacher Collaboration, Student Research, Student Life, Student English, Save Living, "
                "Scholarships Undergraduate, School Biomedical, Residence Life, Publishes Research, "
                "On November, Memorial Hall, Marymount University, Monocacy Elementary, National Association, "
                "Navy Commander, Task Force, Towson University, Tri-State Association, Virgin Islands, "
                "Watershed Studies, Archaeology English, Army Reserve, Blazer Radio, Brodbeck Hall, "
                "Coffman Chapel, Colburn School, Creative Writing, Delaplaine School, Different Type, "
                "Enhance Pre, Fall Festival, Family Farmer, Following Move-In, Honors Partner, Integrating Art, "
                "Leading Colleges, Look Back, Ripley Person, Shrove Tuesday, Souder Named, Students Write, "
                "and Wisteria Magazine in the page text."
            ),
            content_hash="ghi",
            is_relevant=True,
            relevance_reason="accepted",
        )

        names = {mention.name for mention in self.extractor.extract(article)}

        self.assertIn("Autumn Smith", names)
        self.assertFalse(false_positive_phrases & names)

    def test_class_president_is_classified_as_student(self) -> None:
        article = FetchedArticle(
            source_id="hood_news",
            url="https://www.hood.edu/news/commencement",
            title="Commencement",
            published_at=None,
            published_at_source="unknown",
            fetched_at=datetime.now(),
            body=(
                "Senior Class President Noah Turner ’24 and graduate student Maria Guiza, M.S.’24, "
                "addressed their peers during commencement."
            ),
            content_hash="jkl",
            is_relevant=True,
            relevance_reason="accepted",
        )

        names = {mention.name: mention.role_category for mention in self.extractor.extract(article)}

        self.assertEqual(names["Noah Turner"], "student")


if __name__ == "__main__":
    unittest.main()
