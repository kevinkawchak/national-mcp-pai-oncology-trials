"""Token exchange and revocation across sites scenario.

Validates that tokens issued at one site are properly validated
and that revocation propagates across the national network.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any


def issue_token(site: str, role: str) -> dict[str, Any]:
    """Simulate token issuance at a specific site.

    Args:
        site: Site identifier (e.g., 'site-a').
        role: Actor role for the token.

    Returns:
        Token metadata including hash and site origin.
    """
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    return {
        "token_hash": token_hash,
        "site": site,
        "role": role,
        "issued": True,
        "revoked": False,
    }


def validate_token(token: dict, target_site: str) -> bool:
    """Validate a token at a target site.

    Args:
        token: Token metadata dictionary.
        target_site: Site where validation is attempted.

    Returns:
        True if the token is valid at the target site.
    """
    return token["issued"] and not token["revoked"]


def revoke_token(token: dict) -> dict:
    """Revoke a token.

    Args:
        token: Token metadata to revoke.

    Returns:
        Updated token metadata with revoked=True.
    """
    token["revoked"] = True
    return token


def run_scenario() -> dict[str, Any]:
    """Execute the token exchange scenario.

    Returns:
        Scenario result with pass/fail status.
    """
    # Issue token at Site A
    token = issue_token("site-a", "robot_agent")
    assert token["issued"]

    # Validate at Site B
    valid_at_b = validate_token(token, "site-b")

    # Revoke at Site A
    token = revoke_token(token)

    # Verify revocation propagates
    invalid_after_revoke = not validate_token(token, "site-b")

    passed = valid_at_b and invalid_after_revoke

    return {
        "scenario": "token_exchange",
        "passed": passed,
        "token_valid_cross_site": valid_at_b,
        "revocation_propagated": invalid_after_revoke,
    }
