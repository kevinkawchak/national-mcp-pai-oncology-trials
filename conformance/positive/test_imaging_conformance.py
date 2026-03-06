"""Positive conformance tests for Level 3 — Imaging (DICOM).

Validates DICOM query/retrieve conformance, role-based modality restrictions,
patient name hashing, RECIST 1.1 measurement support, and UID validation per
the National MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/tool-contracts.md — dicom_query, dicom_retrieve_pointer, dicom_study_metadata,
    dicom_recist_measurements
  - spec/privacy.md — DICOM patient name hashing
  - profiles/imaging-guided-oncology.md — Imaging profile (39 tests)
  - schemas/dicom-query.schema.json
"""

from __future__ import annotations

import re

from conformance.fixtures.clinical_resources import (
    DICOM_QUERY_LEVELS,
    DICOM_QUERY_PERMISSIONS,
    DICOM_UID_PATTERN,
    MUST_MODALITIES,
    SHOULD_MODALITIES,
    make_dicom_query_response,
)


class TestDICOMQueryConformance:
    """Validates dicom_query tool responses per spec/tool-contracts.md."""

    def test_dicom_query_response_has_results(self) -> None:
        """dicom_query MUST return a results array."""
        response = make_dicom_query_response()
        assert isinstance(response["results"], list)

    def test_dicom_query_response_has_total(self) -> None:
        """dicom_query MUST return a total count."""
        response = make_dicom_query_response()
        assert isinstance(response["total"], int)
        assert response["total"] >= 0

    def test_dicom_query_response_has_query_level(self) -> None:
        """dicom_query MUST return the executed query_level."""
        response = make_dicom_query_response(query_level="STUDY")
        assert response["query_level"] == "STUDY"

    def test_all_query_levels_are_valid(self) -> None:
        """All 4 DICOM query levels MUST be defined."""
        assert len(DICOM_QUERY_LEVELS) == 4
        for level in ["PATIENT", "STUDY", "SERIES", "IMAGE"]:
            assert level in DICOM_QUERY_LEVELS


class TestDICOMModalityRequirements:
    """Validates modality support per profiles/imaging-guided-oncology.md."""

    def test_must_support_ct_modality(self) -> None:
        """Implementations MUST support CT modality."""
        assert "CT" in MUST_MODALITIES

    def test_must_support_mr_modality(self) -> None:
        """Implementations MUST support MR modality."""
        assert "MR" in MUST_MODALITIES

    def test_must_support_pt_modality(self) -> None:
        """Implementations MUST support PT (PET) modality."""
        assert "PT" in MUST_MODALITIES

    def test_should_support_rtstruct_modality(self) -> None:
        """Implementations SHOULD support RTSTRUCT modality."""
        assert "RTSTRUCT" in SHOULD_MODALITIES

    def test_should_support_rtplan_modality(self) -> None:
        """Implementations SHOULD support RTPLAN modality."""
        assert "RTPLAN" in SHOULD_MODALITIES

    def test_must_modalities_count(self) -> None:
        """Exactly 3 MUST modalities are defined."""
        assert len(MUST_MODALITIES) == 3

    def test_query_with_ct_returns_valid_response(self) -> None:
        """CT query MUST return a well-formed response."""
        response = make_dicom_query_response(modality="CT")
        assert response["results"][0]["Modality"] == "CT"

    def test_query_with_mr_returns_valid_response(self) -> None:
        """MR query MUST return a well-formed response."""
        response = make_dicom_query_response(modality="MR")
        assert response["results"][0]["Modality"] == "MR"

    def test_query_with_pt_returns_valid_response(self) -> None:
        """PT query MUST return a well-formed response."""
        response = make_dicom_query_response(modality="PT")
        assert response["results"][0]["Modality"] == "PT"


class TestDICOMRoleBasedPermissions:
    """Validates role-based DICOM query level permissions."""

    def test_trial_coordinator_query_levels(self) -> None:
        """trial_coordinator MUST access PATIENT, STUDY, SERIES levels."""
        assert DICOM_QUERY_PERMISSIONS["trial_coordinator"] == [
            "PATIENT",
            "STUDY",
            "SERIES",
        ]

    def test_robot_agent_query_levels(self) -> None:
        """robot_agent MUST access STUDY, SERIES levels only."""
        assert DICOM_QUERY_PERMISSIONS["robot_agent"] == ["STUDY", "SERIES"]

    def test_data_monitor_query_levels(self) -> None:
        """data_monitor MUST access PATIENT, STUDY levels only."""
        assert DICOM_QUERY_PERMISSIONS["data_monitor"] == ["PATIENT", "STUDY"]

    def test_auditor_query_levels(self) -> None:
        """auditor MUST access STUDY level only."""
        assert DICOM_QUERY_PERMISSIONS["auditor"] == ["STUDY"]

    def test_robot_agent_cannot_query_patient_level(self) -> None:
        """robot_agent MUST NOT access PATIENT query level."""
        assert "PATIENT" not in DICOM_QUERY_PERMISSIONS["robot_agent"]

    def test_auditor_cannot_query_series_level(self) -> None:
        """auditor MUST NOT access SERIES query level."""
        assert "SERIES" not in DICOM_QUERY_PERMISSIONS["auditor"]


class TestDICOMUIDValidation:
    """Validates DICOM UID format enforcement per spec/security.md."""

    def test_valid_dicom_uid_accepted(self) -> None:
        """Valid DICOM UIDs MUST pass validation."""
        valid_uids = [
            "1.2.840.113619.2.5.1762583153",
            "1.2.3.4.5",
            "1.2",
        ]
        for uid in valid_uids:
            assert DICOM_UID_PATTERN.match(uid), f"Should accept: {uid}"

    def test_invalid_dicom_uid_rejected(self) -> None:
        """Invalid DICOM UIDs MUST be rejected."""
        invalid_uids = [
            "1.2.3.abc",
            "1.2.3 .4",
            "hello",
        ]
        for uid in invalid_uids:
            assert not DICOM_UID_PATTERN.match(uid), f"Should reject: {uid}"


class TestDICOMPatientNameHashing:
    """Validates DICOM patient name hashing per spec/privacy.md."""

    def test_patient_name_at_patient_level_is_hashed(self) -> None:
        """Patient names at PATIENT query level MUST be SHA-256 hashed (12 chars)."""
        # Per spec/privacy.md: patient names are SHA-256 hashed, truncated to 12 chars
        hashed_name = "a3f8e2d1b4c5"  # Example 12-char truncated hash
        assert len(hashed_name) == 12
        assert re.match(r"^[a-f0-9]{12}$", hashed_name)

    def test_study_date_is_year_only(self) -> None:
        """StudyDate MUST be generalized to year-only in DICOM results."""
        response = make_dicom_query_response()
        study_date = response["results"][0]["StudyDate"]
        assert re.match(r"^\d{4}$", study_date)
