import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore
from hood_pipeline.infrastructure.sources.faculty_directory import HoodFacultyDirectoryReader


class _NoopFetcher:
    def fetch_text(self, url: str) -> str:
        raise AssertionError("fetch_text should not be called by parse_page tests")


class FacultyDirectoryReaderTest(unittest.TestCase):
    def test_parse_page_extracts_faculty_directory_records(self) -> None:
        html = """
        <main>
          <div class="faculty__listing__member">
            <h2><a href="/academics/faculty/aaron-angello">Aaron Angello</a></h2>
            <ul><li>Undergraduate Faculty</li><li>Graduate Faculty</li></ul>
            <p>Assistant Professor of English</p>
            <p>Phone</p><p>No office phone</p>
            <p>Email</p><p>angello@hood.edu</p>
          </div>

          <div class="faculty__listing__member">
            <h2><a href="/academics/faculty/april-boulton">April Boulton</a></h2>
            <ul><li>Undergraduate Faculty</li><li>Graduate Faculty</li></ul>
            <p>Associate Professor of Biology</p>
            <p>Dean of the Graduate School</p>
            <p>Phone</p><p>301-696-3619</p>
            <p>Email</p><p>boulton@hood.edu</p>
          </div>

          <h2>Work at Hood</h2>
        </main>
        """
        records = HoodFacultyDirectoryReader(_NoopFetcher()).parse_page(
            html,
            "https://www.hood.edu/academics/faculty",
            date(2026, 4, 29),
        )

        self.assertEqual([record.name for record in records], ["Aaron Angello", "April Boulton"])
        self.assertEqual(records[0].role_category, "faculty")
        self.assertEqual(records[0].faculty_types, ["Undergraduate Faculty", "Graduate Faculty"])
        self.assertEqual(records[0].titles, ["Assistant Professor of English"])
        self.assertEqual(records[0].phone, "No office phone")
        self.assertEqual(records[0].email, "angello@hood.edu")
        self.assertEqual(records[0].profile_url, "https://www.hood.edu/academics/faculty/aaron-angello")
        self.assertEqual(records[0].last_seen_in_directory, date(2026, 4, 29))
        self.assertTrue(records[0].active)
        self.assertEqual(records[1].role_category, "administrator")
        self.assertIn("Dean of the Graduate School", records[1].titles)


class FacultyDirectoryPersistenceTest(unittest.TestCase):
    def test_sqlite_retains_directory_entries_and_marks_missing_records_inactive(self) -> None:
        html = """
        <main>
          <h2><a href="/academics/faculty/elizabeth-atwood">Elizabeth Atwood, Ph.D.</a></h2>
          <ul><li>Undergraduate Faculty</li><li>Graduate Faculty</li></ul>
          <p>Associate Professor of Journalism</p>
          <p>Phone</p><p>301-696-3231</p>
          <p>Email</p><p>atwood@hood.edu</p>

          <h2><a href="/academics/faculty/april-boulton">April Boulton</a></h2>
          <ul><li>Undergraduate Faculty</li><li>Graduate Faculty</li></ul>
          <p>Dean of the Graduate School</p>
          <p>Phone</p><p>301-696-3619</p>
          <p>Email</p><p>boulton@hood.edu</p>
        </main>
        """
        records = HoodFacultyDirectoryReader(_NoopFetcher()).parse_page(
            html,
            "https://www.hood.edu/academics/faculty",
            date(2026, 4, 29),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteStore(Path(tmpdir) / "test.db")
            store.initialize()

            store.replace_faculty_staff_directory(records)
            store.replace_faculty_staff_directory([records[1]])
            stored = store.faculty_staff_directory()

        by_name = {record.name: record for record in stored}
        self.assertEqual(set(by_name), {"April Boulton", "Elizabeth Atwood"})
        self.assertTrue(by_name["April Boulton"].active)
        self.assertFalse(by_name["Elizabeth Atwood"].active)
        self.assertEqual(by_name["Elizabeth Atwood"].last_seen_in_directory, date(2026, 4, 29))
        self.assertEqual(by_name["Elizabeth Atwood"].titles, ["Associate Professor of Journalism"])


if __name__ == "__main__":
    unittest.main()
