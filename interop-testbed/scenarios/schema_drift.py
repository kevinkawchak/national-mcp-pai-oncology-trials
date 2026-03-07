"""Schema version mismatch detection between sites scenario.

Validates that schema version differences between sites are
detected and reported before data exchange occurs.
"""

from __future__ import annotations

from typing import Any


def detect_schema_drift(
    site_a_version: str,
    site_b_version: str,
) -> dict[str, Any]:
    """Detect schema version drift between two sites.

    Args:
        site_a_version: Schema version at Site A.
        site_b_version: Schema version at Site B.

    Returns:
        Drift detection result.
    """
    a_parts = [int(x) for x in site_a_version.split(".")]
    b_parts = [int(x) for x in site_b_version.split(".")]

    major_drift = a_parts[0] != b_parts[0]
    minor_drift = a_parts[1] != b_parts[1]
    patch_drift = a_parts[2] != b_parts[2]

    return {
        "site_a_version": site_a_version,
        "site_b_version": site_b_version,
        "major_drift": major_drift,
        "minor_drift": minor_drift,
        "patch_drift": patch_drift,
        "breaking_change": major_drift,
        "compatible": not major_drift,
    }


def run_scenario() -> dict[str, Any]:
    """Execute the schema drift detection scenario.

    Returns:
        Scenario result with drift analysis.
    """
    # Compatible versions (minor drift)
    result_compatible = detect_schema_drift("0.8.0", "0.7.0")

    # Incompatible versions (major drift)
    result_breaking = detect_schema_drift("1.0.0", "0.8.0")

    passed = result_compatible["compatible"] and not result_breaking["compatible"]

    return {
        "scenario": "schema_drift",
        "passed": passed,
        "compatible_test": result_compatible,
        "breaking_test": result_breaking,
    }
