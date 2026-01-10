from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from scanner_bot.core.intervals import Interval
from scanner_bot.core.models import Bar
from scanner_bot.infra.db.sqlite import SQLiteDB


def _to_utc_ms(ts: datetime) -> int:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)
    return int(ts.timestamp() * 1000)


def _from_utc_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def _coerce_interval(x: Interval | str) -> Interval:
    return x if isinstance(x, Interval) else Interval.from_code(x)


class SQLiteBarStore:
    """
    Storage (normalized):
      - sources(id, name, ...)
      - tickers(id, source_id, ticker, UNIQUE(source_id,ticker))
      - intervals(interval_sec PK)
      - bars(ticker_id, interval_sec, ts_utc_ms, ...)  -- no source_id here

    Reads:
      - FROM v_bars (joins live in SQL)
    """

    def __init__(
        self,
        db_path: str | Path,
        source: str,
        create_if_not_exists: bool = False,
        validate_intervals: bool = True,
    ) -> None:
        self.db = SQLiteDB(db_path, create_if_not_exists)
        self.source = source
        self._source_id: int | None = None

        self._interval_secs: set[int] | None = None
        if validate_intervals:
            self._load_interval_secs()

    def _load_interval_secs(self) -> None:
        with self.db.connect() as c:
            rows = c.execute("SELECT interval_sec FROM intervals").fetchall()
        self._interval_secs = {int(r["interval_sec"]) for r in rows}

    def _assert_interval_supported(self, iv: Interval) -> None:
        if self._interval_secs is None:
            return
        if iv.seconds not in self._interval_secs:
            raise ValueError(
                f"Interval {iv.code} ({iv.seconds}s) not present in DB intervals table. "
                "Add via SQL migration/seed."
            )

    def _get_source_id(self, c) -> int:
        if self._source_id is not None:
            return self._source_id
        row = c.execute("SELECT id FROM sources WHERE name = ?", (self.source,)).fetchone()
        if row is None:
            c.execute("INSERT INTO sources(name) VALUES (?)", (self.source,))
            row = c.execute("SELECT id FROM sources WHERE name = ?", (self.source,)).fetchone()
        assert row is not None
        self._source_id = int(row["id"])
        return self._source_id

    def _get_ticker_id(self, c, source_id: int, ticker: str) -> int | None:
        row = c.execute(
            "SELECT id FROM tickers WHERE source_id = ? AND ticker = ?",
            (source_id, ticker),
        ).fetchone()
        return int(row["id"]) if row is not None else None

    def _ensure_ticker_id(self, c, source_id: int, ticker: str) -> int:
        existing = self._get_ticker_id(c, source_id, ticker)
        if existing is not None:
            return existing

        c.execute(
            "INSERT INTO tickers(source_id, ticker) VALUES (?, ?)",
            (source_id, ticker),
        )
        row2 = c.execute(
            "SELECT id FROM tickers WHERE source_id = ? AND ticker = ?",
            (source_id, ticker),
        ).fetchone()
        assert row2 is not None
        return int(row2["id"])

    def upsert_bars(self, bars: Iterable[Bar]) -> int:
        rows: list[tuple[object, ...]] = []
        with self.db.connect() as c:
            source_id = self._get_source_id(c)

            for b in bars:
                iv = b.interval
                self._assert_interval_supported(iv)
                ticker_id = self._ensure_ticker_id(c, source_id, b.ticker)

                rows.append(
                    (
                        ticker_id,
                        iv.seconds,
                        _to_utc_ms(b.ts_utc),
                        b.open,
                        b.high,
                        b.low,
                        b.close,
                        b.adj_close,
                        b.volume,
                    )
                )

            if not rows:
                return 0

            sql = """
            INSERT INTO bars(
              ticker_id, interval_sec, ts_utc_ms,
              open, high, low, close, adj_close, volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker_id, interval_sec, ts_utc_ms) DO UPDATE SET
              open      = excluded.open,
              high      = excluded.high,
              low       = excluded.low,
              close     = excluded.close,
              adj_close = excluded.adj_close,
              volume    = excluded.volume
            """
            cur = c.executemany(sql, rows)
            return int(cur.rowcount) if cur.rowcount is not None and cur.rowcount >= 0 else len(rows)

    def list_bars(
        self,
        ticker: str,
        interval: Interval | str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        iv = _coerce_interval(interval)
        self._assert_interval_supported(iv)

        with self.db.connect() as c:
            source_id = self._get_source_id(c)
            ticker_id = self._get_ticker_id(c, source_id, ticker)
            if ticker_id is None:
                return []

            where = ["source_id = ?", "ticker_id = ?", "interval_sec = ?"]
            args: list[object] = [source_id, ticker_id, iv.seconds]

            if start is not None:
                where.append("ts_utc_ms >= ?")
                args.append(_to_utc_ms(start))
            if end is not None:
                where.append("ts_utc_ms <= ?")
                args.append(_to_utc_ms(end))

            sql = f"""
            SELECT ts_utc_ms, ticker, interval_sec, open, high, low, close, adj_close, volume
            FROM v_bars
            WHERE {" AND ".join(where)}
            ORDER BY ts_utc_ms ASC
            """
            if limit is not None:
                sql += " LIMIT ?"
                args.append(int(limit))

            out: list[Bar] = []
            for r in c.execute(sql, args):
                out.append(
                    Bar(
                        ts_utc=_from_utc_ms(int(r["ts_utc_ms"])),
                        ticker=str(r["ticker"]),
                        interval=Interval.from_seconds(int(r["interval_sec"])),
                        open=r["open"],
                        high=r["high"],
                        low=r["low"],
                        close=r["close"],
                        adj_close=r["adj_close"],
                        volume=r["volume"],
                    )
                )
            return out

    def list_bars_multi(
        self,
        interval: Interval | str,
        tickers: Sequence[str] | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Bar]:
        iv = _coerce_interval(interval)
        self._assert_interval_supported(iv)

        with self.db.connect() as c:
            source_id = self._get_source_id(c)

            where = ["source_id = ?", "interval_sec = ?"]
            args: list[object] = [source_id, iv.seconds]

            if tickers is not None and len(tickers) > 0:
                ticker_ids = []
                for t in tickers:
                    tid = self._get_ticker_id(c, source_id, t)
                    if tid is not None:
                        ticker_ids.append(tid)
                if not ticker_ids:
                    return []

                where.append(f"ticker_id IN ({','.join(['?'] * len(ticker_ids))})")
                args.extend(ticker_ids)

            if start is not None:
                where.append("ts_utc_ms >= ?")
                args.append(_to_utc_ms(start))
            if end is not None:
                where.append("ts_utc_ms <= ?")
                args.append(_to_utc_ms(end))

            sql = f"""
            SELECT ts_utc_ms, ticker, interval_sec, open, high, low, close, adj_close, volume
            FROM v_bars
            WHERE {" AND ".join(where)}
            ORDER BY ticker ASC, ts_utc_ms ASC
            """

            out: list[Bar] = []
            for r in c.execute(sql, args):
                out.append(
                    Bar(
                        ts_utc=_from_utc_ms(int(r["ts_utc_ms"])),
                        ticker=str(r["ticker"]),
                        interval=Interval.from_seconds(int(r["interval_sec"])),
                        open=r["open"],
                        high=r["high"],
                        low=r["low"],
                        close=r["close"],
                        adj_close=r["adj_close"],
                        volume=r["volume"],
                    )
                )
            return out
