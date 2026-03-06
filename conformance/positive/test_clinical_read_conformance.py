"""Positive conformance tests for Level 2 — Clinical Read (FHIR + De-ID).

Validates FHIR read/search responses, HIPAA Safe Harbor de-identification,
HMAC-SHA256 pseudonymization, and date generalization per the National
MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/privacy.md — HIPAA Safe Harbor, pseudonymization
  - spec/tool-contracts.md — fhir_read, fhir_search, fhir_patient_lookup, fhir_study_status
  - profiles/clinical-read.md — Clinical Read profile (29 tests)
  - schemas/fhir-read.schema.json
  - schemas/fhir-search.schema.json
  - schemas/consent-status.schema.json
"""

from __future__ import annotations

import re

from conformance.conftest import load_schema
from conformance.fixtures.clinical_resources import (
    FHIR_ID_PATTERN,
    FHIR_REDACTED_FIELDS,
    HIPAA_SAFE_HARBOR_IDENTIFIERS,
    VALID_FHIR_RESOURCE_TYPES,
    make_deidentified_patient,
    make_fhir_read_response,
    make_fhir_search_response,
)


class TestFHIRReadConformance:
    """Validates fhir_read tool responses per spec/tool-contracts.md."""

    def test_fhir_read_response_contains_resource(self) -> None:
        """fhir_read MUST return a response containing a 'resource' field."""
        response = make_fhir_read_response()
        assert "resource" in response

    def test_fhir_read_resource_has_resource_type(self) -> None:
        """The returned FHIR resource MUST include a resourceType field."""
        response = make_fhir_read_response()
        assert "resourceType" in response["resource"]

    def test_fhir_read_resource_type_is_valid(self) -> None:
        """resourceType MUST be a recognized FHIR R4 type for oncology trials."""
        response = make_fhir_read_response()
        assert response["resource"]["resourceType"] in VALID_FHIR_RESOURCE_TYPES

    def test_fhir_read_resource_has_id(self) -> None:
        """The returned FHIR resource MUST include an id field."""
        response = make_fhir_read_response()
        assert "id" in response["resource"]

    def test_fhir_read_id_pattern_validation(self) -> None:
        """FHIR resource IDs MUST match the safe ID pattern."""
        valid_ids = ["patient-001", "obs.123", "cond_456", "med-req-789"]
        for fhir_id in valid_ids:
            assert FHIR_ID_PATTERN.match(fhir_id), f"Should match: {fhir_id}"


class TestHIPAASafeHarborDeIdentification:
    """Validates HIPAA Safe Harbor de-identification per spec/privacy.md."""

    def test_eighteen_identifiers_defined(self) -> None:
        """The standard MUST define all 18 HIPAA Safe Harbor identifiers."""
        assert len(HIPAA_SAFE_HARBOR_IDENTIFIERS) == 18

    def test_patient_name_is_redacted(self) -> None:
        """Patient name MUST be redacted in de-identified FHIR resources."""
        patient = make_deidentified_patient()
        assert patient["name"] == "[REDACTED]"

    def test_patient_address_is_redacted(self) -> None:
        """Patient address MUST be redacted in de-identified FHIR resources."""
        patient = make_deidentified_patient()
        assert patient["address"] == "[REDACTED]"

    def test_birth_date_is_year_only(self) -> None:
        """birthDate MUST be generalized to year-only format."""
        patient = make_deidentified_patient()
        assert re.match(r"^\d{4}$", patient["birthDate"])

    def test_patient_id_is_pseudonymized(self) -> None:
        """Patient ID MUST be pseudonymized (not the original ID)."""
        patient = make_deidentified_patient()
        assert patient["id"].startswith("hmac_")

    def test_hmac_pseudonym_format(self) -> None:
        """HMAC-SHA256 pseudonyms MUST follow the hmac_ prefix convention."""
        patient = make_deidentified_patient()
        assert re.match(r"^hmac_[a-f0-9]+$", patient["id"])

    def test_redacted_fields_are_not_raw_data(self) -> None:
        """All FHIR redacted fields MUST NOT contain raw patient data."""
        patient = make_deidentified_patient()
        for field in FHIR_REDACTED_FIELDS:
            if field in patient:
                assert patient[field] == "[REDACTED]", (
                    f"Field '{field}' should be [REDACTED], got: {patient[field]}"
                )

    def test_gender_is_preserved(self) -> None:
        """Non-identifying clinical fields like gender SHOULD be preserved."""
        patient = make_deidentified_patient()
        assert patient["gender"] in ["male", "female", "other", "unknown"]


class TestFHIRSearchConformance:
    """Validates fhir_search responses per spec/tool-contracts.md."""

    def test_fhir_search_returns_results_array(self) -> None:
        """fhir_search MUST return a results array."""
        response = make_fhir_search_response()
        assert isinstance(response["results"], list)

    def test_fhir_search_returns_total_count(self) -> None:
        """fhir_search MUST return a total count."""
        response = make_fhir_search_response(total=5)
        assert response["total"] == 5

    def test_fhir_search_results_cap_at_100(self) -> None:
        """fhir_search results MUST be capped at 100 per spec/privacy.md."""
        response = make_fhir_search_response(total=100)
        assert len(response["results"]) <= 100

    def test_fhir_search_all_results_are_deidentified(self) -> None:
        """Every resource in search results MUST be de-identified."""
        response = make_fhir_search_response(total=3)
        for resource in response["results"]:
            assert resource["name"] == "[REDACTED]"
            assert resource["address"] == "[REDACTED]"
            assert re.match(r"^\d{4}$", resource["birthDate"])

    def test_fhir_search_resource_type_field(self) -> None:
        """fhir_search response MUST include resource_type."""
        response = make_fhir_search_response()
        assert "resource_type" in response


class TestConsentStatus:
    """Validates consent status schema per schemas/consent-status.schema.json."""

    def test_consent_schema_exists(self) -> None:
        """consent-status.schema.json MUST exist."""
        schema = load_schema("consent-status.schema.json")
        assert schema["title"] == "Consent Status"

    def test_consent_schema_has_required_fields(self) -> None:
        """Consent status MUST define required fields."""
        schema = load_schema("consent-status.schema.json")
        assert "required" in schema
        assert len(schema["required"]) > 0
