from __future__ import annotations

from typing import Protocol

from hood_pipeline.domain.models import FetchedArticle, PersonMention


class Disambiguator(Protocol):
    def evaluate(self, article: FetchedArticle) -> tuple[bool, str]:
        ...


class PeopleExtractor(Protocol):
    def extract(self, article: FetchedArticle) -> list[PersonMention]:
        ...
