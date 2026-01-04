from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Bar:
    date: date
    ticker: str
    interval: str  # e.g. "1d", "1h"
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    adj_close: float | None
    volume: float | None  # keep float for broad instrument compatibility

    @property
    def adj_factor(self) -> float | None:
        """adj_close / close (None if not computable)."""
        if self.close is None or self.adj_close is None:
            return None
        if self.close == 0:
            return None
        return self.adj_close / self.close
