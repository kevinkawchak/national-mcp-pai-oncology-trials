"""PostgreSQL storage adapter interface for production deployment.

Provides the PostgreSQL storage adapter interface. Requires the
``psycopg2`` or ``asyncpg`` package for actual database connectivity.
This module defines the adapter class; actual connection is deferred
to runtime when PostgreSQL credentials are configured.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from servers.storage.base import BaseStorage


class PostgreSQLStorage(BaseStorage):
    """PostgreSQL-backed storage adapter for production deployment.

    Requires ``psycopg2`` at runtime. Falls back to a connection-error
    state if the driver is not installed.

    Configuration via DSN string:
        ``postgresql://user:pass@host:5432/trialmcp``
    """

    def __init__(self, dsn: str = "") -> None:
        self._dsn = dsn
        self._conn: Any = None
        if dsn:
            self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            import psycopg2

            self._conn = psycopg2.connect(self._dsn)
            self._ensure_schema()
        except ImportError:
            raise ImportError(
                "PostgreSQL adapter requires psycopg2. Install with: pip install psycopg2-binary"
            )

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist."""
        if self._conn is None:
            return
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mcp_store (
                    collection TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value JSONB NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    PRIMARY KEY (collection, key)
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_store_collection
                ON mcp_store (collection)
            """)
        self._conn.commit()

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        if self._conn is None:
            return None
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT value FROM mcp_store WHERE collection=%s AND key=%s",
                (collection, key),
            )
            row = cur.fetchone()
            if row is None:
                return None
            val = row[0]
            return val if isinstance(val, dict) else json.loads(val)

    def put(self, collection: str, key: str, value: dict[str, Any]) -> None:
        if self._conn is None:
            return
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO mcp_store (collection, key, value)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (collection, key)
                   DO UPDATE SET value = EXCLUDED.value""",
                (collection, key, json.dumps(value)),
            )
        self._conn.commit()

    def delete(self, collection: str, key: str) -> bool:
        if self._conn is None:
            return False
        with self._conn.cursor() as cur:
            cur.execute(
                "DELETE FROM mcp_store WHERE collection=%s AND key=%s",
                (collection, key),
            )
            deleted = cur.rowcount > 0
        self._conn.commit()
        return deleted

    def list_keys(self, collection: str) -> list[str]:
        if self._conn is None:
            return []
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT key FROM mcp_store WHERE collection=%s ORDER BY created_at",
                (collection,),
            )
            return [row[0] for row in cur.fetchall()]

    def query(
        self,
        collection: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if self._conn is None:
            return []
        with self._conn.cursor() as cur:
            if filters:
                # Use JSONB containment operator for filtering
                cur.execute(
                    "SELECT value FROM mcp_store WHERE collection=%s AND value @> %s "
                    "ORDER BY created_at LIMIT %s OFFSET %s",
                    (collection, json.dumps(filters), limit, offset),
                )
            else:
                cur.execute(
                    "SELECT value FROM mcp_store WHERE collection=%s "
                    "ORDER BY created_at LIMIT %s OFFSET %s",
                    (collection, limit, offset),
                )
            results = []
            for row in cur.fetchall():
                val = row[0]
                results.append(val if isinstance(val, dict) else json.loads(val))
            return results

    def count(self, collection: str) -> int:
        if self._conn is None:
            return 0
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM mcp_store WHERE collection=%s",
                (collection,),
            )
            return cur.fetchone()[0]

    def append(self, collection: str, value: dict[str, Any]) -> str:
        key = str(uuid.uuid4())
        self.put(collection, key, value)
        return key

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
