CREATE INDEX IF NOT EXISTS idx_bars_ticker_interval_ts
ON bars(ticker_id, interval_sec, ts_utc_ms);

CREATE INDEX IF NOT EXISTS idx_bars_source_interval_ts
ON bars(source_id, interval_sec, ts_utc_ms);
