from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = REPO_ROOT / "data" / "db" / "scanner.db"
INTERVAL = "1d"
PERIOD = "max"
BATCH_SIZE = 15
SLEEP_BETWEEN_BATCHES_SEC = 1.0

UNIVERSE_TOML = REPO_ROOT / "config" / "universe.toml"
