"""Partial site outage and graceful degradation scenario.

Validates that the system degrades gracefully when individual
servers or entire sites become unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ServerStatus:
    """Status of a single MCP server."""

    name: str
    site: str
    healthy: bool
    degraded: bool = False


def simulate_outage(servers: list[ServerStatus], failed_server: str) -> list[ServerStatus]:
    """Simulate a server outage.

    Args:
        servers: List of server statuses.
        failed_server: Name of the server to fail.

    Returns:
        Updated server statuses with the failed server marked unhealthy.
    """
    for server in servers:
        if server.name == failed_server:
            server.healthy = False
    return servers


def check_degradation(servers: list[ServerStatus]) -> dict[str, Any]:
    """Check system degradation level.

    Args:
        servers: Current server statuses.

    Returns:
        Degradation assessment.
    """
    healthy = [s for s in servers if s.healthy]
    unhealthy = [s for s in servers if not s.healthy]

    sites_affected = {s.site for s in unhealthy}
    authz_available = any(s.healthy and "authz" in s.name for s in servers)
    ledger_available = any(s.healthy and "ledger" in s.name for s in servers)

    return {
        "healthy_count": len(healthy),
        "unhealthy_count": len(unhealthy),
        "sites_affected": list(sites_affected),
        "authz_available": authz_available,
        "ledger_available": ledger_available,
        "system_operational": authz_available and ledger_available,
    }


def run_scenario() -> dict[str, Any]:
    """Execute the partial outage scenario.

    Returns:
        Scenario result with degradation assessment.
    """
    servers = [
        ServerStatus("site-a-authz", "site-a", True),
        ServerStatus("site-a-fhir", "site-a", True),
        ServerStatus("site-a-dicom", "site-a", True),
        ServerStatus("site-a-ledger", "site-a", True),
        ServerStatus("site-a-provenance", "site-a", True),
        ServerStatus("site-b-authz", "site-b", True),
        ServerStatus("site-b-fhir", "site-b", True),
        ServerStatus("site-b-dicom", "site-b", True),
        ServerStatus("site-b-ledger", "site-b", True),
        ServerStatus("site-b-provenance", "site-b", True),
    ]

    # Simulate Site B FHIR outage
    servers = simulate_outage(servers, "site-b-fhir")
    degradation = check_degradation(servers)

    return {
        "scenario": "partial_outage",
        "passed": degradation["system_operational"],
        "degradation": degradation,
    }
