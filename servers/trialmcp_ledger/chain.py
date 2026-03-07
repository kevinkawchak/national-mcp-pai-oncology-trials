"""Hash-chained immutable audit ledger with SHA-256 serialization.

Implements the audit chain specification from spec/audit.md including
genesis block initialization, canonical JSON serialization, chain
verification, and concurrency-safe append operations.
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from servers.storage.base import BaseStorage

GENESIS_HASH = "0" * 64
COLLECTION = "audit_chain"


def canonical_json(record: dict[str, Any]) -> str:
    """Produce canonical JSON for hashing (alphabetical keys, no hash)."""
    filtered = {k: v for k, v in sorted(record.items()) if k != "hash"}
    return json.dumps(filtered, sort_keys=True, ensure_ascii=True)


def compute_audit_hash(record: dict[str, Any], prev_hash: str) -> str:
    """Compute the SHA-256 hash for an audit record."""
    canonical = canonical_json(record)
    payload = prev_hash + canonical
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditChain:
    """Hash-chained immutable audit ledger.

    Provides append-only audit record storage with SHA-256 hash chaining
    for tamper detection. Supports both in-memory and persistent storage.
    Thread-safe via locking.
    """

    def __init__(self, storage: BaseStorage | None = None) -> None:
        self._storage = storage
        self._chain: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._last_hash = GENESIS_HASH

        if storage:
            self._load_chain()

    def _load_chain(self) -> None:
        """Load existing chain from persistent storage."""
        if self._storage is None:
            return
        records = self._storage.query(COLLECTION, limit=100000)
        if records:
            self._chain = records
            self._last_hash = records[-1].get("hash", GENESIS_HASH)

    @property
    def length(self) -> int:
        """Return the number of records in the chain."""
        return len(self._chain)

    @property
    def last_hash(self) -> str:
        """Return the hash of the last record in the chain."""
        return self._last_hash

    def append(
        self,
        server: str,
        tool: str,
        caller: str,
        result_summary: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append a new record to the audit chain.

        Returns a schema-valid audit-record per
        schemas/audit-record.schema.json.
        """
        with self._lock:
            record: dict[str, Any] = {
                "audit_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "server": server,
                "tool": tool,
                "caller": caller,
                "parameters": parameters or {},
                "result_summary": result_summary,
                "previous_hash": self._last_hash,
            }
            record["hash"] = compute_audit_hash(record, self._last_hash)
            self._chain.append(record)
            self._last_hash = record["hash"]

            if self._storage:
                self._storage.put(COLLECTION, record["audit_id"], record)

            return record

    def verify(self) -> dict[str, Any]:
        """Verify the integrity of the entire audit chain."""
        if not self._chain:
            return {"valid": False, "reason": "EMPTY_CHAIN"}

        prev = GENESIS_HASH
        for i, record in enumerate(self._chain):
            expected = compute_audit_hash(record, prev)
            if record.get("hash") != expected:
                return {
                    "valid": False,
                    "reason": f"HASH_MISMATCH at index {i}",
                    "index": i,
                }
            if record.get("previous_hash") != prev:
                return {
                    "valid": False,
                    "reason": f"PREV_HASH_MISMATCH at index {i}",
                    "index": i,
                }
            prev = record["hash"]

        return {"valid": True, "length": len(self._chain)}

    def query(
        self,
        server: str | None = None,
        tool: str | None = None,
        caller: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit records with optional filters."""
        results = list(self._chain)
        if server:
            results = [r for r in results if r.get("server") == server]
        if tool:
            results = [r for r in results if r.get("tool") == tool]
        if caller:
            results = [r for r in results if r.get("caller") == caller]
        return results[:limit]

    def export(self, format: str = "json") -> Any:
        """Export the entire audit chain."""
        if format == "json":
            return list(self._chain)
        return list(self._chain)
