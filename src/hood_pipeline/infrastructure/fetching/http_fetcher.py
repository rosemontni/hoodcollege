from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class RequestsArticleFetcher:
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self, user_agent: str, timeout_seconds: int) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.timeout_seconds = timeout_seconds

    def fetch_text(self, url: str) -> str:
        delay_seconds = 1.0
        for attempt in range(3):
            response = self.session.get(url, timeout=self.timeout_seconds)
            if response.status_code in self.RETRYABLE_STATUS_CODES and attempt < 2:
                response.close()
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue
            response.raise_for_status()
            return response.text
        raise RuntimeError(f"Failed to fetch '{url}'.")

    def fetch_clean_article_text(self, url: str) -> str:
        html = self.fetch_text(url)
        parsed = urlparse(url)
        if parsed.netloc == "www.hood.edu":
            return self._clean_hood_news(html)
        if parsed.netloc == "hoodathletics.com":
            return self._clean_hood_athletics(html)
        if parsed.netloc in {"www.reddit.com", "reddit.com", "old.reddit.com"}:
            return self._clean_reddit(html)
        return self._clean_generic(html)

    def _clean_generic(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "footer", "nav"]):
            tag.decompose()
        main = soup.find("article") or soup.find("main") or soup.body or soup
        text = main.get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text

    def _clean_hood_news(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        article = soup.select_one("article.news-detail") or soup.find("main") or soup.body or soup
        for selector in ("section.contact-info", ".media-contact-info", "nav", "footer", "script", "style"):
            for tag in article.select(selector):
                tag.decompose()
        text = article.get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text

    def _clean_hood_athletics(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
            tag.decompose()
        body = soup.body or soup
        raw_lines = [line.strip() for line in body.get_text("\n", strip=True).splitlines()]
        noise_prefixes = (
            "Skip To Main Content",
            "Pause All Rotators",
            "Main Navigation Menu",
            "Summary",
            "Box Score",
            "Print Friendly Version",
            "Related Stories",
            "Related Videos",
            "Videos Now Playing",
            "Story Links",
            "Players Mentioned",
            "Set Scores",
            "Tournament Central",
            "Brochure",
            "Registration",
            "TicketSmarter",
            "Tickets",
            "Ad Blocker Detected",
            "Footer",
        )
        stop_prefixes = ("Related Stories", "Related Videos", "Videos Now Playing")
        lines: list[str] = []
        for line in raw_lines:
            if not line:
                continue
            if any(line.startswith(prefix) for prefix in stop_prefixes):
                break
            if any(line.startswith(prefix) for prefix in noise_prefixes):
                continue
            if re.fullmatch(r"[0-9\-.:/ ]+", line):
                continue
            if len(line) <= 2:
                continue
            lines.append(line)
        text = "\n".join(lines)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text

    def _clean_reddit(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "shreddit-consent-banner"]):
            tag.decompose()
        main = (
            soup.select_one("shreddit-post")
            or soup.select_one("article")
            or soup.find("main")
            or soup.body
            or soup
        )
        text = main.get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text

    @staticmethod
    def parse_rss_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            return None
        return parsed.astimezone(timezone.utc)
