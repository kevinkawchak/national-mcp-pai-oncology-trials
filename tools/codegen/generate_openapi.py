#!/usr/bin/env python3
"""Generate OpenAPI 3.0 specifications from MCP tool contracts.

Parses the tool contracts defined in ``spec/tool-contracts.md`` and the JSON
schemas in ``schemas/`` to produce OpenAPI 3.0 YAML specifications for each
MCP server, enabling REST gateway generation and documentation.

Usage::

    python -m tools.codegen.generate_openapi --spec-dir spec/ --output-dir generated/openapi/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from string import Template
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION = "0.1.0"

OPENAPI_VERSION = "3.0.3"

YAML_HEADER_TEMPLATE = Template(
    "# Auto-generated OpenAPI specification\n"
    "# Server      : ${server_name}\n"
    "# Standard    : National MCP-PAI Oncology Trials v${spec_version}\n"
    "# Generator   : tools.codegen.generate_openapi\n"
    "#\n"
    "# DO NOT EDIT — regenerate with:\n"
    "#     python -m tools.codegen.generate_openapi --spec-dir spec/\n"
)

# Tool contracts extracted from the specification.  These are the canonical
# definitions for all 23 tools across 5 servers.
TOOL_CONTRACTS: dict[str, list[dict[str, Any]]] = {
    "trialmcp-authz": [
        {
            "name": "authz_evaluate",
            "summary": "Evaluate an access request against the policy engine",
            "parameters": [
                {"name": "role", "type": "string", "required": True},
                {"name": "server", "type": "string", "required": True},
                {"name": "tool", "type": "string", "required": True},
            ],
            "response_fields": {
                "allowed": "boolean",
                "matching_rules": "array",
                "effect": "string",
            },
            "errors": ["INVALID_INPUT", "INTERNAL_ERROR"],
        },
        {
            "name": "authz_issue_token",
            "summary": "Issue a scoped session token for an authenticated actor",
            "parameters": [
                {"name": "role", "type": "string", "required": True},
                {"name": "subject", "type": "string", "required": True},
                {"name": "duration_seconds", "type": "integer", "required": False},
            ],
            "response_fields": {
                "token": "string",
                "expires_at": "string",
                "role": "string",
                "subject": "string",
            },
            "errors": ["AUTHZ_DENIED", "INVALID_INPUT", "INTERNAL_ERROR"],
        },
        {
            "name": "authz_validate_token",
            "summary": "Validate a previously issued token",
            "parameters": [
                {"name": "token", "type": "string", "required": True},
            ],
            "response_fields": {
                "valid": "boolean",
                "role": "string",
                "subject": "string",
                "expires_at": "string",
            },
            "errors": ["TOKEN_EXPIRED", "TOKEN_REVOKED", "INVALID_INPUT"],
        },
        {
            "name": "authz_list_policies",
            "summary": "Return all active authorization policies",
            "parameters": [
                {"name": "role_filter", "type": "string", "required": False},
            ],
            "response_fields": {"policies": "array"},
            "errors": ["AUTHZ_DENIED", "INTERNAL_ERROR"],
        },
        {
            "name": "authz_revoke_token",
            "summary": "Revoke an active token",
            "parameters": [
                {"name": "token", "type": "string", "required": True},
            ],
            "response_fields": {"revoked": "boolean", "token_hash": "string"},
            "errors": ["NOT_FOUND", "AUTHZ_DENIED", "INTERNAL_ERROR"],
        },
    ],
    "trialmcp-fhir": [
        {
            "name": "fhir_read",
            "summary": "Read a single FHIR R4 resource by type and ID",
            "parameters": [
                {"name": "resource_type", "type": "string", "required": True},
                {"name": "resource_id", "type": "string", "required": True},
            ],
            "response_fields": {"resource": "object"},
            "errors": ["NOT_FOUND", "VALIDATION_FAILED", "AUTHZ_DENIED"],
        },
        {
            "name": "fhir_search",
            "summary": "Search FHIR R4 resources with optional filters",
            "parameters": [
                {"name": "resource_type", "type": "string", "required": True},
                {"name": "filters", "type": "object", "required": False},
                {"name": "max_results", "type": "integer", "required": False},
            ],
            "response_fields": {"results": "array", "total": "integer"},
            "errors": ["VALIDATION_FAILED", "AUTHZ_DENIED", "INTERNAL_ERROR"],
        },
        {
            "name": "fhir_patient_lookup",
            "summary": "Return pseudonymized patient demographics",
            "parameters": [
                {"name": "patient_id", "type": "string", "required": True},
            ],
            "response_fields": {
                "pseudonym": "string",
                "enrollment_status": "string",
                "birth_year": "integer",
                "gender": "string",
            },
            "errors": ["NOT_FOUND", "VALIDATION_FAILED", "AUTHZ_DENIED"],
        },
        {
            "name": "fhir_study_status",
            "summary": "Return ResearchStudy summary with enrollment counts",
            "parameters": [
                {"name": "study_id", "type": "string", "required": True},
            ],
            "response_fields": {
                "study_id": "string",
                "title": "string",
                "status": "string",
                "enrollment_count": "integer",
                "phase": "string",
            },
            "errors": ["NOT_FOUND", "VALIDATION_FAILED"],
        },
    ],
    "trialmcp-dicom": [
        {
            "name": "dicom_query",
            "summary": "Query DICOM studies with role-based access control",
            "parameters": [
                {"name": "query_level", "type": "string", "required": True},
                {"name": "filters", "type": "object", "required": False},
                {"name": "caller_role", "type": "string", "required": True},
            ],
            "response_fields": {
                "results": "array",
                "total": "integer",
                "query_level": "string",
            },
            "errors": ["AUTHZ_DENIED", "VALIDATION_FAILED", "INTERNAL_ERROR"],
        },
        {
            "name": "dicom_retrieve_pointer",
            "summary": "Generate a time-limited retrieval token for a DICOM study",
            "parameters": [
                {"name": "study_instance_uid", "type": "string", "required": True},
                {"name": "caller_role", "type": "string", "required": True},
            ],
            "response_fields": {
                "retrieval_token": "string",
                "expires_at": "string",
                "study_instance_uid": "string",
            },
            "errors": ["AUTHZ_DENIED", "VALIDATION_FAILED", "NOT_FOUND"],
        },
        {
            "name": "dicom_study_metadata",
            "summary": "Return metadata for a DICOM study",
            "parameters": [
                {"name": "study_instance_uid", "type": "string", "required": True},
                {"name": "caller_role", "type": "string", "required": True},
            ],
            "response_fields": {
                "study_instance_uid": "string",
                "modalities": "array",
                "series_count": "integer",
                "study_date": "string",
                "description": "string",
            },
            "errors": ["AUTHZ_DENIED", "VALIDATION_FAILED", "NOT_FOUND"],
        },
        {
            "name": "dicom_recist_measurements",
            "summary": "Return RECIST 1.1 tumor measurements for a study",
            "parameters": [
                {"name": "study_instance_uid", "type": "string", "required": True},
            ],
            "response_fields": {
                "study_instance_uid": "string",
                "measurements": "array",
                "overall_response": "string",
            },
            "errors": ["NOT_FOUND", "VALIDATION_FAILED"],
        },
    ],
    "trialmcp-ledger": [
        {
            "name": "ledger_append",
            "summary": "Append a new audit record to the hash-chained ledger",
            "parameters": [
                {"name": "server", "type": "string", "required": True},
                {"name": "tool", "type": "string", "required": True},
                {"name": "caller", "type": "string", "required": True},
                {"name": "parameters", "type": "object", "required": True},
                {"name": "result_summary", "type": "string", "required": True},
            ],
            "response_fields": {
                "audit_id": "string",
                "hash": "string",
                "previous_hash": "string",
                "timestamp": "string",
            },
            "errors": ["AUTHZ_DENIED", "INVALID_INPUT", "INTERNAL_ERROR"],
        },
        {
            "name": "ledger_verify",
            "summary": "Verify the integrity of the audit chain",
            "parameters": [
                {"name": "start_index", "type": "integer", "required": False},
                {"name": "end_index", "type": "integer", "required": False},
            ],
            "response_fields": {
                "valid": "boolean",
                "records_checked": "integer",
                "first_invalid_index": "integer",
                "genesis_valid": "boolean",
            },
            "errors": ["INTERNAL_ERROR"],
        },
        {
            "name": "ledger_query",
            "summary": "Query audit records by filter criteria",
            "parameters": [
                {"name": "server", "type": "string", "required": False},
                {"name": "tool", "type": "string", "required": False},
                {"name": "caller", "type": "string", "required": False},
                {"name": "start_time", "type": "string", "required": False},
                {"name": "end_time", "type": "string", "required": False},
            ],
            "response_fields": {"records": "array", "total": "integer"},
            "errors": ["AUTHZ_DENIED", "INVALID_INPUT"],
        },
        {
            "name": "ledger_replay",
            "summary": "Generate a sequential replay trace for compliance review",
            "parameters": [
                {"name": "start_time", "type": "string", "required": False},
                {"name": "end_time", "type": "string", "required": False},
                {"name": "caller", "type": "string", "required": False},
            ],
            "response_fields": {
                "trace": "array",
                "total": "integer",
                "duration": "string",
            },
            "errors": ["AUTHZ_DENIED", "INTERNAL_ERROR"],
        },
        {
            "name": "ledger_chain_status",
            "summary": "Report the health and statistics of the audit chain",
            "parameters": [],
            "response_fields": {
                "total_records": "integer",
                "chain_valid": "boolean",
                "genesis_hash": "string",
                "latest_hash": "string",
                "latest_timestamp": "string",
            },
            "errors": ["INTERNAL_ERROR"],
        },
    ],
    "trialmcp-provenance": [
        {
            "name": "provenance_register_source",
            "summary": "Register a new data source in the provenance graph",
            "parameters": [
                {"name": "source_type", "type": "string", "required": True},
                {"name": "origin_server", "type": "string", "required": True},
                {"name": "description", "type": "string", "required": True},
                {"name": "metadata", "type": "object", "required": False},
            ],
            "response_fields": {"source_id": "string", "registered_at": "string"},
            "errors": ["AUTHZ_DENIED", "INVALID_INPUT", "INTERNAL_ERROR"],
        },
        {
            "name": "provenance_record_access",
            "summary": "Record a data access event in the provenance graph",
            "parameters": [
                {"name": "source_id", "type": "string", "required": True},
                {"name": "action", "type": "string", "required": True},
                {"name": "actor_id", "type": "string", "required": True},
                {"name": "actor_role", "type": "string", "required": True},
                {"name": "tool_call", "type": "string", "required": True},
                {"name": "input_data", "type": "string", "required": False},
                {"name": "output_data", "type": "string", "required": False},
            ],
            "response_fields": {
                "record_id": "string",
                "input_hash": "string",
                "output_hash": "string",
                "timestamp": "string",
            },
            "errors": ["AUTHZ_DENIED", "NOT_FOUND", "INVALID_INPUT"],
        },
        {
            "name": "provenance_get_lineage",
            "summary": "Retrieve the full access history for a data source",
            "parameters": [
                {"name": "source_id", "type": "string", "required": True},
                {"name": "direction", "type": "string", "required": False},
            ],
            "response_fields": {
                "source_id": "string",
                "lineage": "array",
                "total": "integer",
            },
            "errors": ["NOT_FOUND", "INTERNAL_ERROR"],
        },
        {
            "name": "provenance_get_actor_history",
            "summary": "Return all operations performed by a specific actor",
            "parameters": [
                {"name": "actor_id", "type": "string", "required": True},
                {"name": "start_time", "type": "string", "required": False},
                {"name": "end_time", "type": "string", "required": False},
            ],
            "response_fields": {
                "actor_id": "string",
                "records": "array",
                "total": "integer",
            },
            "errors": ["AUTHZ_DENIED", "NOT_FOUND"],
        },
        {
            "name": "provenance_verify_integrity",
            "summary": "Verify data integrity by comparing fingerprints",
            "parameters": [
                {"name": "source_id", "type": "string", "required": True},
                {"name": "data", "type": "string", "required": True},
            ],
            "response_fields": {
                "source_id": "string",
                "verified": "boolean",
                "expected_hash": "string",
                "actual_hash": "string",
            },
            "errors": ["NOT_FOUND", "INTERNAL_ERROR"],
        },
    ],
}

# Map standard error codes to HTTP status codes
ERROR_HTTP_STATUS: dict[str, int] = {
    "INVALID_INPUT": 400,
    "VALIDATION_FAILED": 400,
    "AUTHZ_DENIED": 403,
    "TOKEN_EXPIRED": 401,
    "TOKEN_REVOKED": 401,
    "NOT_FOUND": 404,
    "INTERNAL_ERROR": 500,
}

# Map JSON Schema types to OpenAPI schema types
TYPE_TO_OPENAPI: dict[str, str] = {
    "string": "string",
    "integer": "integer",
    "number": "number",
    "boolean": "boolean",
    "array": "array",
    "object": "object",
}


# ---------------------------------------------------------------------------
# YAML generation helpers (no PyYAML dependency)
# ---------------------------------------------------------------------------


def _yaml_scalar(value: Any, indent: int = 0) -> str:
    """Render a scalar value as a YAML string."""
    prefix = "  " * indent
    if isinstance(value, bool):
        return f"{prefix}{'true' if value else 'false'}"
    if isinstance(value, int):
        return f"{prefix}{value}"
    if isinstance(value, str):
        if any(c in value for c in ":{}\n[]#&*!|>'\"%@`"):
            escaped = value.replace('"', '\\"')
            return f'{prefix}"{escaped}"'
        return f"{prefix}{value}"
    return f"{prefix}{value}"


def _build_parameter_schema(param: dict[str, Any]) -> dict[str, str]:
    """Build an OpenAPI schema object for a tool parameter."""
    openapi_type = TYPE_TO_OPENAPI.get(param["type"], "string")
    schema: dict[str, str] = {"type": openapi_type}
    return schema


def _generate_path_yaml(tool: dict[str, Any], indent: int = 2) -> list[str]:
    """Generate YAML lines for a single tool path entry."""
    pad = "  " * indent
    lines: list[str] = []
    tool_name = tool["name"]
    summary = tool["summary"]

    lines.append(f"{pad}post:")
    lines.append(f"{pad}  summary: {summary}")
    lines.append(f"{pad}  operationId: {tool_name}")
    lines.append(f"{pad}  tags:")
    lines.append(f"{pad}    - {tool_name.split('_')[0]}")

    # Request body
    params = tool.get("parameters", [])
    if params:
        lines.append(f"{pad}  requestBody:")
        lines.append(f"{pad}    required: true")
        lines.append(f"{pad}    content:")
        lines.append(f"{pad}      application/json:")
        lines.append(f"{pad}        schema:")
        lines.append(f"{pad}          type: object")

        required_params = [p["name"] for p in params if p.get("required")]
        if required_params:
            lines.append(f"{pad}          required:")
            for rp in required_params:
                lines.append(f"{pad}            - {rp}")

        lines.append(f"{pad}          properties:")
        for p in params:
            p_type = TYPE_TO_OPENAPI.get(p["type"], "string")
            lines.append(f"{pad}            {p['name']}:")
            lines.append(f"{pad}              type: {p_type}")

    # Responses
    lines.append(f"{pad}  responses:")
    lines.append(f'{pad}    "200":')
    lines.append(f"{pad}      description: Successful response")
    lines.append(f"{pad}      content:")
    lines.append(f"{pad}        application/json:")
    lines.append(f"{pad}          schema:")
    lines.append(f"{pad}            type: object")

    response_fields = tool.get("response_fields", {})
    if response_fields:
        lines.append(f"{pad}            properties:")
        for field_name, field_type in response_fields.items():
            oa_type = TYPE_TO_OPENAPI.get(field_type, "string")
            lines.append(f"{pad}              {field_name}:")
            lines.append(f"{pad}                type: {oa_type}")

    # Error responses
    errors = tool.get("errors", [])
    seen_status: set[int] = set()
    for error_code in errors:
        status = ERROR_HTTP_STATUS.get(error_code, 500)
        if status in seen_status:
            continue
        seen_status.add(status)
        lines.append(f'    "{status}":')
        lines.append(f"      description: {error_code}")
        lines.append("      content:")
        lines.append("        application/json:")
        lines.append("          schema:")
        lines.append('            $ref: "#/components/schemas/ErrorResponse"')

    return lines


# ---------------------------------------------------------------------------
# Full spec generation
# ---------------------------------------------------------------------------


def generate_openapi_for_server(server_name: str) -> str:
    """Generate a complete OpenAPI 3.0 YAML spec for a single MCP server.

    Args:
        server_name: One of the five MCP server identifiers.

    Returns:
        OpenAPI YAML content as a string.
    """
    tools = TOOL_CONTRACTS.get(server_name, [])
    if not tools:
        raise ValueError(f"Unknown server: {server_name}")

    header = YAML_HEADER_TEMPLATE.substitute(
        server_name=server_name,
        spec_version=SPEC_VERSION,
    )

    lines: list[str] = [header]

    # Info section
    lines.extend(
        [
            f"openapi: {OPENAPI_VERSION}",
            "",
            "info:",
            f"  title: {server_name} API",
            f"  version: {SPEC_VERSION}",
            "  description: >-",
            f"    REST gateway for the {server_name} MCP server as defined by",
            "    the National MCP-PAI Oncology Trials Standard.",
            "  contact:",
            "    name: National MCP-PAI Oncology Trials Working Group",
            "  license:",
            "    name: MIT",
            "",
            "servers:",
            "  - url: http://localhost:8000",
            f"    description: Local development {server_name}",
            "",
            "paths:",
        ]
    )

    # Generate paths for each tool
    for tool in tools:
        tool_path = "/" + tool["name"].replace("_", "/")
        lines.append(f"  {tool_path}:")
        lines.extend(_generate_path_yaml(tool, indent=2))
        lines.append("")

    # Components section with shared error schema
    lines.extend(
        [
            "components:",
            "  schemas:",
            "    ErrorResponse:",
            "      type: object",
            "      required:",
            "        - error_code",
            "        - message",
            "      properties:",
            "        error_code:",
            "          type: string",
            "          description: Standard error code from the MCP-PAI error registry",
            "        message:",
            "          type: string",
            "          description: Human-readable error description",
            "        details:",
            "          type: object",
            "          description: Additional error context",
            "",
            "  securitySchemes:",
            "    BearerAuth:",
            "      type: http",
            "      scheme: bearer",
            "      description: MCP session token issued by trialmcp-authz",
            "",
            "security:",
            "  - BearerAuth: []",
            "",
        ]
    )

    return "\n".join(lines)


def generate_all(output_dir: Path) -> list[Path]:
    """Generate OpenAPI specs for all MCP servers.

    Args:
        output_dir: Directory to write generated YAML files.

    Returns:
        List of paths to generated files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for server_name in TOOL_CONTRACTS:
        try:
            spec = generate_openapi_for_server(server_name)
            filename = server_name.replace("-", "_") + "_openapi.yaml"
            out_path = output_dir / filename
            out_path.write_text(spec)
            generated.append(out_path)

            tool_count = len(TOOL_CONTRACTS[server_name])
            print(f"  Generated: {filename} ({tool_count} operations)")
        except (ValueError, KeyError) as exc:
            print(f"  ERROR: {server_name}: {exc}")

    return generated


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """Resolve the repository root."""
    candidate = Path(__file__).resolve().parent.parent.parent
    if (candidate / "pyproject.toml").exists():
        return candidate
    return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for OpenAPI specification generation."""
    parser = argparse.ArgumentParser(
        description=("Generate OpenAPI 3.0 specs from MCP-PAI Oncology Trials tool contracts."),
    )
    parser.add_argument(
        "--output-dir",
        default=str(_repo_root() / "generated" / "openapi"),
        help="Output directory for generated OpenAPI YAML files",
    )
    parser.add_argument(
        "--server",
        default=None,
        choices=list(TOOL_CONTRACTS.keys()),
        help="Generate for a specific server only (default: all)",
    )

    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir).resolve()

    print("Generating OpenAPI 3.0 specifications")
    print(f"  Output: {output_dir}")

    if args.server:
        output_dir.mkdir(parents=True, exist_ok=True)
        spec = generate_openapi_for_server(args.server)
        filename = args.server.replace("-", "_") + "_openapi.yaml"
        out_path = output_dir / filename
        out_path.write_text(spec)
        print(f"  Generated: {out_path}")
        generated = [out_path]
    else:
        generated = generate_all(output_dir)

    print(f"\nGenerated {len(generated)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
