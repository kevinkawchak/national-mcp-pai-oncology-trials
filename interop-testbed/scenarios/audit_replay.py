"""Auditor audit chain replay and verification scenario.

Validates that an auditor can replay the complete audit chain
from genesis to current head and verify integrity at every link.
"""

from __future__ import annotations

from typing import Any

from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    compute_audit_hash,
    make_audit_chain,
)


def replay_chain(chain: list[dict]) -> list[dict[str, Any]]:
    """Replay an audit chain and verify each link.

    Args:
        chain: List of audit records in chronological order.

    Returns:
        List of verification results per record.
    """
    results = []
    for i, record in enumerate(chain):
        expected_prev = GENESIS_HASH if i == 0 else chain[i - 1]["hash"]
        computed_hash = compute_audit_hash(record)

        results.append(
            {
                "index": i,
                "audit_id": record["audit_id"],
                "previous_hash_valid": record["previous_hash"] == expected_prev,
                "hash_valid": record["hash"] == computed_hash,
                "server": record["server"],
            }
        )
    return results


def run_scenario() -> dict[str, Any]:
    """Execute the audit replay scenario.

    Returns:
        Scenario result with pass/fail status and verification details.
    """
    chain = make_audit_chain(length=10)
    verification = replay_chain(chain)

    all_valid = all(r["previous_hash_valid"] and r["hash_valid"] for r in verification)

    return {
        "scenario": "audit_replay",
        "passed": all_valid,
        "chain_length": len(chain),
        "records_verified": len(verification),
        "all_hashes_valid": all_valid,
    }
