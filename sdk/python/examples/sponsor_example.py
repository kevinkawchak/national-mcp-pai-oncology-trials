"""Sponsor cross-site oversight example for the National MCP-PAI Oncology Trials SDK.

Demonstrates a sponsor's multi-site oversight workflow:
1. Authenticate as a sponsor
2. Query study status across all trial sites
3. Aggregate enrolment and procedure metrics
4. Review cross-site audit compliance
5. Generate a multi-site status report
6. Export aggregated data for regulatory submission
"""

from __future__ import annotations

import asyncio
import logging
import sys
from collections import Counter
from typing import Any

from trialmcp_client import (
    ActorRole,
    AuthCredentials,
    ClientConfig,
    TrialMCPClient,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("example.sponsor")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SPONSOR_ID = "sponsor_pharma_global"
TRIAL_IDS = ["NCT00000042", "NCT00000099", "NCT00000128"]
SITE_IDS = [
    "site-east-001",
    "site-west-002",
    "site-central-003",
    "site-south-004",
    "site-north-005",
]


def build_config() -> ClientConfig:
    """Build the client configuration for the sponsor."""
    return ClientConfig(
        auth=AuthCredentials(
            actor_id=SPONSOR_ID,
            role=ActorRole.SPONSOR,
        ),
        site_id="sponsor-hq",
        environment="staging",
    )


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> None:
    """Step 1: Authenticate as a sponsor with cross-site read access."""
    logger.info("=== Step 1: Sponsor authentication ===")

    token = await client.authz.issue_token(
        subject=SPONSOR_ID,
        role=ActorRole.SPONSOR.value,
        ttl_seconds=14400,
    )
    logger.info("Sponsor session started, expires: %s", token.expires_at)

    # Verify sponsor permissions
    access_checks = [
        {"role": ActorRole.SPONSOR.value, "server": "trialmcp-fhir", "tool": "fhir_search"},
        {"role": ActorRole.SPONSOR.value, "server": "trialmcp-fhir", "tool": "fhir_study_status"},
        {"role": ActorRole.SPONSOR.value, "server": "trialmcp-ledger", "tool": "ledger_query"},
        {"role": ActorRole.SPONSOR.value, "server": "trialmcp-ledger", "tool": "ledger_export"},
    ]
    decisions = await client.authz.batch_evaluate(access_checks)
    for check, decision in zip(access_checks, decisions):
        logger.info("  %s/%s: %s", check["server"], check["tool"], decision.effect.value)


async def step_multi_site_status(client: TrialMCPClient) -> dict[str, Any]:
    """Step 2: Query study status across all trial sites."""
    logger.info("=== Step 2: Multi-site study status ===")

    study_data: dict[str, Any] = {}

    for trial_id in TRIAL_IDS:
        status = await client.fhir.study_status(study_id=trial_id)
        study_data[trial_id] = {
            "status": status.status,
            "title": status.title,
            "enrollment": status.enrollment_count,
            "sites": status.site_count,
            "last_updated": status.last_updated,
        }
        logger.info(
            "  %s: status=%s, enrolled=%d, sites=%d",
            trial_id,
            status.status,
            status.enrollment_count,
            status.site_count,
        )

    return study_data


async def step_aggregate_metrics(
    client: TrialMCPClient,
) -> dict[str, Any]:
    """Step 3: Aggregate enrolment and procedure metrics across sites."""
    logger.info("=== Step 3: Aggregate metrics ===")

    metrics: dict[str, Any] = {
        "total_subjects": 0,
        "subjects_by_site": {},
        "procedures_by_type": Counter(),
        "active_robots": set(),
    }

    for trial_id in TRIAL_IDS:
        # Search for research subjects in each trial
        subjects = await client.fhir.search(
            resource_type="ResearchSubject",
            query_params={"study": trial_id},
            max_results=100,
        )
        metrics["total_subjects"] += subjects.total
        logger.info("  %s: %d subjects", trial_id, subjects.total)

    # Query audit records to count procedure types
    for site_id in SITE_IDS:
        records = await client.ledger.query(
            tool="procedure_schedule",
            limit=100,
        )
        metrics["subjects_by_site"][site_id] = len(records)

        for record in records:
            proc_type = record.parameters.get("procedure_type", "unknown")
            metrics["procedures_by_type"][proc_type] += 1
            robot_id = record.parameters.get("robot_id")
            if robot_id:
                metrics["active_robots"].add(robot_id)

    # Convert set to list for serialisation
    metrics["active_robots"] = list(metrics["active_robots"])

    logger.info("Aggregate metrics:")
    logger.info("  Total subjects: %d", metrics["total_subjects"])
    logger.info("  Active robots: %d", len(metrics["active_robots"]))
    logger.info("  Procedures by type:")
    for proc_type, count in metrics["procedures_by_type"].most_common():
        logger.info("    %s: %d", proc_type, count)

    return metrics


async def step_cross_site_compliance(client: TrialMCPClient) -> dict[str, Any]:
    """Step 4: Review cross-site audit compliance."""
    logger.info("=== Step 4: Cross-site compliance review ===")

    compliance: dict[str, Any] = {
        "sites_verified": 0,
        "sites_with_issues": [],
        "total_records": 0,
    }

    # Verify chain integrity
    verification = await client.ledger.verify_full_chain()
    compliance["chain_valid"] = verification.valid
    compliance["total_records"] = verification.records_checked

    if verification.valid:
        logger.info(
            "Chain integrity verified across %d records",
            verification.records_checked,
        )
    else:
        logger.error(
            "Chain integrity FAILED at %s",
            verification.broken_at_id,
        )

    # Check each server's health
    health = await client.health_check_all()
    for server_name, status in health.items():
        server_status = status.get("status", "unknown")
        logger.info("  %s: %s", server_name, server_status)

    # Check circuit breaker states
    cb_status = client.circuit_breakers.status()
    for server_name, cb_state in cb_status.items():
        if cb_state["state"] != "closed":
            compliance["sites_with_issues"].append(
                {
                    "server": server_name,
                    "circuit_breaker": cb_state["state"],
                }
            )
            logger.warning(
                "  Circuit breaker for %s is %s",
                server_name,
                cb_state["state"],
            )

    compliance["sites_verified"] = len(SITE_IDS)
    return compliance


async def step_generate_report(
    client: TrialMCPClient,
    study_data: dict[str, Any],
    metrics: dict[str, Any],
    compliance: dict[str, Any],
) -> None:
    """Step 5: Generate a multi-site status report."""
    logger.info("=== Step 5: Multi-site status report ===")

    report_lines = [
        "=== SPONSOR MULTI-SITE STATUS REPORT ===",
        f"Sponsor: {SPONSOR_ID}",
        f"Trials monitored: {len(TRIAL_IDS)}",
        f"Sites monitored: {len(SITE_IDS)}",
        "",
        "--- Study Status ---",
    ]
    for trial_id, data in study_data.items():
        report_lines.append(
            f"  {trial_id}: {data['status']} (enrolled={data['enrollment']}, sites={data['sites']})"
        )

    report_lines.extend(
        [
            "",
            "--- Aggregate Metrics ---",
            f"  Total subjects: {metrics['total_subjects']}",
            f"  Active robots: {len(metrics.get('active_robots', []))}",
            "",
            "--- Compliance ---",
            f"  Chain integrity: {'VALID' if compliance.get('chain_valid') else 'INVALID'}",
            f"  Records verified: {compliance.get('total_records', 0)}",
            f"  Sites verified: {compliance.get('sites_verified', 0)}",
            f"  Issues found: {len(compliance.get('sites_with_issues', []))}",
        ]
    )

    for line in report_lines:
        logger.info(line)


async def step_export_data(client: TrialMCPClient) -> None:
    """Step 6: Export aggregated data for regulatory submission."""
    logger.info("=== Step 6: Export for regulatory submission ===")

    export_result = await client.ledger.export(
        format="jsonl",
        include_hashes=True,
    )
    logger.info("Audit data exported: %s", export_result.get("status", "completed"))

    # Record the export event
    await client.ledger.append(
        server="trialmcp-ledger",
        tool="sponsor_export",
        caller=SPONSOR_ID,
        parameters={
            "trials": TRIAL_IDS,
            "sites": SITE_IDS,
            "format": "jsonl",
        },
        result_summary=(f"Sponsor data export for {len(TRIAL_IDS)} trials, {len(SITE_IDS)} sites"),
    )
    logger.info("Export recorded in audit ledger")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete sponsor oversight workflow."""
    logger.info("Starting sponsor oversight workflow for %s", SPONSOR_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        await step_authenticate(client)
        study_data = await step_multi_site_status(client)
        metrics = await step_aggregate_metrics(client)
        compliance = await step_cross_site_compliance(client)
        await step_generate_report(client, study_data, metrics, compliance)
        await step_export_data(client)

    logger.info("Sponsor oversight workflow completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
