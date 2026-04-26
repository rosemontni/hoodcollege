import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import SummaryPoint, WeeklyConnection
from hood_pipeline.infrastructure.writing.summary import SummaryArtifactsWriter


class SummaryWriterTest(unittest.TestCase):
    def test_summary_writer_creates_markdown_and_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = SummaryArtifactsWriter(Path(tmpdir))
            connection_graph_path = writer.write_connection_network_graph(
                date(2026, 3, 20),
                [
                    WeeklyConnection(
                        left_name="Debbie Ricker",
                        right_name="Matthew Gelhard",
                        connection_type="co_mention",
                        supporting_article_count=2,
                        shared_context="Observed together.",
                    )
                ],
            )
            connection_graph_html_path = writer.write_connection_network_html(
                date(2026, 3, 20),
                [
                    WeeklyConnection(
                        left_name="Debbie Ricker",
                        right_name="Matthew Gelhard",
                        connection_type="co_mention",
                        supporting_article_count=2,
                        shared_context="Observed together.",
                    )
                ],
            )
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
                ],
                connection_graph_name=Path(connection_graph_path).name,
                connection_graph_html_name=Path(connection_graph_html_path).name,
            )
            summary_text = Path(summary_path).read_text(encoding="utf-8")
            graph_text = Path(graph_path).read_text(encoding="utf-8")
            connection_graph_text = Path(connection_graph_path).read_text(encoding="utf-8")
            connection_graph_html_text = Path(connection_graph_html_path).read_text(encoding="utf-8")
            self.assertIn("Discovery Summary", summary_text)
            self.assertIn("Students", summary_text)
            self.assertIn("Connection Network", summary_text)
            self.assertIn("Interactive file: `connection-network.html`", summary_text)
            self.assertIn("<svg", graph_text)
            self.assertIn("Discovery Growth", graph_text)
            self.assertIn("<svg", connection_graph_text)
            self.assertIn("Top 2 people by cumulative connection degree", connection_graph_text)
            self.assertIn("Drag nodes to rearrange the network", connection_graph_html_text)
            self.assertIn("pointerdown", connection_graph_html_text)


if __name__ == "__main__":
    unittest.main()
