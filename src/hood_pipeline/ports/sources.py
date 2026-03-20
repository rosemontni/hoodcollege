from __future__ import annotations

from typing import Protocol

from hood_pipeline.domain.models import SourceDefinition, SourceItem


class SourceReader(Protocol):
    def read(self, definition: SourceDefinition) -> list[SourceItem]:
        ...
