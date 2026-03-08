"""Comprehensive tests for integration modules.

Covers FHIR, DICOM, identity, clinical, privacy, and federation
integration layers.
"""

from __future__ import annotations

import asyncio
import base64
import json
import time

import pytest

from integrations.clinical.econsent_adapter import (
    ConsentCategory as EConsentCategory,
)
from integrations.clinical.econsent_adapter import (
    ConsentDocumentRef,
    ConsentRecord,
    IRBApproval,
)
from integrations.clinical.econsent_adapter import (
    ConsentStatus as EConsentStatus,
)
from integrations.clinical.scheduling_adapter import (
    ConflictType,
    RobotAssignment,
    ScheduleConflict,
    ScheduledProcedure,
    TimeWindow,
    ValidationResult,
)
from integrations.clinical.scheduling_adapter import (
    ProcedureStatus as SchedProcedureStatus,
)
from integrations.dicom.base_adapter import QueryLevel
from integrations.dicom.mock_adapter import MockDicomAdapter
from integrations.dicom.modality_filter import (
    MUST_MODALITIES,
    ModalityFilter,
)
from integrations.dicom.recist import (
    EXAMPLE_BASELINE_MEASUREMENTS,
    EXAMPLE_FOLLOWUP_MEASUREMENTS,
    OverallResponse,
    calculate_overall_response,
    calculate_sum_of_diameters,
    compare_timepoints,
    validate_new_lesion,
    validate_non_target_assessment,
    validate_target_lesions,
)
from integrations.dicom.safety import (
    SafetyValidator,
    SafetyViolation,
)
from integrations.federation.policy_enforcement import (
    ComputationPolicy,
    ComputationType,
    DataParticipationPolicy,
    DataParticipationScope,
    FederationPolicyEnforcer,
    ResultReleasePolicy,
    SiteFederationPolicy,
)
from integrations.federation.secure_aggregation import (
    Share,
    aggregate_shares,
    apply_mask,
    compute_commitment,
    generate_mask,
    remove_mask,
)
from integrations.fhir.bundle_handler import (
    BundleParser,
    BundleValidationError,
    create_batch_bundle,
    create_searchset_bundle,
    create_transaction_bundle,
    create_transaction_response,
    make_entry,
    make_response_entry,
    validate_bundle,
)
from integrations.fhir.capability import (
    CapabilityParser,
    generate_capability_statement,
)
from integrations.fhir.deidentification import (
    HIPAA_IDENTIFIERS,
    REDACTED,
    DeidentificationPipeline,
    DeidentificationVerifier,
)
from integrations.fhir.mock_adapter import MockFHIRAdapter
from integrations.fhir.patient_filter import (
    ConsentCategory,
    ConsentStore,
    PatientResourceFilter,
)
from integrations.fhir.terminology import (
    ICD10_SYSTEM,
    LOINC_SYSTEM,
    RXNORM_SYSTEM,
    SNOMED_SYSTEM,
    TerminologyRegistry,
)
from integrations.identity.base_adapter import (
    AuthResult,
)
from integrations.identity.oidc_adapter import (
    OIDCAdapter,
    _decode_jwt_parts,
)
from integrations.identity.policy_engine import (
    Decision,
    PolicyEngine,
    PolicyInput,
)
from integrations.privacy.access_control import (
    AccessControlManager,
    AccessRequest,
    AccessSubject,
    DataClassification,
    Permission,
    PermissionEffect,
    Role,
)
from integrations.privacy.data_residency import (
    DataCategory,
    DataResidencyManager,
    Jurisdiction,
    SiteBoundaryPolicy,
    TransferDecision,
    TransferRequest,
    get_default_retention_rules,
)
from integrations.privacy.privacy_budget import (
    BudgetStatus,
    PrivacyBudgetManager,
)

# ===================================================================
# Helpers
# ===================================================================


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_jwt(payload: dict, header: dict | None = None) -> str:
    """Build a minimal unsigned JWT string."""
    hdr = header or {"alg": "RS256", "typ": "JWT"}
    hdr_b64 = base64.urlsafe_b64encode(json.dumps(hdr).encode()).rstrip(b"=").decode()
    pay_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    sig_b64 = base64.urlsafe_b64encode(b"fakesig").rstrip(b"=").decode()
    return f"{hdr_b64}.{pay_b64}.{sig_b64}"


async def _always_valid_verifier(
    signing_input: bytes,
    signature: bytes,
    header: dict,
) -> bool:
    return True


async def _always_invalid_verifier(
    signing_input: bytes,
    signature: bytes,
    header: dict,
) -> bool:
    return False


# ===================================================================
# 1. FHIR Mock Adapter
# ===================================================================


class TestMockFHIRAdapter:
    """Tests for MockFHIRAdapter."""

    def setup_method(self) -> None:
        self.adapter = MockFHIRAdapter()

    def test_read_patient(self) -> None:
        result = self.adapter.read("Patient", "patient-onc-001")
        assert result is not None
        assert result["resourceType"] == "Patient"
        assert result["id"] == "patient-onc-001"

    def test_read_nonexistent_returns_none(self) -> None:
        assert self.adapter.read("Patient", "does-not-exist") is None

    def test_read_research_study(self) -> None:
        result = self.adapter.read("ResearchStudy", "study-pai-lung-001")
        assert result is not None
        assert result["status"] == "active"

    def test_search_patients_returns_bundle(self) -> None:
        bundle = self.adapter.search("Patient")
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "searchset"
        assert bundle["total"] == 3

    def test_search_with_filter(self) -> None:
        bundle = self.adapter.search("Patient", params={"gender": "female"})
        assert bundle["total"] == 1
        entry = bundle["entry"][0]["resource"]
        assert entry["gender"] == "female"

    def test_search_with_limit(self) -> None:
        bundle = self.adapter.search("Patient", limit=1)
        assert len(bundle["entry"]) == 1

    def test_patient_lookup_found(self) -> None:
        result = self.adapter.patient_lookup("patient-onc-002")
        assert result is not None
        assert result["id"] == "patient-onc-002"

    def test_patient_lookup_not_found(self) -> None:
        assert self.adapter.patient_lookup("no-such-id") is None

    def test_study_status_found(self) -> None:
        result = self.adapter.study_status("study-pai-lung-001")
        assert result is not None
        assert result["status"] == "active"

    def test_study_status_not_found(self) -> None:
        assert self.adapter.study_status("bad-id") is None

    def test_capability_statement(self) -> None:
        cs = self.adapter.capability_statement()
        assert cs["resourceType"] == "CapabilityStatement"
        assert cs["fhirVersion"] == "4.0.1"

    def test_search_observations(self) -> None:
        bundle = self.adapter.search("Observation")
        assert bundle["total"] == 3


# ===================================================================
# 2. FHIR De-identification
# ===================================================================


