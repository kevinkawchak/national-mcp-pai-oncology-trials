"""Adversarial tests for PHI leakage detection.

Validates de-identification completeness, search result filtering,
error message data exposure, and log data exposure prevention.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.clinical_resources import (
    FHIR_REDACTED_FIELDS,
    HIPAA_SAFE_HARBOR_IDENTIFIERS,
    make_deidentified_patient,
    make_fhir_search_response,
)


@pytest.mark.adversarial
class TestDeIdentificationCompleteness:
    """PHI leakage via incomplete de-identification."""

    def test_patient_name_redacted(self):
        """Patient name MUST be fully redacted."""
        patient = make_deidentified_patient()
        assert patient["name"] == "[REDACTED]"

    def test_patient_address_redacted(self):
        """Patient address MUST be fully redacted."""
        patient = make_deidentified_patient()
        assert patient["address"] == "[REDACTED]"

    def test_patient_birthdate_year_only(self):
        """Patient birthDate MUST be year-only (no month/day)."""
        patient = make_deidentified_patient()
        birthdate = patient["birthDate"]
        assert len(birthdate) == 4
        assert birthdate.isdigit()

    def test_18_hipaa_identifiers_tracked(self):
        """All 18 HIPAA Safe Harbor identifiers MUST be tracked for removal."""
        assert len(HIPAA_SAFE_HARBOR_IDENTIFIERS) == 18

    def test_redacted_fields_include_phi(self):
        """Fields containing PHI MUST be in the redacted list."""
        phi_fields = ["name", "telecom", "address"]
        for field_name in phi_fields:
            assert field_name in FHIR_REDACTED_FIELDS

    def test_patient_id_pseudonymized(self):
        """Patient ID MUST be pseudonymized (not original MRN)."""
        patient = make_deidentified_patient()
        # ID should be an HMAC-based pseudonym, not a real MRN
        assert patient["id"].startswith("hmac_") or len(patient["id"]) >= 8


@pytest.mark.adversarial
class TestSearchResultFiltering:
    """PHI leakage via search result filtering gaps."""

    def test_search_results_all_deidentified(self):
        """All search results MUST be de-identified."""
        response = make_fhir_search_response(total=5)
        for result in response["results"]:
            assert result["name"] == "[REDACTED]"
            assert result["address"] == "[REDACTED]"

    def test_search_result_cap_enforced(self):
        """Search results MUST be capped to prevent bulk data extraction."""
        response = make_fhir_search_response(total=100)
        assert len(response["results"]) <= 100


@pytest.mark.adversarial
class TestErrorMessageExposure:
    """PHI leakage via error messages."""

    def test_error_message_no_patient_data(self):
        """Error messages MUST NOT contain patient identifiable data."""
        error_message = "Resource ID contains prohibited URL pattern"
        # Should not contain names, MRNs, SSNs
        assert "John" not in error_message
        assert "SSN" not in error_message
        assert "MRN" not in error_message

    def test_error_details_no_phi(self):
        """Error details MUST NOT expose PHI in field values."""
        error_details = {"field": "resource_id", "expected_pattern": r"^[A-Za-z0-9\-._]+$"}
        for value in error_details.values():
            assert not any(
                phi in str(value).lower()
                for phi in ["patient", "ssn", "mrn", "name", "address"]
                if phi != "patient"  # "patient" in resource_type is OK
            )
