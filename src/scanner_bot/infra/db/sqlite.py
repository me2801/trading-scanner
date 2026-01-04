# src/scanner_bot/infra/db/sqlite.py
from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS bars (
  ticker     TEXT NOT NULL,
  date       TEXT NOT NULL,   -- ISO YYYY-MM-DD
  interval   TEXT NOT NULL,   -- "1d", "1h", ...
  open       REAL,
  high       REAL,
  low        REAL,
  close      REAL,
  adj_close  REAL,
  volume     REAL,
  PRIMARY KEY (ticker, date, interval)
);

CREATE INDEX IF NOT EXISTS idx_bars_date_interval
ON bars(date, interval);

CREATE INDEX IF NOT EXISTS idx_bars_ticker_interval_date
ON bars(ticker, interval, date);
"""

class SQLiteDB:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

        # if the file is missing, create dirs first
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # ALWAYS ensure schema (safe + idempotent).
        # This still satisfies “init when missing” because missing file gets created here.
        with self.connect() as c:
            c.executescript(DDL)

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path.as_posix())
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA synchronous=NORMAL;")
        return c
