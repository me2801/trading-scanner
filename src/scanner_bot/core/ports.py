from __future__ import annotations

from datetime import date
from typing import Protocol, Iterable

from scanner_bot.core.models import Bar


class BarStore(Protocol):
    def upsert_bars(self, bars: Iterable[Bar]) -> int:
        """Insert/update bars. Returns number of rows affected (best-effort)."""
        ...

    def list_bars(
        self,
        ticker: str,
        interval: str,
        start: date | None = None,
        end: date | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        """Return bars ordered by date ascending."""
        ...
