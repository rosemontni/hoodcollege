from __future__ import annotations

from datetime import date
from hashlib import sha256

from hood_pipeline.domain.models import DailyRunResult, FetchedArticle, PersonMention, SourceDefinition


class DailyRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> DailyRunResult:
        source_items = []
        for item in self.services.config.load_source_definitions():
            definition = SourceDefinition(
                source_id=str(item["source_id"]),
                name=str(item["name"]),
                reader=str(item["reader"]),
                url=str(item["url"]),
                enabled=bool(item.get("enabled", True)),
                metadata=dict(item.get("metadata", {})),
            )
            if not definition.enabled:
                continue
            reader = self.services.source_readers[definition.reader]
            source_items.extend(reader.read(definition))

        seen = len(source_items)
        stored_articles: list[FetchedArticle] = []
        mentions: list[PersonMention] = []

        for source_item in source_items:
            body = self.services.fetcher.fetch_clean_article_text(source_item.url)
            fetched_at = self.services.clock.now()
            content_hash = sha256(body.encode("utf-8")).hexdigest()
            if self.services.sqlite.has_article(source_item.url, content_hash):
                continue
            article = FetchedArticle(
                source_id=source_item.source_id,
                url=source_item.url,
                title=source_item.title,
                published_at=source_item.published_at,
                fetched_at=fetched_at,
                body=body,
                content_hash=content_hash,
                is_relevant=False,
                relevance_reason="unclassified",
            )
            is_relevant, reason = self.services.disambiguator.evaluate(article)
            article = FetchedArticle(
                source_id=article.source_id,
                url=article.url,
                title=article.title,
                published_at=article.published_at,
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

            extracted = self.services.extractor.extract(article)
            self.services.sqlite.replace_article_mentions(article_id, extracted, run_date)
            stored_articles.append(article)
            mentions.extend(extracted)

        discovery_path = self.services.discovery_writer.write_daily_story(
            run_date,
            stored_articles,
            self.services.sqlite.mentions_for_date(run_date),
        )
        return DailyRunResult(
            run_date=run_date,
            articles_seen=seen,
            articles_stored=len(stored_articles),
            relevant_articles=stored_articles,
            mentions=self.services.sqlite.mentions_for_date(run_date),
            discovery_path=discovery_path,
        )
