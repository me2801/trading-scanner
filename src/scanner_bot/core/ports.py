from __future__ import annotations

from datetime import datetime
from typing import Iterable, Protocol, Sequence

from scanner_bot.core.intervals import Interval
from scanner_bot.core.models import Bar


class BarStore(Protocol):
    def upsert_bars(self, bars: Iterable[Bar]) -> int:
        """Insert/update bars. Returns number of rows affected (best-effort)."""
        ...

    def list_bars(
        self,
        ticker: str,
        interval: Interval | str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        """Return bars ordered by timestamp ascending."""
        ...

    def list_bars_multi(
        self,
        interval: Interval | str,
        tickers: Sequence[str] | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Bar]:
        """Bulk read bars for many tickers (or all if tickers is None)."""
        ...
