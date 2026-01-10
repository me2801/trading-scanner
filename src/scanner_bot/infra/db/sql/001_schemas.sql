CREATE TABLE IF NOT EXISTS sources (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  provider    TEXT,
  account     TEXT,
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- IMPORTANT:
-- ticker is NOT globally unique anymore. It is unique per source.
CREATE TABLE IF NOT EXISTS tickers (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id   INTEGER NOT NULL,
  ticker      TEXT NOT NULL,
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE (source_id, ticker),
  FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS intervals (
  interval_sec INTEGER PRIMARY KEY,      -- e.g. 60, 300, 3600, 86400
  code         TEXT NOT NULL UNIQUE       -- e.g. "1m","5m","1h","1d"
);

-- IMPORTANT:
-- bars no longer has source_id (source is implied via tickers.source_id)
CREATE TABLE IF NOT EXISTS bars (
  ticker_id    INTEGER NOT NULL,
  interval_sec INTEGER NOT NULL,
  ts_utc_ms    INTEGER NOT NULL,          -- epoch milliseconds UTC

  open         REAL,
  high         REAL,
  low          REAL,
  close        REAL,
  adj_close    REAL,
  volume       REAL,

  PRIMARY KEY (ticker_id, interval_sec, ts_utc_ms),
  FOREIGN KEY (ticker_id) REFERENCES tickers(id),
  FOREIGN KEY (interval_sec) REFERENCES intervals(interval_sec)
);
