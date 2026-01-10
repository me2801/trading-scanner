from __future__ import annotations

from scanner_bot.config.ingest_config import (
    BATCH_SIZE,
    DB_PATH,
    INTERVAL,
    PERIOD,
    SLEEP_BETWEEN_BATCHES_SEC,
    UNIVERSE_TOML,
)
from scanner_bot.config.universe import load_universe_from_toml
from scanner_bot.infra.ingest.yfinance_ingest import ingest_yfinance_tickers


def main() -> None:
    tickers = load_universe_from_toml(UNIVERSE_TOML)

    # IMPORTANT: must match sources.name in the normalized DB
    source = "yfinance"

    ingest_yfinance_tickers(
        tickers=tickers,
        db_path=DB_PATH,
        source=source,
        interval_code=INTERVAL,
        period=PERIOD,
        batch_size=BATCH_SIZE,
        sleep_between_batches_sec=SLEEP_BETWEEN_BATCHES_SEC,
    )


if __name__ == "__main__":
    main()
