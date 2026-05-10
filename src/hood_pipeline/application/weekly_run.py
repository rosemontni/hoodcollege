from __future__ import annotations

from datetime import date

from hood_pipeline.application.connection_network import build_cumulative_connections
from hood_pipeline.application.social_network_run import SocialNetworkRunService
from hood_pipeline.domain.models import WeeklyRunResult


class WeeklyRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> WeeklyRunResult:
        rows = self.services.sqlite.mentions_through_date(run_date)
        connections = build_cumulative_connections(rows, run_date)
        self.services.sqlite.replace_connection_snapshot(run_date, connections)
        report_path = self.services.connection_writer.write_weekly_report(run_date, connections)
        SocialNetworkRunService(self.services).run(run_date)
        return WeeklyRunResult(run_date=run_date, connections=connections, report_path=report_path)
