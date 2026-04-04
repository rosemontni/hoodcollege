from __future__ import annotations

from collections import deque
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from hood_pipeline.domain.models import SourceDefinition, SourceItem


class HoodSiteListingReader:
    DEFAULT_MAX_LISTING_PAGES = 12
    DEFAULT_PAGINATION_PARAM = "page"

    def __init__(self, fetcher) -> None:
        self.fetcher = fetcher

    def read(self, definition: SourceDefinition) -> list[SourceItem]:
        domain = self._domain_for(definition)
        listing_path = self._normalized_path(definition.url)
        article_prefixes = self._article_path_prefixes(definition, listing_path)
        article_path_substrings = self._article_path_substrings(definition)
        pagination_param = str(
            definition.metadata.get("pagination_query_param", self.DEFAULT_PAGINATION_PARAM)
        )
        max_listing_pages = int(
            definition.metadata.get("max_listing_pages", self.DEFAULT_MAX_LISTING_PAGES)
        )

        pending_listing_urls = deque([self._normalize_url(definition.url)])
        seen_listing_urls: set[str] = set()
        seen_article_urls: set[str] = set()
        items: list[SourceItem] = []

        while pending_listing_urls and len(seen_listing_urls) < max_listing_pages:
            listing_url = pending_listing_urls.popleft()
            if listing_url in seen_listing_urls:
                continue
            seen_listing_urls.add(listing_url)

            html = self.fetcher.fetch_text(listing_url)
            soup = BeautifulSoup(html, "html.parser")

            for anchor in soup.select("a[href]"):
                href = anchor.get("href", "").strip()
                if not href:
                    continue
                absolute = self._normalize_url(urljoin(listing_url, href))
                parsed = urlparse(absolute)
                if parsed.netloc.lower() != domain:
                    continue
                if self._is_pagination_url(parsed, listing_path, pagination_param):
                    if absolute not in seen_listing_urls:
                        pending_listing_urls.append(absolute)
                    continue
                if not self._matches_article_path(parsed.path, article_prefixes, article_path_substrings):
                    continue
                if absolute in seen_article_urls:
                    continue
                title = " ".join(anchor.get_text(" ", strip=True).split())
                if not title:
                    continue
                seen_article_urls.add(absolute)
                items.append(
                    SourceItem(
                        source_id=definition.source_id,
                        source_name=definition.name,
                        url=absolute,
                        title=title,
                        published_at=None,
                        summary="",
                    )
                )
        return items

    def _domain_for(self, definition: SourceDefinition) -> str:
        return str(definition.metadata.get("domain") or urlparse(definition.url).netloc).lower()

    def _article_path_prefixes(
        self,
        definition: SourceDefinition,
        listing_path: str,
    ) -> tuple[str, ...]:
        raw_prefixes = definition.metadata.get("article_path_prefixes")
        if not raw_prefixes:
            raw_prefixes = [f"{listing_path}/"]
        return tuple(self._normalized_path(str(prefix)) for prefix in raw_prefixes)

    def _is_pagination_url(self, parsed, listing_path: str, pagination_param: str) -> bool:
        if self._normalized_path(parsed.path) != listing_path:
            return False
        return pagination_param in parse_qs(parsed.query)

    def _matches_article_path(
        self,
        path: str,
        article_prefixes: tuple[str, ...],
        article_path_substrings: tuple[str, ...],
    ) -> bool:
        if not any(path.startswith(prefix) for prefix in article_prefixes):
            return False
        if article_path_substrings and not any(token in path for token in article_path_substrings):
            return False
        return True

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(fragment=""))

    def _normalized_path(self, path_or_url: str) -> str:
        path = urlparse(path_or_url).path or path_or_url
        trimmed = path.rstrip("/")
        return trimmed or "/"

    def _article_path_substrings(self, definition: SourceDefinition) -> tuple[str, ...]:
        raw_tokens = definition.metadata.get("article_path_substrings_any", [])
        return tuple(str(token) for token in raw_tokens)


class HoodNewsReader(HoodSiteListingReader):
    pass