class TestDeidentification:
    """Tests for DeidentificationPipeline and Verifier."""

    def setup_method(self) -> None:
        self.pipeline = DeidentificationPipeline(hmac_key="test-key")

    def test_hipaa_identifiers_count(self) -> None:
        assert len(HIPAA_IDENTIFIERS) == 18

    def test_pseudonymize_id_deterministic(self) -> None:
        a = self.pipeline.pseudonymize_id("patient-001")
        b = self.pipeline.pseudonymize_id("patient-001")
        assert a == b
        assert len(a) == 64  # SHA-256 hex

    def test_pseudonymize_id_different_inputs(self) -> None:
        a = self.pipeline.pseudonymize_id("patient-001")
        b = self.pipeline.pseudonymize_id("patient-002")
        assert a != b

    def test_generalize_date_full(self) -> None:
        assert DeidentificationPipeline.generalize_date("1980-06-15") == "1980"

    def test_generalize_date_already_year(self) -> None:
        assert DeidentificationPipeline.generalize_date("1980") == "1980"

    def test_scrub_text_ssn(self) -> None:
        text = "SSN: 123-45-6789 is private"
        scrubbed = DeidentificationPipeline.scrub_text(text)
        assert "123-45-6789" not in scrubbed
        assert REDACTED in scrubbed

    def test_scrub_text_email(self) -> None:
        text = "Contact jane.doe@example.com for info"
        scrubbed = DeidentificationPipeline.scrub_text(text)
        assert "jane.doe@example.com" not in scrubbed

    def test_scrub_text_phone(self) -> None:
        text = "Call (555) 123-4567 now"
        scrubbed = DeidentificationPipeline.scrub_text(text)
        assert "(555) 123-4567" not in scrubbed

    def test_deidentify_resource_removes_name(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "name": [{"family": "Smith", "given": ["John"]}],
        }
        result = self.pipeline.deidentify_resource(resource)
        assert result["name"] == [{"text": REDACTED}]

    def test_deidentify_resource_removes_address(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "address": [{"city": "Boston"}],
        }
        result = self.pipeline.deidentify_resource(resource)
        assert result["address"] == [{"text": REDACTED}]

    def test_deidentify_resource_generalizes_birthdate(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "birthDate": "1980-06-15",
        }
        result = self.pipeline.deidentify_resource(resource)
        assert result["birthDate"] == "1980"

    def test_deidentify_resource_removes_telecom(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "telecom": [{"system": "phone", "value": "555-1234"}],
        }
        result = self.pipeline.deidentify_resource(resource)
        assert "telecom" not in result

    def test_deidentify_resource_removes_photo(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "photo": [{"data": "base64..."}],
        }
        result = self.pipeline.deidentify_resource(resource)
        assert "photo" not in result

    def test_deidentify_resource_pseudonymizes_ids(self) -> None:
        resource = {
            "resourceType": "Patient",
            "id": "p1",
            "identifier": [{"system": "mrn", "value": "MRN-12345"}],
        }
        result = self.pipeline.deidentify_resource(resource)
        ident_val = result["identifier"][0]["value"]
        assert len(ident_val) == 64

    def test_deidentify_resource_pseudonymizes_patient_id(
        self,
    ) -> None:
        resource = {"resourceType": "Patient", "id": "p1"}
        result = self.pipeline.deidentify_resource(resource)
        assert result["id"] != "p1"
        assert len(result["id"]) == 64

    def test_deidentify_bundle(self) -> None:
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "p1",
                        "name": [{"family": "Doe"}],
                    }
                }
            ],
        }
        result = self.pipeline.deidentify_bundle(bundle)
        entry_resource = result["entry"][0]["resource"]
        assert entry_resource["name"] == [{"text": REDACTED}]

    def test_verifier_is_compliant(self) -> None:
        verifier = DeidentificationVerifier(self.pipeline)
        assert verifier.is_compliant() is True

    def test_verifier_verify_all_no_failures(self) -> None:
        verifier = DeidentificationVerifier(self.pipeline)
        results = verifier.verify_all()
        for failures in results.values():
            assert failures == []


# ===================================================================
# 3. FHIR Bundle Handler
# ===================================================================


class TestBundleHandler:
    """Tests for bundle creation, parsing, and validation."""

    def test_create_searchset_bundle(self) -> None:
        resources = [{"resourceType": "Patient", "id": "p1"}]
        bundle = create_searchset_bundle(resources)
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "searchset"
        assert bundle["total"] == 1

    def test_create_searchset_bundle_with_links(self) -> None:
        bundle = create_searchset_bundle(
            [],
            link_self="http://example.com/Patient",
            link_next="http://example.com/Patient?page=2",
        )
        assert len(bundle["link"]) == 2

    def test_create_transaction_bundle(self) -> None:
        entry = make_entry(
            {"resourceType": "Patient", "id": "p1"},
            method="POST",
            url="Patient",
        )
        bundle = create_transaction_bundle([entry])
        assert bundle["type"] == "transaction"
        assert len(bundle["entry"]) == 1

    def test_create_batch_bundle(self) -> None:
        entry = make_entry(
            {"resourceType": "Patient", "id": "p1"},
            method="POST",
            url="Patient",
        )
        bundle = create_batch_bundle([entry])
        assert bundle["type"] == "batch"

    def test_create_transaction_response(self) -> None:
        resp_entry = make_response_entry("201 Created")
        bundle = create_transaction_response([resp_entry])
        assert bundle["type"] == "transaction-response"

    def test_validate_bundle_valid_searchset(self) -> None:
        bundle = create_searchset_bundle([{"resourceType": "Patient", "id": "p1"}])
        errors = validate_bundle(bundle)
        assert errors == []

    def test_validate_bundle_wrong_resource_type(self) -> None:
        errors = validate_bundle({"resourceType": "Patient"})
        assert any("resourceType" in e for e in errors)

    def test_validate_bundle_invalid_type(self) -> None:
        errors = validate_bundle({"resourceType": "Bundle", "type": "bogus"})
        assert any("Invalid bundle type" in e for e in errors)

    def test_validate_transaction_missing_request(self) -> None:
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [{"resource": {"resourceType": "Patient"}}],
        }
        errors = validate_bundle(bundle)
        assert any("request" in e for e in errors)

    def test_bundle_parser_resources(self) -> None:
        bundle = create_searchset_bundle(
            [
                {"resourceType": "Patient", "id": "p1"},
                {"resourceType": "Observation", "id": "o1"},
            ]
        )
        parser = BundleParser(bundle)
        assert len(parser.resources()) == 2
        assert parser.bundle_type == "searchset"
        assert parser.total == 2

    def test_bundle_parser_resources_by_type(self) -> None:
        bundle = create_searchset_bundle(
            [
                {"resourceType": "Patient", "id": "p1"},
                {"resourceType": "Observation", "id": "o1"},
            ]
        )
        parser = BundleParser(bundle)
        patients = parser.resources_by_type("Patient")
        assert len(patients) == 1

    def test_bundle_parser_invalid_raises(self) -> None:
        with pytest.raises(BundleValidationError):
            BundleParser({"resourceType": "Patient"})

    def test_bundle_parser_links(self) -> None:
        bundle = create_searchset_bundle(
            [],
            link_self="http://self",
            link_next="http://next",
        )
        parser = BundleParser(bundle)
        assert parser.self_link == "http://self"
        assert parser.next_link == "http://next"

    def test_make_entry_with_if_match(self) -> None:
        entry = make_entry(
            {"resourceType": "Patient", "id": "p1"},
            method="PUT",
            url="Patient/p1",
            if_match='W/"1"',
        )
        assert entry["request"]["ifMatch"] == 'W/"1"'

    def test_make_response_entry_full(self) -> None:
        entry = make_response_entry(
            "200 OK",
            location="Patient/p1",
            etag='W/"2"',
            last_modified="2025-01-01T00:00:00Z",
            resource={"resourceType": "Patient", "id": "p1"},
        )
        assert entry["response"]["status"] == "200 OK"
        assert entry["response"]["etag"] == 'W/"2"'
        assert "resource" in entry


