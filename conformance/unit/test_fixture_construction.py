"""Unit tests for fixture construction and schema shapes.

Validates that conformance test fixtures produce correctly
structured data matching the expected JSON Schema shapes,
without requiring any server connections.
"""

from __future__ import annotations

from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    SAMPLE_ERROR_RESPONSE,
    SAMPLE_HEALTH_STATUS,
    VALID_ERROR_CODES,
    VALID_SERVERS,
    compute_audit_hash,
    make_audit_chain,
    make_audit_record,
)
from conformance.fixtures.authz_decisions import (
    DEFAULT_ALLOW_RULES,
    UNAUTHORIZED_ACCESS_ATTEMPTS,
    VALID_ROLES,
    make_allow_decision,
    make_deny_decision,
)
from conformance.fixtures.clinical_resources import (
    DICOM_QUERY_LEVELS,
    HIPAA_SAFE_HARBOR_IDENTIFIERS,
    MUST_MODALITIES,
    SHOULD_MODALITIES,
    make_deidentified_patient,
    make_dicom_query_response,
    make_fhir_read_response,
    make_fhir_search_response,
)
from conformance.fixtures.provenance_records import (
    VALID_ACTION_TYPES,
    VALID_SOURCE_TYPES,
    make_provenance_dag,
    make_provenance_record,
)


class TestAuditRecordFixtures:
    """Unit tests for audit record fixture construction."""

    def test_audit_record_has_required_fields(self):
        record = make_audit_record()
        required = [
            "audit_id",
            "timestamp",
            "server",
            "tool",
            "caller",
            "result_summary",
            "hash",
            "previous_hash",
        ]
        for field_name in required:
            assert field_name in record, f"Missing required field: {field_name}"

    def test_audit_record_hash_is_sha256(self):
        record = make_audit_record()
        assert len(record["hash"]) == 64
        assert all(c in "0123456789abcdef" for c in record["hash"])

    def test_audit_chain_links_correctly(self):
        chain = make_audit_chain(length=5)
        assert len(chain) == 5
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_audit_chain_genesis(self):
        chain = make_audit_chain(length=3)
        assert chain[0]["previous_hash"] == GENESIS_HASH

    def test_compute_hash_deterministic(self):
        record = make_audit_record()
        h1 = compute_audit_hash(record)
        h2 = compute_audit_hash(record)
        assert h1 == h2

    def test_sample_error_response_structure(self):
        assert SAMPLE_ERROR_RESPONSE["error"] is True
        assert SAMPLE_ERROR_RESPONSE["code"] in VALID_ERROR_CODES
        assert "message" in SAMPLE_ERROR_RESPONSE

    def test_sample_health_status_structure(self):
        assert "server_name" in SAMPLE_HEALTH_STATUS
        assert "status" in SAMPLE_HEALTH_STATUS
        assert "checked_at" in SAMPLE_HEALTH_STATUS
        assert isinstance(SAMPLE_HEALTH_STATUS["dependencies"], list)

    def test_valid_servers_count(self):
        assert len(VALID_SERVERS) == 5

    def test_valid_error_codes_count(self):
        assert len(VALID_ERROR_CODES) == 9

    def test_genesis_hash_is_64_zeros(self):
        assert GENESIS_HASH == "0" * 64


class TestAuthzFixtures:
    """Unit tests for authorization decision fixture construction."""

    def test_allow_decision_structure(self):
        decision = make_allow_decision()
        assert decision["allowed"] is True
        assert decision["effect"] == "ALLOW"
        assert "server" in decision
        assert "evaluated_at" in decision

    def test_deny_decision_structure(self):
        decision = make_deny_decision()
        assert decision["allowed"] is False
        assert decision["effect"] == "DENY"
        assert "deny_reason" in decision

    def test_allow_rules_has_six_roles(self):
        assert len(DEFAULT_ALLOW_RULES) == 6
        assert set(DEFAULT_ALLOW_RULES.keys()) == set(VALID_ROLES)

    def test_rbac_deny_by_default(self):
        """Verify that each role has explicitly defined permissions (deny-by-default)."""
        for role in VALID_ROLES:
            assert role in DEFAULT_ALLOW_RULES
            assert isinstance(DEFAULT_ALLOW_RULES[role], list)

    def test_unauthorized_attempts_exist(self):
        assert len(UNAUTHORIZED_ACCESS_ATTEMPTS) >= 6

    def test_allow_decision_has_matching_rules(self):
        decision = make_allow_decision()
        assert "matching_rules" in decision
        assert isinstance(decision["matching_rules"], list)
        assert len(decision["matching_rules"]) >= 1


class TestClinicalFixtures:
    """Unit tests for clinical resource fixture construction."""

    def test_deidentified_patient_resource_type(self):
        patient = make_deidentified_patient()
        assert patient["resourceType"] == "Patient"

    def test_deidentified_patient_name_redacted(self):
        patient = make_deidentified_patient()
        assert patient["name"] == "[REDACTED]"

    def test_deidentified_patient_address_redacted(self):
        patient = make_deidentified_patient()
        assert patient["address"] == "[REDACTED]"

    def test_deidentified_patient_year_only_birthdate(self):
        patient = make_deidentified_patient()
        assert len(patient["birthDate"]) == 4

    def test_fhir_read_response_structure(self):
        response = make_fhir_read_response()
        assert "resource" in response

    def test_fhir_search_response_structure(self):
        response = make_fhir_search_response()
        assert "results" in response
        assert isinstance(response["results"], list)
        assert response["total"] == 3

    def test_dicom_query_response_structure(self):
        response = make_dicom_query_response()
        assert "results" in response
        assert isinstance(response["results"], list)

    def test_hipaa_identifiers_count(self):
        assert len(HIPAA_SAFE_HARBOR_IDENTIFIERS) == 18

    def test_must_modalities(self):
        assert set(MUST_MODALITIES) == {"CT", "MR", "PT"}

    def test_should_modalities(self):
        assert set(SHOULD_MODALITIES) == {"RTSTRUCT", "RTPLAN"}

    def test_dicom_query_levels(self):
        assert set(DICOM_QUERY_LEVELS) == {"PATIENT", "STUDY", "SERIES", "IMAGE"}


class TestProvenanceFixtures:
    """Unit tests for provenance record fixture construction."""

    def test_provenance_record_structure(self):
        record = make_provenance_record()
        assert "record_id" in record
        assert "timestamp" in record
        assert "origin_server" in record
        assert "action" in record

    def test_provenance_record_has_hashes(self):
        record = make_provenance_record()
        assert "input_hash" in record
        assert "output_hash" in record
        assert len(record["input_hash"]) == 64
        assert len(record["output_hash"]) == 64

    def test_provenance_dag_depth(self):
        dag = make_provenance_dag(depth=3)
        assert len(dag) == 3

    def test_provenance_record_valid_source_type(self):
        record = make_provenance_record()
        assert record["source_type"] in VALID_SOURCE_TYPES

    def test_provenance_record_valid_action(self):
        record = make_provenance_record()
        assert record["action"] in VALID_ACTION_TYPES
