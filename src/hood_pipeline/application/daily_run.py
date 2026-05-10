from __future__ import annotations

import sys
from datetime import date
from hashlib import sha256
from pathlib import Path

from hood_pipeline.application.connection_network import build_cumulative_connections
from hood_pipeline.application.monthly_run import MonthlyRunService
from hood_pipeline.application.social_network_run import SocialNetworkRunService
from hood_pipeline.domain.models import DailyRunResult, FetchedArticle, SourceDefinition


class DailyRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> DailyRunResult:
        source_items_by_url = {}
        definitions_by_source_id = {}
        for item in self.services.config.load_source_definitions():
            definition = SourceDefinition(
                source_id=str(item["source_id"]),
                name=str(item["name"]),
                reader=str(item["reader"]),
                url=str(item["url"]),
                enabled=bool(item.get("enabled", True)),
                metadata=dict(item.get("metadata", {})),
            )
            definitions_by_source_id[definition.source_id] = definition
            if not definition.enabled:
                continue
            reader = self.services.source_readers.get(definition.reader)
            if reader is None:
                raise ValueError(f"Unknown source reader '{definition.reader}' for source '{definition.source_id}'.")
            try:
                for source_item in reader.read(definition):
                    source_items_by_url[source_item.url] = source_item
            except Exception as exc:
                print(
                    f"Skipping source '{definition.source_id}' because reader failed: {exc}",
                    file=sys.stderr,
                )

        source_items = list(source_items_by_url.values())

        seen = len(source_items)
        stored_articles: list[FetchedArticle] = []
        monthly_report_path = None

        for source_item in source_items:
            definition = definitions_by_source_id.get(source_item.source_id)
            if definition is not None and not self._should_fetch_source_item(source_item, definition):
                continue
            try:
                body, published_at, published_at_source = self.services.fetcher.fetch_article(
                    source_item.url,
                    fallback_published_at=source_item.published_at,
                )
            except Exception as exc:
                print(f"Skipping article '{source_item.url}' because fetch failed: {exc}", file=sys.stderr)
                continue
            fetched_at = self.services.clock.now()
            content_hash = sha256(body.encode("utf-8")).hexdigest()
            article = FetchedArticle(
                source_id=source_item.source_id,
                url=source_item.url,
                title=source_item.title,
                published_at=published_at,
                published_at_source=published_at_source,
                fetched_at=fetched_at,
                body=body,
                content_hash=content_hash,
                is_relevant=False,
                relevance_reason="unclassified",
            )
            existing = self.services.sqlite.stored_article(source_item.url)
            if existing is not None and existing.content_hash == content_hash:
                if self._should_backfill_story_date(existing, article):
                    self.services.sqlite.update_article_story_date(
                        source_item.url,
                        article.published_at,
                        article.published_at_source,
                    )
                continue
            is_relevant, reason = self.services.disambiguator.evaluate(article)
            article = FetchedArticle(
                source_id=article.source_id,
                url=article.url,
                title=article.title,
                published_at=article.published_at,
                published_at_source=article.published_at_source,
                fetched_at=article.fetched_at,
                body=article.body,
                content_hash=article.content_hash,
                is_relevant=is_relevant,
                relevance_reason=reason,
            )
            article_id = self.services.sqlite.upsert_article(article)
            if not article.is_relevant:
                self.services.sqlite.replace_article_mentions(article_id, [], run_date)
                continue

            try:
                extracted = self.services.extractor.extract(article)
            except Exception as exc:
                print(
                    f"Continuing without mentions for '{source_item.url}' because extraction failed: {exc}",
                    file=sys.stderr,
                )
                extracted = []
            self.services.sqlite.replace_article_mentions(article_id, extracted, run_date)
            stored_articles.append(article)

        daily_articles = self.services.sqlite.relevant_articles_for_seen_date(run_date)
        discovery_path = self.services.discovery_writer.write_daily_story(
            run_date,
            daily_articles,
            self.services.sqlite.mentions_for_date(run_date),
        )
        cumulative_connections = build_cumulative_connections(
            self.services.sqlite.mentions_through_date(run_date),
            run_date,
        )
        connection_graph_path = self.services.summary_writer.write_connection_network_graph(
            run_date,
            cumulative_connections,
            max_people=25,
        )
        connection_graph_html_path = self.services.summary_writer.write_connection_network_html(
            run_date,
            cumulative_connections,
            max_people=25,
        )
        summary_path, summary_graph_path = self.services.summary_writer.write_summary(
            self.services.sqlite.cumulative_people_summary(),
            connection_graph_name=Path(connection_graph_path).name,
            connection_graph_html_name=Path(connection_graph_html_path).name,
        )
        SocialNetworkRunService(self.services).run(run_date)
        if run_date.day == 1:
            monthly_report_path = MonthlyRunService(self.services).run(run_date).report_path
        return DailyRunResult(
            run_date=run_date,
            articles_seen=seen,
            articles_stored=len(stored_articles),
            relevant_articles=daily_articles,
            mentions=self.services.sqlite.mentions_for_date(run_date),
            discovery_path=discovery_path,
            summary_path=summary_path,
            summary_graph_path=summary_graph_path,
            connection_graph_path=connection_graph_path,
            connection_graph_html_path=connection_graph_html_path,
            monthly_report_path=monthly_report_path,
        )

    @staticmethod
    def _should_fetch_source_item(source_item, definition: SourceDefinition) -> bool:
        keywords = definition.metadata.get("prefetch_keywords_any", [])
        if not keywords:
            return True
        combined = f"{source_item.title}\n{source_item.summary}".lower()
        return any(str(keyword).lower() in combined for keyword in keywords)

    @staticmethod
    def _should_backfill_story_date(existing, article: FetchedArticle) -> bool:
        if article.published_at is None:
            return False
        existing_priority = _date_source_priority(existing.published_at_source)
        new_priority = _date_source_priority(article.published_at_source)
        return existing.published_at is None or new_priority > existing_priority


DATE_SOURCE_PRIORITY = {
    "unknown": 0,
    "url": 1,
    "visible_text": 2,
    "source_item": 3,
    "time_tag": 4,
    "json_ld": 5,
    "meta": 6,
}


def _date_source_priority(source: str) -> int:
    return DATE_SOURCE_PRIORITY.get(source, 0)
