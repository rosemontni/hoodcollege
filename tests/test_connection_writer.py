import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import WeeklyConnection
from hood_pipeline.infrastructure.writing.markdown import MarkdownConnectionWriter


class ConnectionWriterTest(unittest.TestCase):
    def test_writer_describes_cumulative_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownConnectionWriter(Path(tmpdir))
            report_path = writer.write_weekly_report(
                date(2026, 4, 25),
                [
                    WeeklyConnection(
                        left_name="Alice Carter",
                        right_name="Bob Smith",
                        connection_type="co_mention",
                        supporting_article_count=3,
                        shared_context="Observed together repeatedly.",
                    ),
                    WeeklyConnection(
                        left_name="Bob Smith",
                        right_name="Carol Jones",
                        connection_type="co_mention",
                        supporting_article_count=1,
                        shared_context="Observed together once.",
                    ),
                ],
            )

            report_text = Path(report_path).read_text(encoding="utf-8")

            self.assertIn("Cumulative Connections", report_text)
            self.assertIn("People in network: 3", report_text)
            self.assertIn("Connections in network: 2", report_text)
            self.assertIn("Connected groups: 1", report_text)
            self.assertIn("**Bob Smith** is directly connected to 2 people.", report_text)
            self.assertIn("Group 1 (3 people): Alice Carter, Bob Smith, Carol Jones", report_text)


if __name__ == "__main__":
    unittest.main()
