import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.application.social_network_analysis import SocialNetworkAnalyzer
from hood_pipeline.infrastructure.writing.social_network import SocialNetworkAnalysisWriter


class SocialNetworkAnalysisTest(unittest.TestCase):
    def test_analyzer_reports_role_aware_network_metrics(self) -> None:
        rows = [
            self._row("a1", "Alice Faculty", "faculty", "hood_news", "2026-05-01"),
            self._row("a1", "Blake Admin", "administrator", "hood_news", "2026-05-01"),
            self._row("a1", "Casey Student", "student", "hood_news", "2026-05-01"),
            self._row("a2", "Alice Faculty", "faculty", "hood_news", "2026-05-02"),
            self._row("a2", "Blake Admin", "administrator", "hood_news", "2026-05-02"),
            self._row("a3", "Dana Faculty", "faculty", "hood_stories", "2026-05-04"),
            self._row("a3", "Casey Student", "student", "hood_stories", "2026-05-04"),
            self._row("a4", "Evan Staff", "staff", "hood_stories", "2026-05-04"),
        ]

        report = SocialNetworkAnalyzer().analyze(date(2026, 5, 9), rows)

        strongest = report.strongest_bonds[0]
        self.assertEqual(strongest["left"], "Alice Faculty")
        self.assertEqual(strongest["right"], "Blake Admin")
        self.assertEqual(strongest["shared_article_count"], 2)
        self.assertEqual(report.overview["people"], 5)
        self.assertIn("faculty_visibility", report.narratives)
        self.assertIn("faculty", report.role_leaders)
        self.assertEqual(report.faculty_visibility[0]["name"], "Alice Faculty")
        self.assertTrue(
            any(item["name"] == "Casey Student" for item in report.faculty_administration_connectors)
        )
        self.assertTrue(report.role_mixing)

    def test_writer_creates_narrated_markdown_and_json(self) -> None:
        rows = [
            self._row("a1", "Alice Faculty", "faculty", "hood_news", "2026-05-01"),
            self._row("a1", "Blake Admin", "administrator", "hood_news", "2026-05-01"),
        ]
        report = SocialNetworkAnalyzer().analyze(date(2026, 5, 9), rows)
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path, json_path = SocialNetworkAnalysisWriter(Path(tmpdir)).write_report(report)

            markdown_text = Path(markdown_path).read_text(encoding="utf-8")
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))

        self.assertIn("## Strongest Public Co-Mention Bonds", markdown_text)
        self.assertIn("This report analyzes public co-mentions", markdown_text)
        self.assertEqual(payload["run_date"], "2026-05-09")
        self.assertEqual(payload["overview"]["people"], 2)

    def _row(
        self,
        article_url: str,
        name: str,
        role_category: str,
        source_id: str,
        seen_date: str,
    ) -> dict[str, str]:
        return {
            "article_url": article_url,
            "name": name,
            "role_category": role_category,
            "source_id": source_id,
            "seen_date": seen_date,
            "title": article_url,
        }


if __name__ == "__main__":
    unittest.main()
