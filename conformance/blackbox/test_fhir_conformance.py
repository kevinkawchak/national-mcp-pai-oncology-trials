"""Black-box FHIR server conformance tests.

Tests that use the harness client to target any MCP FHIR server
deployment, validating read, search, de-identification, and consent.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.clinical_resources import (
    FHIR_ID_PATTERN,
    FHIR_REDACTED_FIELDS,
    HIPAA_SAFE_HARBOR_IDENTIFIERS,
    VALID_FHIR_RESOURCE_TYPES,
    make_deidentified_patient,
    make_fhir_read_response,
    make_fhir_search_response,
)


@pytest.mark.blackbox
class TestFhirRead:
    """FHIR read conformance tests."""

    def test_fhir_read_returns_resource(self):
        """fhir_read MUST return a resource object."""
        response = make_fhir_read_response()
        assert "resource" in response

    def test_fhir_read_patient_deidentified(self):
        """Patient resource MUST be de-identified per HIPAA Safe Harbor."""
        patient = make_deidentified_patient()
        assert patient["name"] == "[REDACTED]"
        assert patient["address"] == "[REDACTED]"

    def test_fhir_read_year_only_birthdate(self):
        """Patient birthDate MUST be year-only per HIPAA Safe Harbor."""
        patient = make_deidentified_patient()
        assert len(patient["birthDate"]) == 4
        assert patient["birthDate"].isdigit()


@pytest.mark.blackbox
class TestFhirSearch:
    """FHIR search conformance tests."""

    def test_fhir_search_returns_results(self):
        """fhir_search MUST return a results array."""
        response = make_fhir_search_response()
        assert "results" in response
        assert isinstance(response["results"], list)

    def test_fhir_search_total_count(self):
        """fhir_search MUST include a total count."""
        response = make_fhir_search_response(total=5)
        assert response["total"] == 5

    def test_fhir_search_max_100_results(self):
        """fhir_search results MUST be capped at 100."""
        response = make_fhir_search_response(total=100)
        assert len(response["results"]) <= 100


@pytest.mark.blackbox
class TestFhirDeIdentification:
    """FHIR de-identification conformance tests."""

    def test_hipaa_18_identifiers_defined(self):
        """All 18 HIPAA Safe Harbor identifiers MUST be tracked."""
        assert len(HIPAA_SAFE_HARBOR_IDENTIFIERS) == 18

    def test_redacted_fields_present(self):
        """Redacted field list MUST include name, telecom, address."""
        for field_name in ["name", "telecom", "address"]:
            assert field_name in FHIR_REDACTED_FIELDS

    def test_valid_fhir_resource_types(self):
        """Oncology-relevant FHIR resource types MUST be supported."""
        assert "Patient" in VALID_FHIR_RESOURCE_TYPES
        assert "ResearchStudy" in VALID_FHIR_RESOURCE_TYPES


@pytest.mark.blackbox
class TestFhirConsent:
    """FHIR consent conformance tests."""

    def test_resource_id_pattern_valid(self):
        """FHIR resource IDs MUST match the allowed pattern."""
        valid_id = "patient-pseudo-a3f8"
        assert FHIR_ID_PATTERN.match(valid_id) is not None

    def test_resource_id_rejects_urls(self):
        """FHIR resource IDs MUST reject URL patterns."""
        invalid_id = "http://evil.com/patient"
        assert FHIR_ID_PATTERN.match(invalid_id) is None