# ===================================================================
# 4. FHIR Capability Statement
# ===================================================================


class TestCapabilityStatement:
    """Tests for capability statement generation and parsing."""

    def test_generate_default(self) -> None:
        cs = generate_capability_statement()
        assert cs["resourceType"] == "CapabilityStatement"
        assert cs["fhirVersion"] == "4.0.1"
        assert cs["status"] == "active"

    def test_generate_custom_params(self) -> None:
        cs = generate_capability_statement(
            server_url="http://custom.example.com/fhir",
            software_name="CustomSoft",
            software_version="2.0.0",
        )
        assert cs["software"]["name"] == "CustomSoft"
        assert cs["software"]["version"] == "2.0.0"

    def test_parser_supported_resources(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        types = parser.supported_resource_types()
        assert "Patient" in types
        assert "ResearchStudy" in types
        assert "Observation" in types

    def test_parser_supports_resource(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        assert parser.supports_resource("Patient") is True
        assert parser.supports_resource("Bogus") is False

    def test_parser_interactions_for(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        interactions = parser.interactions_for("Consent")
        assert "read" in interactions
        assert "create" in interactions

    def test_parser_search_params(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        params = parser.search_params_for("Patient")
        param_names = [p["name"] for p in params]
        assert "_id" in param_names
        assert "name" in param_names

    def test_parser_system_interactions(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        si = parser.system_interactions()
        assert "transaction" in si
        assert "batch" in si

    def test_parser_smart_security(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        assert parser.has_smart_security() is True

    def test_parser_fhir_version(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        assert parser.fhir_version == "4.0.1"

    def test_parser_formats(self) -> None:
        cs = generate_capability_statement()
        parser = CapabilityParser(cs)
        assert "json" in parser.formats


# ===================================================================
# 5. FHIR Terminology
# ===================================================================


class TestTerminology:
    """Tests for TerminologyRegistry."""

    def setup_method(self) -> None:
        self.registry = TerminologyRegistry()

    def test_lookup_icd10(self) -> None:
        entry = self.registry.lookup(ICD10_SYSTEM, "C34.1")
        assert entry is not None
        assert "lung" in entry.display.lower()

    def test_lookup_snomed(self) -> None:
        entry = self.registry.lookup(SNOMED_SYSTEM, "254637007")
        assert entry is not None
        assert "lung" in entry.display.lower()

    def test_lookup_loinc(self) -> None:
        entry = self.registry.lookup(LOINC_SYSTEM, "2857-1")
        assert entry is not None
        assert "prostate" in entry.display.lower()

    def test_lookup_rxnorm(self) -> None:
        entry = self.registry.lookup(RXNORM_SYSTEM, "51499")
        assert entry is not None
        assert entry.display == "Cisplatin"

    def test_lookup_display_found(self) -> None:
        display = self.registry.lookup_display(ICD10_SYSTEM, "C61")
        assert "prostate" in display.lower()

    def test_lookup_display_not_found(self) -> None:
        display = self.registry.lookup_display(ICD10_SYSTEM, "UNKNOWN")
        assert display == "UNKNOWN"

    def test_codes_in_system(self) -> None:
        codes = self.registry.codes_in_system(RXNORM_SYSTEM)
        assert len(codes) > 0

    def test_map_code_icd10_to_snomed(self) -> None:
        targets = self.registry.map_code(ICD10_SYSTEM, "C34.1", SNOMED_SYSTEM)
        assert len(targets) >= 1
        assert targets[0].system == SNOMED_SYSTEM

    def test_map_code_reverse(self) -> None:
        targets = self.registry.map_code(SNOMED_SYSTEM, "399068003", ICD10_SYSTEM)
        assert len(targets) >= 1
        assert targets[0].code == "C61"

    def test_add_code(self) -> None:
        entry = self.registry.add_code(ICD10_SYSTEM, "C99", "Test neoplasm")
        assert self.registry.lookup(ICD10_SYSTEM, "C99") == entry

    def test_to_fhir_coding(self) -> None:
        coding = self.registry.to_fhir_coding(ICD10_SYSTEM, "C61")
        assert coding is not None
        assert coding["system"] == ICD10_SYSTEM
        assert coding["code"] == "C61"

    def test_to_fhir_coding_unknown(self) -> None:
        assert self.registry.to_fhir_coding(ICD10_SYSTEM, "ZZZ") is None

    def test_to_fhir_codeable_concept(self) -> None:
        cc = self.registry.to_fhir_codeable_concept(LOINC_SYSTEM, "2857-1")
        assert cc is not None
        assert "coding" in cc
        assert "text" in cc


# ===================================================================
# 6. FHIR Patient Filter
# ===================================================================


class TestPatientFilter:
    """Tests for consent-based patient resource filtering."""

    def setup_method(self) -> None:
        self.store = ConsentStore()
        self.filter = PatientResourceFilter(self.store)

    def test_consent_record_grant_and_check(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        assert record.is_granted(ConsentCategory.GENERAL_TRIAL)

    def test_consent_record_deny(self) -> None:
        record = self.store.get_or_create("p1")
        record.deny(ConsentCategory.IMAGING)
        assert not record.is_granted(ConsentCategory.IMAGING)

    def test_consent_record_withdraw(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        record.withdraw(ConsentCategory.GENERAL_TRIAL)
        assert not record.is_granted(ConsentCategory.GENERAL_TRIAL)

    def test_patient_accessible_with_consent(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        resource = {"resourceType": "Patient", "id": "p1"}
        assert self.filter.is_accessible(resource) is True

    def test_patient_not_accessible_without_consent(self) -> None:
        resource = {"resourceType": "Patient", "id": "p1"}
        assert self.filter.is_accessible(resource) is False

    def test_imaging_study_requires_imaging_consent(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        resource = {
            "resourceType": "ImagingStudy",
            "subject": {"reference": "Patient/p1"},
        }
        assert self.filter.is_accessible(resource) is False
        record.grant(ConsentCategory.IMAGING)
        assert self.filter.is_accessible(resource) is True

    def test_filter_resources(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        resources = [
            {"resourceType": "Patient", "id": "p1"},
            {"resourceType": "Patient", "id": "p2"},
        ]
        filtered = self.filter.filter_resources(resources)
        assert len(filtered) == 1

    def test_filter_bundle(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 2,
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1"}},
                {"resource": {"resourceType": "Patient", "id": "p2"}},
            ],
        }
        result = self.filter.filter_bundle(bundle)
        assert result["total"] == 1

    def test_consent_store_has_consent(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        assert self.store.has_consent("p1", [ConsentCategory.GENERAL_TRIAL])
        assert not self.store.has_consent("p2", [ConsentCategory.GENERAL_TRIAL])

    def test_consent_to_fhir(self) -> None:
        record = self.store.get_or_create("p1")
        record.grant(ConsentCategory.GENERAL_TRIAL)
        fhir = record.to_fhir_consent()
        assert fhir["resourceType"] == "Consent"
        assert fhir["status"] == "active"

    def test_research_study_accessible_without_patient(
        self,
    ) -> None:
        resource = {
            "resourceType": "ResearchStudy",
            "id": "study-1",
        }
        assert self.filter.is_accessible(resource) is True


# ===================================================================
# 7. DICOM Mock Adapter
# ===================================================================


class TestMockDicomAdapter:
    """Tests for MockDicomAdapter."""

    def setup_method(self) -> None:
        self.adapter = MockDicomAdapter()

    def test_query_studies(self) -> None:
        results = self.adapter.query(QueryLevel.STUDY, {})
        assert len(results) == 4

    def test_query_studies_with_filter(self) -> None:
        results = self.adapter.query(QueryLevel.STUDY, {"PatientID": "ONC-TRIAL-001"})
        assert len(results) == 1

    def test_query_series(self) -> None:
        results = self.adapter.query(QueryLevel.SERIES, {"Modality": "CT"})
        assert len(results) >= 3

    def test_query_with_limit_and_offset(self) -> None:
        all_results = self.adapter.query(QueryLevel.STUDY, {})
        paged = self.adapter.query(QueryLevel.STUDY, {}, limit=2, offset=1)
        assert len(paged) == 2
        assert paged[0] == all_results[1]

    def test_retrieve_metadata_study(self) -> None:
        uid = "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639"
        meta = self.adapter.retrieve_metadata(uid)
        assert meta["PatientID"] == "ONC-TRIAL-001"

    def test_retrieve_metadata_series(self) -> None:
        study_uid = "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639"
        series_uid = "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10001"
        meta = self.adapter.retrieve_metadata(study_uid, series_uid)
        assert meta["Modality"] == "CT"

    def test_retrieve_metadata_not_found(self) -> None:
        with pytest.raises(KeyError):
            self.adapter.retrieve_metadata("nonexistent")

    def test_validate_modality_supported(self) -> None:
        assert self.adapter.validate_modality("CT") is True

    def test_validate_modality_unsupported(self) -> None:
        assert self.adapter.validate_modality("US") is False

    def test_ping(self) -> None:
        assert self.adapter.ping() is True


# ===================================================================
# 8. DICOM Modality Filter
# ===================================================================


class TestModalityFilter:
    """Tests for role-based modality restrictions."""

    def setup_method(self) -> None:
        self.filter = ModalityFilter()

    def test_robot_agent_can_access_ct(self) -> None:
        assert self.filter.is_permitted("robot_agent", "CT")

    def test_robot_agent_cannot_access_rtplan(self) -> None:
        assert not self.filter.is_permitted("robot_agent", "RTPLAN")

    def test_auditor_can_access_rtplan(self) -> None:
        assert self.filter.is_permitted("auditor", "RTPLAN")

    def test_trial_coordinator_has_all(self) -> None:
        assert self.filter.is_permitted("trial_coordinator", "RTPLAN")
        assert self.filter.is_permitted("trial_coordinator", "CT")

    def test_unknown_role_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown role"):
            self.filter.is_permitted("bogus_role", "CT")

    def test_filter_results(self) -> None:
        results = [
            {"Modality": "CT", "id": "1"},
            {"Modality": "RTPLAN", "id": "2"},
        ]
        filtered = self.filter.filter_results("robot_agent", results)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"

    def test_get_permitted_modalities(self) -> None:
        permitted = self.filter.get_permitted_modalities("robot_agent")
        assert permitted == MUST_MODALITIES

    def test_grant_modality(self) -> None:
        self.filter.grant_modality("robot_agent", "RTPLAN")
        assert self.filter.is_permitted("robot_agent", "RTPLAN")

    def test_revoke_modality(self) -> None:
        self.filter.revoke_modality("robot_agent", "CT")
        assert not self.filter.is_permitted("robot_agent", "CT")


# ===================================================================
# 9. DICOM RECIST Validator
# ===================================================================


class TestRECIST:
    """Tests for RECIST 1.1 validation."""

    def test_validate_target_lesions_valid(self) -> None:
        lesions = EXAMPLE_BASELINE_MEASUREMENTS["target_lesions"]
        errors = validate_target_lesions(lesions)
        assert errors == []

    def test_validate_too_many_lesions(self) -> None:
        lesions = [
            {
                "lesion_id": f"TL-{i}",
                "organ": f"organ_{i}",
                "longest_diameter_mm": 15.0,
            }
            for i in range(6)
        ]
        errors = validate_target_lesions(lesions)
        assert any("Too many target lesions" in e for e in errors)

    def test_validate_too_many_per_organ(self) -> None:
        lesions = [
            {
                "lesion_id": f"TL-{i}",
                "organ": "liver",
                "longest_diameter_mm": 15.0,
            }
            for i in range(3)
        ]
        errors = validate_target_lesions(lesions)
        assert any("liver" in e for e in errors)

    def test_validate_lesion_too_small(self) -> None:
        lesions = [
            {
                "lesion_id": "TL-1",
                "organ": "lung",
                "longest_diameter_mm": 5.0,
            }
        ]
        errors = validate_target_lesions(lesions)
        assert len(errors) == 1

    def test_validate_lymph_node_threshold(self) -> None:
        lesions = [
            {
                "lesion_id": "TL-1",
                "organ": "lymph_node",
                "longest_diameter_mm": 12.0,
            }
        ]
        errors = validate_target_lesions(lesions)
        assert any("Lymph node" in e for e in errors)

    def test_validate_non_target_valid(self) -> None:
        assert validate_non_target_assessment("CR") is True
        assert validate_non_target_assessment("non-CR/non-PD") is True
        assert validate_non_target_assessment("PD") is True

    def test_validate_non_target_invalid(self) -> None:
        assert validate_non_target_assessment("bogus") is False

    def test_validate_new_lesion_errors(self) -> None:
        errors = validate_new_lesion({})
        assert len(errors) == 4  # 4 required fields

    def test_validate_new_lesion_valid(self) -> None:
        lesion = {
            "lesion_id": "NL-1",
            "organ": "liver",
            "description": "New hepatic lesion",
            "detection_date": "2025-03-01",
        }
        errors = validate_new_lesion(lesion)
        assert errors == []

    def test_calculate_sum_of_diameters(self) -> None:
        lesions = [
            {"longest_diameter_mm": 10.0},
            {"longest_diameter_mm": 20.0},
        ]
        assert calculate_sum_of_diameters(lesions) == 30.0

    def test_overall_response_pd_new_lesions(self) -> None:
        result = calculate_overall_response(100.0, 100.0, 100.0, has_new_lesions=True)
        assert result == OverallResponse.PD

    def test_overall_response_cr(self) -> None:
        result = calculate_overall_response(100.0, 100.0, 0.0)
        assert result == OverallResponse.CR

    def test_overall_response_pr(self) -> None:
        result = calculate_overall_response(100.0, 100.0, 65.0)
        assert result == OverallResponse.PR

    def test_overall_response_sd(self) -> None:
        result = calculate_overall_response(100.0, 100.0, 95.0)
        assert result == OverallResponse.SD

    def test_compare_timepoints(self) -> None:
        result = compare_timepoints(
            EXAMPLE_BASELINE_MEASUREMENTS,
            EXAMPLE_FOLLOWUP_MEASUREMENTS,
        )
        assert "overall_response" in result
        assert result["overall_response"] == "PR"


# ===================================================================
# 10. DICOM Safety Validator
# ===================================================================


class TestDicomSafety:
    """Tests for DICOM safety constraints."""

    def setup_method(self) -> None:
        self.validator = SafetyValidator(strict=True)
        self.lenient = SafetyValidator(strict=False)

    def test_clean_metadata_passes(self) -> None:
        meta = {
            "StudyInstanceUID": "1.2.3",
            "Modality": "CT",
        }
        self.validator.validate_metadata_response(meta)

    def test_pixel_data_raises_strict(self) -> None:
        meta = {"7FE00010": b"\x00" * 2048}
        with pytest.raises(SafetyViolation):
            self.validator.validate_metadata_response(meta)

    def test_pixel_data_warns_lenient(self) -> None:
        meta = {"7FE00010": b"\x00" * 2048}
        self.lenient.validate_metadata_response(meta)

    def test_strip_pixel_fields(self) -> None:
        meta = {
            "StudyInstanceUID": "1.2.3",
            "7FE00010": b"\x00" * 2048,
        }
        cleaned = self.lenient.strip_pixel_fields(meta)
        assert "7FE00010" not in cleaned
        assert "StudyInstanceUID" in cleaned

    def test_strip_bulk_data_uri(self) -> None:
        meta = {
            "StudyInstanceUID": "1.2.3",
            "SomeField": {"BulkDataURI": "http://example.com"},
        }
        cleaned = self.lenient.strip_pixel_fields(meta)
        assert "SomeField" not in cleaned

    def test_validate_image_reference_valid(self) -> None:
        ref = {
            "StudyInstanceUID": "1.2.3",
            "Modality": "CT",
        }
        errors = self.validator.validate_image_reference(ref)
        assert errors == []

    def test_validate_image_reference_missing_uid(self) -> None:
        ref = {"Modality": "CT"}
        errors = self.validator.validate_image_reference(ref)
        assert any("StudyInstanceUID" in e for e in errors)

    def test_check_retrieval_auth_no_role(self) -> None:
        assert not self.validator.check_retrieval_authorization("", "1.2.3")

    def test_check_retrieval_auth_valid(self) -> None:
        assert self.validator.check_retrieval_authorization("robot_agent", "1.2.3")

    def test_check_retrieval_auth_with_context(self) -> None:
        ctx = {
            "token": "abc",
            "trial_id": "trial-1",
            "enrolled_studies": ["1.2.3"],
        }
        assert self.validator.check_retrieval_authorization(
            "robot_agent", "1.2.3", authorization_context=ctx
        )

    def test_check_retrieval_auth_not_enrolled(self) -> None:
        ctx = {
            "token": "abc",
            "trial_id": "trial-1",
            "enrolled_studies": ["9.9.9"],
        }
        assert not self.validator.check_retrieval_authorization(
            "robot_agent", "1.2.3", authorization_context=ctx
        )


# ===================================================================
# 11. OIDC Adapter
# ===================================================================


class TestOIDCAdapter:
    """Tests for OIDC/JWT validation."""

    def setup_method(self) -> None:
        self.adapter = OIDCAdapter(
            issuer="https://idp.example.com",
            audience="oncology-api",
            signature_verifier=_always_valid_verifier,
        )

    def test_validate_token_success(self) -> None:
        now = int(time.time())
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "sub": "user-1",
                "exp": now + 3600,
            }
        )
        claims = _run(self.adapter.validate_token(token))
        assert claims["sub"] == "user-1"

    def test_validate_token_bad_issuer(self) -> None:
        token = _make_jwt(
            {
                "iss": "https://wrong.example.com",
                "aud": "oncology-api",
                "exp": int(time.time()) + 3600,
            }
        )
        with pytest.raises(ValueError, match="Issuer"):
            _run(self.adapter.validate_token(token))

    def test_validate_token_bad_audience(self) -> None:
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "wrong-api",
                "exp": int(time.time()) + 3600,
            }
        )
        with pytest.raises(ValueError, match="Audience"):
            _run(self.adapter.validate_token(token))

    def test_validate_token_expired(self) -> None:
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "exp": int(time.time()) - 3600,
            }
        )
        with pytest.raises(ValueError, match="expired"):
            _run(self.adapter.validate_token(token))

    def test_validate_token_bad_signature(self) -> None:
        adapter = OIDCAdapter(
            issuer="https://idp.example.com",
            audience="oncology-api",
            signature_verifier=_always_invalid_verifier,
        )
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "exp": int(time.time()) + 3600,
            }
        )
        with pytest.raises(ValueError, match="signature"):
            _run(adapter.validate_token(token))

    def test_get_user_info(self) -> None:
        now = int(time.time())
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "sub": "user-1",
                "email": "user@example.com",
                "name": "Test User",
                "roles": ["admin"],
                "exp": now + 3600,
            }
        )
        info = _run(self.adapter.get_user_info(token))
        assert info.subject == "user-1"
        assert info.email == "user@example.com"
        assert "admin" in info.roles

    def test_authenticate_success(self) -> None:
        now = int(time.time())
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "sub": "user-1",
                "exp": now + 3600,
            }
        )
        result, data = _run(self.adapter.authenticate({"token": token}))
        assert result == AuthResult.GRANTED

    def test_authenticate_no_token(self) -> None:
        result, data = _run(self.adapter.authenticate({}))
        assert result == AuthResult.INVALID

    def test_authenticate_expired(self) -> None:
        token = _make_jwt(
            {
                "iss": "https://idp.example.com",
                "aud": "oncology-api",
                "exp": int(time.time()) - 3600,
            }
        )
        result, data = _run(self.adapter.authenticate({"token": token}))
        assert result == AuthResult.EXPIRED

    def test_authorize_defers(self) -> None:
        decision = _run(self.adapter.authorize("user-1", "resource", "read"))
        assert decision.result == AuthResult.DENIED

    def test_decode_jwt_malformed(self) -> None:
        with pytest.raises(ValueError, match="three"):
            _decode_jwt_parts("only.two")


