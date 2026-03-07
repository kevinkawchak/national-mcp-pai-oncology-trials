"""NON-NORMATIVE Level 1 Illustrative Implementation -- Core MCP Server.

This module demonstrates the minimum viable MCP server that satisfies
Level 1 (Core) conformance as defined in spec/conformance.md.  It
implements the trialmcp-authz and trialmcp-ledger tool contracts
required by profiles/base-profile.md.

IMPORTANT: This is an illustrative implementation only.  It is
provided to demonstrate schema-compliant payload shapes and is not
suitable for production deployment.  The normative requirements are
defined in /spec/, /schemas/, and /profiles/.

See Also
--------
- spec/tool-contracts.md : Normative tool signatures
- spec/security.md       : Deny-by-default RBAC requirements
- spec/audit.md          : Hash-chained audit ledger requirements
- schemas/               : Machine-readable JSON Schema contracts

References
----------
1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI
   Oncology Clinical Trial Systems*.
   DOI: 10.5281/zenodo.18869776
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End
   Framework for Robotic Systems in Clinical Trials*.
   DOI: 10.5281/zenodo.18445179
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning
   for Physical AI Oncology Trials*.
   DOI: 10.5281/zenodo.18840880
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Token store (in-memory, non-production)
# ---------------------------------------------------------------------------
_tokens: dict[str, dict[str, Any]] = {}

# Default deny-by-default policy matrix aligned with spec/actor-model.md
DEFAULT_POLICY: dict[str, list[str]] = {
    "robot_agent": [
        "fhir_read",
        "dicom_query",
        "dicom_retrieve_pointer",
        "ledger_append",
        "provenance_record_access",
    ],
    "trial_coordinator": [
        "fhir_read",
        "fhir_search",
        "fhir_patient_lookup",
        "fhir_study_status",
        "dicom_query",
        "dicom_retrieve_pointer",
        "dicom_study_metadata",
        "authz_list_policies",
    ],
    "data_monitor": [
        "fhir_read",
        "fhir_search",
        "dicom_query",
        "dicom_study_metadata",
    ],
    "auditor": [
        "ledger_query",
        "ledger_verify",
        "ledger_replay",
        "ledger_chain_status",
    ],
    "sponsor": [
        "authz_list_policies",
    ],
    "cro": [
        "authz_list_policies",
        "fhir_study_status",
    ],
}

# Genesis hash for the audit chain per spec/audit.md
GENESIS_HASH = "0" * 64


# ---------------------------------------------------------------------------
# AuthZ helpers
# ---------------------------------------------------------------------------


def authz_evaluate(role: str, tool: str, server: str = "trialmcp-authz") -> dict[str, Any]:
    """Evaluate an authorization request against the default policy.

    Returns a schema-valid authz-decision per
    schemas/authz-decision.schema.json.

    Fields align to the canonical schema:
      allowed, effect, role, server, tool, matching_rules (structured),
      evaluated_at, and optionally deny_reason.
    """
    allowed_tools = DEFAULT_POLICY.get(role, [])
    effect = "ALLOW" if tool in allowed_tools else "DENY"
    allowed = effect == "ALLOW"
    result: dict[str, Any] = {
        "allowed": allowed,
        "effect": effect,
        "role": role,
        "server": server,
        "tool": tool,
        "matching_rules": (
            [{"role": role, "server": server, "tool": tool, "effect": "ALLOW"}] if allowed else []
        ),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
    if not allowed:
        result["deny_reason"] = (
            f"Role '{role}' is denied access to tool '{tool}' by default policy."
        )
    return result


def authz_issue_token(role: str, expires_in: int = 3600) -> dict[str, Any]:
    """Issue a bearer token for the given role.

    Returns token metadata per spec/security.md.
    """
    if expires_in > 86400:
        expires_in = 86400
    raw = uuid.uuid4().hex
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    _tokens[token_hash] = {
        "role": role,
        "issued_at": now.isoformat(),
        "expires_at": (
            datetime.fromtimestamp(now.timestamp() + expires_in, tz=timezone.utc)
        ).isoformat(),
        "revoked": False,
    }
    return {
        "token_hash": token_hash,
        "role": role,
        "issued_at": _tokens[token_hash]["issued_at"],
        "expires_at": _tokens[token_hash]["expires_at"],
    }


def authz_validate_token(token_hash: str) -> dict[str, Any]:
    """Validate a previously issued token."""
    meta = _tokens.get(token_hash)
    if meta is None:
        return {"valid": False, "reason": "TOKEN_NOT_FOUND"}
    if meta["revoked"]:
        return {"valid": False, "reason": "TOKEN_REVOKED"}
    expires = datetime.fromisoformat(meta["expires_at"])
    if datetime.now(timezone.utc) > expires:
        return {"valid": False, "reason": "TOKEN_EXPIRED"}
    return {"valid": True, "role": meta["role"]}


def authz_revoke_token(token_hash: str) -> dict[str, Any]:
    """Immediately revoke a token."""
    meta = _tokens.get(token_hash)
    if meta is None:
        return {"revoked": False, "reason": "TOKEN_NOT_FOUND"}
    meta["revoked"] = True
    return {"revoked": True, "token_hash": token_hash}


# ---------------------------------------------------------------------------
# Ledger helpers
# ---------------------------------------------------------------------------


def _canonical_json(record: dict[str, Any]) -> str:
    """Produce canonical JSON for hashing (alphabetical keys, no hash)."""
    filtered = {k: v for k, v in sorted(record.items()) if k != "hash"}
    return json.dumps(filtered, sort_keys=True, ensure_ascii=True)


def compute_audit_hash(record: dict[str, Any], prev_hash: str) -> str:
    """Compute the SHA-256 hash for an audit record."""
    canonical = _canonical_json(record)
    payload = prev_hash + canonical
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ledger_append(
    server: str,
    tool: str,
    caller: str,
    result_summary: str,
    previous_hash: str = GENESIS_HASH,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append a new record to the audit ledger.

    Returns a schema-valid audit-record per
    schemas/audit-record.schema.json.

    Fields align to the canonical schema:
      audit_id, timestamp, server, tool, caller, parameters,
      result_summary, previous_hash, hash.
    """
    record: dict[str, Any] = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": server,
        "tool": tool,
        "caller": caller,
        "parameters": parameters or {},
        "result_summary": result_summary,
        "previous_hash": previous_hash,
    }
    record["hash"] = compute_audit_hash(record, previous_hash)
    return record


def ledger_verify(chain: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify the integrity of an audit chain."""
    if not chain:
        return {"valid": False, "reason": "EMPTY_CHAIN"}
    prev = GENESIS_HASH
    for i, record in enumerate(chain):
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
    return {"valid": True, "length": len(chain)}


# ---------------------------------------------------------------------------
# Health / capability
# ---------------------------------------------------------------------------


def health_status(
    server_name: str = "trialmcp-ledger",
) -> dict[str, Any]:
    """Return server health per schemas/health-status.schema.json.

    Fields align to the canonical schema:
      server_name, status, version, uptime_seconds, checked_at,
      dependencies (array of typed objects).
    """
    return {
        "server_name": server_name,
        "status": "healthy",
        "version": "0.6.0",
        "uptime_seconds": 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "dependencies": [],
    }


def error_response(code: str, message: str, tool: str = "", server: str = "") -> dict[str, Any]:
    """Return standardised error per schemas/error-response.schema.json."""
    resp: dict[str, Any] = {
        "error": True,
        "code": code,
        "message": message,
    }
    if server:
        resp["server"] = server
    if tool:
        resp["tool"] = tool
    resp["timestamp"] = datetime.now(timezone.utc).isoformat()
    return resp
