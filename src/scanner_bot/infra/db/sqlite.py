from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from collections.abc import Iterator


def _load_sql_scripts() -> list[str]:
    pkg = "scanner_bot.infra.db.sql"
    scripts: list[tuple[str, str]] = []
    for entry in resources.files(pkg).iterdir():
        if entry.is_file() and entry.name.endswith(".sql"):
            scripts.append((entry.name, entry.read_text(encoding="utf-8")))
    scripts.sort(key=lambda x: x[0])
    return [txt for _, txt in scripts]


class SQLiteDB:
    def __init__(self, db_path: str | Path, create_if_not_exists: bool = False) -> None:
        self.db_path = Path(db_path)
        if str(db_path) == ":memory:":
            self._path = ":memory:"
        else:
            self._path = self.db_path.as_posix()
            if not self.db_path.exists():
                if not create_if_not_exists:
                    raise FileNotFoundError(f"SQLite DB file not found: {self.db_path.resolve()}")
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._apply_schema()

    def _apply_schema(self) -> None:
        scripts = _load_sql_scripts()
        with self.connect() as c:
            c.execute("PRAGMA foreign_keys = ON;")
            c.execute("PRAGMA journal_mode = WAL;")
            c.execute("PRAGMA synchronous = NORMAL;")
            for script in scripts:
                c.executescript(script)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self._path)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