# ===================================================================
# 12. Policy Engine
# ===================================================================


class TestPolicyEngine:
    """Tests for OPA-compatible policy engine."""

    def setup_method(self) -> None:
        self.engine = PolicyEngine(cache_ttl_seconds=60)

    def test_deny_by_default(self) -> None:
        inp = PolicyInput(
            subject="user-1",
            resource="Patient/1",
            action="read",
        )
        result = _run(self.engine.evaluate(inp))
        assert result.decision == Decision.DENY

    def test_allow_with_rule(self) -> None:
        self.engine.add_rule(
            {
                "effect": "allow",
                "match": {"action": "read"},
                "description": "allow reads",
            }
        )
        inp = PolicyInput(
            subject="user-1",
            resource="Patient/1",
            action="read",
        )
        result = _run(self.engine.evaluate(inp))
        assert result.decision == Decision.ALLOW

    def test_deny_overrides_allow(self) -> None:
        self.engine.add_rule(
            {
                "effect": "allow",
                "match": {"action": "read"},
                "description": "allow reads",
            }
        )
        self.engine.add_rule(
            {
                "effect": "deny",
                "match": {"subject": "blocked"},
                "description": "block user",
            }
        )
        inp = PolicyInput(
            subject="blocked",
            resource="Patient/1",
            action="read",
        )
        result = _run(self.engine.evaluate(inp))
        assert result.decision == Decision.DENY

    def test_caching(self) -> None:
        self.engine.add_rule(
            {
                "effect": "allow",
                "match": {"action": "read"},
                "description": "allow reads",
            }
        )
        inp = PolicyInput(
            subject="user-1",
            resource="Patient/1",
            action="read",
        )
        r1 = _run(self.engine.evaluate(inp))
        r2 = _run(self.engine.evaluate(inp))
        assert r1.evaluated_at == r2.evaluated_at

    def test_clear_cache(self) -> None:
        self.engine.add_rule(
            {
                "effect": "allow",
                "match": {"action": "read"},
                "description": "allow reads",
            }
        )
        inp = PolicyInput(
            subject="user-1",
            resource="Patient/1",
            action="read",
        )
        _run(self.engine.evaluate(inp))
        self.engine.clear_cache()
        # Cache is cleared; no assertion needed, just no crash

    def test_invalid_rule_raises(self) -> None:
        with pytest.raises(ValueError, match="effect"):
            self.engine.add_rule({"effect": "maybe"})

    def test_load_rules(self) -> None:
        self.engine.load_rules(
            [
                {
                    "effect": "allow",
                    "match": {},
                    "description": "allow all",
                }
            ]
        )
        inp = PolicyInput(subject="u", resource="r", action="a")
        result = _run(self.engine.evaluate(inp))
        assert result.decision == Decision.ALLOW

    def test_set_policy_version(self) -> None:
        self.engine.set_policy_version("1.2.3")
        self.engine.add_rule(
            {
                "effect": "allow",
                "match": {},
                "description": "all",
            }
        )
        inp = PolicyInput(subject="u", resource="r", action="a")
        result = _run(self.engine.evaluate(inp))
        assert result.policy_version == "1.2.3"


