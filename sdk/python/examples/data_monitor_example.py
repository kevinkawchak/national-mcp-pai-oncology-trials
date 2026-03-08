"""Data monitor review workflow for the National MCP-PAI Oncology Trials SDK.

Demonstrates a data monitor's review workflow:
1. Authenticate as a data monitor
2. Query audit records for a specific time window
3. Verify audit chain integrity
4. Review provenance of data transformations
5. Detect anomalies in access patterns
6. Generate a compliance summary
"""

from __future__ import annotations

import asyncio
import logging
import sys
from collections import Counter
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
logger = logging.getLogger("example.data_monitor")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MONITOR_ID = "data_monitor_smith"
REVIEW_WINDOW_START = "2026-03-01T00:00:00Z"
REVIEW_WINDOW_END = "2026-03-08T23:59:59Z"


def build_config() -> ClientConfig:
    """Build the client configuration for the data monitor."""
    return ClientConfig(
        auth=AuthCredentials(
            actor_id=MONITOR_ID,
            role=ActorRole.DATA_MONITOR,
        ),
        site_id="site-east-001",
        environment="staging",
    )


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> None:
    """Step 1: Authenticate and verify data monitor permissions."""
    logger.info("=== Step 1: Authentication ===")

    token = await client.authz.issue_token(
        subject=MONITOR_ID,
        role=ActorRole.DATA_MONITOR.value,
        ttl_seconds=14400,  # 4-hour review session
    )
    logger.info("Data monitor session started, expires: %s", token.expires_at)

    # Verify read-only permissions (data monitors should not have write access)
    read_check = await client.authz.check_access(
        role=ActorRole.DATA_MONITOR.value,
        server="trialmcp-ledger",
        tool="ledger_query",
    )
    logger.info("Ledger query permission: %s", read_check)


async def step_query_audit_records(client: TrialMCPClient) -> list[AuditRecord]:
    """Step 2: Query audit records for the review window."""
    logger.info("=== Step 2: Query audit records ===")

    # Query records across all servers
    all_records: list[AuditRecord] = []
    servers = [
        "trialmcp-authz",
        "trialmcp-fhir",
        "trialmcp-dicom",
        "trialmcp-ledger",
        "trialmcp-provenance",
    ]

    for server in servers:
        records = await client.ledger.query(
            server=server,
            start_time=REVIEW_WINDOW_START,
            end_time=REVIEW_WINDOW_END,
            limit=100,
        )
        all_records.extend(records)
        logger.info("  %s: %d records", server, len(records))

    logger.info("Total audit records in review window: %d", len(all_records))
    return all_records


async def step_verify_chain_integrity(client: TrialMCPClient) -> None:
    """Step 3: Verify audit chain integrity."""
    logger.info("=== Step 3: Verify chain integrity ===")

    verification = await client.ledger.verify_full_chain()

    if verification.valid:
        logger.info(
            "Chain integrity VERIFIED: %d records checked, no breaks detected",
            verification.records_checked,
        )
    else:
        logger.error(
            "CHAIN INTEGRITY FAILURE at record %s: %s",
            verification.broken_at_id,
            verification.error_message,
        )
        logger.error("CRITICAL: 21 CFR Part 11 compliance violation detected")


async def step_review_provenance(client: TrialMCPClient) -> None:
    """Step 4: Review provenance of data transformations."""
    logger.info("=== Step 4: Review provenance ===")

    # Sample source IDs for review (in production, derived from audit records)
    sample_source_ids = [
        "e5f6a1b2-c3d4-7890-bcde-34567890abcd",
        "f6a1b2c3-d4e5-7890-cdef-4567890abcde",
    ]

    for source_id in sample_source_ids:
        logger.info("Reviewing provenance for source %s:", source_id)

        # Trace forward lineage
        forward = await client.provenance.query_forward(
            source_id=source_id,
            max_depth=5,
        )
        logger.info("  Forward lineage: %d records", len(forward))

        # Verify provenance integrity
        prov_check = await client.provenance.verify(source_id=source_id)
        status = "VALID" if prov_check.valid else "BROKEN"
        logger.info(
            "  Integrity: %s (%d records checked)",
            status,
            prov_check.records_checked,
        )

        if prov_check.broken_links:
            logger.warning("  Broken links: %s", prov_check.broken_links)


