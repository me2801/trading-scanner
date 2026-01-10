CREATE VIEW IF NOT EXISTS v_bars AS
SELECT
  b.source_id,
  s.name AS source,

  b.ticker_id,
  t.ticker AS ticker,

  b.interval_sec,
  i.code AS interval,

  b.ts_utc_ms,
  b.open, b.high, b.low, b.close, b.adj_close, b.volume
FROM bars b
JOIN sources  s ON s.id = b.source_id
JOIN tickers  t ON t.id = b.ticker_id
JOIN intervals i ON i.interval_sec = b.interval_sec;


CREATE VIEW IF NOT EXISTS v_bars_check AS
SELECT
  source,
  ticker,
  interval,

  COUNT(*)                         AS n_rows,
  MIN(ts_utc_ms)                   AS first_ts_utc_ms,
  MAX(ts_utc_ms)                   AS last_ts_utc_ms,

  SUM(CASE WHEN (close IS NULL AND adj_close IS NULL) THEN 1 ELSE 0 END) AS n_missing_px,
  SUM(CASE WHEN volume IS NULL THEN 1 ELSE 0 END)                        AS n_missing_volume
FROM v_bars
GROUP BY source, ticker, interval;

-- 2) Latest bar per (source, ticker, interval)
CREATE VIEW IF NOT EXISTS v_bars_latest AS
SELECT
  source,
  ticker,
  interval,
  ts_utc_ms,
  open, high, low, close, adj_close, volume
FROM (
  SELECT
    source,
    ticker,
    interval,
    ts_utc_ms,
    open, high, low, close, adj_close, volume,
    ROW_NUMBER() OVER (
      PARTITION BY source, ticker, interval
      ORDER BY ts_utc_ms DESC
    ) AS rn
  FROM v_bars
)
WHERE rn = 1;
