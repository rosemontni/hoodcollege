from __future__ import annotations

from dataclasses import dataclass

from hood_pipeline.config import AppConfig
from hood_pipeline.infrastructure.extraction.heuristic_people_extractor import HeuristicPeopleExtractor
from hood_pipeline.infrastructure.extraction.hood_disambiguator import HoodDisambiguator
from hood_pipeline.infrastructure.fetching.http_fetcher import RequestsArticleFetcher
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore
from hood_pipeline.infrastructure.runtime.local_clock import LocalClock
from hood_pipeline.infrastructure.sources.hood_athletics import HoodAthleticsRssReader
from hood_pipeline.infrastructure.sources.hood_news import HoodNewsReader
from hood_pipeline.infrastructure.writing.markdown import MarkdownConnectionWriter, MarkdownDiscoveryWriter


@dataclass(frozen=True)
class Services:
    config: AppConfig
    clock: LocalClock
    fetcher: RequestsArticleFetcher
    disambiguator: HoodDisambiguator
    extractor: HeuristicPeopleExtractor
    sqlite: SQLiteStore
    discovery_writer: MarkdownDiscoveryWriter
    connection_writer: MarkdownConnectionWriter
    source_readers: dict[str, object]


def build_services() -> Services:
    config = AppConfig.load()
    config.ensure_directories()
    sqlite = SQLiteStore(config.database_path)
    sqlite.initialize()
    return Services(
        config=config,
        clock=LocalClock(),
        fetcher=RequestsArticleFetcher(
            user_agent=config.user_agent,
            timeout_seconds=config.request_timeout_seconds,
        ),
        disambiguator=HoodDisambiguator(),
        extractor=HeuristicPeopleExtractor(),
        sqlite=sqlite,
        discovery_writer=MarkdownDiscoveryWriter(config.discoveries_dir),
        connection_writer=MarkdownConnectionWriter(config.connections_dir),
        source_readers={
            "hood_news_html": HoodNewsReader(
                RequestsArticleFetcher(
                    user_agent=config.user_agent,
                    timeout_seconds=config.request_timeout_seconds,
                )
            ),
            "rss": HoodAthleticsRssReader(
                RequestsArticleFetcher(
                    user_agent=config.user_agent,
                    timeout_seconds=config.request_timeout_seconds,
                )
            ),
        },
    )
