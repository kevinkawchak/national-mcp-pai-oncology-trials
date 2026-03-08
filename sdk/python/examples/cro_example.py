"""CRO multi-site validation example for the National MCP-PAI Oncology Trials SDK.

Demonstrates a Contract Research Organisation (CRO) multi-site validation workflow:
1. Authenticate as a CRO
2. Validate data consistency across sites
3. Cross-site provenance verification
4. Protocol deviation detection
5. Inter-site imaging quality review
6. Generate a multi-site validation report
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
logger = logging.getLogger("example.cro")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CRO_ID = "cro_contract_research_alpha"
TRIAL_ID = "NCT00000042"
SITE_IDS = [
    "site-east-001",
    "site-west-002",
    "site-central-003",
]
EXPECTED_MODALITIES = {"CT", "MR", "PT"}


def build_config() -> ClientConfig:
    """Build the client configuration for the CRO."""
    return ClientConfig(
        auth=AuthCredentials(
            actor_id=CRO_ID,
            role=ActorRole.CRO,
        ),
        site_id="cro-hq",
        environment="staging",
    )


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> None:
    """Step 1: Authenticate as a CRO with cross-site validation access."""
    logger.info("=== Step 1: CRO authentication ===")

    token = await client.authz.issue_token(
        subject=CRO_ID,
        role=ActorRole.CRO.value,
        ttl_seconds=14400,
    )
    logger.info("CRO session started, expires: %s", token.expires_at)

    # Verify CRO-specific permissions
    required_tools = [
        ("trialmcp-fhir", "fhir_search"),
        ("trialmcp-fhir", "fhir_study_status"),
        ("trialmcp-dicom", "dicom_query"),
        ("trialmcp-ledger", "ledger_query"),
        ("trialmcp-ledger", "ledger_verify"),
        ("trialmcp-provenance", "provenance_query_forward"),
        ("trialmcp-provenance", "provenance_verify"),
    ]
    requests = [
        {"role": ActorRole.CRO.value, "server": srv, "tool": tool} for srv, tool in required_tools
    ]
    decisions = await client.authz.batch_evaluate(requests)

    denied_count = sum(1 for d in decisions if not d.allowed)
    if denied_count > 0:
        logger.warning("%d required tools are not authorised for CRO", denied_count)
    else:
        logger.info("All %d required tools authorised", len(required_tools))


async def step_validate_data_consistency(
    client: TrialMCPClient,
) -> dict[str, Any]:
    """Step 2: Validate data consistency across sites."""
    logger.info("=== Step 2: Cross-site data consistency ===")

    consistency_results: dict[str, Any] = {
        "sites_checked": 0,
        "inconsistencies": [],
        "subject_counts": {},
    }

    # Check that each site has the expected research subjects
    for site_id in SITE_IDS:
        subjects = await client.fhir.search(
            resource_type="ResearchSubject",
            query_params={"study": TRIAL_ID, "_tag": site_id},
            max_results=100,
        )
        consistency_results["subject_counts"][site_id] = subjects.total
        logger.info("  %s: %d research subjects", site_id, subjects.total)
        consistency_results["sites_checked"] += 1

    # Check for variance in subject counts
    counts = list(consistency_results["subject_counts"].values())
    if counts:
        avg = sum(counts) / len(counts)
        for site_id, count in consistency_results["subject_counts"].items():
            if avg > 0 and abs(count - avg) / avg > 0.5:
                issue = {
                    "type": "enrolment_variance",
                    "site_id": site_id,
                    "count": count,
                    "average": avg,
                }
                consistency_results["inconsistencies"].append(issue)
                logger.warning(
                    "  VARIANCE: %s has %d subjects (avg=%.1f)",
                    site_id,
                    count,
                    avg,
                )

    return consistency_results


async def step_cross_site_provenance(client: TrialMCPClient) -> dict[str, Any]:
    """Step 3: Cross-site provenance verification."""
    logger.info("=== Step 3: Cross-site provenance ===")

    provenance_results: dict[str, Any] = {
        "sources_verified": 0,
        "verification_failures": [],
    }

    # Query provenance records and verify integrity
    sample_sources = [
        "e5f6a1b2-c3d4-7890-bcde-34567890abcd",
        "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
        "b2c3d4e5-f6a1-7890-bcde-2345678901cd",
    ]

    for source_id in sample_sources:
        # Verify provenance chain
        verification = await client.provenance.verify(source_id=source_id)
        provenance_results["sources_verified"] += 1

        if verification.valid:
            logger.info(
                "  Source %s: VALID (%d records)",
                source_id[:8],
                verification.records_checked,
            )
        else:
            provenance_results["verification_failures"].append(
                {
                    "source_id": source_id,
                    "error": verification.error_message,
                    "broken_links": verification.broken_links,
                }
            )
            logger.error(
                "  Source %s: FAILED — %s",
                source_id[:8],
                verification.error_message,
            )

        # Trace full lineage
        lineage = await client.provenance.full_lineage(source_id=source_id)
        logger.info(
            "  Lineage: %d forward, %d backward",
            len(lineage["forward"]),
            len(lineage["backward"]),
        )

    return provenance_results


async def step_protocol_deviation_detection(
    client: TrialMCPClient,
) -> list[dict[str, Any]]:
    """Step 4: Detect protocol deviations across sites."""
    logger.info("=== Step 4: Protocol deviation detection ===")

    deviations: list[dict[str, Any]] = []

    # Check audit records for unexpected tool usage patterns
    all_records = await client.ledger.query(limit=200)

    # Group by caller role
    role_tool_usage: dict[str, Counter[str]] = {}
    for record in all_records:
        caller_prefix = record.caller.split("_")[0] if "_" in record.caller else record.caller
        role_tool_usage.setdefault(caller_prefix, Counter())[record.tool] += 1

    # Check for robot agents accessing tools they should not
    robot_records = await client.ledger.query(
        caller="robot_agent",
        limit=100,
    )
    write_tools = {"ledger_export", "authz_revoke_token"}
    for record in robot_records:
        if record.tool in write_tools:
            deviation = {
                "type": "unauthorized_tool_access",
                "caller": record.caller,
                "tool": record.tool,
                "timestamp": record.timestamp,
            }
            deviations.append(deviation)
            logger.warning(
                "  DEVIATION: %s accessed %s at %s",
                record.caller,
                record.tool,
                record.timestamp,
            )

    # Check for procedure ordering violations
    procedure_records = await client.ledger.query(tool="task_order_update", limit=100)
    expected_order = ["safety_check", "in_progress", "completed"]
    task_states: dict[str, list[str]] = {}
    for record in procedure_records:
        task_id = record.parameters.get("task_id", "")
        status = record.parameters.get("status", "")
        if task_id and status:
            task_states.setdefault(task_id, []).append(status)

    for task_id, states in task_states.items():
        # Verify expected ordering
        filtered = [s for s in states if s in expected_order]
        indices = [expected_order.index(s) for s in filtered if s in expected_order]
        if indices and indices != sorted(indices):
            deviation = {
                "type": "procedure_order_violation",
                "task_id": task_id,
                "states": states,
            }
            deviations.append(deviation)
            logger.warning(
                "  DEVIATION: Task %s has out-of-order states: %s",
                task_id[:8],
                states,
            )

    if not deviations:
        logger.info("  No protocol deviations detected")

    return deviations


async def step_imaging_quality_review(client: TrialMCPClient) -> dict[str, Any]:
    """Step 5: Inter-site imaging quality review."""
    logger.info("=== Step 5: Imaging quality review ===")

    imaging_summary: dict[str, Any] = {
        "sites": {},
        "modality_counts": Counter(),
        "quality_issues": [],
    }

    for site_id in SITE_IDS:
        # Query DICOM studies for this site
        site_studies = await client.dicom.query(
            patient_pseudonym=f"hmac_site_{site_id[-3:]}",
            limit=50,
        )

        site_modalities: Counter[str] = Counter()
        for study in site_studies.studies:
            site_modalities[study.modality] += 1
            imaging_summary["modality_counts"][study.modality] += 1

        imaging_summary["sites"][site_id] = {
            "total_studies": site_studies.total,
            "modalities": dict(site_modalities),
        }

        logger.info(
            "  %s: %d studies, modalities=%s",
            site_id,
            site_studies.total,
            dict(site_modalities),
        )

        # Check for missing expected modalities
        available = set(site_modalities.keys())
        missing = EXPECTED_MODALITIES - available
        if missing and site_studies.total > 0:
            issue = {
                "site_id": site_id,
                "missing_modalities": sorted(missing),
            }
            imaging_summary["quality_issues"].append(issue)
            logger.warning(
                "  QUALITY: %s missing modalities: %s",
                site_id,
                sorted(missing),
            )

    return imaging_summary


async def step_generate_validation_report(
    client: TrialMCPClient,
    consistency: dict[str, Any],
    provenance: dict[str, Any],
    deviations: list[dict[str, Any]],
    imaging: dict[str, Any],
) -> None:
    """Step 6: Generate a multi-site validation report."""
    logger.info("=== Step 6: Multi-site validation report ===")

    total_issues = (
        len(consistency.get("inconsistencies", []))
        + len(provenance.get("verification_failures", []))
        + len(deviations)
        + len(imaging.get("quality_issues", []))
    )

    report_lines = [
        "=== CRO MULTI-SITE VALIDATION REPORT ===",
        f"CRO: {CRO_ID}",
        f"Trial: {TRIAL_ID}",
        f"Sites validated: {len(SITE_IDS)}",
        "",
        "--- Data Consistency ---",
        f"  Sites checked: {consistency.get('sites_checked', 0)}",
        f"  Inconsistencies: {len(consistency.get('inconsistencies', []))}",
        "",
        "--- Provenance Integrity ---",
        f"  Sources verified: {provenance.get('sources_verified', 0)}",
        f"  Failures: {len(provenance.get('verification_failures', []))}",
        "",
        "--- Protocol Deviations ---",
        f"  Deviations detected: {len(deviations)}",
        "",
        "--- Imaging Quality ---",
        f"  Quality issues: {len(imaging.get('quality_issues', []))}",
        "",
        f"TOTAL ISSUES: {total_issues}",
        f"VALIDATION STATUS: {'PASSED' if total_issues == 0 else 'REQUIRES REVIEW'}",
    ]

    for line in report_lines:
        logger.info(line)

    # Record the validation in the audit ledger
    await client.ledger.append(
        server="trialmcp-ledger",
        tool="cro_validation",
        caller=CRO_ID,
        parameters={
            "trial_id": TRIAL_ID,
            "sites_validated": len(SITE_IDS),
            "total_issues": total_issues,
        },
        result_summary=(f"CRO validation: {len(SITE_IDS)} sites, {total_issues} issues found"),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete CRO multi-site validation workflow."""
    logger.info("Starting CRO multi-site validation for %s", CRO_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        await step_authenticate(client)
        consistency = await step_validate_data_consistency(client)
        provenance = await step_cross_site_provenance(client)
        deviations = await step_protocol_deviation_detection(client)
        imaging = await step_imaging_quality_review(client)
        await step_generate_validation_report(client, consistency, provenance, deviations, imaging)

    logger.info("CRO multi-site validation completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
