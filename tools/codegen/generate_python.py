#!/usr/bin/env python3
"""Generate Python dataclass and Pydantic models from JSON schemas.

Reads the JSON Schema files in the ``schemas/`` directory of the National
MCP-PAI Oncology Trials Standard and produces typed Python model classes
suitable for use in server implementations.

Usage::

    python -m tools.codegen.generate_python --schemas-dir schemas/ --output-dir generated/
    python -m tools.codegen.generate_python --style pydantic --schemas-dir schemas/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path
from string import Template
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION = "0.1.0"

# Map JSON Schema types to Python type annotations
JSON_TYPE_MAP: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "list[Any]",
    "object": "dict[str, Any]",
    "null": "None",
}

# Template for the generated module header
MODULE_HEADER_TEMPLATE = Template(
    '"""Auto-generated models from National MCP-PAI Oncology Trials Standard.\n'
    "\n"
    "Schema source : ${schema_file}\n"
    "Standard ver. : ${spec_version}\n"
    "Generator     : tools.codegen.generate_python\n"
    "Style         : ${style}\n"
    "\n"
    "DO NOT EDIT — regenerate with:\n"
    "    python -m tools.codegen.generate_python --schemas-dir schemas/\n"
    '"""\n'
    "\n"
    "from __future__ import annotations\n"
)

DATACLASS_IMPORTS = "\nfrom dataclasses import dataclass, field\nfrom typing import Any\n\n"

PYDANTIC_IMPORTS = "\nfrom typing import Any\n\nfrom pydantic import BaseModel, Field\n\n"


# ---------------------------------------------------------------------------
# Schema parsing utilities
# ---------------------------------------------------------------------------


def _sanitize_class_name(raw: str) -> str:
    """Convert a schema title or filename into a valid PascalCase class name."""
    # Remove file extensions and schema suffixes
    name = raw.replace(".schema.json", "").replace(".json", "")
    # Convert kebab-case / snake_case to PascalCase
    parts = re.split(r"[-_ ]+", name)
    return "".join(part.capitalize() for part in parts if part)


def _sanitize_field_name(raw: str) -> str:
    """Convert a JSON property name to a valid Python identifier."""
    name = raw.replace("-", "_").replace(" ", "_")
    # Prefix with underscore if it starts with a digit
    if name and name[0].isdigit():
        name = f"f_{name}"
    # Avoid Python keywords
    if name in {"class", "type", "import", "from", "return", "pass", "def", "if", "else"}:
        name = f"{name}_"
    return name


def _resolve_python_type(prop_def: dict[str, Any], required: bool) -> str:
    """Resolve a JSON Schema property definition to a Python type hint."""
    if "enum" in prop_def:
        # Use a Literal type for enums
        values = prop_def["enum"]
        literal_args = ", ".join(repr(v) for v in values)
        base_type = f"Literal[{literal_args}]"
    elif "const" in prop_def:
        base_type = f"Literal[{repr(prop_def['const'])}]"
    elif prop_def.get("type") == "array":
        items = prop_def.get("items", {})
        item_type = _resolve_python_type(items, required=True)
        base_type = f"list[{item_type}]"
    elif prop_def.get("type") == "object":
        base_type = "dict[str, Any]"
    else:
        json_type = prop_def.get("type", "string")
        if isinstance(json_type, list):
            # Union type
            py_types = [JSON_TYPE_MAP.get(t, "Any") for t in json_type]
            base_type = " | ".join(py_types)
        else:
            base_type = JSON_TYPE_MAP.get(json_type, "Any")

    if not required:
        base_type = f"{base_type} | None"

    return base_type


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------


def _generate_dataclass(
    class_name: str,
    properties: dict[str, Any],
    required_fields: list[str],
    description: str,
) -> str:
    """Generate a Python dataclass from schema properties."""
    lines: list[str] = []
    lines.append("@dataclass")
    lines.append(f"class {class_name}:")

    # Docstring
    doc = description or f"Auto-generated model for {class_name}."
    wrapped = textwrap.fill(doc, width=96)
    lines.append(f'    """{wrapped}"""')
    lines.append("")

    if not properties:
        lines.append("    pass")
        lines.append("")
        return "\n".join(lines)

    # Sort fields: required first, then optional
    required_set = set(required_fields)
    sorted_props = sorted(properties.items(), key=lambda kv: kv[0] not in required_set)

    for prop_name, prop_def in sorted_props:
        is_required = prop_name in required_set
        field_name = _sanitize_field_name(prop_name)
        py_type = _resolve_python_type(prop_def, required=is_required)
        field_desc = prop_def.get("description", "")

        if is_required:
            lines.append(f"    {field_name}: {py_type}")
        else:
            lines.append(f"    {field_name}: {py_type} = field(default=None)")

        if field_desc:
            comment = textwrap.shorten(field_desc, width=80, placeholder="...")
            lines.append(f'    """{comment}"""')
        lines.append("")

    return "\n".join(lines)


