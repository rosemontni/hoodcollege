import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import SummaryPoint
from hood_pipeline.infrastructure.writing.summary import SummaryArtifactsWriter


class SummaryWriterTest(unittest.TestCase):
    def test_summary_writer_creates_markdown_and_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = SummaryArtifactsWriter(Path(tmpdir))
            summary_path, graph_path = writer.write_summary(
                [
                    SummaryPoint(
                        run_date=date(2026, 3, 19),
                        counts_by_role={"student": 2, "faculty": 1},
                        total=3,
                    ),
                    SummaryPoint(
                        run_date=date(2026, 3, 20),
                        counts_by_role={"student": 3, "faculty": 1, "staff": 1},
                        total=5,
                    ),
                ]
            )
            summary_text = Path(summary_path).read_text(encoding="utf-8")
            graph_text = Path(graph_path).read_text(encoding="utf-8")
            self.assertIn("Discovery Summary", summary_text)
            self.assertIn("Students", summary_text)
            self.assertIn("<svg", graph_text)
            self.assertIn("Discovery Growth", graph_text)


if __name__ == "__main__":
    unittest.main()
