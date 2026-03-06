"""Positive conformance tests for Level 1 — Core (AuthZ + Audit).

Validates audit record production, error envelope format, health check
responses, and authorization decision structure per the National MCP-PAI
Oncology Trials Standard.

Specification references:
  - spec/audit.md — Hash-chained ledger requirements
  - spec/security.md — Deny-by-default RBAC
  - spec/tool-contracts.md — Error code taxonomy
  - profiles/base-profile.md — Base conformance profile (19 tests)
  - schemas/audit-record.schema.json
  - schemas/error-response.schema.json
  - schemas/health-status.schema.json
  - schemas/authz-decision.schema.json
"""

from __future__ import annotations

import re

from conformance.conftest import assert_schema_valid, schema_has_required_fields
from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    SAMPLE_AUDIT_RECORD,
    SAMPLE_ERROR_RESPONSE,
    SAMPLE_HEALTH_STATUS,
    VALID_ERROR_CODES,
    VALID_SERVERS,
    compute_audit_hash,
    make_audit_chain,
    make_audit_record,
)
from conformance.fixtures.authz_decisions import (
    VALID_ROLES,
    make_allow_decision,
    make_deny_decision,
)


class TestAuditRecordProduction:
    """Validates audit record production per spec/audit.md."""

    def test_audit_record_has_all_required_fields(self) -> None:
        """Every audit record MUST include all 9 required fields."""
        record = make_audit_record()
        required = schema_has_required_fields("audit-record.schema.json")
        for field in required:
            assert field in record, f"Missing required field: {field}"

    def test_audit_id_is_uuid_format(self) -> None:
        """audit_id MUST be a UUID v4."""
        record = make_audit_record()
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(record["audit_id"])

    def test_timestamp_is_iso8601_utc(self) -> None:
        """timestamp MUST be ISO 8601 UTC."""
        record = make_audit_record()
        assert record["timestamp"].endswith("Z")

    def test_server_is_valid_mcp_server(self) -> None:
        """server MUST be one of the 5 MCP server names."""
        for server in VALID_SERVERS:
            record = make_audit_record(server=server)
            assert record["server"] in VALID_SERVERS

    def test_hash_is_64_char_hex(self) -> None:
        """hash MUST be a 64-character lowercase hex string (SHA-256)."""
        record = make_audit_record()
        assert re.match(r"^[0-9a-f]{64}$", record["hash"])

    def test_previous_hash_is_64_char_hex(self) -> None:
        """previous_hash MUST be a 64-character lowercase hex string."""
        record = make_audit_record()
        assert re.match(r"^[0-9a-f]{64}$", record["previous_hash"])

    def test_genesis_record_uses_zero_hash(self) -> None:
        """The genesis record MUST use '0' * 64 as previous_hash."""
        record = make_audit_record(previous_hash=GENESIS_HASH)
        assert record["previous_hash"] == "0" * 64

    def test_hash_computation_is_deterministic(self) -> None:
        """Hash computation MUST be deterministic for canonical JSON."""
        record = make_audit_record()
        recomputed = compute_audit_hash(record)
        assert record["hash"] == recomputed

    def test_chain_links_consecutive_hashes(self) -> None:
        """Each record's previous_hash MUST equal the preceding record's hash."""
        chain = make_audit_chain(length=5)
        assert chain[0]["previous_hash"] == GENESIS_HASH
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_sample_audit_record_validates_against_schema(self) -> None:
        """The sample audit record MUST validate against audit-record.schema.json."""
        assert_schema_valid(SAMPLE_AUDIT_RECORD, "audit-record.schema.json")


class TestErrorEnvelope:
    """Validates error response format per spec/tool-contracts.md."""

    def test_error_response_has_required_fields(self) -> None:
        """Error responses MUST include error, code, and message."""
        required = schema_has_required_fields("error-response.schema.json")
        for field in required:
            assert field in SAMPLE_ERROR_RESPONSE, f"Missing: {field}"

    def test_error_field_is_true(self) -> None:
        """The error field MUST always be true."""
        assert SAMPLE_ERROR_RESPONSE["error"] is True

    def test_error_code_is_from_taxonomy(self) -> None:
        """Error codes MUST be from the 9-code taxonomy."""
        assert SAMPLE_ERROR_RESPONSE["code"] in VALID_ERROR_CODES

    def test_all_nine_error_codes_are_defined(self) -> None:
        """The standard defines exactly 9 error codes."""
        assert len(VALID_ERROR_CODES) == 9

    def test_error_response_validates_against_schema(self) -> None:
        """The sample error response MUST validate against error-response.schema.json."""
        assert_schema_valid(SAMPLE_ERROR_RESPONSE, "error-response.schema.json")


class TestHealthCheck:
    """Validates health check response per schemas/health-status.schema.json."""

    def test_health_status_has_required_fields(self) -> None:
        """Health responses MUST include required fields."""
        required = schema_has_required_fields("health-status.schema.json")
        for field in required:
            assert field in SAMPLE_HEALTH_STATUS, f"Missing: {field}"

    def test_health_status_valid_server_name(self) -> None:
        """server_name MUST be a valid MCP server name."""
        assert SAMPLE_HEALTH_STATUS["server_name"] in VALID_SERVERS

    def test_health_status_valid_status_values(self) -> None:
        """status MUST be one of: healthy, degraded, unhealthy."""
        assert SAMPLE_HEALTH_STATUS["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_status_validates_against_schema(self) -> None:
        """The sample health status MUST validate against health-status.schema.json."""
        assert_schema_valid(SAMPLE_HEALTH_STATUS, "health-status.schema.json")


class TestAuthorizationDecision:
    """Validates authorization decision structure per spec/security.md."""

    def test_allow_decision_has_required_fields(self) -> None:
        """ALLOW decisions MUST include all required fields."""
        decision = make_allow_decision()
        required = schema_has_required_fields("authz-decision.schema.json")
        for field in required:
            assert field in decision, f"Missing: {field}"

    def test_deny_decision_has_required_fields(self) -> None:
        """DENY decisions MUST include all required fields."""
        decision = make_deny_decision()
        required = schema_has_required_fields("authz-decision.schema.json")
        for field in required:
            assert field in decision, f"Missing: {field}"

    def test_allow_decision_effect_is_allow(self) -> None:
        """ALLOW decisions MUST have effect='ALLOW' and allowed=True."""
        decision = make_allow_decision()
        assert decision["allowed"] is True
        assert decision["effect"] == "ALLOW"

    def test_deny_decision_effect_is_deny(self) -> None:
        """DENY decisions MUST have effect='DENY' and allowed=False."""
        decision = make_deny_decision()
        assert decision["allowed"] is False
        assert decision["effect"] == "DENY"

    def test_role_is_from_six_actor_model(self) -> None:
        """Role MUST be from the 6-actor model."""
        for role in VALID_ROLES:
            decision = make_allow_decision(role=role)
            assert decision["role"] in VALID_ROLES

    def test_allow_decision_validates_against_schema(self) -> None:
        """ALLOW decisions MUST validate against authz-decision.schema.json."""
        assert_schema_valid(make_allow_decision(), "authz-decision.schema.json")

    def test_deny_decision_validates_against_schema(self) -> None:
        """DENY decisions MUST validate against authz-decision.schema.json."""
        assert_schema_valid(make_deny_decision(), "authz-decision.schema.json")
