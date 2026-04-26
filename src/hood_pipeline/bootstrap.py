from __future__ import annotations

from dataclasses import dataclass

from hood_pipeline.config import AppConfig
from hood_pipeline.infrastructure.extraction.heuristic_people_extractor import HeuristicPeopleExtractor
from hood_pipeline.infrastructure.extraction.hood_disambiguator import HoodDisambiguator
from hood_pipeline.infrastructure.fetching.http_fetcher import RequestsArticleFetcher
from hood_pipeline.infrastructure.persistence.sqlite import SQLiteStore
from hood_pipeline.infrastructure.runtime.local_clock import LocalClock
from hood_pipeline.infrastructure.sources.hood_athletics import FeedReader
from hood_pipeline.infrastructure.sources.hood_news import HoodSiteListingReader
from hood_pipeline.infrastructure.writing.markdown import MarkdownConnectionWriter, MarkdownDiscoveryWriter
from hood_pipeline.infrastructure.writing.pages import GitHubPagesSiteWriter
from hood_pipeline.infrastructure.writing.summary import SummaryArtifactsWriter


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
    summary_writer: SummaryArtifactsWriter
    pages_writer: GitHubPagesSiteWriter
    source_readers: dict[str, object]


def build_services() -> Services:
    config = AppConfig.load()
    config.ensure_directories()
    sqlite = SQLiteStore(config.database_path)
    sqlite.initialize()
    fetcher = RequestsArticleFetcher(
        user_agent=config.user_agent,
        timeout_seconds=config.request_timeout_seconds,
    )
    hood_site_reader = HoodSiteListingReader(fetcher)
    feed_reader = FeedReader(fetcher)
    return Services(
        config=config,
        clock=LocalClock(),
        fetcher=fetcher,
        disambiguator=HoodDisambiguator(),
        extractor=HeuristicPeopleExtractor(),
        sqlite=sqlite,
        discovery_writer=MarkdownDiscoveryWriter(config.discoveries_dir),
        connection_writer=MarkdownConnectionWriter(config.connections_dir),
        summary_writer=SummaryArtifactsWriter(config.summary_dir),
        pages_writer=GitHubPagesSiteWriter(config.repo_root.name, config.summary_dir),
        source_readers={
            "hood_news_html": hood_site_reader,
            "hood_site_listing": hood_site_reader,
            "rss": feed_reader,
            "feed": feed_reader,
        },
    )
