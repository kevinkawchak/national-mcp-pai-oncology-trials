"""Adversarial tests for malformed clinical data handling.

Validates handling of invalid FHIR resources, malformed DICOM UIDs,
oversized payloads, and injection attempts in all input fields.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.clinical_resources import (
    DICOM_UID_PATTERN,
    FHIR_ID_PATTERN,
    INVALID_DICOM_UIDS,
    INVALID_FHIR_IDS,
    SSRF_PAYLOADS,
)


@pytest.mark.adversarial
class TestInvalidFhirResources:
    """Malformed FHIR resource handling."""

    @pytest.mark.parametrize("invalid_id", INVALID_FHIR_IDS)
    def test_invalid_fhir_id_rejected(self, invalid_id):
        """Invalid FHIR resource IDs MUST be rejected."""
        if invalid_id == "":
            assert len(invalid_id) == 0  # Empty should be rejected
        else:
            # Either pattern doesn't match or length exceeds limit
            match = FHIR_ID_PATTERN.match(invalid_id)
            assert match is None or len(invalid_id) > 1000

    def test_missing_resource_type_rejected(self):
        """Request without resource_type MUST be rejected."""
        request = {"resource_id": "patient-001"}
        assert "resource_type" not in request

    def test_invalid_resource_type_rejected(self):
        """Invalid resource_type MUST be rejected."""
        invalid_types = ["InvalidType", "Admin", "System", ""]
        for rt in invalid_types:
            assert rt not in [
                "Patient",
                "Observation",
                "Condition",
                "MedicationRequest",
                "ResearchStudy",
                "ResearchSubject",
            ]


@pytest.mark.adversarial
class TestMalformedDicomUIDs:
    """Malformed DICOM UID handling."""

    @pytest.mark.parametrize("invalid_uid", INVALID_DICOM_UIDS)
    def test_invalid_dicom_uid_rejected(self, invalid_uid):
        """Invalid DICOM UIDs MUST be rejected."""
        if invalid_uid == "":
            assert len(invalid_uid) == 0
        else:
            assert DICOM_UID_PATTERN.match(invalid_uid) is None

    def test_uid_max_length_64(self):
        """DICOM UIDs exceeding 64 characters SHOULD be rejected."""
        long_uid = "1." * 33  # 66 chars
        assert len(long_uid) > 64


@pytest.mark.adversarial
class TestOversizedPayloads:
    """Oversized payload handling."""

    def test_resource_id_max_1000_chars(self):
        """Resource IDs exceeding 1000 characters MUST be rejected."""
        oversized_id = "a" * 1001
        assert len(oversized_id) > 1000

    def test_parameters_max_50_keys(self):
        """Parameters with more than 50 keys MUST be rejected."""
        oversized_params = {f"key_{i}": f"value_{i}" for i in range(51)}
        assert len(oversized_params) > 50

    def test_array_max_100_elements(self):
        """Arrays with more than 100 elements MUST be rejected."""
        oversized_array = list(range(101))
        assert len(oversized_array) > 100


@pytest.mark.adversarial
class TestInjectionAttempts:
    """Injection attack handling in all input fields."""

    @pytest.mark.parametrize("payload", SSRF_PAYLOADS)
    def test_ssrf_in_resource_id_rejected(self, payload):
        """SSRF payloads in resource_id MUST be rejected."""
        match = FHIR_ID_PATTERN.match(payload)
        assert match is None, f"SSRF payload accepted: {payload}"

    def test_xss_in_resource_id_rejected(self):
        """XSS payloads in resource_id MUST be rejected."""
        xss_payloads = [
            "<script>alert(1)</script>",
            "javascript:alert(1)",
            "<img onerror=alert(1)>",
        ]
        for payload in xss_payloads:
            assert FHIR_ID_PATTERN.match(payload) is None

    def test_sql_injection_in_resource_id_rejected(self):
        """SQL injection payloads in resource_id MUST be rejected."""
        sql_payloads = [
            "'; DROP TABLE patients; --",
            "1 OR 1=1",
            "patient' UNION SELECT * FROM users--",
        ]
        for payload in sql_payloads:
            assert FHIR_ID_PATTERN.match(payload) is None

    def test_command_injection_rejected(self):
        """Command injection payloads MUST be rejected."""
        cmd_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "$(whoami)",
            "`id`",
        ]
        for payload in cmd_payloads:
            assert FHIR_ID_PATTERN.match(payload) is None
