import tempfile
import unittest
from datetime import date
from pathlib import Path

from hood_pipeline.domain.models import SummaryPoint, WeeklyConnection
from hood_pipeline.infrastructure.writing.pages import GitHubPagesSiteWriter
from hood_pipeline.infrastructure.writing.summary import SummaryArtifactsWriter


class PagesWriterTest(unittest.TestCase):
    def test_pages_writer_builds_site_from_summary_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            summary_dir = root / "summary"
            monthly_dir = root / "monthly"
            output_dir = root / "_site"
            summary_writer = SummaryArtifactsWriter(summary_dir)
            connections = [
                WeeklyConnection(
                    left_name="Debbie Ricker",
                    right_name="Matthew Gelhard",
                    connection_type="co_mention",
                    supporting_article_count=2,
                    shared_context="Observed together.",
                )
            ]
            connection_graph_path = summary_writer.write_connection_network_graph(date(2026, 4, 26), connections)
            connection_graph_html_path = summary_writer.write_connection_network_html(date(2026, 4, 26), connections)
            summary_writer.write_summary(
                [
                    SummaryPoint(
                        run_date=date(2026, 4, 25),
                        counts_by_role={"student": 2, "faculty": 1},
                        total=3,
                    ),
                    SummaryPoint(
                        run_date=date(2026, 4, 26),
                        counts_by_role={"student": 3, "faculty": 1, "administrator": 1},
                        total=5,
                    ),
                ],
                connection_graph_name=Path(connection_graph_path).name,
                connection_graph_html_name=Path(connection_graph_html_path).name,
            )
            monthly_dir.mkdir(parents=True, exist_ok=True)
            (monthly_dir / "2026-04.md").write_text(
                "\n".join(
                    [
                        "# Hood College Monthly Report for April 2026",
                        "",
                        "Published on 2026-05-01, this report covers Hood College stories dated from 2026-04-01 through 2026-04-30.",
                        "",
                        "## Snapshot",
                        "",
                        "- Dated relevant stories: 5",
                        "- Distinct people mentioned: 8",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            index_path = GitHubPagesSiteWriter("hoodcollege", summary_dir, monthly_dir).build_site(output_dir)

            self.assertTrue(Path(index_path).exists())
            index_text = Path(index_path).read_text(encoding="utf-8")
            self.assertIn("Interactive People Network for Hood College", index_text)
            self.assertIn('iframe src="connection-network.html"', index_text)
            self.assertIn("Cumulative Discovery Table", index_text)
            self.assertIn("Monthly Report", index_text)
            self.assertIn("Hood College Monthly Report for April 2026", index_text)
            self.assertIn("2026-04-26", index_text)
            self.assertIn("connection-network.svg", index_text)
            self.assertTrue((output_dir / ".nojekyll").exists())
            self.assertTrue((output_dir / "404.html").exists())
            self.assertTrue((output_dir / "connection-network.html").exists())
            self.assertTrue((output_dir / "discovery-growth.svg").exists())
            self.assertTrue((output_dir / "monthly" / "2026-04.html").exists())


if __name__ == "__main__":
    unittest.main()
