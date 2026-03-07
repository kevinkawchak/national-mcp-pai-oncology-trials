"""SQLite storage adapter for single-site MCP server deployment.

Stores records as JSON blobs in a SQLite database, suitable for
single-site deployments where PostgreSQL is not required.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from typing import Any

from servers.storage.base import BaseStorage

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS mcp_store (
    collection TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (collection, key)
)
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_mcp_store_collection
ON mcp_store (collection)
"""


class SQLiteStorage(BaseStorage):
    """SQLite-backed storage adapter for single-site deployment.

    Stores all records as JSON text in a single table keyed by
    (collection, key). Supports concurrent reads but serializes writes.
    """

    def __init__(self, dsn: str = ":memory:") -> None:
        self._dsn = dsn
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(dsn, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(CREATE_TABLE_SQL)
        self._conn.execute(CREATE_INDEX_SQL)
        self._conn.commit()

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        cursor = self._conn.execute(
            "SELECT value FROM mcp_store WHERE collection=? AND key=?",
            (collection, key),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def put(self, collection: str, key: str, value: dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO mcp_store (collection, key, value) VALUES (?, ?, ?)",
                (collection, key, json.dumps(value, ensure_ascii=True)),
            )
            self._conn.commit()

    def delete(self, collection: str, key: str) -> bool:
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM mcp_store WHERE collection=? AND key=?",
                (collection, key),
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def list_keys(self, collection: str) -> list[str]:
        cursor = self._conn.execute(
            "SELECT key FROM mcp_store WHERE collection=? ORDER BY created_at",
            (collection,),
        )
        return [row[0] for row in cursor.fetchall()]

    def query(
        self,
        collection: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        cursor = self._conn.execute(
            "SELECT value FROM mcp_store WHERE collection=? ORDER BY created_at LIMIT ? OFFSET ?",
            (collection, limit, offset),
        )
        results = []
        for row in cursor.fetchall():
            record = json.loads(row[0])
            if filters:
                if all(record.get(k) == v for k, v in filters.items()):
                    results.append(record)
            else:
                results.append(record)
        return results

    def count(self, collection: str) -> int:
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM mcp_store WHERE collection=?",
            (collection,),
        )
        return cursor.fetchone()[0]

    def append(self, collection: str, value: dict[str, Any]) -> str:
        key = str(uuid.uuid4())
        self.put(collection, key, value)
        return key

    def close(self) -> None:
        self._conn.close()
