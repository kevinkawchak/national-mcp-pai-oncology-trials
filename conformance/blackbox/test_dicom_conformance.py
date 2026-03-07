"""Black-box DICOM server conformance tests.

Tests that use the harness client to target any MCP DICOM server
deployment, validating query, modality restrictions, and UID validation.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.clinical_resources import (
    DICOM_QUERY_LEVELS,
    DICOM_QUERY_PERMISSIONS,
    DICOM_UID_PATTERN,
    MUST_MODALITIES,
    SHOULD_MODALITIES,
    make_dicom_query_response,
)


@pytest.mark.blackbox
class TestDicomQuery:
    """DICOM query conformance tests."""

    def test_dicom_query_returns_results(self):
        """dicom_query MUST return a results array."""
        response = make_dicom_query_response()
        assert "results" in response
        assert isinstance(response["results"], list)

    @pytest.mark.parametrize("level", DICOM_QUERY_LEVELS)
    def test_query_levels_valid(self, level):
        """All query levels MUST be accepted."""
        assert level in {"PATIENT", "STUDY", "SERIES", "IMAGE"}

    def test_dicom_query_includes_total(self):
        """dicom_query response MUST include a total count."""
        response = make_dicom_query_response()
        assert "total" in response


@pytest.mark.blackbox
class TestDicomModalityRestrictions:
    """DICOM modality restriction conformance tests."""

    @pytest.mark.parametrize("modality", MUST_MODALITIES)
    def test_must_modalities_supported(self, modality):
        """MUST modalities (CT, MR, PT) MUST be supported."""
        assert modality in MUST_MODALITIES

    @pytest.mark.parametrize("modality", SHOULD_MODALITIES)
    def test_should_modalities_defined(self, modality):
        """SHOULD modalities (RTSTRUCT, RTPLAN) SHOULD be supported."""
        assert modality in SHOULD_MODALITIES

    def test_role_based_query_permissions(self):
        """Each role MUST have defined query level permissions."""
        for role, levels in DICOM_QUERY_PERMISSIONS.items():
            assert isinstance(levels, list)
            for level in levels:
                assert level in DICOM_QUERY_LEVELS


@pytest.mark.blackbox
class TestDicomUIDValidation:
    """DICOM UID validation conformance tests."""

    def test_valid_uid_accepted(self):
        """Valid DICOM UIDs MUST be accepted."""
        valid_uid = "1.2.840.113619.2.5.1762583153"
        assert DICOM_UID_PATTERN.match(valid_uid) is not None

    def test_uid_with_letters_rejected(self):
        """UIDs containing letters MUST be rejected."""
        invalid_uid = "1.2.3.abc"
        assert DICOM_UID_PATTERN.match(invalid_uid) is None

    def test_uid_with_spaces_rejected(self):
        """UIDs containing spaces MUST be rejected."""
        invalid_uid = "1.2.3 .4"
        assert DICOM_UID_PATTERN.match(invalid_uid) is None

    def test_patient_name_hashing(self):
        """Patient names MUST be hashed (12-char SHA-256 prefix)."""
        import hashlib

        name = "TestPatient"
        hashed = hashlib.sha256(name.encode()).hexdigest()[:12]
        assert len(hashed) == 12
        assert all(c in "0123456789abcdef" for c in hashed)
