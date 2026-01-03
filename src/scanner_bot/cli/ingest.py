from __future__ import annotations

import argparse
from pathlib import Path
import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Download daily OHLCV CSV from Stooq.")
    parser.add_argument("--symbol", default="aapl.us", help="Stooq symbol, e.g. aapl.us, msft.us, spy.us")
    args = parser.parse_args()

    symbol = args.symbol.lower().strip()
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"

    out_dir = Path("data") / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{symbol}.csv"

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    out_path.write_bytes(r.content)
    print(f"[ingest] saved {symbol} -> {out_path}")
