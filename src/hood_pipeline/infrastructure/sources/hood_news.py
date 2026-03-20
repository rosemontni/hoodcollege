from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from hood_pipeline.domain.models import SourceDefinition, SourceItem


class HoodNewsReader:
    def __init__(self, fetcher) -> None:
        self.fetcher = fetcher

    def read(self, definition: SourceDefinition) -> list[SourceItem]:
        html = self.fetcher.fetch_text(definition.url)
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        items: list[SourceItem] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            if not href:
                continue
            absolute = urljoin(definition.url, href)
            parsed = urlparse(absolute)
            if parsed.netloc != "www.hood.edu":
                continue
            if "/news/" not in parsed.path or parsed.path.rstrip("/") == "/news":
                continue
            if absolute in seen:
                continue
            title = " ".join(anchor.get_text(" ", strip=True).split())
            if not title:
                continue
            seen.add(absolute)
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
