"""In-memory storage adapter for testing and local development.

All data is stored in Python dicts and lost on process exit.
Thread-safe via a simple lock.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from servers.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
    """In-memory storage adapter.

    Suitable for testing, local development, and the quickstart demo.
    Not suitable for production — all data is lost on process exit.
    """

    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}
        self._ordered: dict[str, list[str]] = {}
        self._lock = threading.Lock()

    def _ensure_collection(self, collection: str) -> None:
        if collection not in self._data:
            self._data[collection] = {}
            self._ordered[collection] = []

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        with self._lock:
            self._ensure_collection(collection)
            return self._data[collection].get(key)

    def put(self, collection: str, key: str, value: dict[str, Any]) -> None:
        with self._lock:
            self._ensure_collection(collection)
            is_new = key not in self._data[collection]
            self._data[collection][key] = value
            if is_new:
                self._ordered[collection].append(key)

    def delete(self, collection: str, key: str) -> bool:
        with self._lock:
            self._ensure_collection(collection)
            if key in self._data[collection]:
                del self._data[collection][key]
                self._ordered[collection].remove(key)
                return True
            return False

    def list_keys(self, collection: str) -> list[str]:
        with self._lock:
            self._ensure_collection(collection)
            return list(self._ordered[collection])

    def query(
        self,
        collection: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with self._lock:
            self._ensure_collection(collection)
            results = []
            for key in self._ordered[collection]:
                record = self._data[collection][key]
                if filters:
                    if all(record.get(k) == v for k, v in filters.items()):
                        results.append(record)
                else:
                    results.append(record)
            return results[offset : offset + limit]

    def count(self, collection: str) -> int:
        with self._lock:
            self._ensure_collection(collection)
            return len(self._data[collection])

    def append(self, collection: str, value: dict[str, Any]) -> str:
        key = str(uuid.uuid4())
        self.put(collection, key, value)
        return key

    def close(self) -> None:
        with self._lock:
            self._data.clear()
            self._ordered.clear()
