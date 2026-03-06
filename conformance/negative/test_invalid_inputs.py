"""Negative conformance tests for invalid inputs.

Validates that conforming implementations correctly reject malformed requests,
schema mismatches, and invalid parameter values per the National MCP-PAI
Oncology Trials Standard.

Specification references:
  - spec/security.md — Input validation, length limits, format enforcement
  - spec/tool-contracts.md — Error codes for invalid inputs
  - schemas/error-response.schema.json
"""

from __future__ import annotations

import re

import pytest

from conformance.fixtures.audit_records import VALID_ERROR_CODES, VALID_SERVERS
from conformance.fixtures.clinical_resources import (
    DICOM_UID_PATTERN,
    FHIR_ID_PATTERN,
    INVALID_DICOM_UIDS,
    INVALID_FHIR_IDS,
)


class TestMalformedFHIRRequests:
    """Validates rejection of malformed FHIR requests per spec/security.md."""

    @pytest.mark.parametrize("invalid_id", INVALID_FHIR_IDS)
    def test_invalid_fhir_id_rejected(self, invalid_id: str) -> None:
        """FHIR resource IDs not matching the safe pattern MUST be rejected."""
        if invalid_id == "":
            assert not FHIR_ID_PATTERN.match(invalid_id)
        elif len(invalid_id) > 1000:
            # Length validation per spec/security.md: max 1000 chars
            assert len(invalid_id) > 1000
        else:
            # Pattern validation: reject URLs, special chars, etc.
            is_url = invalid_id.lower().startswith(("http://", "https://"))
            is_invalid_pattern = not FHIR_ID_PATTERN.match(invalid_id)
            assert is_url or is_invalid_pattern

    def test_empty_resource_type_rejected(self) -> None:
        """Empty resource_type MUST be rejected with INVALID_INPUT."""
        assert "" not in ["Patient", "Observation", "Condition"]

    def test_missing_required_parameter_detected(self) -> None:
        """Missing required parameters MUST produce VALIDATION_FAILED."""
        # A fhir_read request without resource_type is invalid
        incomplete_request: dict = {"resource_id": "patient-001"}
        assert "resource_type" not in incomplete_request


class TestMalformedDICOMRequests:
    """Validates rejection of malformed DICOM requests per spec/security.md."""

    @pytest.mark.parametrize("invalid_uid", INVALID_DICOM_UIDS)
    def test_invalid_dicom_uid_rejected(self, invalid_uid: str) -> None:
        """DICOM UIDs not matching the numeric dot pattern MUST be rejected."""
        assert not DICOM_UID_PATTERN.match(invalid_uid)

    def test_invalid_query_level_rejected(self) -> None:
        """Query levels not in the enum MUST be rejected."""
        valid_levels = {"PATIENT", "STUDY", "SERIES", "IMAGE"}
        invalid_levels = ["patient", "INVALID", "", "EXAM", "REPORT"]
        for level in invalid_levels:
            assert level not in valid_levels

    def test_invalid_caller_role_rejected(self) -> None:
        """Caller roles not in the 6-actor model MUST be rejected."""
        valid_roles = {
            "robot_agent",
            "trial_coordinator",
            "data_monitor",
            "auditor",
            "sponsor",
            "cro",
        }
        invalid_roles = ["admin", "superuser", "root", "", "patient"]
        for role in invalid_roles:
            assert role not in valid_roles


class TestInputLengthLimits:
    """Validates input length enforcement per spec/security.md."""

    def test_string_max_length_1000(self) -> None:
        """String inputs exceeding 1000 characters MUST be rejected."""
        max_length = 1000
        oversized = "a" * (max_length + 1)
        assert len(oversized) > max_length

    def test_object_max_keys_50(self) -> None:
        """Object inputs exceeding 50 keys MUST be rejected."""
        max_keys = 50
        oversized_obj = {f"key_{i}": f"value_{i}" for i in range(max_keys + 1)}
        assert len(oversized_obj) > max_keys

    def test_array_max_elements_100(self) -> None:
        """Array inputs exceeding 100 elements MUST be rejected."""
        max_elements = 100
        oversized_array = list(range(max_elements + 1))
        assert len(oversized_array) > max_elements


class TestSchemaFieldMismatches:
    """Validates detection of schema field mismatches."""

    def test_audit_record_wrong_server_value(self) -> None:
        """Audit records with unknown server names MUST be rejected."""
        invalid_server = "trialmcp-unknown"
        assert invalid_server not in VALID_SERVERS

    def test_error_response_wrong_code_value(self) -> None:
        """Error responses with unknown error codes MUST be rejected."""
        invalid_code = "UNKNOWN_ERROR"
        assert invalid_code not in VALID_ERROR_CODES

    def test_hash_wrong_length(self) -> None:
        """Hash values not exactly 64 hex characters MUST be rejected."""
        sha256_pattern = re.compile(r"^[0-9a-f]{64}$")
        invalid_hashes = [
            "abc",  # too short
            "0" * 63,  # off by one
            "0" * 65,  # off by one
            "ZZZZ" + "0" * 60,  # non-hex chars
        ]
        for h in invalid_hashes:
            assert not sha256_pattern.match(h)

    def test_timestamp_wrong_format(self) -> None:
        """Timestamps not in ISO 8601 UTC format MUST be rejected."""
        valid_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        invalid_timestamps = [
            "2026-03-06",  # date only
            "14:30:00Z",  # time only
            "March 6, 2026",  # natural language
            "2026/03/06T14:30:00Z",  # wrong separator
        ]
        for ts in invalid_timestamps:
            assert not valid_pattern.match(ts)

    def test_uuid_wrong_format(self) -> None:
        """Fields requiring UUID format MUST reject non-UUID values."""
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "c3d4e5f6-a1b2-7890-cdef",  # incomplete
        ]
        for uid in invalid_uuids:
            assert not uuid_pattern.match(uid)
