"""Abstract base storage interface for MCP servers.

Defines the contract that all storage adapters (memory, SQLite,
PostgreSQL) must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):
    """Abstract storage interface for MCP server persistence.

    All storage adapters implement this interface to provide
    consistent CRUD operations across backend types.
    """

    @abstractmethod
    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        """Retrieve a record by key from a collection."""

    @abstractmethod
    def put(self, collection: str, key: str, value: dict[str, Any]) -> None:
        """Store a record by key in a collection."""

    @abstractmethod
    def delete(self, collection: str, key: str) -> bool:
        """Delete a record by key. Returns True if found and deleted."""

    @abstractmethod
    def list_keys(self, collection: str) -> list[str]:
        """List all keys in a collection."""

    @abstractmethod
    def query(
        self,
        collection: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query records in a collection with optional filters."""

    @abstractmethod
    def count(self, collection: str) -> int:
        """Count records in a collection."""

    @abstractmethod
    def append(self, collection: str, value: dict[str, Any]) -> str:
        """Append a record to a collection. Returns the assigned key."""

    @abstractmethod
    def close(self) -> None:
        """Release storage resources."""
