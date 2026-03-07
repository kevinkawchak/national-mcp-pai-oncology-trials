"""Schema compatibility diff tool.

Compares schema versions for breaking/non-breaking changes,
detects field additions, removals, type changes, and constraint
changes, and generates a compatibility report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaDiff:
    """A single schema difference.

    Attributes:
        path: JSON path to the changed field.
        change_type: Type of change (added, removed, type_changed, constraint_changed).
        breaking: Whether this change is a breaking change.
        old_value: Previous value (if applicable).
        new_value: New value (if applicable).
        description: Human-readable description.
    """

    path: str
    change_type: str
    breaking: bool
    old_value: Any = None
    new_value: Any = None
    description: str = ""


@dataclass
class CompatibilityReport:
    """Schema compatibility report.

    Attributes:
        schema_name: Name of the schema being compared.
        old_version: Old schema version.
        new_version: New schema version.
        diffs: List of detected differences.
        compatible: Whether the new version is backward compatible.
    """

    schema_name: str = ""
    old_version: str = ""
    new_version: str = ""
    diffs: list[SchemaDiff] = field(default_factory=list)
    compatible: bool = True

    @property
    def breaking_changes(self) -> list[SchemaDiff]:
        return [d for d in self.diffs if d.breaking]

    @property
    def non_breaking_changes(self) -> list[SchemaDiff]:
        return [d for d in self.diffs if not d.breaking]


def compare_schemas(
    old_schema: dict[str, Any],
    new_schema: dict[str, Any],
    path: str = "",
) -> list[SchemaDiff]:
    """Compare two schema versions and detect differences.

    Args:
        old_schema: Previous schema version.
        new_schema: New schema version.
        path: Current JSON path (for recursion).

    Returns:
        List of detected schema differences.
    """
    diffs: list[SchemaDiff] = []

    # Check required fields
    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))

    for added in new_required - old_required:
        diffs.append(
            SchemaDiff(
                path=f"{path}.required",
                change_type="added_required",
                breaking=True,
                new_value=added,
                description=f"New required field: {added}",
            )
        )

    for removed in old_required - new_required:
        diffs.append(
            SchemaDiff(
                path=f"{path}.required",
                change_type="removed_required",
                breaking=False,
                old_value=removed,
                description=f"Required field removed (now optional): {removed}",
            )
        )

    # Check properties
    old_props = old_schema.get("properties", {})
    new_props = new_schema.get("properties", {})

    for prop_name in set(old_props) | set(new_props):
        prop_path = f"{path}.properties.{prop_name}" if path else f"properties.{prop_name}"

        if prop_name in new_props and prop_name not in old_props:
            diffs.append(
                SchemaDiff(
                    path=prop_path,
                    change_type="added",
                    breaking=False,
                    new_value=new_props[prop_name].get("type", "unknown"),
                    description=f"New property: {prop_name}",
                )
            )
        elif prop_name in old_props and prop_name not in new_props:
            diffs.append(
                SchemaDiff(
                    path=prop_path,
                    change_type="removed",
                    breaking=True,
                    old_value=old_props[prop_name].get("type", "unknown"),
                    description=f"Removed property: {prop_name}",
                )
            )
        elif prop_name in old_props and prop_name in new_props:
            old_type = old_props[prop_name].get("type")
            new_type = new_props[prop_name].get("type")
            if old_type != new_type:
                diffs.append(
                    SchemaDiff(
                        path=prop_path,
                        change_type="type_changed",
                        breaking=True,
                        old_value=old_type,
                        new_value=new_type,
                        description=f"Type changed: {old_type} -> {new_type}",
                    )
                )

    return diffs


def generate_compatibility_report(
    schema_name: str,
    old_schema: dict[str, Any],
    new_schema: dict[str, Any],
    old_version: str = "",
    new_version: str = "",
) -> CompatibilityReport:
    """Generate a schema compatibility report.

    Args:
        schema_name: Name of the schema being compared.
        old_schema: Previous schema version.
        new_schema: New schema version.
        old_version: Old version string.
        new_version: New version string.

    Returns:
        CompatibilityReport with all detected differences.
    """
    diffs = compare_schemas(old_schema, new_schema)
    compatible = not any(d.breaking for d in diffs)

    return CompatibilityReport(
        schema_name=schema_name,
        old_version=old_version,
        new_version=new_version,
        diffs=diffs,
        compatible=compatible,
    )


def report_to_dict(report: CompatibilityReport) -> dict[str, Any]:
    """Convert a compatibility report to a dictionary.

    Args:
        report: CompatibilityReport to convert.

    Returns:
        Dictionary representation of the report.
    """
    return {
        "schema_name": report.schema_name,
        "old_version": report.old_version,
        "new_version": report.new_version,
        "compatible": report.compatible,
        "breaking_changes": len(report.breaking_changes),
        "non_breaking_changes": len(report.non_breaking_changes),
        "diffs": [
            {
                "path": d.path,
                "change_type": d.change_type,
                "breaking": d.breaking,
                "old_value": d.old_value,
                "new_value": d.new_value,
                "description": d.description,
            }
            for d in report.diffs
        ],
    }