# ===================================================================
# 13. Clinical eConsent Adapter (data model tests)
# ===================================================================


class TestEConsentDataModels:
    """Tests for eConsent data models."""

    def test_consent_record_is_valid(self) -> None:
        record = ConsentRecord(
            consent_id="c1",
            participant_id="p1",
            trial_id="t1",
            status=EConsentStatus.ACTIVE,
            granted_at=time.time(),
        )
        assert record.is_valid is True

    def test_consent_record_expired(self) -> None:
        record = ConsentRecord(
            consent_id="c1",
            participant_id="p1",
            trial_id="t1",
            status=EConsentStatus.ACTIVE,
            expires_at=time.time() - 100,
        )
        assert record.is_valid is False

    def test_consent_record_withdrawn(self) -> None:
        record = ConsentRecord(
            consent_id="c1",
            participant_id="p1",
            trial_id="t1",
            status=EConsentStatus.WITHDRAWN,
        )
        assert record.is_valid is False

    def test_consent_document_ref(self) -> None:
        ref = ConsentDocumentRef(
            document_id="d1",
            version="1.0",
            title="Consent Form",
            url="https://example.com/consent/d1",
        )
        assert ref.language == "en"

    def test_irb_approval(self) -> None:
        irb = IRBApproval(
            irb_id="irb-1",
            protocol_id="prot-1",
            approval_number="AP-2025-001",
            approved_at=time.time(),
            expires_at=time.time() + 86400 * 365,
            institution="University Hospital",
        )
        assert irb.status == "approved"

    def test_consent_categories(self) -> None:
        assert len(EConsentCategory) == 6


