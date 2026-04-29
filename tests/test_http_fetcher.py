import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import requests

from hood_pipeline.infrastructure.fetching.http_fetcher import RequestsArticleFetcher


class _FakeResponse:
    def __init__(self, status_code: int, text: str) -> None:
        self.status_code = status_code
        self.text = text

    def close(self) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} error")
            error.response = self
            raise error


class _FakeSession:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls = 0
        self.headers = {}

    def get(self, url: str, timeout: int):
        response = self.responses[self.calls]
        self.calls += 1
        return response


class RequestsArticleFetcherTest(unittest.TestCase):
    def test_fetch_text_retries_on_429_then_succeeds(self) -> None:
        fetcher = RequestsArticleFetcher("test-agent", 5)
        fetcher.session = _FakeSession(
            [
                _FakeResponse(429, "too many requests"),
                _FakeResponse(200, "ok"),
            ]
        )

        with patch("hood_pipeline.infrastructure.fetching.http_fetcher.time.sleep", return_value=None):
            text = fetcher.fetch_text("https://example.com/article")

        self.assertEqual(text, "ok")
        self.assertEqual(fetcher.session.calls, 2)

    def test_fetch_article_infers_date_from_meta_tag(self) -> None:
        fetcher = RequestsArticleFetcher("test-agent", 5)
        fetcher.session = _FakeSession(
            [
                _FakeResponse(
                    200,
                    (
                        '<html><head><meta property="article:published_time" '
                        'content="2026-04-23T09:30:00-04:00"></head>'
                        "<body><article>Story body</article></body></html>"
                    ),
                )
            ]
        )

        body, published_at, source = fetcher.fetch_article("https://example.com/story")

        self.assertEqual(body, "Story body")
        self.assertEqual(published_at, datetime(2026, 4, 23, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(source, "meta")

    def test_fetch_article_falls_back_to_source_item_date(self) -> None:
        fetcher = RequestsArticleFetcher("test-agent", 5)
        fetcher.session = _FakeSession([_FakeResponse(200, "<html><body><article>Story body</article></body></html>")])

        body, published_at, source = fetcher.fetch_article(
            "https://example.com/story",
            fallback_published_at=datetime(2026, 4, 20, 8, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(body, "Story body")
        self.assertEqual(published_at, datetime(2026, 4, 20, 8, 0, tzinfo=timezone.utc))
        self.assertEqual(source, "source_item")


if __name__ == "__main__":
    unittest.main()
