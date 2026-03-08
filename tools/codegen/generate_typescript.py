#!/usr/bin/env python3
"""Generate TypeScript interfaces from JSON schemas.

Reads the JSON Schema files in the ``schemas/`` directory of the National
MCP-PAI Oncology Trials Standard and produces TypeScript interface definitions
suitable for use in client and server implementations.

Usage::

    python -m tools.codegen.generate_typescript --schemas-dir schemas/ --output-dir generated/ts/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from string import Template
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION = "0.1.0"

# Map JSON Schema types to TypeScript types
JSON_TO_TS_TYPE: dict[str, str] = {
    "string": "string",
    "integer": "number",
    "number": "number",
    "boolean": "boolean",
    "null": "null",
    "object": "Record<string, unknown>",
    "array": "unknown[]",
}

TS_FILE_HEADER_TEMPLATE = Template(
    "/**\n"
    " * Auto-generated TypeScript interfaces from National MCP-PAI Oncology Trials Standard.\n"
    " *\n"
    " * Schema source : ${schema_file}\n"
    " * Standard ver. : ${spec_version}\n"
    " * Generator     : tools.codegen.generate_typescript\n"
    " *\n"
    " * DO NOT EDIT — regenerate with:\n"
    " *     python -m tools.codegen.generate_typescript --schemas-dir schemas/\n"
    " */\n"
)

INDEX_HEADER = (
    "/**\n"
    " * Auto-generated barrel exports for National MCP-PAI Oncology Trials Standard.\n"
    " *\n"
    " * DO NOT EDIT — regenerate with:\n"
    " *     python -m tools.codegen.generate_typescript --schemas-dir schemas/\n"
    " */\n"
)


# ---------------------------------------------------------------------------
# Naming utilities
# ---------------------------------------------------------------------------


def _to_pascal_case(raw: str) -> str:
    """Convert a schema title or filename to PascalCase."""
    name = raw.replace(".schema.json", "").replace(".json", "")
    parts = re.split(r"[-_ ]+", name)
    return "".join(part.capitalize() for part in parts if part)


def _to_camel_case(raw: str) -> str:
    """Convert a property name to camelCase."""
    parts = re.split(r"[-_ ]+", raw)
    if not parts:
        return raw
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _to_kebab_case(raw: str) -> str:
    """Convert a name to kebab-case for file names."""
    name = raw.replace(".schema.json", "").replace(".json", "")
    # Already kebab-case in our schemas
    return name.lower()


# ---------------------------------------------------------------------------
# Type resolution
# ---------------------------------------------------------------------------


def _resolve_ts_type(prop_def: dict[str, Any]) -> str:
    """Resolve a JSON Schema property to a TypeScript type string."""
    if "enum" in prop_def:
        values = prop_def["enum"]
        return " | ".join(repr(v).replace("'", '"') for v in values)

    if "const" in prop_def:
        val = prop_def["const"]
        if isinstance(val, str):
            return f'"{val}"'
        return str(val).lower()

    json_type = prop_def.get("type", "unknown")

    if isinstance(json_type, list):
        ts_types = [JSON_TO_TS_TYPE.get(t, "unknown") for t in json_type]
        return " | ".join(ts_types)

    if json_type == "array":
        items = prop_def.get("items", {})
        item_type = _resolve_ts_type(items)
        return f"Array<{item_type}>"

    if json_type == "object":
        if "properties" in prop_def:
            return "Record<string, unknown>"
        return "Record<string, unknown>"

    return JSON_TO_TS_TYPE.get(json_type, "unknown")


# ---------------------------------------------------------------------------
# Interface generation
# ---------------------------------------------------------------------------


def _generate_interface(
    name: str,
    properties: dict[str, Any],
    required_fields: list[str],
    description: str,
    indent: int = 0,
) -> list[str]:
    """Generate a TypeScript interface definition.

    Args:
        name: Interface name in PascalCase.
        properties: JSON Schema properties dict.
        required_fields: List of required property names.
        description: JSDoc description.
        indent: Indentation level for nested interfaces.

    Returns:
        Lines of TypeScript source code.
    """
    prefix = "  " * indent
    lines: list[str] = []

    # JSDoc comment
    if description:
        lines.append(f"{prefix}/**")
        # Wrap long descriptions
        max_width = 90 - len(prefix) - 3
        words = description.split()
        current_line = f"{prefix} *"
        for word in words:
            if len(current_line) + len(word) + 1 > max_width + len(prefix) + 3:
                lines.append(current_line)
                current_line = f"{prefix} * {word}"
            else:
                current_line += f" {word}"
        if current_line.strip() != "*":
            lines.append(current_line)
        lines.append(f"{prefix} */")

    lines.append(f"{prefix}export interface {name} {{")

    required_set = set(required_fields)

    for prop_name, prop_def in properties.items():
        field_desc = prop_def.get("description", "")
        ts_name = _to_camel_case(prop_name) if "-" in prop_name else prop_name
        optional = "" if prop_name in required_set else "?"
        ts_type = _resolve_ts_type(prop_def)

        if field_desc:
            short_desc = field_desc[:100] + ("..." if len(field_desc) > 100 else "")
            lines.append(f"{prefix}  /** {short_desc} */")

        lines.append(f"{prefix}  {ts_name}{optional}: {ts_type};")

    lines.append(f"{prefix}}}")
    return lines


def _generate_nested_interfaces(
    parent_name: str,
    properties: dict[str, Any],
) -> list[list[str]]:
    """Generate interfaces for nested object properties.

    Returns a list of interface line-lists that should be emitted before the
    parent interface so that forward references are satisfied.
    """
    nested: list[list[str]] = []

    for prop_name, prop_def in properties.items():
        if prop_def.get("type") == "object" and "properties" in prop_def:
            nested_name = f"{parent_name}{_to_pascal_case(prop_name)}"
            nested_props = prop_def.get("properties", {})
            nested_required = prop_def.get("required", [])
            nested_desc = prop_def.get("description", f"Nested type for {prop_name}.")

            # Recurse for deeply nested objects
            nested.extend(_generate_nested_interfaces(nested_name, nested_props))

            nested.append(
                _generate_interface(nested_name, nested_props, nested_required, nested_desc)
            )

            # Also check array items
        if prop_def.get("type") == "array":
            items = prop_def.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                item_name = f"{parent_name}{_to_pascal_case(prop_name)}Item"
                item_props = items.get("properties", {})
                item_required = items.get("required", [])
                item_desc = items.get("description", f"Array item type for {prop_name}.")
                nested.append(_generate_interface(item_name, item_props, item_required, item_desc))

    return nested


def generate_typescript_from_schema(schema_path: Path) -> str:
    """Generate TypeScript interface code from a single JSON Schema file.

    Args:
        schema_path: Path to a ``.schema.json`` file.

    Returns:
        Complete TypeScript source code as a string.
    """
    with open(schema_path) as fh:
        schema = json.load(fh)

    title = schema.get("title", schema_path.stem)
    interface_name = _to_pascal_case(title)
    description = schema.get("description", "")
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    header = TS_FILE_HEADER_TEMPLATE.substitute(
        schema_file=schema_path.name,
        spec_version=SPEC_VERSION,
    )

    all_lines: list[str] = [header]

    # Generate nested interfaces first
    nested_blocks = _generate_nested_interfaces(interface_name, properties)
    for block in nested_blocks:
        all_lines.extend(block)
        all_lines.append("")

    # Generate top-level interface
    top_lines = _generate_interface(interface_name, properties, required_fields, description)
    all_lines.extend(top_lines)
    all_lines.append("")

    return "\n".join(all_lines)


# ---------------------------------------------------------------------------
# Batch generation
# ---------------------------------------------------------------------------


def generate_all(schemas_dir: Path, output_dir: Path) -> list[Path]:
    """Generate TypeScript interfaces for all schemas in a directory.

    Args:
        schemas_dir: Directory containing ``.schema.json`` files.
        output_dir: Directory to write generated ``.ts`` files.

    Returns:
        List of paths to generated files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    exports: list[str] = []

    schema_files = sorted(schemas_dir.glob("*.schema.json"))
    if not schema_files:
        print(f"WARNING: No .schema.json files found in {schemas_dir}")
        return generated

    for schema_file in schema_files:
        module_name = _to_kebab_case(schema_file.stem.replace(".schema", ""))
        try:
            source = generate_typescript_from_schema(schema_file)
            out_path = output_dir / f"{module_name}.ts"
            out_path.write_text(source)
            generated.append(out_path)
            exports.append(f'export * from "./{module_name}";')
            interface_name = _to_pascal_case(schema_file.stem.replace(".schema", ""))
            print(f"  Generated: {out_path.name} ({interface_name})")
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"  ERROR: {schema_file.name}: {exc}")

    # Generate index.ts barrel export
    index_content = INDEX_HEADER + "\n" + "\n".join(exports) + "\n"
    index_path = output_dir / "index.ts"
    index_path.write_text(index_content)
    generated.append(index_path)

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
    """CLI entry point for TypeScript interface generation."""
    parser = argparse.ArgumentParser(
        description=("Generate TypeScript interfaces from MCP-PAI Oncology Trials JSON schemas."),
    )
    parser.add_argument(
        "--schemas-dir",
        default=str(_repo_root() / "schemas"),
        help="Path to schemas directory",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_repo_root() / "generated" / "typescript"),
        help="Output directory for generated TypeScript files",
    )

    args = parser.parse_args(argv)
    schemas_dir = Path(args.schemas_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    print("Generating TypeScript interfaces")
    print(f"  Schemas: {schemas_dir}")
    print(f"  Output:  {output_dir}")

    generated = generate_all(schemas_dir, output_dir)
    print(f"\nGenerated {len(generated)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