def _generate_pydantic_model(
    class_name: str,
    properties: dict[str, Any],
    required_fields: list[str],
    description: str,
) -> str:
    """Generate a Pydantic BaseModel from schema properties."""
    lines: list[str] = []
    lines.append(f"class {class_name}(BaseModel):")

    doc = description or f"Auto-generated Pydantic model for {class_name}."
    wrapped = textwrap.fill(doc, width=96)
    lines.append(f'    """{wrapped}"""')
    lines.append("")

    if not properties:
        lines.append("    pass")
        lines.append("")
        return "\n".join(lines)

    required_set = set(required_fields)
    sorted_props = sorted(properties.items(), key=lambda kv: kv[0] not in required_set)

    for prop_name, prop_def in sorted_props:
        is_required = prop_name in required_set
        field_name = _sanitize_field_name(prop_name)
        py_type = _resolve_python_type(prop_def, required=is_required)
        field_desc = prop_def.get("description", "")

        if is_required:
            if field_desc:
                escaped = field_desc.replace('"', '\\"')
                lines.append(f'    {field_name}: {py_type} = Field(..., description="{escaped}")')
            else:
                lines.append(f"    {field_name}: {py_type}")
        else:
            if field_desc:
                escaped = field_desc.replace('"', '\\"')
                lines.append(
                    f'    {field_name}: {py_type} = Field(default=None, description="{escaped}")'
                )
            else:
                lines.append(f"    {field_name}: {py_type} = None")
        lines.append("")

    return "\n".join(lines)


def generate_models_from_schema(
    schema_path: Path,
    style: str = "dataclass",
) -> str:
    """Generate Python model code from a single JSON Schema file.

    Args:
        schema_path: Path to a ``.schema.json`` file.
        style: Either ``"dataclass"`` or ``"pydantic"``.

    Returns:
        Complete Python module source code as a string.
    """
    with open(schema_path) as fh:
        schema = json.load(fh)

    title = schema.get("title", schema_path.stem)
    class_name = _sanitize_class_name(title)
    description = schema.get("description", "")

    # Build module header
    header = MODULE_HEADER_TEMPLATE.substitute(
        schema_file=schema_path.name,
        spec_version=SPEC_VERSION,
        style=style,
    )

    uses_literal = False
    needs_literal_check = json.dumps(schema)
    if '"enum"' in needs_literal_check or '"const"' in needs_literal_check:
        uses_literal = True

    if style == "pydantic":
        imports = PYDANTIC_IMPORTS
    else:
        imports = DATACLASS_IMPORTS

    if uses_literal:
        imports = imports.rstrip("\n") + "\nfrom typing import Literal\n\n"

    # Collect classes to generate
    classes: list[str] = []

    # Generate nested object classes first
    top_properties = schema.get("properties", {})
    top_required = schema.get("required", [])

    for prop_name, prop_def in top_properties.items():
        if prop_def.get("type") == "object" and "properties" in prop_def:
            nested_class = _sanitize_class_name(prop_name)
            nested_props = prop_def.get("properties", {})
            nested_required = prop_def.get("required", [])
            nested_desc = prop_def.get("description", f"Nested model for {prop_name}.")

            if style == "pydantic":
                classes.append(
                    _generate_pydantic_model(
                        nested_class, nested_props, nested_required, nested_desc
                    )
                )
            else:
                classes.append(
                    _generate_dataclass(nested_class, nested_props, nested_required, nested_desc)
                )

    # Generate top-level class
    if style == "pydantic":
        classes.append(
            _generate_pydantic_model(class_name, top_properties, top_required, description)
        )
    else:
        classes.append(_generate_dataclass(class_name, top_properties, top_required, description))

    return header + imports + "\n".join(classes) + "\n"


# ---------------------------------------------------------------------------
# Batch generation
# ---------------------------------------------------------------------------


def generate_all(
    schemas_dir: Path,
    output_dir: Path,
    style: str = "dataclass",
) -> list[Path]:
    """Generate Python models for all schemas in a directory.

    Args:
        schemas_dir: Directory containing ``.schema.json`` files.
        output_dir: Directory to write generated ``.py`` files.
        style: Either ``"dataclass"`` or ``"pydantic"``.

    Returns:
        List of paths to generated files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    schema_files = sorted(schemas_dir.glob("*.schema.json"))
    if not schema_files:
        print(f"WARNING: No .schema.json files found in {schemas_dir}")
        return generated

    # Generate __init__.py
    init_path = output_dir / "__init__.py"
    init_lines = [
        '"""Auto-generated models for National MCP-PAI Oncology Trials Standard."""',
        "",
    ]

    for schema_file in schema_files:
        module_name = schema_file.stem.replace(".schema", "").replace("-", "_")
        try:
            source = generate_models_from_schema(schema_file, style=style)
            out_path = output_dir / f"{module_name}.py"
            out_path.write_text(source)
            generated.append(out_path)

            # Add to __init__.py
            class_name = _sanitize_class_name(schema_file.stem.replace(".schema", ""))
            init_lines.append(f"from .{module_name} import {class_name}")

            print(f"  Generated: {out_path.name} ({class_name})")
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"  ERROR: {schema_file.name}: {exc}")

    init_lines.append("")
    init_path.write_text("\n".join(init_lines))
    generated.append(init_path)

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
    """CLI entry point for Python model generation."""
    parser = argparse.ArgumentParser(
        description="Generate Python models from MCP-PAI Oncology Trials JSON schemas.",
    )
    parser.add_argument(
        "--schemas-dir",
        default=str(_repo_root() / "schemas"),
        help="Path to schemas directory",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_repo_root() / "generated" / "python"),
        help="Output directory for generated Python files",
    )
    parser.add_argument(
        "--style",
        choices=["dataclass", "pydantic"],
        default="dataclass",
        help="Model style: dataclass or pydantic (default: dataclass)",
    )

    args = parser.parse_args(argv)
    schemas_dir = Path(args.schemas_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    print(f"Generating Python models ({args.style})")
    print(f"  Schemas: {schemas_dir}")
    print(f"  Output:  {output_dir}")

    generated = generate_all(schemas_dir, output_dir, style=args.style)
    print(f"\nGenerated {len(generated)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
