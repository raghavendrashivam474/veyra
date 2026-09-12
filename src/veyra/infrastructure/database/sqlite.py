"""SQLite database connectivity and verification adapter."""

import sqlite3
from pathlib import Path


class SQLiteDatabase:
    """Manages SQLite connectivity and verification."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def ping(self) -> bool:
        """Verify SQLite connection is operational."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
        except Exception:
            return False
