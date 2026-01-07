# src/scanner_bot/infra/db/sqlite.py
from __future__ import annotations

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Iterator

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
    def __init__(self, db_path: str | Path, create_if_not_exists: bool = False) -> None:
        self.db_path = Path(db_path)

        # Special-case tests if you ever use it
        if str(db_path) == ":memory:":
            self._path_str = ":memory:"
            with self.connect() as c:
                c.executescript(DDL)
            return

        self._path_str = str(self.db_path)

        if not self.db_path.exists():
            if not create_if_not_exists:
                raise FileNotFoundError(
                    f"SQLite DB file not found: {self.db_path.resolve()} "
                    "(likely a wrong relative path)."
                )
            # create dirs only when we are allowed to create the DB file
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure schema (safe + idempotent)
        with self.connect() as c:
            c.executescript(DDL)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.db_path.as_posix())
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
