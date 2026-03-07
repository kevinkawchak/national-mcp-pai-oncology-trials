"""Schema migration utilities for MCP server storage.

Tracks schema versions and applies migrations for SQLite and
PostgreSQL storage backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Migration:
    """Represents a single schema migration."""

    version: int
    description: str
    up_sql: str
    down_sql: str = ""


# Migration registry — add new migrations here
MIGRATIONS: list[Migration] = [
    Migration(
        version=1,
        description="Initial mcp_store table",
        up_sql="""
            CREATE TABLE IF NOT EXISTS mcp_store (
                collection TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (collection, key)
            );
            CREATE INDEX IF NOT EXISTS idx_mcp_store_collection
            ON mcp_store (collection);
        """,
        down_sql="DROP TABLE IF EXISTS mcp_store;",
    ),
    Migration(
        version=2,
        description="Add schema_version tracking table",
        up_sql="""
            CREATE TABLE IF NOT EXISTS mcp_schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT (datetime('now')),
                description TEXT
            );
        """,
        down_sql="DROP TABLE IF EXISTS mcp_schema_version;",
    ),
]


def get_current_version(conn: Any) -> int:
    """Get the current schema version from the database."""
    try:
        cursor = conn.execute("SELECT MAX(version) FROM mcp_schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except Exception:
        return 0


def apply_migrations(conn: Any, target_version: int | None = None) -> list[int]:
    """Apply pending migrations up to the target version.

    Returns the list of applied migration versions.
    """
    current = get_current_version(conn)
    max_version = target_version or max(m.version for m in MIGRATIONS)
    applied: list[int] = []

    for migration in sorted(MIGRATIONS, key=lambda m: m.version):
        if migration.version <= current:
            continue
        if migration.version > max_version:
            break

        for statement in migration.up_sql.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(statement)

        conn.execute(
            "INSERT OR IGNORE INTO mcp_schema_version (version, description) VALUES (?, ?)",
            (migration.version, migration.description),
        )
        conn.commit()
        applied.append(migration.version)

    return applied
