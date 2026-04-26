from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from hood_pipeline.application.build_pages import BuildPagesSiteService
from hood_pipeline.application.daily_run import DailyRunService
from hood_pipeline.application.weekly_run import WeeklyRunService
from hood_pipeline.bootstrap import build_services


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hood-pipeline")
    subcommands = parser.add_subparsers(dest="command", required=True)

    daily = subcommands.add_parser("daily-run", help="Fetch new items and write the daily discovery.")
    daily.add_argument("--date", dest="run_date", help="Run date in YYYY-MM-DD.")

    weekly = subcommands.add_parser("weekly-run", help="Build the weekly connections report.")
    weekly.add_argument("--date", dest="run_date", help="Week-ending date in YYYY-MM-DD.")

    pages = subcommands.add_parser("build-pages", help="Build the static GitHub Pages site.")
    pages.add_argument(
        "--output-dir",
        default="_site",
        help="Directory where the Pages site should be written.",
    )

    init_db = subcommands.add_parser("init-db", help="Create the local SQLite schema.")
    init_db.add_argument("--force", action="store_true", help="Reserved for future use.")
    return parser


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    services = build_services()

    if args.command == "init-db":
        services.sqlite.initialize()
        print(f"Initialized database at {services.config.database_path}")
        return 0

    if args.command == "daily-run":
        run_date = _parse_date(args.run_date) or services.clock.now().date()
        result = DailyRunService(services).run(run_date)
        print(
            f"Daily run complete for {result.run_date}: "
            f"{result.articles_stored} stored / {result.articles_seen} seen, "
            f"{len(result.mentions)} mentions, discovery {result.discovery_path}, "
            f"summary {result.summary_path}, "
            f"network {result.connection_graph_path}, "
            f"interactive {result.connection_graph_html_path}"
        )
        return 0

    if args.command == "weekly-run":
        run_date = _parse_date(args.run_date) or services.clock.now().date()
        result = WeeklyRunService(services).run(run_date)
        print(
            f"Weekly run complete for {result.run_date}: "
            f"{len(result.connections)} connections, report {result.report_path}"
        )
        return 0

    if args.command == "build-pages":
        output_dir = Path(args.output_dir)
        index_path = BuildPagesSiteService(services).run(output_dir)
        print(f"Pages build complete: {index_path}")
        return 0

    parser.error("Unknown command.")
    return 2
