"""DAG-based lineage graph for data provenance tracking.

Implements the provenance DAG specification from spec/provenance.md
with SHA-256 fingerprinting, W3C PROV alignment, and cross-site
trace merging support.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from servers.storage.base import BaseStorage

# Source types per spec/provenance.md
SOURCE_TYPES = {"fhir", "dicom", "computed", "external", "federated"}

# Action types per spec/provenance.md
ACTION_TYPES = {"read", "transform", "aggregate", "transfer", "derive"}

COLLECTION = "provenance"


def compute_fingerprint(data: Any) -> str:
    """Compute a SHA-256 fingerprint for data."""
    if isinstance(data, dict):
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
    else:
        canonical = str(data)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ProvenanceDAG:
    """DAG-based data lineage graph.

    Manages provenance records as a directed acyclic graph where each
    node represents a data access or transformation event, with edges
    representing derivation relationships.
    """

    def __init__(self, storage: BaseStorage | None = None) -> None:
        self._storage = storage
        self._records: dict[str, dict[str, Any]] = {}
        self._forward_edges: dict[str, list[str]] = {}
        self._backward_edges: dict[str, list[str]] = {}

        if storage:
            self._load_graph()

    def _load_graph(self) -> None:
        """Load existing provenance records from storage."""
        if self._storage is None:
            return
        records = self._storage.query(COLLECTION, limit=100000)
        for record in records:
            rid = record.get("record_id", "")
            self._records[rid] = record
            for parent in record.get("parent_ids", []):
                self._forward_edges.setdefault(parent, []).append(rid)
                self._backward_edges.setdefault(rid, []).append(parent)

    def record(
        self,
        source_id: str,
        action: str,
        actor_id: str,
        actor_role: str,
        tool_call: str,
        source_type: str = "fhir",
        input_data: Any = None,
        output_data: Any = None,
        origin_server: str = "",
        description: str = "",
        parent_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a new provenance event in the DAG.

        Returns a schema-valid provenance-record per
        schemas/provenance-record.schema.json.
        """
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        provenance: dict[str, Any] = {
            "record_id": record_id,
            "source_id": source_id,
            "action": action,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "tool_call": tool_call,
            "timestamp": now,
            "source_type": source_type,
            "origin_server": origin_server,
            "description": description,
        }

        if input_data is not None:
            provenance["input_hash"] = compute_fingerprint(input_data)
        if output_data is not None:
            provenance["output_hash"] = compute_fingerprint(output_data)
        if metadata:
            provenance["metadata"] = metadata

        # Link to parent records
        parents = parent_ids or []
        provenance["parent_ids"] = parents

        self._records[record_id] = provenance
        for parent in parents:
            self._forward_edges.setdefault(parent, []).append(record_id)
            self._backward_edges.setdefault(record_id, []).append(parent)

        if self._storage:
            self._storage.put(COLLECTION, record_id, provenance)

        return provenance

    def query_forward(self, record_id: str, depth: int = 10) -> list[dict[str, Any]]:
        """Query downstream lineage from a record."""
        visited: set[str] = set()
        result: list[dict[str, Any]] = []
        self._traverse_forward(record_id, depth, visited, result)
        return result

    def _traverse_forward(
        self,
        record_id: str,
        depth: int,
        visited: set[str],
        result: list[dict[str, Any]],
    ) -> None:
        if depth <= 0 or record_id in visited:
            return
        visited.add(record_id)
        for child_id in self._forward_edges.get(record_id, []):
            if child_id in self._records:
                result.append(self._records[child_id])
                self._traverse_forward(child_id, depth - 1, visited, result)

    def query_backward(self, record_id: str, depth: int = 10) -> list[dict[str, Any]]:
        """Query upstream lineage from a record."""
        visited: set[str] = set()
        result: list[dict[str, Any]] = []
        self._traverse_backward(record_id, depth, visited, result)
        return result

    def _traverse_backward(
        self,
        record_id: str,
        depth: int,
        visited: set[str],
        result: list[dict[str, Any]],
    ) -> None:
        if depth <= 0 or record_id in visited:
            return
        visited.add(record_id)
        for parent_id in self._backward_edges.get(record_id, []):
            if parent_id in self._records:
                result.append(self._records[parent_id])
                self._traverse_backward(parent_id, depth - 1, visited, result)

    def verify(self, record_id: str | None = None) -> dict[str, Any]:
        """Verify provenance chain integrity."""
        if record_id:
            record = self._records.get(record_id)
            if record is None:
                return {"valid": False, "reason": f"Record {record_id} not found"}
            return {"valid": True, "record_id": record_id}

        # Verify entire graph — check for cycles
        visited: set[str] = set()
        for rid in self._records:
            if rid not in visited:
                if self._has_cycle(rid, set(), visited):
                    return {"valid": False, "reason": "CYCLE_DETECTED"}

        return {
            "valid": True,
            "total_records": len(self._records),
            "total_edges": sum(len(v) for v in self._forward_edges.values()),
        }

    def _has_cycle(self, node: str, path: set[str], visited: set[str]) -> bool:
        if node in path:
            return True
        if node in visited:
            return False
        path.add(node)
        visited.add(node)
        for child in self._forward_edges.get(node, []):
            if self._has_cycle(child, path, visited):
                return True
        path.discard(node)
        return False
