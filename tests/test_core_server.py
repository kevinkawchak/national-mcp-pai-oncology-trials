"""Unit tests for reference.python.core_server module."""

from __future__ import annotations

import re

from reference.python.core_server import (
    DEFAULT_POLICY,
    GENESIS_HASH,
    authz_evaluate,
    authz_issue_token,
    authz_revoke_token,
    authz_validate_token,
    compute_audit_hash,
    error_response,
    health_status,
    ledger_append,
    ledger_verify,
)

# ---------------------------------------------------------------------------
# AuthZ evaluate
# ---------------------------------------------------------------------------


class TestAuthzEvaluate:
    def test_allow_permitted_tool(self):
        result = authz_evaluate("auditor", "ledger_query")
        assert result["decision"] == "ALLOW"

    def test_deny_unpermitted_tool(self):
        result = authz_evaluate("auditor", "fhir_read")
        assert result["decision"] == "DENY"

    def test_deny_unknown_role(self):
        result = authz_evaluate("unknown_role", "fhir_read")
        assert result["decision"] == "DENY"

    def test_returns_iso_timestamp(self):
        result = authz_evaluate("auditor", "ledger_query")
        assert "T" in result["timestamp"]

    def test_returns_matching_rules(self):
        result = authz_evaluate("auditor", "ledger_query")
        assert isinstance(result["matching_rules"], list)
        assert len(result["matching_rules"]) > 0

    def test_default_resource_id_is_empty_string(self):
        result = authz_evaluate("auditor", "ledger_query")
        assert result["resource_id"] == ""


# ---------------------------------------------------------------------------
# AuthZ tokens
# ---------------------------------------------------------------------------


class TestAuthzTokens:
    def test_issue_token_returns_hash(self):
        result = authz_issue_token("auditor")
        assert "token_hash" in result
        assert len(result["token_hash"]) == 64

    def test_issue_token_max_expiry_cap(self):
        result = authz_issue_token("auditor", expires_in=999999)
        assert "expires_at" in result

    def test_validate_token_valid(self):
        issued = authz_issue_token("auditor")
        result = authz_validate_token(issued["token_hash"])
        assert result["valid"] is True

    def test_validate_token_not_found(self):
        result = authz_validate_token("nonexistent_hash")
        assert result["valid"] is False
        assert result["reason"] == "TOKEN_NOT_FOUND"

    def test_validate_token_revoked(self):
        issued = authz_issue_token("auditor")
        authz_revoke_token(issued["token_hash"])
        result = authz_validate_token(issued["token_hash"])
        assert result["valid"] is False
        assert result["reason"] == "TOKEN_REVOKED"

    def test_revoke_token_success(self):
        issued = authz_issue_token("auditor")
        result = authz_revoke_token(issued["token_hash"])
        assert result["revoked"] is True

    def test_revoke_token_not_found(self):
        result = authz_revoke_token("nonexistent_hash")
        assert result["revoked"] is False


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


class TestLedger:
    def test_compute_audit_hash_deterministic(self):
        record = {"server": "authz", "tool": "test", "caller": "user"}
        h1 = compute_audit_hash(record, GENESIS_HASH)
        h2 = compute_audit_hash(record, GENESIS_HASH)
        assert h1 == h2

    def test_compute_audit_hash_is_sha256(self):
        record = {"server": "authz", "tool": "test", "caller": "user"}
        h = compute_audit_hash(record, GENESIS_HASH)
        assert len(h) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", h)

    def test_ledger_append_returns_required_fields(self):
        record = ledger_append("authz", "evaluate", "user1", "OK")
        required = {"record_id", "timestamp", "server", "tool", "caller", "hash", "prev_hash"}
        assert required.issubset(record.keys())

    def test_ledger_append_default_genesis(self):
        record = ledger_append("authz", "evaluate", "user1", "OK")
        assert record["prev_hash"] == GENESIS_HASH

    def test_ledger_append_chain_linking(self):
        r1 = ledger_append("authz", "evaluate", "user1", "OK")
        r2 = ledger_append("authz", "evaluate", "user1", "OK2", prev_hash=r1["hash"])
        assert r2["prev_hash"] == r1["hash"]

    def test_ledger_verify_valid_chain(self):
        r1 = ledger_append("authz", "evaluate", "user1", "OK")
        r2 = ledger_append("authz", "evaluate", "user1", "OK2", prev_hash=r1["hash"])
        result = ledger_verify([r1, r2])
        assert result["valid"] is True

    def test_ledger_verify_empty_chain(self):
        result = ledger_verify([])
        assert result["valid"] is False

    def test_ledger_verify_tampered_chain(self):
        r1 = ledger_append("authz", "evaluate", "user1", "OK")
        r1["result_summary"] = "TAMPERED"
        result = ledger_verify([r1])
        assert result["valid"] is False


# ---------------------------------------------------------------------------
# Health / error
# ---------------------------------------------------------------------------


class TestHealthAndError:
    def test_health_status_required_fields(self):
        h = health_status()
        required = {"server", "status", "version", "timestamp"}
        assert required.issubset(h.keys())

    def test_health_status_value(self):
        h = health_status()
        assert h["status"] == "healthy"

    def test_error_response_required_fields(self):
        e = error_response("AUTH_DENIED", "not allowed", "evaluate")
        required = {"error", "code", "message", "tool", "timestamp"}
        assert required.issubset(e.keys())

    def test_error_response_error_is_true(self):
        e = error_response("AUTH_DENIED", "not allowed")
        assert e["error"] is True

    def test_error_response_code(self):
        e = error_response("AUTH_DENIED", "not allowed")
        assert e["code"] == "AUTH_DENIED"


# ---------------------------------------------------------------------------
# Policy matrix
# ---------------------------------------------------------------------------


class TestPolicyMatrix:
    def test_default_policy_has_six_roles(self):
        assert len(DEFAULT_POLICY) == 6
