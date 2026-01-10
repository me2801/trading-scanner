

CREATE TABLE IF NOT EXISTS sources (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  provider    TEXT,
  account     TEXT,
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS tickers (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS intervals (
  interval_sec INTEGER PRIMARY KEY,      -- e.g. 60, 300, 3600, 86400
  code         TEXT NOT NULL UNIQUE       -- e.g. "1m","5m","1h","1d"
);

CREATE TABLE IF NOT EXISTS bars (
  source_id    INTEGER NOT NULL,
  ticker_id    INTEGER NOT NULL,
  interval_sec INTEGER NOT NULL,
  ts_utc_ms    INTEGER NOT NULL,          -- epoch milliseconds UTC

  open         REAL,
  high         REAL,
  low          REAL,
  close        REAL,
  adj_close    REAL,
  volume       REAL,

  PRIMARY KEY (source_id, ticker_id, interval_sec, ts_utc_ms),
  FOREIGN KEY (source_id) REFERENCES sources(id),
  FOREIGN KEY (ticker_id) REFERENCES tickers(id),
  FOREIGN KEY (interval_sec) REFERENCES intervals(interval_sec)
);
