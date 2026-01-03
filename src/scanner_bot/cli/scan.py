from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a toy scan on ingested CSV.")
    parser.add_argument("--symbol", default="aapl.us", help="Must match a downloaded file in data/raw/")
    args = parser.parse_args()

    symbol = args.symbol.lower().strip()
    csv_path = Path("data") / "raw" / f"{symbol}.csv"
    if not csv_path.exists():
        raise SystemExit(f"[scan] missing {csv_path}. Run `scanner-ingest --symbol {symbol}` first.")

    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    df["SMA20"] = df["Close"].rolling(20).mean()

    last = df.iloc[-1]
    signal = bool(last["Close"] > last["SMA20"]) if pd.notna(last["SMA20"]) else False

    out_dir = Path("data") / "signals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{symbol}.json"

    payload = {
        "symbol": symbol,
        "dt": str(last["Date"].date()),
        "close": float(last["Close"]),
        "sma20": None if pd.isna(last["SMA20"]) else float(last["SMA20"]),
        "signal_close_gt_sma20": signal,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[scan] wrote {out_path}")
    print(payload)
