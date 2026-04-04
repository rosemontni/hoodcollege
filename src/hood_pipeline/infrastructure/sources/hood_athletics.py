from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from hood_pipeline.domain.models import SourceDefinition, SourceItem


class FeedReader:
    def __init__(self, fetcher) -> None:
        self.fetcher = fetcher

    def read(self, definition: SourceDefinition) -> list[SourceItem]:
        xml_payload = self.fetcher.fetch_text(definition.url)
        root = ET.fromstring(xml_payload)
        local_name = self._local_name(root.tag)
        if local_name == "feed":
            return self._read_atom(root, definition)
        if local_name == "rss":
            return self._read_rss(root, definition)
        return []

    def _read_rss(self, root, definition: SourceDefinition) -> list[SourceItem]:
        items: list[SourceItem] = []
        channel = root.find("channel")
        if channel is None:
            return items
        for node in channel.findall("item"):
            link = (node.findtext("link") or "").strip()
            title = (node.findtext("title") or "").strip()
            description_html = node.findtext("description") or ""
            summary = self._html_to_text(description_html)
            published_at = self.fetcher.parse_rss_datetime(node.findtext("pubDate"))
            if not self._should_include_item(link, title, summary, definition):
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

    def _read_atom(self, root, definition: SourceDefinition) -> list[SourceItem]:
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        items: list[SourceItem] = []
        for node in root.findall("atom:entry", namespace):
            title = " ".join((node.findtext("atom:title", default="", namespaces=namespace) or "").split())
            summary_html = (
                node.findtext("atom:content", default="", namespaces=namespace)
                or node.findtext("atom:summary", default="", namespaces=namespace)
                or ""
            )
            summary = self._html_to_text(summary_html)
            link = self._atom_link(node, namespace)
            published_at = self._parse_atom_datetime(
                node.findtext("atom:updated", default=None, namespaces=namespace)
                or node.findtext("atom:published", default=None, namespaces=namespace)
            )
            if not self._should_include_item(link, title, summary, definition):
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

    def _atom_link(self, node, namespace: dict[str, str]) -> str:
        for link_node in node.findall("atom:link", namespace):
            href = (link_node.get("href") or "").strip()
            rel = (link_node.get("rel") or "alternate").strip()
            if href and rel == "alternate":
                return href
        for link_node in node.findall("atom:link", namespace):
            href = (link_node.get("href") or "").strip()
            if href:
                return href
        return ""

    def _should_include_item(
        self,
        link: str,
        title: str,
        summary: str,
        definition: SourceDefinition,
    ) -> bool:
        if not link or not title:
            return False
        includes = tuple(str(value) for value in definition.metadata.get("item_url_contains_any", []))
        if includes and not any(token in link for token in includes):
            return False
        excludes = tuple(str(value) for value in definition.metadata.get("item_url_excludes_any", []))
        if any(token in link for token in excludes):
            return False
        title_excludes = tuple(str(value).lower() for value in definition.metadata.get("item_text_excludes_any", []))
        combined = f"{title}\n{summary}".lower()
        if any(token in combined for token in title_excludes):
            return False
        return True

    @staticmethod
    def _parse_atom_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _local_name(tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    @staticmethod
    def _html_to_text(value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return ""
        if "<" not in stripped and "&lt;" not in stripped:
            return " ".join(stripped.split())
        return BeautifulSoup(stripped, "html.parser").get_text(" ", strip=True)


HoodAthleticsRssReader = FeedReader
