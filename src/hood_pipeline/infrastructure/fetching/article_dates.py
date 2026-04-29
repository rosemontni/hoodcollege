from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
import json
import re
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup


class ArticleDateInferer:
    META_KEYS = (
        ("property", "article:published_time"),
        ("name", "article:published_time"),
        ("property", "og:published_time"),
        ("name", "og:published_time"),
        ("name", "parsely-pub-date"),
        ("name", "publish-date"),
        ("name", "publication_date"),
        ("name", "pubdate"),
        ("name", "date"),
        ("name", "dc.date"),
        ("name", "dc.date.issued"),
        ("name", "citation_publication_date"),
        ("itemprop", "datePublished"),
    )

    MONTH_NAME_PATTERN = re.compile(
        r"\b("
        r"January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
        r")\s+\d{1,2},\s+\d{4}\b",
        re.IGNORECASE,
    )
    NUMERIC_URL_PATTERN = re.compile(r"/(20\d{2})/(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])(?:/|$)")
    ISO_URL_PATTERN = re.compile(r"\b(20\d{2})-(0[1-9]|1[0-2])-([0-3]\d)\b")

    def infer(self, url: str, html: str, fallback: datetime | None = None) -> tuple[datetime | None, str]:
        soup = BeautifulSoup(html, "html.parser")
        for extractor in (
            self._from_meta,
            self._from_json_ld,
            self._from_time_tag,
        ):
            inferred = extractor(soup)
            if inferred is not None:
                return inferred, extractor.__name__.removeprefix("_from_")

        if fallback is not None:
            return self._to_utc(fallback), "source_item"

        inferred_from_url = self._from_url(url)
        if inferred_from_url is not None:
            return inferred_from_url, "url"

        inferred_from_text = self._from_visible_text(soup)
        if inferred_from_text is not None:
            return inferred_from_text, "visible_text"

        return None, "unknown"

    def _from_meta(self, soup: BeautifulSoup) -> datetime | None:
        for attribute, key in self.META_KEYS:
            tag = soup.find("meta", attrs={attribute: key})
            if tag is None:
                continue
            candidate = tag.get("content")
            parsed = self._parse_datetime(candidate)
            if parsed is not None:
                return parsed
        return None

    def _from_json_ld(self, soup: BeautifulSoup) -> datetime | None:
        for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = (tag.string or tag.get_text()).strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            parsed = self._extract_json_ld_date(payload)
            if parsed is not None:
                return parsed
        return None

    def _extract_json_ld_date(self, payload) -> datetime | None:
        if isinstance(payload, list):
            for item in payload:
                parsed = self._extract_json_ld_date(item)
                if parsed is not None:
                    return parsed
            return None
        if isinstance(payload, dict):
            for key in ("datePublished", "dateCreated", "uploadDate", "dateModified"):
                parsed = self._parse_datetime(payload.get(key))
                if parsed is not None:
                    return parsed
            for key in ("@graph", "mainEntity", "itemListElement"):
                value = payload.get(key)
                if value is None:
                    continue
                parsed = self._extract_json_ld_date(value)
                if parsed is not None:
                    return parsed
        return None

    def _from_time_tag(self, soup: BeautifulSoup) -> datetime | None:
        for tag in soup.find_all("time"):
            parsed = self._parse_datetime(tag.get("datetime") or tag.get_text(" ", strip=True))
            if parsed is not None:
                return parsed
        return None

    def _from_url(self, url: str) -> datetime | None:
        decoded = unquote(urlparse(url).path)
        numeric_match = self.NUMERIC_URL_PATTERN.search(decoded)
        if numeric_match:
            return self._date_only_to_utc(
                date(
                    int(numeric_match.group(1)),
                    int(numeric_match.group(2)),
                    int(numeric_match.group(3)),
                )
            )
        iso_match = self.ISO_URL_PATTERN.search(decoded)
        if iso_match:
            return self._date_only_to_utc(
                date(
                    int(iso_match.group(1)),
                    int(iso_match.group(2)),
                    int(iso_match.group(3)),
                )
            )
        return None

    def _from_visible_text(self, soup: BeautifulSoup) -> datetime | None:
        text = soup.get_text(" ", strip=True)[:6000]
        match = self.MONTH_NAME_PATTERN.search(text)
        if match is None:
            return None
        return self._parse_datetime(match.group(0))

    def _parse_datetime(self, value) -> datetime | None:
        if not value or not isinstance(value, str):
            return None
        candidate = " ".join(value.strip().split())
        candidate = candidate.replace("Published ", "").replace("Updated ", "")

        for normalizer in (
            lambda item: item,
            lambda item: item.replace("Z", "+00:00"),
        ):
            try:
                parsed = datetime.fromisoformat(normalizer(candidate))
            except ValueError:
                pass
            else:
                return self._to_utc(parsed)

        try:
            parsed = parsedate_to_datetime(candidate)
        except (TypeError, ValueError, IndexError):
            parsed = None
        if parsed is not None:
            return self._to_utc(parsed)

        for pattern in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ):
            try:
                parsed_date = datetime.strptime(candidate, pattern)
            except ValueError:
                continue
            return self._to_utc(parsed_date)
        return None

    def _date_only_to_utc(self, value: date) -> datetime:
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)

    def _to_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
