from __future__ import annotations

from typing import Protocol


class ArticleFetcher(Protocol):
    def fetch_text(self, url: str) -> str:
        ...
