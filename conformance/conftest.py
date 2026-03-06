"""Shared fixtures and schema validation helpers for the conformance test suite.

Provides pytest fixtures that load JSON schemas from /schemas/ and helper
functions for validating MCP server outputs against the National MCP-PAI
Oncology Trials Standard.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# Resolve the repository root and schemas directory
REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"

# All schema files defined by the standard (v0.2.0+)
SCHEMA_FILES = [
    "capability-descriptor.schema.json",
    "robot-capability-profile.schema.json",
    "site-capability-profile.schema.json",
    "task-order.schema.json",
    "audit-record.schema.json",
    "provenance-record.schema.json",
    "consent-status.schema.json",
    "authz-decision.schema.json",
    "dicom-query.schema.json",
    "fhir-read.schema.json",
    "fhir-search.schema.json",
    "error-response.schema.json",
    "health-status.schema.json",
]


def load_schema(schema_name: str) -> dict:
    """Load a JSON schema file from the /schemas/ directory.

    Args:
        schema_name: Filename of the schema (e.g., 'audit-record.schema.json').

    Returns:
        Parsed JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If the schema file does not exist.
    """
    schema_path = SCHEMAS_DIR / schema_name
    if not schema_path.exists():
        msg = f"Schema not found: {schema_path}"
        raise FileNotFoundError(msg)
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_against_schema(instance: dict, schema_name: str) -> list[str]:
    """Validate an instance against a JSON schema and return all errors.

    Uses jsonschema for validation against JSON Schema draft 2020-12.

    Args:
        instance: The data to validate.
        schema_name: Filename of the schema to validate against.

    Returns:
        List of validation error messages (empty if valid).
    """
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema package required for schema validation tests")

    schema = load_schema(schema_name)
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(instance)]


def assert_schema_valid(instance: dict, schema_name: str) -> None:
    """Assert that an instance is valid against a JSON schema.

    Args:
        instance: The data to validate.
        schema_name: Filename of the schema to validate against.

    Raises:
        AssertionError: If validation fails, with all error messages.
    """
    errors = validate_against_schema(instance, schema_name)
    assert not errors, f"Schema validation failed for {schema_name}:\n" + "\n".join(
        f"  - {e}" for e in errors
    )


def schema_has_required_fields(schema_name: str) -> list[str]:
    """Return the list of required fields from a schema.

    Args:
        schema_name: Filename of the schema.

    Returns:
        List of required field names.
    """
    schema = load_schema(schema_name)
    return schema.get("required", [])


def all_schema_names() -> list[str]:
    """Return all schema filenames defined by the standard."""
    return SCHEMA_FILES.copy()


# --- Pytest Fixtures ---


@pytest.fixture()
def schemas_dir() -> Path:
    """Return the path to the /schemas/ directory."""
    return SCHEMAS_DIR


@pytest.fixture()
def repo_root() -> Path:
    """Return the repository root path."""
    return REPO_ROOT


@pytest.fixture()
def all_schemas() -> dict[str, dict]:
    """Load all 13 JSON schemas as a dictionary keyed by filename."""
    return {name: load_schema(name) for name in SCHEMA_FILES}


@pytest.fixture()
def audit_record_schema() -> dict:
    """Load the audit-record schema."""
    return load_schema("audit-record.schema.json")


@pytest.fixture()
def error_response_schema() -> dict:
    """Load the error-response schema."""
    return load_schema("error-response.schema.json")


@pytest.fixture()
def health_status_schema() -> dict:
    """Load the health-status schema."""
    return load_schema("health-status.schema.json")


@pytest.fixture()
def authz_decision_schema() -> dict:
    """Load the authz-decision schema."""
    return load_schema("authz-decision.schema.json")


@pytest.fixture()
def fhir_read_schema() -> dict:
    """Load the fhir-read schema."""
    return load_schema("fhir-read.schema.json")


@pytest.fixture()
def dicom_query_schema() -> dict:
    """Load the dicom-query schema."""
    return load_schema("dicom-query.schema.json")


@pytest.fixture()
def provenance_record_schema() -> dict:
    """Load the provenance-record schema."""
    return load_schema("provenance-record.schema.json")


@pytest.fixture(params=SCHEMA_FILES)
def each_schema(request: Any) -> tuple[str, dict]:
    """Parametrized fixture yielding (schema_name, schema_dict) for every schema."""
    name = request.param
    return name, load_schema(name)