async def step_detect_anomalies(
    client: TrialMCPClient,
    records: list[AuditRecord],
) -> list[dict[str, Any]]:
    """Step 5: Detect anomalies in access patterns."""
    logger.info("=== Step 5: Anomaly detection ===")

    anomalies: list[dict[str, Any]] = []

    # Analysis 1: Unusual access frequency per caller
    caller_counts: Counter[str] = Counter()
    for record in records:
        caller_counts[record.caller] += 1

    if caller_counts:
        mean_count = sum(caller_counts.values()) / len(caller_counts)
        threshold = mean_count * 3  # Flag callers with 3x average activity

        for caller, count in caller_counts.most_common():
            if count > threshold:
                anomaly = {
                    "type": "high_frequency_access",
                    "caller": caller,
                    "count": count,
                    "threshold": threshold,
                }
                anomalies.append(anomaly)
                logger.warning(
                    "  ANOMALY: %s made %d calls (threshold: %.0f)",
                    caller,
                    count,
                    threshold,
                )

    # Analysis 2: Unusual tool access patterns
    tool_by_caller: dict[str, set[str]] = {}
    for record in records:
        tool_by_caller.setdefault(record.caller, set()).add(record.tool)

    for caller, tools in tool_by_caller.items():
        if len(tools) > 10:
            anomaly = {
                "type": "broad_tool_access",
                "caller": caller,
                "tool_count": len(tools),
                "tools": sorted(tools),
            }
            anomalies.append(anomaly)
            logger.warning(
                "  ANOMALY: %s accessed %d distinct tools",
                caller,
                len(tools),
            )

    # Analysis 3: Access outside normal hours (simplified check)
    off_hours_count = 0
    for record in records:
        if record.timestamp:
            hour_str = record.timestamp[11:13]
            try:
                hour = int(hour_str)
                if hour < 6 or hour > 22:
                    off_hours_count += 1
            except ValueError:
                pass

    if off_hours_count > 0:
        anomaly = {
            "type": "off_hours_access",
            "count": off_hours_count,
        }
        anomalies.append(anomaly)
        logger.warning("  ANOMALY: %d accesses outside normal hours", off_hours_count)

    if not anomalies:
        logger.info("  No anomalies detected")

    return anomalies


async def step_compliance_summary(
    client: TrialMCPClient,
    records: list[AuditRecord],
    anomalies: list[dict[str, Any]],
) -> None:
    """Step 6: Generate a compliance summary."""
    logger.info("=== Step 6: Compliance summary ===")

    # Gather statistics
    server_counts: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    caller_counts: Counter[str] = Counter()

    for record in records:
        server_counts[record.server] += 1
        tool_counts[record.tool] += 1
        caller_counts[record.caller] += 1

    logger.info("Review period: %s to %s", REVIEW_WINDOW_START, REVIEW_WINDOW_END)
    logger.info("Total records reviewed: %d", len(records))
    logger.info("Unique callers: %d", len(caller_counts))
    logger.info("Anomalies detected: %d", len(anomalies))

    logger.info("Records by server:")
    for server, count in server_counts.most_common():
        logger.info("  %s: %d", server, count)

    logger.info("Top tools by usage:")
    for tool, count in tool_counts.most_common(5):
        logger.info("  %s: %d", tool, count)

    # Record the review itself in the audit ledger
    await client.ledger.append(
        server="trialmcp-ledger",
        tool="data_monitor_review",
        caller=MONITOR_ID,
        parameters={
            "review_start": REVIEW_WINDOW_START,
            "review_end": REVIEW_WINDOW_END,
            "records_reviewed": len(records),
        },
        result_summary=(
            f"Data monitor review completed: {len(records)} records, {len(anomalies)} anomalies"
        ),
    )
    logger.info("Review recorded in audit ledger")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete data monitor review workflow."""
    logger.info("Starting data monitor review workflow for %s", MONITOR_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        await step_authenticate(client)
        records = await step_query_audit_records(client)
        await step_verify_chain_integrity(client)
        await step_review_provenance(client)
        anomalies = await step_detect_anomalies(client, records)
        await step_compliance_summary(client, records, anomalies)

    logger.info("Data monitor review workflow completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
