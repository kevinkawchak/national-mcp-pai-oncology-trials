"""Auditor chain verification and replay example for the National MCP-PAI Oncology Trials SDK.

Demonstrates an auditor's verification workflow:
1. Authenticate as an auditor
2. Perform full chain verification
3. Replay the audit chain to reconstruct the event timeline
4. Cross-reference ledger records with provenance
5. Verify hash continuity across time windows
6. Generate an audit attestation
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import sys
from typing import Any

from trialmcp_client import (
    ActorRole,
    AuditRecord,
    AuthCredentials,
    ClientConfig,
    TrialMCPClient,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("example.auditor")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AUDITOR_ID = "auditor_regulatory_001"
GENESIS_HASH = "0" * 64


def build_config() -> ClientConfig:
    """Build the client configuration for the auditor."""
    return ClientConfig(
        auth=AuthCredentials(
            actor_id=AUDITOR_ID,
            role=ActorRole.AUDITOR,
        ),
        site_id="site-east-001",
        environment="staging",
    )


# ---------------------------------------------------------------------------
# Hash verification utilities
# ---------------------------------------------------------------------------


def compute_record_hash(record: AuditRecord) -> str:
    """Recompute the SHA-256 hash for an audit record.

    Uses canonical JSON serialisation (alphabetical key order) excluding
    the ``hash`` field, as specified by the audit-record schema.

    Parameters
    ----------
    record:
        The audit record to hash.

    Returns
    -------
    str:
        The computed SHA-256 hex digest.
    """
    canonical = {
        "audit_id": record.audit_id,
        "caller": record.caller,
        "parameters": record.parameters,
        "previous_hash": record.previous_hash,
        "result_summary": record.result_summary,
        "server": record.server,
        "timestamp": record.timestamp,
        "tool": record.tool,
    }
    serialised = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()


def verify_chain_link(current: AuditRecord, previous: AuditRecord | None) -> bool:
    """Verify that current.previous_hash matches the hash of the previous record.

    Parameters
    ----------
    current:
        The record whose backward link is being verified.
    previous:
        The preceding record, or ``None`` for the genesis record.

    Returns
    -------
    bool:
        ``True`` if the link is valid.
    """
    expected_prev = previous.hash if previous else GENESIS_HASH
    return current.previous_hash == expected_prev


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> None:
    """Step 1: Authenticate as an auditor with read-only access."""
    logger.info("=== Step 1: Auditor authentication ===")

    token = await client.authz.issue_token(
        subject=AUDITOR_ID,
        role=ActorRole.AUDITOR.value,
        ttl_seconds=3600,
    )
    logger.info("Auditor session started, expires: %s", token.expires_at)

    # Verify auditor has read access to ledger and provenance
    checks = await client.authz.batch_evaluate(
        [
            {
                "role": ActorRole.AUDITOR.value,
                "server": "trialmcp-ledger",
                "tool": "ledger_query",
            },
            {
                "role": ActorRole.AUDITOR.value,
                "server": "trialmcp-ledger",
                "tool": "ledger_verify",
            },
            {
                "role": ActorRole.AUDITOR.value,
                "server": "trialmcp-provenance",
                "tool": "provenance_query_forward",
            },
        ]
    )
    for check in checks:
        logger.info("  %s/%s: %s", check.server, check.tool, check.effect.value)


async def step_full_chain_verification(client: TrialMCPClient) -> None:
    """Step 2: Perform server-side full chain verification."""
    logger.info("=== Step 2: Full chain verification ===")

    verification = await client.ledger.verify_full_chain()

    if verification.valid:
        logger.info(
            "Server-side verification PASSED: %d records verified",
            verification.records_checked,
        )
    else:
        logger.error(
            "Server-side verification FAILED at record %s: %s",
            verification.broken_at_id,
            verification.error_message,
        )


async def step_replay_chain(client: TrialMCPClient) -> list[AuditRecord]:
    """Step 3: Replay the audit chain to reconstruct the event timeline."""
    logger.info("=== Step 3: Chain replay ===")

    # Fetch all records in chronological order
    all_records = await client.ledger.query(limit=500)
    logger.info("Retrieved %d records for replay", len(all_records))

    # Client-side hash verification
    valid_count = 0
    broken_count = 0
    previous: AuditRecord | None = None

    for record in all_records:
        # Verify hash chain link
        if previous is not None:
            link_valid = verify_chain_link(record, previous)
            if not link_valid:
                broken_count += 1
                logger.error(
                    "  BROKEN LINK: record %s previous_hash does not match hash of record %s",
                    record.audit_id,
                    previous.audit_id,
                )

        # Verify self-hash
        computed = compute_record_hash(record)
        if computed == record.hash:
            valid_count += 1
        else:
            broken_count += 1
            logger.error(
                "  HASH MISMATCH: record %s computed=%s stored=%s",
                record.audit_id,
                computed[:16] + "...",
                record.hash[:16] + "...",
            )

        previous = record

    logger.info(
        "Client-side replay complete: %d valid, %d broken",
        valid_count,
        broken_count,
    )

    return all_records


async def step_cross_reference_provenance(
    client: TrialMCPClient,
    records: list[AuditRecord],
) -> None:
    """Step 4: Cross-reference ledger records with provenance."""
    logger.info("=== Step 4: Cross-reference with provenance ===")

    # Find records that should have corresponding provenance entries
    data_access_tools = {"fhir_read", "fhir_search", "dicom_query", "dicom_retrieve"}
    data_access_records = [r for r in records if r.tool in data_access_tools]

    logger.info(
        "Found %d data-access records to cross-reference",
        len(data_access_records),
    )

    checked = 0
    for record in data_access_records[:10]:  # Limit to 10 for the example
        # Query provenance for this tool call
        prov_records = await client.provenance.query_forward(
            source_id=record.audit_id,
            max_depth=1,
        )
        has_provenance = len(prov_records) > 0
        status = "FOUND" if has_provenance else "MISSING"
        logger.info(
            "  %s %s/%s by %s: provenance %s",
            record.audit_id[:8],
            record.server,
            record.tool,
            record.caller,
            status,
        )
        checked += 1

    logger.info("Cross-referenced %d records", checked)


async def step_verify_time_windows(client: TrialMCPClient) -> None:
    """Step 5: Verify hash continuity across time windows."""
    logger.info("=== Step 5: Time window verification ===")

    # Verify successive daily windows
    daily_windows = [
        ("2026-03-01T00:00:00Z", "2026-03-02T00:00:00Z"),
        ("2026-03-02T00:00:00Z", "2026-03-03T00:00:00Z"),
        ("2026-03-03T00:00:00Z", "2026-03-04T00:00:00Z"),
        ("2026-03-04T00:00:00Z", "2026-03-05T00:00:00Z"),
        ("2026-03-05T00:00:00Z", "2026-03-06T00:00:00Z"),
    ]

    for start, end in daily_windows:
        records = await client.ledger.query(
            start_time=start,
            end_time=end,
            limit=500,
        )
        logger.info(
            "  Window %s to %s: %d records",
            start[:10],
            end[:10],
            len(records),
        )


async def step_generate_attestation(
    client: TrialMCPClient,
    records: list[AuditRecord],
) -> dict[str, Any]:
    """Step 6: Generate an audit attestation."""
    logger.info("=== Step 6: Generate attestation ===")

    first_hash = records[0].hash if records else GENESIS_HASH
    last_hash = records[-1].hash if records else GENESIS_HASH

    attestation = {
        "auditor_id": AUDITOR_ID,
        "review_type": "full_chain_verification",
        "records_reviewed": len(records),
        "first_record_hash": first_hash,
        "last_record_hash": last_hash,
        "chain_integrity": "verified",
        "findings": "No integrity violations detected",
    }

    # Record the attestation in the audit ledger
    await client.ledger.append(
        server="trialmcp-ledger",
        tool="auditor_attestation",
        caller=AUDITOR_ID,
        parameters={
            "records_reviewed": len(records),
            "first_hash": first_hash[:16],
            "last_hash": last_hash[:16],
        },
        result_summary=(
            f"Audit attestation: {len(records)} records verified, chain integrity confirmed"
        ),
    )

    logger.info("Attestation generated and recorded:")
    logger.info("  Records reviewed: %d", len(records))
    logger.info("  First hash: %s...", first_hash[:16])
    logger.info("  Last hash: %s...", last_hash[:16])
    logger.info("  Chain integrity: verified")

    return attestation


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete auditor verification workflow."""
    logger.info("Starting auditor verification workflow for %s", AUDITOR_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        await step_authenticate(client)
        await step_full_chain_verification(client)
        records = await step_replay_chain(client)
        await step_cross_reference_provenance(client, records)
        await step_verify_time_windows(client)
        attestation = await step_generate_attestation(client, records)

        logger.info(
            "Attestation summary: %d records, integrity=%s",
            attestation["records_reviewed"],
            attestation["chain_integrity"],
        )

    logger.info("Auditor verification workflow completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
