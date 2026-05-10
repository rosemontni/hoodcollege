from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from hood_pipeline.application.social_network_analysis import (
    SocialNetworkAnalysisReport,
    SocialNetworkAnalyzer,
)


@dataclass(frozen=True)
class SocialNetworkRunResult:
    run_date: date
    report: SocialNetworkAnalysisReport
    markdown_path: str
    json_path: str


class SocialNetworkRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> SocialNetworkRunResult:
        analyzer = SocialNetworkAnalyzer()
        report = analyzer.analyze(
            run_date,
            self.services.sqlite.network_evidence_through_date(run_date),
        )
        markdown_path, json_path = self.services.social_network_writer.write_report(report)
        return SocialNetworkRunResult(
            run_date=run_date,
            report=report,
            markdown_path=markdown_path,
            json_path=json_path,
        )
