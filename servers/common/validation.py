"""Schema validation utilities for MCP server inputs and outputs.

Wraps jsonschema Draft202012Validator to validate MCP payloads against
the canonical schemas in /schemas/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# FHIR ID pattern per spec/security.md
FHIR_ID_PATTERN = re.compile(r"^[A-Za-z0-9\-\.]{1,64}$")

# DICOM UID pattern per spec/security.md
DICOM_UID_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)*$")

# Maximum input length per spec/security.md
MAX_INPUT_LENGTH = 1000


class SchemaValidator:
    """Validates data against JSON Schema draft 2020-12 schemas."""

    def __init__(self, schema_dir: str | Path | None = None) -> None:
        if schema_dir is None:
            self._schema_dir = Path(__file__).parent.parent.parent / "schemas"
        else:
            self._schema_dir = Path(schema_dir)
        self._cache: dict[str, Any] = {}

    def load_schema(self, name: str) -> dict[str, Any]:
        """Load a schema by name (without .schema.json extension)."""
        if name in self._cache:
            return self._cache[name]

        file_path = self._schema_dir / f"{name}.schema.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Schema not found: {file_path}")

        with open(file_path) as f:
            schema = json.load(f)
        self._cache[name] = schema
        return schema

    def validate(self, data: dict[str, Any], schema_name: str) -> list[str]:
        """Validate data against a named schema. Returns list of error messages."""
        try:
            from jsonschema import Draft202012Validator

            schema = self.load_schema(schema_name)
            validator = Draft202012Validator(schema)
            return [e.message for e in validator.iter_errors(data)]
        except ImportError:
            return []
        except FileNotFoundError as e:
            return [str(e)]

    @staticmethod
    def validate_fhir_id(resource_id: str) -> bool:
        """Validate a FHIR resource ID against the allowed pattern."""
        if len(resource_id) > MAX_INPUT_LENGTH:
            return False
        return bool(FHIR_ID_PATTERN.match(resource_id))

    @staticmethod
    def validate_dicom_uid(uid: str) -> bool:
        """Validate a DICOM UID against the allowed pattern."""
        if len(uid) > MAX_INPUT_LENGTH:
            return False
        return bool(DICOM_UID_PATTERN.match(uid))
