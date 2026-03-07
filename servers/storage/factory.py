"""Storage factory with config-driven backend selection.

Creates the appropriate storage adapter based on the configured
storage_backend setting.
"""

from __future__ import annotations

from servers.storage.base import BaseStorage
from servers.storage.memory import MemoryStorage


def create_storage(backend: str = "memory", dsn: str = "") -> BaseStorage:
    """Create a storage adapter based on the backend type.

    Args:
        backend: One of "memory", "sqlite", "postgresql".
        dsn: Connection string (required for sqlite and postgresql).

    Returns:
        A BaseStorage implementation.
    """
    if backend == "memory":
        return MemoryStorage()

    if backend == "sqlite":
        from servers.storage.sqlite_adapter import SQLiteStorage

        return SQLiteStorage(dsn=dsn or ":memory:")

    if backend == "postgresql":
        from servers.storage.postgres_adapter import PostgreSQLStorage

        return PostgreSQLStorage(dsn=dsn)

    raise ValueError(
        f"Unknown storage backend: {backend}. Use 'memory', 'sqlite', or 'postgresql'."
    )
