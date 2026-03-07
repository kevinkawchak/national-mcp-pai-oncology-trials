"""New site onboarding certification flow scenario.

Validates the process of certifying a new site for participation
in the national MCP-PAI oncology trials network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OnboardingCheck:
    """A single onboarding certification check."""

    name: str
    category: str
    required: bool
    passed: bool = False
    details: str = ""


def build_onboarding_checklist() -> list[OnboardingCheck]:
    """Build the site onboarding certification checklist.

    Returns:
        List of required and recommended onboarding checks.
    """
    return [
        OnboardingCheck(
            "authz_server_deployed",
            "infrastructure",
            True,
            details="AuthZ server MUST be deployed and accessible",
        ),
        OnboardingCheck(
            "ledger_server_deployed",
            "infrastructure",
            True,
            details="Ledger server MUST be deployed with genesis block",
        ),
        OnboardingCheck(
            "fhir_server_deployed",
            "infrastructure",
            True,
            details="FHIR server MUST be deployed with de-identification",
        ),
        OnboardingCheck(
            "dicom_server_deployed",
            "infrastructure",
            True,
            details="DICOM server MUST be deployed with modality restrictions",
        ),
        OnboardingCheck(
            "provenance_server_deployed",
            "infrastructure",
            True,
            details="Provenance server MUST be deployed with DAG support",
        ),
        OnboardingCheck(
            "rbac_policy_configured",
            "security",
            True,
            details="RBAC policies MUST be configured for all 6 roles",
        ),
        OnboardingCheck(
            "tls_configured",
            "security",
            True,
            details="TLS MUST be configured for all server endpoints",
        ),
        OnboardingCheck(
            "schema_version_compatible",
            "compatibility",
            True,
            details="Schema version MUST be compatible with national standard",
        ),
        OnboardingCheck(
            "conformance_tests_passed",
            "validation",
            True,
            details="Base conformance tests MUST pass",
        ),
        OnboardingCheck(
            "regulatory_overlay_applied",
            "compliance",
            True,
            details="Applicable state regulatory overlay MUST be configured",
        ),
    ]


def certify_site(checklist: list[OnboardingCheck]) -> dict[str, Any]:
    """Evaluate site certification status.

    Args:
        checklist: Completed onboarding checklist.

    Returns:
        Certification result.
    """
    required_checks = [c for c in checklist if c.required]
    required_passed = [c for c in required_checks if c.passed]

    return {
        "certified": len(required_passed) == len(required_checks),
        "total_checks": len(checklist),
        "required_checks": len(required_checks),
        "required_passed": len(required_passed),
        "failed_checks": [c.name for c in required_checks if not c.passed],
    }


def run_scenario() -> dict[str, Any]:
    """Execute the site onboarding scenario.

    Returns:
        Scenario result with certification details.
    """
    checklist = build_onboarding_checklist()
    # Simulate all checks passing
    for check in checklist:
        check.passed = True

    certification = certify_site(checklist)

    return {
        "scenario": "site_onboarding",
        "passed": certification["certified"],
        "certification": certification,
    }
