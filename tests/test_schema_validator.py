"""Unit tests for reference.python.schema_validator module."""

from __future__ import annotations

import pytest

from reference.python.schema_validator import (
    list_schemas,
    load_schema,
    validate,
)


class TestLoadSchema:
    def test_load_existing_schema(self):
        schema = load_schema("audit-record")
        assert "$id" in schema or "title" in schema

    def test_load_schema_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_schema("nonexistent-schema-xyz")


class TestListSchemas:
    def test_returns_thirteen_schemas(self):
        schemas = list_schemas()
        assert len(schemas) == 13

    def test_schemas_are_sorted(self):
        schemas = list_schemas()
        assert schemas == sorted(schemas)


class TestValidate:
    def test_valid_instance(self):
        schema = load_schema("error-response")
        instance = schema["examples"][0]
        errors = validate(instance, "error-response")
        assert errors == []

    def test_invalid_instance(self):
        errors = validate({"invalid": True}, "error-response")
        assert len(errors) > 0
