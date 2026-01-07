from __future__ import annotations

from datetime import date
from typing import Protocol, Iterable, Sequence

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

    def list_bars_multi(
        self,
        interval: str,
        tickers: Sequence[str] | None = None,
        start: date | None = None,
        end: date | None = None,
    ) -> list[Bar]:
        """Bulk read bars for many tickers (or all if tickers is None)."""
        ...