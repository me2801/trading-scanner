import re
from pathlib import Path
import tomllib

def parse_tickers(raw: str) -> list[str]:
    parts = re.split(r"[\n\r,]+", raw)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if ":" in p:
            p = p.split(":", 1)[1].strip()
        p = re.sub(r"\s+", "", p)
        if p:
            out.append(p)

    # de-dupe preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for t in out:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped

def load_universe_from_toml(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing universe file: {path.resolve()}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw = (data.get("universe") or {}).get("raw")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"No [universe].raw found (or empty) in {path.resolve()}")

    tickers = parse_tickers(raw)
    if not tickers:
        raise ValueError(f"Universe resolved to 0 tickers from {path.resolve()}")
    return tickers
