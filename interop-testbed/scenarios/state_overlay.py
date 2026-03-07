"""California/New York/FDA regulatory overlay enforcement scenario.

Validates that state-specific regulatory overlays are correctly
applied based on site jurisdiction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegulatoryOverlay:
    """A regulatory overlay requirement."""

    name: str
    jurisdiction: str
    requirements: list[str] = field(default_factory=list)


CALIFORNIA_OVERLAY = RegulatoryOverlay(
    name="state-us-ca",
    jurisdiction="California",
    requirements=[
        "CCPA Right to Know",
        "CCPA Right to Delete",
        "CCPA Right to Opt-Out",
        "Sensitive PI protections",
        "Data minimization",
    ],
)

NEW_YORK_OVERLAY = RegulatoryOverlay(
    name="state-us-ny",
    jurisdiction="New York",
    requirements=[
        "PHL Article 27-F (HIV confidentiality)",
        "SHIELD Act security safeguards",
        "MHL Article 33 (mental health)",
        "DOH 10 NYCRR",
    ],
)

FDA_OVERLAY = RegulatoryOverlay(
    name="country-us-fda",
    jurisdiction="United States",
    requirements=[
        "21 CFR Part 11 Subpart B electronic records",
        "Electronic signatures (§11.50, §11.70, §11.100)",
        "SaMD classification",
        "Good Machine Learning Practice",
    ],
)


def get_overlays_for_site(state: str) -> list[RegulatoryOverlay]:
    """Determine applicable regulatory overlays for a site.

    Args:
        state: US state where the site is located.

    Returns:
        List of applicable regulatory overlays.
    """
    overlays = [FDA_OVERLAY]  # Federal overlay always applies

    if state == "California":
        overlays.append(CALIFORNIA_OVERLAY)
    elif state == "New York":
        overlays.append(NEW_YORK_OVERLAY)

    return overlays


def run_scenario() -> dict[str, Any]:
    """Execute the regulatory overlay enforcement scenario.

    Returns:
        Scenario result with overlay analysis.
    """
    ca_overlays = get_overlays_for_site("California")
    ny_overlays = get_overlays_for_site("New York")
    tx_overlays = get_overlays_for_site("Texas")

    passed = (
        len(ca_overlays) == 2  # FDA + California
        and len(ny_overlays) == 2  # FDA + New York
        and len(tx_overlays) == 1  # FDA only
    )

    return {
        "scenario": "state_overlay",
        "passed": passed,
        "california_overlays": len(ca_overlays),
        "new_york_overlays": len(ny_overlays),
        "texas_overlays": len(tx_overlays),
    }
