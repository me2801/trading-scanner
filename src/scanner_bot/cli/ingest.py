# src/scanner_bot/cli/ingest.py
from __future__ import annotations

import re
import time
from datetime import date
from pathlib import Path

import pandas as pd

from scanner_bot.core.models import Bar
from scanner_bot.infra.db.sqllite_barstore import SQLiteBarStore

# ---------- CONFIG (edit here, not via CLI) ----------
DB_PATH = Path("data/db/scanner.db")
INTERVAL = "1d"
PERIOD = "max"
BATCH_SIZE = 15
SLEEP_BETWEEN_BATCHES_SEC = 1.0

# Optional: if this file exists, we load tickers from it.
# Put your messy NASDAQ: / NYSE: list in here.
TICKERS_FILE = Path("books/tickers.txt")

from scanner_bot.config.ingest_config import (
    BATCH_SIZE, DB_PATH, INTERVAL, PERIOD, SLEEP_BETWEEN_BATCHES_SEC, UNIVERSE_TOML
)
from scanner_bot.config.universe import load_universe_from_toml




def _f(x: object) -> float | None:
    if x is None or pd.isna(x):
        return None
    try:
        return float(x)  # type: ignore[arg-type]
    except Exception:
        return None


def _bars_from_df(ticker: str, interval: str, df: pd.DataFrame) -> list[Bar]:
    df = df.dropna(how="all")
    if df.empty:
        return []

    bars: list[Bar] = []
    # expects columns: Open, High, Low, Close, Adj Close, Volume
    for ts, row in df.iterrows():
        d = ts.date() if hasattr(ts, "date") else date.fromisoformat(str(ts))
        bars.append(
            Bar(
                date=d,
                ticker=ticker,
                interval=interval,
                open=_f(row.get("Open")),
                high=_f(row.get("High")),
                low=_f(row.get("Low")),
                close=_f(row.get("Close")),
                adj_close=_f(row.get("Adj Close")),
                volume=_f(row.get("Volume")),
            )
        )
    return bars


def main() -> None:
    try:
        import yfinance as yf
    except Exception as e:
        raise SystemExit(
            "yfinance is not installed in this env. Install it (uv): `uv add yfinance`"
        ) from e

    tickers = load_universe_from_toml(UNIVERSE_TOML)
    if not tickers:
        raise SystemExit("No tickers found (check books/tickers.txt or DEFAULT_RAW_TICKERS).")

    store = SQLiteBarStore(DB_PATH, create_if_not_exists=True)

    print(f"[ingest] db={DB_PATH} interval={INTERVAL} period={PERIOD} tickers={len(tickers)}")

    ok = empty = missing = 0
    total_bars = 0

    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i : i + BATCH_SIZE]
        print(f"[ingest] downloading {i+1}-{min(i+BATCH_SIZE, len(tickers))}/{len(tickers)}: {batch}")

        df = yf.download(
            tickers=batch,
            period=PERIOD,
            interval=INTERVAL,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=True,
        )

        if df is None or getattr(df, "empty", True):
            print("[ingest] WARNING: empty batch response")
            time.sleep(SLEEP_BETWEEN_BATCHES_SEC)
            continue

        if isinstance(df.columns, pd.MultiIndex):
            available = set(df.columns.get_level_values(0))
            for t in batch:
                if t not in available:
                    print(f"[ingest] missing ticker in response: {t}")
                    missing += 1
                    continue
                bars = _bars_from_df(t, INTERVAL, df[t])
                if not bars:
                    print(f"[ingest] empty history: {t}")
                    empty += 1
                    continue
                store.upsert_bars(bars)
                ok += 1
                total_bars += len(bars)
                print(f"[ingest] upserted {t}: {len(bars)} bars")
        else:
            # single-ticker shape
            t = batch[0]
            bars = _bars_from_df(t, INTERVAL, df)
            if not bars:
                print(f"[ingest] empty history: {t}")
                empty += 1
            else:
                store.upsert_bars(bars)
                ok += 1
                total_bars += len(bars)
                print(f"[ingest] upserted {t}: {len(bars)} bars")

        time.sleep(SLEEP_BETWEEN_BATCHES_SEC)

    print(f"[ingest] done ok={ok} empty={empty} missing={missing} total_bars={total_bars} db={DB_PATH}")


if __name__ == "__main__":
    main()