# ===================================================================
# 14. Clinical Scheduling Adapter (data model tests)
# ===================================================================


class TestSchedulingDataModels:
    """Tests for scheduling data models."""

    def test_time_window(self) -> None:
        tw = TimeWindow(
            start="2025-03-15T09:00:00Z",
            end="2025-03-15T12:00:00Z",
        )
        assert tw.timezone == "UTC"

    def test_scheduled_procedure(self) -> None:
        proc = ScheduledProcedure(
            procedure_id="proc-1",
            trial_id="trial-1",
            participant_id="p1",
            procedure_type="lobectomy",
            status=SchedProcedureStatus.SCHEDULED,
            time_window=TimeWindow(
                start="2025-03-15T09:00:00Z",
                end="2025-03-15T12:00:00Z",
            ),
            site_id="site-1",
        )
        assert proc.status == SchedProcedureStatus.SCHEDULED

    def test_robot_assignment(self) -> None:
        ra = RobotAssignment(
            robot_id="robot-1",
            robot_type="davinci",
            capability="thoracoscopy",
            assigned_at="2025-03-14T10:00:00Z",
        )
        assert ra.robot_id == "robot-1"

    def test_schedule_conflict(self) -> None:
        sc = ScheduleConflict(
            conflict_type=ConflictType.TIME_OVERLAP,
            procedure_id="proc-1",
            conflicting_procedure_id="proc-2",
            description="Time overlap detected",
        )
        assert sc.conflict_type == ConflictType.TIME_OVERLAP

    def test_validation_result(self) -> None:
        vr = ValidationResult(valid=True)
        assert vr.valid is True
        assert vr.errors == []

    def test_procedure_status_values(self) -> None:
        assert len(SchedProcedureStatus) == 5


# ===================================================================
# 15. Privacy Access Control
# ===================================================================


