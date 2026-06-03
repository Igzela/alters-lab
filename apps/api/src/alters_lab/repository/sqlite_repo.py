"""SQLite repository — persistent storage using Python's built-in sqlite3."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from alters_lab.repository.base import Repository, TransactionContext
from alters_lab.services.p6_runtime import validate_record_id


class SqliteRepository(Repository):
    """SQLite-backed repository. Stores records as JSON in a single table."""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._in_transaction = False
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _ensure_schema(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                area TEXT NOT NULL,
                record_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (area, record_id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_records_area ON records(area)
        """)
        conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def write(self, area: str, record_id: str, data: dict[str, Any]) -> Path:
        validate_record_id(record_id)
        conn = self._get_conn()
        json_data = json.dumps(data, ensure_ascii=False, default=str)
        conn.execute(
            """INSERT INTO records (area, record_id, data, updated_at)
               VALUES (?, ?, ?, datetime('now'))
               ON CONFLICT(area, record_id) DO UPDATE SET
               data = excluded.data, updated_at = excluded.updated_at""",
            (area, record_id, json_data),
        )
        if not self._in_transaction:
            conn.commit()
        return self._db_path

    def read(self, area: str, record_id: str) -> dict[str, Any]:
        validate_record_id(record_id)
        conn = self._get_conn()
        row = conn.execute(
            "SELECT data FROM records WHERE area = ? AND record_id = ?",
            (area, record_id),
        ).fetchone()
        if row is None:
            raise FileNotFoundError(f"Record not found: {area}/{record_id}")
        return json.loads(row["data"])

    def list_records(self, area: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT data FROM records WHERE area = ? ORDER BY record_id",
            (area,),
        ).fetchall()
        return [json.loads(row["data"]) for row in rows]

    def delete(self, area: str, record_id: str) -> Path:
        validate_record_id(record_id)
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM records WHERE area = ? AND record_id = ?",
            (area, record_id),
        )
        if not self._in_transaction:
            conn.commit()
        if cursor.rowcount == 0:
            raise FileNotFoundError(f"Record not found: {area}/{record_id}")
        return self._db_path

    def exists(self, area: str, record_id: str) -> bool:
        validate_record_id(record_id)
        conn = self._get_conn()
        row = conn.execute(
            "SELECT 1 FROM records WHERE area = ? AND record_id = ?",
            (area, record_id),
        ).fetchone()
        return row is not None

    def transaction(self) -> SqliteTransaction:
        return SqliteTransaction(self)

    def count(self, area: str) -> int:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM records WHERE area = ?",
            (area,),
        ).fetchone()
        return row["cnt"] if row else 0

    def list_areas(self) -> list[str]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT DISTINCT area FROM records ORDER BY area",
        ).fetchall()
        return [row["area"] for row in rows]


class SqliteTransaction(TransactionContext):
    """SQLite transaction with commit/rollback."""

    def __init__(self, repo: SqliteRepository):
        self._repo = repo
        self._conn = repo._get_conn()

    def __enter__(self) -> SqliteTransaction:
        self._repo._in_transaction = True
        self._conn.execute("BEGIN")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._repo._in_transaction = False
        super().__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()
