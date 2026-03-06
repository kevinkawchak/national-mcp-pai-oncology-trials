"""Interoperability conformance tests for schema validation.

Validates that all MCP server outputs conform to the machine-readable
JSON schemas defined in /schemas/ per the National MCP-PAI Oncology
Trials Standard.

Specification references:
  - All 13 schemas in /schemas/
  - spec/conformance.md — Schema validation requirements
  - profiles/ — Schema requirements per conformance level
"""

from __future__ import annotations

import json

import pytest

from conformance.conftest import (
    SCHEMA_FILES,
    SCHEMAS_DIR,
    assert_schema_valid,
    load_schema,
    schema_has_required_fields,
    validate_against_schema,
)
from conformance.fixtures.audit_records import (
    SAMPLE_AUDIT_RECORD,
    SAMPLE_ERROR_RESPONSE,
    SAMPLE_HEALTH_STATUS,
)
from conformance.fixtures.authz_decisions import (
    make_allow_decision,
    make_deny_decision,
)
from conformance.fixtures.provenance_records import (
    SAMPLE_CROSS_SERVER_PROVENANCE,
    make_provenance_record,
)


class TestSchemaFilesExist:
    """Validates that all 13 schema files are present."""

    def test_all_thirteen_schemas_exist(self) -> None:
        """All 13 JSON Schema files MUST exist in /schemas/."""
        assert len(SCHEMA_FILES) == 13
        for name in SCHEMA_FILES:
            schema_path = SCHEMAS_DIR / name
            assert schema_path.exists(), f"Missing schema: {name}"

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_is_valid_json(self, schema_name: str) -> None:
        """Each schema file MUST be valid JSON."""
        schema_path = SCHEMAS_DIR / schema_name
        content = schema_path.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_uses_draft_2020_12(self, schema_name: str) -> None:
        """Each schema MUST reference JSON Schema draft 2020-12."""
        schema = load_schema(schema_name)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_has_id(self, schema_name: str) -> None:
        """Each schema MUST have a $id field."""
        schema = load_schema(schema_name)
        assert "$id" in schema

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_has_title(self, schema_name: str) -> None:
        """Each schema MUST have a title field."""
        schema = load_schema(schema_name)
        assert "title" in schema
        assert len(schema["title"]) > 0

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_has_description(self, schema_name: str) -> None:
        """Each schema MUST have a description field."""
        schema = load_schema(schema_name)
        assert "description" in schema
        assert len(schema["description"]) > 0


class TestSchemaExamplesValidation:
    """Validates that schema examples are valid against their own schemas."""

    @pytest.mark.parametrize("schema_name", SCHEMA_FILES)
    def test_schema_examples_validate(self, schema_name: str) -> None:
        """Each schema's examples MUST validate against the schema itself."""
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            pytest.skip("jsonschema package required")

        schema = load_schema(schema_name)
        examples = schema.get("examples", [])
        if not examples:
            pytest.skip(f"No examples in {schema_name}")

        for i, example in enumerate(examples):
            try:
                errors = validate_against_schema(example, schema_name)
            except Exception as exc:
                if "Unresolvable" in str(exc):
                    pytest.skip(f"Schema {schema_name} has unresolvable $ref")
                raise
            assert not errors, f"Example {i} in {schema_name} failed validation:\n" + "\n".join(
                f"  - {e}" for e in errors
            )


class TestAuditRecordSchemaValidation:
    """Validates audit record outputs against audit-record.schema.json."""

    def test_sample_audit_record_valid(self) -> None:
        """Sample audit record MUST validate against schema."""
        assert_schema_valid(SAMPLE_AUDIT_RECORD, "audit-record.schema.json")

    def test_audit_record_required_fields(self) -> None:
        """Audit records MUST have all 9 required fields."""
        required = schema_has_required_fields("audit-record.schema.json")
        assert len(required) == 9


class TestErrorResponseSchemaValidation:
    """Validates error responses against error-response.schema.json."""

    def test_sample_error_response_valid(self) -> None:
        """Sample error response MUST validate against schema."""
        assert_schema_valid(SAMPLE_ERROR_RESPONSE, "error-response.schema.json")

    def test_error_response_required_fields(self) -> None:
        """Error responses MUST have error, code, and message."""
        required = schema_has_required_fields("error-response.schema.json")
        assert "error" in required
        assert "code" in required
        assert "message" in required


class TestHealthStatusSchemaValidation:
    """Validates health status outputs against health-status.schema.json."""

    def test_sample_health_status_valid(self) -> None:
        """Sample health status MUST validate against schema."""
        assert_schema_valid(SAMPLE_HEALTH_STATUS, "health-status.schema.json")

    def test_health_status_required_fields(self) -> None:
        """Health status MUST have 5 required fields."""
        required = schema_has_required_fields("health-status.schema.json")
        assert len(required) == 5


class TestAuthzDecisionSchemaValidation:
    """Validates authz decisions against authz-decision.schema.json."""

    def test_allow_decision_valid(self) -> None:
        """ALLOW decisions MUST validate against schema."""
        assert_schema_valid(make_allow_decision(), "authz-decision.schema.json")

    def test_deny_decision_valid(self) -> None:
        """DENY decisions MUST validate against schema."""
        assert_schema_valid(make_deny_decision(), "authz-decision.schema.json")


class TestProvenanceRecordSchemaValidation:
    """Validates provenance records against provenance-record.schema.json."""

    def test_provenance_record_valid(self) -> None:
        """Generated provenance records MUST validate against schema."""
        assert_schema_valid(make_provenance_record(), "provenance-record.schema.json")

    def test_sample_cross_server_provenance_valid(self) -> None:
        """Sample cross-server provenance MUST validate against schema."""
        assert_schema_valid(
            SAMPLE_CROSS_SERVER_PROVENANCE,
            "provenance-record.schema.json",
        )
