"""Sample audit records and hash chains for conformance testing.

Extracted from schemas/audit-record.schema.json and spec/audit.md.
Provides valid and invalid audit record fixtures used across the
conformance test suite.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

# Genesis hash per spec/audit.md: 64 zero characters
GENESIS_HASH = "0" * 64

# Valid MCP servers per the standard
VALID_SERVERS = [
    "trialmcp-authz",
    "trialmcp-fhir",
    "trialmcp-dicom",
    "trialmcp-ledger",
    "trialmcp-provenance",
]

# Standard error codes per spec/tool-contracts.md
VALID_ERROR_CODES = [
    "AUTHZ_DENIED",
    "VALIDATION_FAILED",
    "NOT_FOUND",
    "INTERNAL_ERROR",
    "TOKEN_EXPIRED",
    "TOKEN_REVOKED",
    "PERMISSION_DENIED",
    "INVALID_INPUT",
    "RATE_LIMITED",
]


def compute_audit_hash(record: dict) -> str:
    """Compute SHA-256 hash of an audit record per spec/audit.md.

    Uses canonical JSON serialization (alphabetical key order, UTF-8)
    excluding the hash field itself.
    """
    hashable = {k: v for k, v in sorted(record.items()) if k != "hash"}
    canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_audit_record(
    server: str = "trialmcp-ledger",
    tool: str = "ledger_append",
    caller: str = "robot_agent_001",
    parameters: dict | None = None,
    result_summary: str = "Operation completed successfully",
    previous_hash: str = GENESIS_HASH,
) -> dict:
    """Create a well-formed audit record conforming to audit-record.schema.json."""
    record = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "server": server,
        "tool": tool,
        "caller": caller,
        "parameters": parameters or {},
        "result_summary": result_summary,
        "previous_hash": previous_hash,
    }
    record["hash"] = compute_audit_hash(record)
    return record


def make_audit_chain(length: int = 5) -> list[dict]:
    """Build a valid hash chain of audit records."""
    chain: list[dict] = []
    prev_hash = GENESIS_HASH
    servers_cycle = VALID_SERVERS
    for i in range(length):
        server = servers_cycle[i % len(servers_cycle)]
        record = make_audit_record(
            server=server,
            tool=f"tool_{i}",
            caller=f"actor_{i}",
            result_summary=f"Chain record {i}",
            previous_hash=prev_hash,
        )
        chain.append(record)
        prev_hash = record["hash"]
    return chain


# Pre-built fixture: single valid audit record
SAMPLE_AUDIT_RECORD = {
    "audit_id": "c3d4e5f6-a1b2-7890-cdef-1234567890ab",
    "timestamp": "2026-03-06T14:30:00Z",
    "server": "trialmcp-fhir",
    "tool": "fhir_read",
    "caller": "robot_agent_001",
    "parameters": {
        "resource_type": "Patient",
        "resource_id": "patient-pseudo-a3f8",
    },
    "result_summary": "Patient resource retrieved and de-identified successfully",
    "hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "previous_hash": GENESIS_HASH,
}

# Pre-built fixture: valid error response
SAMPLE_ERROR_RESPONSE = {
    "error": True,
    "code": "VALIDATION_FAILED",
    "message": "Resource ID contains prohibited URL pattern",
    "server": "trialmcp-fhir",
    "tool": "fhir_read",
    "timestamp": "2026-03-06T14:30:00Z",
    "details": {
        "field": "resource_id",
        "expected_pattern": r"^[A-Za-z0-9\-._]+$",
    },
}

# Pre-built fixture: valid health status
SAMPLE_HEALTH_STATUS = {
    "server_name": "trialmcp-ledger",
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "checked_at": "2026-03-06T14:30:00Z",
    "conformance_level": 1,
    "dependencies": [
        {"name": "audit_database", "status": "healthy", "latency_ms": 2.5},
    ],
    "metrics": {
        "total_requests": 15420,
        "error_rate": 0.1,
        "avg_latency_ms": 12.3,
        "audit_chain_length": 15420,
        "audit_chain_valid": True,
    },
    "site_id": "site-east-001",
}
