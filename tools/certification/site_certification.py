"""Site certification report generator.

Validates site capability profiles, required server deployments,
regulatory overlay compliance, and determines conformance level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CertificationCheck:
    """A single certification check result."""

    name: str
    category: str
    required: bool
    passed: bool = False
    details: str = ""


@dataclass
class SiteCertification:
    """Site certification report.

    Attributes:
        site_id: Site identifier.
        timestamp: Certification timestamp.
        profile: Target conformance profile.
        level: Achieved conformance level.
        checks: List of certification checks.
        certified: Whether the site is certified.
    """

    site_id: str = ""
    timestamp: str = ""
    profile: str = "base"
    level: int = 0
    checks: list[CertificationCheck] = field(default_factory=list)
    certified: bool = False

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


REQUIRED_SERVERS = ["authz", "fhir", "dicom", "ledger", "provenance"]

PROFILE_REQUIREMENTS: dict[str, list[str]] = {
    "base": ["authz", "ledger"],
    "clinical-read": ["authz", "fhir", "ledger"],
    "imaging-guided-oncology": ["authz", "fhir", "dicom", "ledger"],
    "multi-site-federated": ["authz", "fhir", "dicom", "ledger", "provenance"],
    "robot-assisted-procedure": ["authz", "fhir", "dicom", "ledger", "provenance"],
}


def validate_site_capability(
    site_config: dict[str, Any],
    profile: str = "base",
) -> SiteCertification:
    """Validate a site's capability profile against certification requirements.

    Args:
        site_config: Site configuration dictionary with 'servers', 'jurisdiction',
                     'regulatory_overlays' keys.
        profile: Target conformance profile.

    Returns:
        SiteCertification with check results.
    """
    cert = SiteCertification(
        site_id=site_config.get("site_id", "unknown"),
        profile=profile,
    )

    # Check required servers
    deployed_servers = site_config.get("servers", [])
    required = PROFILE_REQUIREMENTS.get(profile, ["authz", "ledger"])

    for server in required:
        check = CertificationCheck(
            name=f"{server}_server_deployed",
            category="infrastructure",
            required=True,
            passed=server in deployed_servers,
            details=f"{server} server {'deployed' if server in deployed_servers else 'missing'}",
        )
        cert.checks.append(check)

    # Check regulatory overlay
    jurisdiction = site_config.get("jurisdiction", "")
    overlays = site_config.get("regulatory_overlays", [])
    cert.checks.append(
        CertificationCheck(
            name="fda_overlay_applied",
            category="compliance",
            required=True,
            passed="country-us-fda" in overlays,
            details="FDA 21 CFR Part 11 overlay",
        )
    )

    if jurisdiction == "California":
        cert.checks.append(
            CertificationCheck(
                name="california_overlay_applied",
                category="compliance",
                required=True,
                passed="state-us-ca" in overlays,
                details="California CCPA/CPRA overlay",
            )
        )
    elif jurisdiction == "New York":
        cert.checks.append(
            CertificationCheck(
                name="new_york_overlay_applied",
                category="compliance",
                required=True,
                passed="state-us-ny" in overlays,
                details="New York PHL/SHIELD overlay",
            )
        )

    # Determine certification status
    required_checks = [c for c in cert.checks if c.required]
    cert.certified = all(c.passed for c in required_checks)

    # Determine conformance level
    if cert.certified:
        if set(REQUIRED_SERVERS).issubset(set(deployed_servers)):
            cert.level = 5  # Robot Procedure
        elif "provenance" in deployed_servers:
            cert.level = 4  # Federated
        elif "dicom" in deployed_servers:
            cert.level = 3  # Imaging
        elif "fhir" in deployed_servers:
            cert.level = 2  # Clinical Read
        else:
            cert.level = 1  # Base

    return cert


def generate_certification_report(cert: SiteCertification) -> dict[str, Any]:
    """Generate a machine-readable certification report.

    Args:
        cert: SiteCertification to report.

    Returns:
        Certification report dictionary.
    """
    return {
        "site_id": cert.site_id,
        "timestamp": cert.timestamp,
        "profile": cert.profile,
        "level": cert.level,
        "certified": cert.certified,
        "checks": [
            {
                "name": c.name,
                "category": c.category,
                "required": c.required,
                "passed": c.passed,
                "details": c.details,
            }
            for c in cert.checks
        ],
        "summary": {
            "total_checks": len(cert.checks),
            "required": sum(1 for c in cert.checks if c.required),
            "passed": sum(1 for c in cert.checks if c.passed),
            "failed": [c.name for c in cert.checks if c.required and not c.passed],
        },
    }
