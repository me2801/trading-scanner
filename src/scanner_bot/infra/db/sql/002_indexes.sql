-- Speeds up “scan latest bars for an interval across many tickers”
CREATE INDEX IF NOT EXISTS idx_bars_interval_ts
ON bars(interval_sec, ts_utc_ms);

-- Useful if you sometimes search tickers across sources
CREATE INDEX IF NOT EXISTS idx_tickers_ticker
ON tickers(ticker);
