from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = REPO_ROOT / "data" / "db" / "scanner.db"

# This becomes sources.name in the normalized DB schema (aligned with FTMO/EPAT)
SOURCE = "yfinance"

# yfinance interval codes: "1m","5m","15m","1h","1d", ...
INTERVAL = "1d"

# Examples: "7d", "60d", "730d", "max"
PERIOD = "max"

BATCH_SIZE = 15
SLEEP_BETWEEN_BATCHES_SEC = 1.0

UNIVERSE_TOML = REPO_ROOT / "config" / "universe.toml"