class TestAccessControl:
    """Tests for RBAC + ABAC access control."""

    def setup_method(self) -> None:
        self.mgr = AccessControlManager()
        self.mgr.register_role(
            Role(
                name="researcher",
                permissions=[
                    Permission(
                        resource="Patient",
                        action="read",
                    ),
                ],
                max_classification=(DataClassification.CONFIDENTIAL),
            )
        )

    def test_rbac_allow(self) -> None:
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=["researcher"],
                clearance=DataClassification.CONFIDENTIAL,
            ),
            resource="Patient",
            action="read",
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.ALLOW

    def test_rbac_deny_no_matching_role(self) -> None:
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=["viewer"],
                clearance=DataClassification.CONFIDENTIAL,
            ),
            resource="Patient",
            action="read",
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.DENY

    def test_classification_enforcement(self) -> None:
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=["researcher"],
                clearance=DataClassification.PUBLIC,
            ),
            resource="Patient",
            action="read",
            resource_classification=(DataClassification.RESTRICTED),
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.DENY
        assert any("clearance" in r.lower() for r in decision.reasons)

    def test_abac_deny_rule(self) -> None:
        self.mgr.add_abac_policy(
            {
                "effect": "deny",
                "condition": {"department": "external"},
                "description": "block externals",
            }
        )
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=["researcher"],
                clearance=DataClassification.CONFIDENTIAL,
                attributes={"department": "external"},
            ),
            resource="Patient",
            action="read",
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.DENY

    def test_abac_allow_fallback(self) -> None:
        self.mgr.add_abac_policy(
            {
                "effect": "allow",
                "condition": {"special": True},
                "description": "special access",
            }
        )
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=[],
                clearance=DataClassification.INTERNAL,
                attributes={"special": True},
            ),
            resource="Something",
            action="read",
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.ALLOW

    def test_check_classification_static(self) -> None:
        assert AccessControlManager.check_classification(
            DataClassification.RESTRICTED,
            DataClassification.CONFIDENTIAL,
        )
        assert not AccessControlManager.check_classification(
            DataClassification.PUBLIC,
            DataClassification.RESTRICTED,
        )

    def test_register_and_list_roles(self) -> None:
        self.mgr.register_role(Role(name="admin", permissions=[]))
        roles = self.mgr.list_roles()
        names = [r.name for r in roles]
        assert "researcher" in names
        assert "admin" in names

    def test_get_role(self) -> None:
        role = self.mgr.get_role("researcher")
        assert role is not None
        assert role.name == "researcher"

    def test_wildcard_permission(self) -> None:
        self.mgr.register_role(
            Role(
                name="admin",
                permissions=[
                    Permission(
                        resource="*",
                        action="*",
                    )
                ],
                max_classification=(DataClassification.RESTRICTED),
            )
        )
        req = AccessRequest(
            subject=AccessSubject(
                subject_id="u1",
                roles=["admin"],
                clearance=DataClassification.RESTRICTED,
            ),
            resource="Anything",
            action="delete",
        )
        decision = self.mgr.evaluate(req)
        assert decision.effect == PermissionEffect.ALLOW


# ===================================================================
# 16. Privacy Budget
# ===================================================================


class TestPrivacyBudget:
    """Tests for differential privacy budget accounting."""

    def setup_method(self) -> None:
        self.mgr = PrivacyBudgetManager(default_epsilon=1.0, low_threshold=0.1)

    def test_register_site(self) -> None:
        budget = self.mgr.register_site("site-1")
        assert budget.total_epsilon == 1.0
        assert budget.remaining_epsilon == 1.0
        assert budget.status == BudgetStatus.AVAILABLE

    def test_allocate(self) -> None:
        self.mgr.register_site("site-1")
        alloc = self.mgr.allocate("site-1", 0.3, "query-1")
        assert alloc.epsilon == 0.3
        budget = self.mgr.get_budget("site-1")
        assert budget.consumed_epsilon == pytest.approx(0.3)

    def test_allocate_exceeds_budget(self) -> None:
        self.mgr.register_site("site-1")
        with pytest.raises(ValueError, match="exceeds"):
            self.mgr.allocate("site-1", 2.0, "query-1")

    def test_allocate_negative(self) -> None:
        self.mgr.register_site("site-1")
        with pytest.raises(ValueError, match="positive"):
            self.mgr.allocate("site-1", -0.1, "query-1")

    def test_budget_exhaustion(self) -> None:
        self.mgr.register_site("site-1")
        self.mgr.allocate("site-1", 1.0, "query-1")
        assert self.mgr.is_exhausted("site-1") is True

    def test_budget_low_status(self) -> None:
        self.mgr.register_site("site-1")
        self.mgr.allocate("site-1", 0.95, "query-1")
        budget = self.mgr.get_budget("site-1")
        assert budget.status == BudgetStatus.LOW

    def test_can_allocate(self) -> None:
        self.mgr.register_site("site-1")
        assert self.mgr.can_allocate("site-1", 0.5) is True
        assert self.mgr.can_allocate("site-1", 1.5) is False

    def test_reset_budget(self) -> None:
        self.mgr.register_site("site-1")
        self.mgr.allocate("site-1", 0.5, "q1")
        self.mgr.reset_budget("site-1")
        budget = self.mgr.get_budget("site-1")
        assert budget.consumed_epsilon == 0.0

    def test_unregistered_site_raises(self) -> None:
        with pytest.raises(KeyError):
            self.mgr.get_budget("nonexistent")


# ===================================================================
# 17. Privacy Data Residency
# ===================================================================


class TestDataResidency:
    """Tests for data residency enforcement."""

    def setup_method(self) -> None:
        self.mgr = DataResidencyManager()
        self.mgr.register_site_policy(
            SiteBoundaryPolicy(
                site_id="site-A",
                jurisdiction=Jurisdiction.US_FEDERAL,
                allow_outbound_transfer=True,
                allowed_destination_sites=["site-B"],
                allowed_data_categories=[
                    DataCategory.PHI,
                    DataCategory.AGGREGATE_STATS,
                ],
            )
        )
        self.mgr.register_site_policy(
            SiteBoundaryPolicy(
                site_id="site-B",
                jurisdiction=Jurisdiction.US_FEDERAL,
                allowed_data_categories=[
                    DataCategory.PHI,
                    DataCategory.AGGREGATE_STATS,
                ],
            )
        )

    def test_transfer_approved(self) -> None:
        req = TransferRequest(
            request_id="xfer-1",
            source_site_id="site-A",
            destination_site_id="site-B",
            data_category=DataCategory.AGGREGATE_STATS,
            justification="Analysis",
        )
        result = self.mgr.authorize_transfer(req)
        assert result.decision == TransferDecision.APPROVED

    def test_transfer_denied_outbound(self) -> None:
        self.mgr.register_site_policy(
            SiteBoundaryPolicy(
                site_id="site-C",
                jurisdiction=Jurisdiction.CALIFORNIA_CCPA,
                allow_outbound_transfer=False,
            )
        )
        req = TransferRequest(
            request_id="xfer-2",
            source_site_id="site-C",
            destination_site_id="site-A",
            data_category=DataCategory.PHI,
            justification="Research",
        )
        result = self.mgr.authorize_transfer(req)
        assert result.decision == TransferDecision.DENIED

    def test_transfer_denied_not_in_allowed_list(self) -> None:
        req = TransferRequest(
            request_id="xfer-3",
            source_site_id="site-A",
            destination_site_id="site-C",
            data_category=DataCategory.PHI,
            justification="Research",
        )
        result = self.mgr.authorize_transfer(req)
        assert result.decision == TransferDecision.DENIED

    def test_transfer_denied_unknown_source(self) -> None:
        req = TransferRequest(
            request_id="xfer-4",
            source_site_id="unknown",
            destination_site_id="site-B",
            data_category=DataCategory.PHI,
            justification="Test",
        )
        result = self.mgr.authorize_transfer(req)
        assert result.decision == TransferDecision.DENIED

    def test_get_default_retention_rules(self) -> None:
        rules = get_default_retention_rules(Jurisdiction.US_FEDERAL)
        assert len(rules) >= 2

    def test_retention_compliance(self) -> None:
        ok, reason = self.mgr.check_retention_compliance(
            "site-A", DataCategory.PHI, data_age_days=100
        )
        assert ok is True

    def test_get_site_policy(self) -> None:
        policy = self.mgr.get_site_policy("site-A")
        assert policy.jurisdiction == Jurisdiction.US_FEDERAL


