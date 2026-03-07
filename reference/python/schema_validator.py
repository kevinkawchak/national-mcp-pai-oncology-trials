"""NON-NORMATIVE Reference Implementation — JSON Schema Validator.

Provides utilities for validating MCP server inputs and outputs against
the 13 machine-readable JSON schemas defined in /schemas/.  This is a
thin wrapper around ``jsonschema`` that loads schemas from the
repository's ``schemas/`` directory.

See Also
--------
- schemas/  : 13 JSON Schema draft 2020-12 contracts
- spec/conformance.md : Schema validation requirements per level

References
----------
1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI
   Oncology Clinical Trial Systems*.
   DOI: 10.5281/zenodo.18869776
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End
   Framework for Robotic Systems in Clinical Trials*.
   DOI: 10.5281/zenodo.18445179
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning
   for Physical AI Oncology Trials*.
   DOI: 10.5281/zenodo.18840880
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, ValidationError  # noqa: F401
except ImportError:
    Draft202012Validator = None  # type: ignore[assignment,misc]
    ValidationError = None  # type: ignore[assignment,misc]

# Path to the repository's schema directory
_SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    """Load a JSON Schema file by short name.

    Parameters
    ----------
    name : str
        Schema short name, e.g. ``"audit-record"`` (without
        ``.schema.json`` suffix).

    Returns
    -------
    dict
        Parsed JSON Schema.

    Raises
    ------
    FileNotFoundError
        If the schema file does not exist.
    """
    path = _SCHEMA_DIR / f"{name}.schema.json"
    if not path.exists():
        msg = f"Schema not found: {path}"
        raise FileNotFoundError(msg)
    return json.loads(path.read_text(encoding="utf-8"))


def list_schemas() -> list[str]:
    """Return short names of all available schemas.

    Returns
    -------
    list[str]
        Sorted list of schema short names (e.g. ``["audit-record",
        "authz-decision", ...]``).
    """
    return sorted(p.name.replace(".schema.json", "") for p in _SCHEMA_DIR.glob("*.schema.json"))


def validate(instance: dict[str, Any], schema_name: str) -> list[str]:
    """Validate *instance* against the named schema.

    Parameters
    ----------
    instance : dict
        The JSON object to validate.
    schema_name : str
        Schema short name (e.g. ``"audit-record"``).

    Returns
    -------
    list[str]
        Empty list on success, otherwise a list of error messages.

    Raises
    ------
    RuntimeError
        If ``jsonschema`` is not installed.
    """
    try:
        from jsonschema import Draft202012Validator as _Validator
    except ImportError:
        msg = "jsonschema is required for validation. Install with: pip install jsonschema>=4.17"
        raise RuntimeError(msg)
    schema = load_schema(schema_name)
    validator = _Validator(schema)
    return [e.message for e in validator.iter_errors(instance)]


def validate_all_examples() -> dict[str, list[str]]:
    """Validate every schema's embedded ``examples`` against itself.

    Returns
    -------
    dict[str, list[str]]
        Mapping from schema name to a list of error messages (empty
        list means all examples pass).
    """
    results: dict[str, list[str]] = {}
    for name in list_schemas():
        schema = load_schema(name)
        errors: list[str] = []
        for example in schema.get("examples", []):
            errors.extend(validate(example, name))
        results[name] = errors
    return results
