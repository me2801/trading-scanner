# src/scanner_bot/infra/db/sqlite_barstore.py
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

from scanner_bot.core.models import Bar
from scanner_bot.core.ports import BarStore
from scanner_bot.infra.db.sqlite import SQLiteDB


class SQLiteBarStore(BarStore):
    def __init__(self, db_path: str | Path,  create_if_not_exists: bool = False) -> None:
        # SQLiteDB ensures the file exists + schema is applied (idempotent)
        self.db = SQLiteDB(db_path, create_if_not_exists)

    def upsert_bars(self, bars: Iterable[Bar]) -> int:
        rows: list[tuple[object, ...]] = []
        for b in bars:
            rows.append(
                (
                    b.ticker,
                    b.date.isoformat(),
                    b.interval,
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
        INSERT INTO bars (ticker, date, interval, open, high, low, close, adj_close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker, date, interval) DO UPDATE SET
          open=excluded.open,
          high=excluded.high,
          low=excluded.low,
          close=excluded.close,
          adj_close=excluded.adj_close,
          volume=excluded.volume
        """

        with self.db.connect() as c:
            cur = c.executemany(sql, rows)
            return cur.rowcount if cur.rowcount is not None else 0

    def list_bars(
        self,
        ticker: str,
        interval: str,
        start: date | None = None,
        end: date | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        where = ["ticker = ?", "interval = ?"]
        args: list[object] = [ticker, interval]

        if start is not None:
            where.append("date >= ?")
            args.append(start.isoformat())
        if end is not None:
            where.append("date <= ?")
            args.append(end.isoformat())

        sql = f"""
        SELECT ticker, date, interval, open, high, low, close, adj_close, volume
        FROM bars
        WHERE {" AND ".join(where)}
        ORDER BY date ASC
        """

        if limit is not None:
            sql += " LIMIT ?"
            args.append(int(limit))

        out: list[Bar] = []
        with self.db.connect() as c:
            for r in c.execute(sql, args):
                out.append(
                    Bar(
                        date=date.fromisoformat(r["date"]),
                        ticker=r["ticker"],
                        interval=r["interval"],
                        open=r["open"],
                        high=r["high"],
                        low=r["low"],
                        close=r["close"],
                        adj_close=r["adj_close"],
                        volume=r["volume"],
                    )
                )
        return out
