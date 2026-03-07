#!/usr/bin/env python3
"""Generate typed Python dataclasses and TypeScript interfaces from JSON schemas.

Reads all /schemas/*.schema.json files and produces:
  - models/python/generated_models.py  (dataclasses)
  - models/typescript/generated_models.ts  (TypeScript interfaces)

This script is the canonical contract generation pipeline — the CI
workflow regenerates models and fails if committed output differs.

Usage:
    python scripts/generate_models.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
PY_OUT = REPO_ROOT / "models" / "python" / "generated_models.py"
TS_OUT = REPO_ROOT / "models" / "typescript" / "generated_models.ts"


def _snake_to_pascal(name: str) -> str:
    """Convert kebab-case schema name to PascalCase class name."""
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


def _json_type_to_python(prop: dict, required: bool) -> str:
    """Map a JSON Schema property to a Python type annotation."""
    jtype = prop.get("type", "Any")
    if jtype == "string":
        base = "str"
    elif jtype == "integer":
        base = "int"
    elif jtype == "number":
        base = "float"
    elif jtype == "boolean":
        base = "bool"
    elif jtype == "array":
        items = prop.get("items", {})
        item_type = _json_type_to_python(items, True)
        base = f"list[{item_type}]"
    elif jtype == "object":
        base = "dict[str, Any]"
    else:
        base = "Any"
    if not required:
        base = f"{base} | None"
    return base


def _json_type_to_ts(prop: dict, required: bool) -> str:
    """Map a JSON Schema property to a TypeScript type."""
    jtype = prop.get("type", "any")
    if jtype == "string":
        base = "string"
    elif jtype in ("integer", "number"):
        base = "number"
    elif jtype == "boolean":
        base = "boolean"
    elif jtype == "array":
        items = prop.get("items", {})
        item_type = _json_type_to_ts(items, True)
        base = f"{item_type}[]"
    elif jtype == "object":
        base = "Record<string, unknown>"
    else:
        base = "any"
    if not required:
        base = f"{base} | null"
    return base


def generate_python(schemas: list[tuple[str, dict]]) -> str:
    """Generate Python dataclass source code from schemas."""
    lines = [
        '"""Auto-generated typed models from /schemas/*.schema.json.',
        "",
        "DO NOT EDIT — regenerate with: python scripts/generate_models.py",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "from typing import Any",
        "",
    ]

    for short_name, schema in schemas:
        class_name = _snake_to_pascal(short_name)
        title = schema.get("title", short_name)
        desc = schema.get("description", "")
        required_fields = set(schema.get("required", []))
        props = schema.get("properties", {})

        lines.append("")
        lines.append("@dataclass")
        lines.append(f"class {class_name}:")
        lines.append(f'    """{title}.')
        if desc:
            wrapped = textwrap.fill(desc, width=90, initial_indent="    ", subsequent_indent="    ")
            lines.append("")
            lines.append(wrapped)
        lines.append('    """')
        lines.append("")

        # Required fields first, then optional
        required_props = [(k, v) for k, v in props.items() if k in required_fields]
        optional_props = [(k, v) for k, v in props.items() if k not in required_fields]

        for field_name, prop in required_props:
            py_type = _json_type_to_python(prop, True)
            field_desc = prop.get("description", "")
            if field_desc:
                lines.append(f"    {field_name}: {py_type}")
            else:
                lines.append(f"    {field_name}: {py_type}")

        for field_name, prop in optional_props:
            py_type = _json_type_to_python(prop, False)
            lines.append(f"    {field_name}: {py_type} = None")

        if not props:
            lines.append("    pass")

        lines.append("")

    return "\n".join(lines)


def generate_typescript(schemas: list[tuple[str, dict]]) -> str:
    """Generate TypeScript interface source code from schemas."""
    lines = [
        "/**",
        " * Auto-generated typed interfaces from /schemas/*.schema.json.",
        " *",
        " * DO NOT EDIT — regenerate with: python scripts/generate_models.py",
        " */",
        "",
    ]

    for short_name, schema in schemas:
        class_name = _snake_to_pascal(short_name)
        title = schema.get("title", short_name)
        required_fields = set(schema.get("required", []))
        props = schema.get("properties", {})

        lines.append(f"/** {title} */")
        lines.append(f"export interface {class_name} {{")

        for field_name, prop in props.items():
            is_required = field_name in required_fields
            ts_type = _json_type_to_ts(prop, True)
            optional = "" if is_required else "?"
            desc = prop.get("description", "")
            if desc:
                lines.append(f"  /** {desc} */")
            lines.append(f"  {field_name}{optional}: {ts_type};")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Generate models from all schemas."""
    schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
    schemas: list[tuple[str, dict]] = []
    for sf in schema_files:
        short_name = sf.name.replace(".schema.json", "")
        schema = json.loads(sf.read_text(encoding="utf-8"))
        schemas.append((short_name, schema))

    print(f"Found {len(schemas)} schemas")

    py_src = generate_python(schemas)
    PY_OUT.parent.mkdir(parents=True, exist_ok=True)
    PY_OUT.write_text(py_src, encoding="utf-8")
    print(f"  -> {PY_OUT}")

    ts_src = generate_typescript(schemas)
    TS_OUT.parent.mkdir(parents=True, exist_ok=True)
    TS_OUT.write_text(ts_src, encoding="utf-8")
    print(f"  -> {TS_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
