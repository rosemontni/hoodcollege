from __future__ import annotations

import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from hood_pipeline.domain.models import SourceDefinition, SourceItem


class HoodAthleticsRssReader:
    def __init__(self, fetcher) -> None:
        self.fetcher = fetcher

    def read(self, definition: SourceDefinition) -> list[SourceItem]:
        xml_payload = self.fetcher.fetch_text(definition.url)
        root = ET.fromstring(xml_payload)
        items: list[SourceItem] = []
        channel = root.find("channel")
        if channel is None:
            return items
        for node in channel.findall("item"):
            link = (node.findtext("link") or "").strip()
            title = (node.findtext("title") or "").strip()
            description_html = node.findtext("description") or ""
            summary = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)
            published_at = self.fetcher.parse_rss_datetime(node.findtext("pubDate"))
            if not link or not title:
                continue
            items.append(
                SourceItem(
                    source_id=definition.source_id,
                    source_name=definition.name,
                    url=link,
                    title=title,
                    published_at=published_at,
                    summary=summary,
                )
            )
        return items
