from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from scanner_bot.core.intervals import Interval


@dataclass(frozen=True, slots=True)
class Bar:
    ts_utc: datetime
    ticker: str
    interval: Interval
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    adj_close: float | None
    volume: float | None

    @property
    def adj_factor(self) -> float | None:
        """adj_close / close (None if not computable)."""
        if self.close is None or self.adj_close is None:
            return None
        if self.close == 0:
            return None
        return self.adj_close / self.close