# ===================================================================
# 18. Federation Coordinator (data model tests)
# ===================================================================


class TestFederationDataModels:
    """Tests for federation coordinator data models."""

    def test_site_enrollment(self) -> None:
        from integrations.federation.coordinator import (
            SiteEnrollment,
            SiteStatus,
        )

        enrollment = SiteEnrollment(site_id="s1", site_name="Hospital A")
        assert enrollment.status == SiteStatus.PENDING

    def test_round_state(self) -> None:
        from integrations.federation.coordinator import (
            RoundPhase,
            RoundState,
        )

        rs = RoundState(round_id="r1", round_number=1)
        assert rs.phase == RoundPhase.INITIALIZE

    def test_federation_session(self) -> None:
        from integrations.federation.coordinator import (
            FederationSession,
            FederationStatus,
        )

        session = FederationSession(session_id="fs1", trial_id="t1")
        assert session.status == FederationStatus.CREATED


# ===================================================================
# 19. Federation Secure Aggregation
# ===================================================================


class TestSecureAggregation:
    """Tests for secure aggregation helpers."""

    def test_generate_mask_length(self) -> None:
        mask = generate_mask(10)
        assert len(mask) == 10

    def test_generate_mask_modulus(self) -> None:
        mask = generate_mask(100, modulus=256)
        assert all(0 <= v < 256 for v in mask)

    def test_apply_mask(self) -> None:
        values = [10, 20, 30]
        mask = [1, 2, 3]
        masked = apply_mask(values, mask, modulus=100)
        assert masked == [11, 22, 33]

    def test_remove_mask(self) -> None:
        values = [10, 20, 30]
        mask = [1, 2, 3]
        masked = apply_mask(values, mask, modulus=100)
        restored = remove_mask(masked, mask, modulus=100)
        assert restored == values

    def test_apply_mask_length_mismatch(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            apply_mask([1, 2], [1], modulus=100)

    def test_compute_commitment_deterministic(self) -> None:
        mask = [10, 20, 30]
        c1 = compute_commitment(mask)
        c2 = compute_commitment(mask)
        assert c1 == c2
        assert len(c1) == 64

    def test_aggregate_shares_simple(self) -> None:
        shares = [
            Share(site_id="s1", round_id="r1", values=[10, 20]),
            Share(site_id="s2", round_id="r1", values=[30, 40]),
        ]
        result = aggregate_shares(shares, modulus=1000)
        assert result == [40, 60]

    def test_aggregate_shares_empty(self) -> None:
        with pytest.raises(ValueError, match="No shares"):
            aggregate_shares([])

    def test_aggregate_shares_mismatched_lengths(self) -> None:
        shares = [
            Share(site_id="s1", round_id="r1", values=[10]),
            Share(site_id="s2", round_id="r1", values=[10, 20]),
        ]
        with pytest.raises(ValueError, match="same vector"):
            aggregate_shares(shares)

    def test_mask_apply_remove_roundtrip(self) -> None:
        values = [100, 200, 300]
        mask = generate_mask(3)
        masked = apply_mask(values, mask)
        restored = remove_mask(masked, mask)
        assert restored == values


# ===================================================================
# 20. Federation Policy Enforcement
# ===================================================================


class TestFederationPolicyEnforcement:
    """Tests for site-level federation policy enforcement."""

    def setup_method(self) -> None:
        self.enforcer = FederationPolicyEnforcer()
        self.enforcer.register_policy(
            SiteFederationPolicy(
                site_id="site-1",
                data_participation=DataParticipationPolicy(
                    site_id="site-1",
                    scope=(DataParticipationScope.DEIDENTIFIED_ONLY),
                    included_data_types=["imaging", "labs"],
                ),
                computation_policies=[
                    ComputationPolicy(
                        computation_type=(ComputationType.MODEL_TRAINING),
                        allowed=True,
                    ),
                    ComputationPolicy(
                        computation_type=(ComputationType.CUSTOM),
                        allowed=False,
                    ),
                ],
                result_release=ResultReleasePolicy(
                    site_id="site-1",
                    min_contributing_sites=3,
                    require_differential_privacy=True,
                ),
            )
        )

    def test_data_participation_allowed(self) -> None:
        result = self.enforcer.check_data_participation("site-1", "imaging")
        assert result.allowed is True

    def test_data_participation_denied_type(self) -> None:
        result = self.enforcer.check_data_participation("site-1", "genomics")
        assert result.allowed is False

    def test_computation_allowed(self) -> None:
        result = self.enforcer.check_computation("site-1", ComputationType.MODEL_TRAINING)
        assert result.allowed is True

    def test_computation_denied(self) -> None:
        result = self.enforcer.check_computation("site-1", ComputationType.CUSTOM)
        assert result.allowed is False

    def test_computation_no_policy_denied(self) -> None:
        result = self.enforcer.check_computation("site-1", ComputationType.SURVIVAL_ANALYSIS)
        assert result.allowed is False

    def test_result_release_authorized(self) -> None:
        result = self.enforcer.authorize_result_release(
            "site-1",
            contributing_site_count=5,
            has_differential_privacy=True,
        )
        assert result.allowed is True

    def test_result_release_denied_site_count(self) -> None:
        result = self.enforcer.authorize_result_release(
            "site-1",
            contributing_site_count=2,
            has_differential_privacy=True,
        )
        assert result.allowed is False

    def test_result_release_denied_no_dp(self) -> None:
        result = self.enforcer.authorize_result_release(
            "site-1",
            contributing_site_count=5,
            has_differential_privacy=False,
        )
        assert result.allowed is False

    def test_check_minimum_sites_pass(self) -> None:
        result = self.enforcer.check_minimum_sites(["site-1", "site-2", "site-3"])
        assert result.allowed is True

    def test_check_minimum_sites_fail(self) -> None:
        result = self.enforcer.check_minimum_sites(["site-1"])
        assert result.allowed is False

    def test_disabled_site(self) -> None:
        self.enforcer.register_policy(
            SiteFederationPolicy(
                site_id="site-disabled",
                data_participation=DataParticipationPolicy(site_id="site-disabled"),
                enabled=False,
            )
        )
        result = self.enforcer.check_data_participation("site-disabled", "imaging")
        assert result.allowed is False

    def test_unknown_site_raises(self) -> None:
        with pytest.raises(KeyError):
            self.enforcer.get_policy("nonexistent")
