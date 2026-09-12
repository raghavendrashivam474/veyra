"""Unit tests for SQLite connectivity."""

from veyra.infrastructure.database.sqlite import SQLiteDatabase


def test_sqlite_ping(tmp_path):
    db_file = tmp_path / "test.db"
    db = SQLiteDatabase(db_file)
    assert db.ping() is True
    assert db_file.exists()
