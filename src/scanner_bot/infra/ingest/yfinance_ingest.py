from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from scanner_bot.core.intervals import Interval
from scanner_bot.core.models import Bar
from scanner_bot.infra.db.sqlite_barstore import SQLiteBarStore


def _f(x: object) -> float | None:
    if x is None or pd.isna(x):
        return None
    try:
        return float(x)  # type: ignore[arg-type]
    except Exception:
        return None


def _to_utc(ts: object) -> datetime:
    """
    yfinance index values are usually pandas.Timestamp.
    Normalize to tz-aware UTC datetime.
    """
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
    else:
        t = t.tz_convert("UTC")
    return t.to_pydatetime()


def _bars_from_df(ticker: str, interval: Interval, df: pd.DataFrame) -> list[Bar]:
    df = df.dropna(how="all")
    if df.empty:
        return []

    cols = {str(c).lower(): c for c in df.columns}

    def col(name: str) -> object:
        return cols.get(name.lower(), name)

    bars: list[Bar] = []
    for ts, row in df.iterrows():
        ts_utc = _to_utc(ts)
        # hard-guard for tz correctness
        if ts_utc.tzinfo is None:
            ts_utc = ts_utc.replace(tzinfo=timezone.utc)
        else:
            ts_utc = ts_utc.astimezone(timezone.utc)

        bars.append(
            Bar(
                ts_utc=ts_utc,
                ticker=ticker,
                interval=interval,
                open=_f(row.get(col("open"))),
                high=_f(row.get(col("high"))),
                low=_f(row.get(col("low"))),
                close=_f(row.get(col("close"))),
                adj_close=_f(row.get(col("adj close"))) or _f(row.get(col("adj_close"))),
                volume=_f(row.get(col("volume"))),
            )
        )
    return bars


def ingest_yfinance_tickers(
    *,
    tickers: list[str],
    db_path,
    source: str,
    interval_code: str,
    period: str,
    batch_size: int = 15,
    sleep_between_batches_sec: float = 1.0,
) -> dict[str, Any]:
    """
    Shared ingestion entry point for:
      - CLI: scanner-ingest
      - Notebook: books/dataload.ipynb

    Assumes FTMO-aligned DB layer:
      - SQLiteBarStore(db_path, source=..., create_if_not_exists=...)
      - normalized schema + v_bars view
    """
    try:
        import yfinance as yf
    except Exception as e:
        raise RuntimeError("yfinance is not installed. Install it: `uv add yfinance`") from e

    tickers = [t.strip().upper() for t in tickers if t and t.strip()]
    if not tickers:
        raise ValueError("No tickers provided.")

    interval_enum = Interval.from_code(interval_code)
    store = SQLiteBarStore(db_path, source=source, create_if_not_exists=True)

    ok = 0
    empty = 0
    total_bars = 0

    print(
        f"[ingest_yf] db={db_path} source={source} interval={interval_code} period={period} tickers={len(tickers)}"
    )

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i : i + batch_size]
       
        df = yf.download(
            batch,
            period=period,
            interval=interval_code,
            group_by="ticker",      # <-- add this
            auto_adjust=False,
            actions=False,
            threads=False,
            progress=False,
        )

        # Multi-ticker shape => MultiIndex columns with top level ticker symbol
        if isinstance(df.columns, pd.MultiIndex):
            for t in batch:
                if t not in df.columns.get_level_values(0):
                    print(f"[ingest_yf] missing in batch result: {t}")
                    empty += 1
                    continue
                bars = _bars_from_df(t, interval_enum, df[t])
                if not bars:
                    print(f"[ingest_yf] empty history: {t}")
                    empty += 1
                    continue
                store.upsert_bars(bars)
                ok += 1
                total_bars += len(bars)
                print(f"[ingest_yf] upserted {t}: {len(bars)} bars")
        else:
            # Single-ticker shape
            t = batch[0]
            bars = _bars_from_df(t, interval_enum, df)
            if not bars:
                print(f"[ingest_yf] empty history: {t}")
                empty += 1
            else:
                store.upsert_bars(bars)
                ok += 1
                total_bars += len(bars)
                print(f"[ingest_yf] upserted {t}: {len(bars)} bars")

        if sleep_between_batches_sec > 0:
            time.sleep(sleep_between_batches_sec)

    stats = {
        "tickers_total": len(tickers),
        "ok": ok,
        "empty": empty,
        "total_bars": total_bars,
        "interval": interval_code,
        "period": period,
        "source": source,
        "db_path": str(db_path),
    }
    print(f"[ingest_yf] done {stats}")
    return stats
