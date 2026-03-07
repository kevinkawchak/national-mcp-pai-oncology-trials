"""Storage adapters for MCP server persistence.

Provides abstract base storage, in-memory adapter (testing/local),
SQLite adapter (single-site), and PostgreSQL adapter interface
(production deployment).
"""

from servers.storage.base import BaseStorage
from servers.storage.factory import create_storage
from servers.storage.memory import MemoryStorage

__all__ = [
    "BaseStorage",
    "MemoryStorage",
    "create_storage",
]
