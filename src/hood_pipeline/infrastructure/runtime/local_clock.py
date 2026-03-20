from __future__ import annotations

from datetime import datetime


class LocalClock:
    def now(self) -> datetime:
        return datetime.now().astimezone()
