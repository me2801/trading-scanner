from __future__ import annotations
from enum import Enum


class Interval(Enum):
    S1   = ("1s", 1)
    S5   = ("5s", 5)
    S10  = ("10s", 10)
    S15  = ("15s", 15)
    S30  = ("30s", 30)

    M1   = ("1m", 60)
    M2   = ("2m", 120)
    M3   = ("3m", 180)
    M5   = ("5m", 300)
    M10  = ("10m", 600)
    M15  = ("15m", 900)
    M30  = ("30m", 1800)
    M45  = ("45m", 2700)

    H1   = ("1h", 3600)
    H2   = ("2h", 7200)
    H3   = ("3h", 10800)
    H4   = ("4h", 14400)
    H6   = ("6h", 21600)
    H8   = ("8h", 28800)
    H12  = ("12h", 43200)

    D1   = ("1d", 86400)

    def __init__(self, code: str, seconds: int) -> None:
        self._code = code
        self._seconds = seconds

    @property
    def code(self) -> str:
        return self._code

    @property
    def seconds(self) -> int:
        return self._seconds

    @property
    def minutes(self) -> float:
        return self._seconds / 60.0

    @classmethod
    def from_code(cls, code: str) -> "Interval":
        for v in cls:
            if v.code == code:
                return v
        raise ValueError(f"Unknown interval code: {code!r}")

    @classmethod
    def from_seconds(cls, seconds: int) -> "Interval":
        for v in cls:
            if v.seconds == seconds:
                return v
        raise ValueError(f"Unknown interval seconds: {seconds}")
