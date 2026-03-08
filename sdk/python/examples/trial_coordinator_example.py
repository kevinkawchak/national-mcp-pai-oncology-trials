"""Trial coordinator workflow example for the National MCP-PAI Oncology Trials SDK.

Demonstrates a trial coordinator's study management workflow:
1. Authenticate as a trial coordinator
2. Create and configure a research study
3. Enrol patients into the study
4. Schedule procedures across trial sites
5. Review study status and enrolment progress
6. Export audit records for regulatory review
"""

from __future__ import annotations

import asyncio
import logging
import sys
import uuid

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
logger = logging.getLogger("example.trial_coordinator")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COORDINATOR_ID = "coordinator_dr_chen"
TRIAL_ID = "NCT00000042"
SITE_IDS = ["site-east-001", "site-west-002", "site-central-003"]


def build_config() -> ClientConfig:
    """Build the client configuration for the trial coordinator."""
    return ClientConfig(
        auth=AuthCredentials(
            actor_id=COORDINATOR_ID,
            role=ActorRole.TRIAL_COORDINATOR,
        ),
        site_id=SITE_IDS[0],
        environment="staging",
    )


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> None:
    """Step 1: Authenticate and verify coordinator permissions."""
    logger.info("=== Step 1: Authentication ===")

    token = await client.authz.issue_token(
        subject=COORDINATOR_ID,
        role=ActorRole.TRIAL_COORDINATOR.value,
        ttl_seconds=28800,  # 8-hour session
    )
    logger.info("Coordinator session started, expires: %s", token.expires_at)

    # Verify broad permissions
    decision = await client.authz.evaluate(
        role=ActorRole.TRIAL_COORDINATOR.value,
        server="trialmcp-fhir",
        tool="fhir_search",
    )
    logger.info("FHIR search permission: %s", decision.effect.value)


async def step_create_study(client: TrialMCPClient) -> None:
    """Step 2: Create a new research study via FHIR."""
    logger.info("=== Step 2: Create research study ===")

    # Read existing study or search for it
    study = await client.fhir.read_research_study(TRIAL_ID)
    logger.info(
        "Study %s loaded: type=%s",
        TRIAL_ID,
        study.resource_type,
    )

    # Record the study creation in the audit ledger
    await client.ledger.append(
        server="trialmcp-fhir",
        tool="study_create",
        caller=COORDINATOR_ID,
        parameters={
            "trial_id": TRIAL_ID,
            "title": "Phase III Multi-Site PAI Oncology Trial",
            "sites": SITE_IDS,
        },
        result_summary=f"Research study {TRIAL_ID} created with {len(SITE_IDS)} sites",
    )
    logger.info("Study creation recorded in audit ledger")


async def step_enrol_patients(client: TrialMCPClient) -> None:
    """Step 3: Enrol patients into the study."""
    logger.info("=== Step 3: Patient enrolment ===")

    # Simulate enrolling patients across sites
    patient_pseudonyms = [f"hmac_{uuid.uuid4().hex[:12]}" for _ in range(5)]

    for i, pseudonym in enumerate(patient_pseudonyms):
        site = SITE_IDS[i % len(SITE_IDS)]

        # Look up patient to verify eligibility
        patient = await client.fhir.patient_lookup(
            patient_pseudonym=pseudonym,
            include_conditions=True,
        )
        logger.info(
            "  Patient %s verified at %s (type=%s)",
            pseudonym[:16],
            site,
            patient.resource_type,
        )

        # Record enrolment event
        await client.ledger.append(
            server="trialmcp-fhir",
            tool="patient_enrol",
            caller=COORDINATOR_ID,
            parameters={
                "trial_id": TRIAL_ID,
                "site_id": site,
                "patient_pseudonym": pseudonym,
                "enrolment_index": i + 1,
            },
            result_summary=f"Patient enrolled at {site}",
        )

    logger.info("Enrolled %d patients across %d sites", len(patient_pseudonyms), len(SITE_IDS))


async def step_schedule_procedures(client: TrialMCPClient) -> None:
    """Step 4: Schedule procedures for enrolled patients."""
    logger.info("=== Step 4: Schedule procedures ===")

    procedure_types = [
        "biopsy_needle_placement",
        "diagnostic_imaging_assist",
        "radiation_positioning",
    ]

    for site in SITE_IDS:
        for proc_type in procedure_types:
            task_id = str(uuid.uuid4())
            robot_id = str(uuid.uuid4())

            await client.ledger.append(
                server="trialmcp-fhir",
                tool="procedure_schedule",
                caller=COORDINATOR_ID,
                parameters={
                    "task_id": task_id,
                    "trial_id": TRIAL_ID,
                    "site_id": site,
                    "procedure_type": proc_type,
                    "robot_id": robot_id,
                },
                result_summary=f"Scheduled {proc_type} at {site}",
            )
            logger.info("  Scheduled %s at %s (task=%s)", proc_type, site, task_id[:8])

    logger.info(
        "Scheduled %d procedures across %d sites",
        len(SITE_IDS) * len(procedure_types),
        len(SITE_IDS),
    )


async def step_review_status(client: TrialMCPClient) -> None:
    """Step 5: Review study status and enrolment progress."""
    logger.info("=== Step 5: Review study status ===")

    # Get overall study status
    status = await client.fhir.study_status(study_id=TRIAL_ID)
    logger.info(
        "Study %s: status=%s, enrolled=%d, sites=%d",
        status.study_id,
        status.status,
        status.enrollment_count,
        status.site_count,
    )

    # Search for research subjects
    subjects = await client.fhir.search_research_subjects(study_id=TRIAL_ID)
    logger.info("Found %d research subjects in study", subjects.total)

    # Check recent audit activity
    recent = await client.ledger.get_latest_records(count=5)
    logger.info("Last %d audit records:", len(recent))
    for record in recent:
        logger.info(
            "  [%s] %s/%s by %s: %s",
            record.timestamp,
            record.server,
            record.tool,
            record.caller,
            record.result_summary,
        )


async def step_export_audit(client: TrialMCPClient) -> None:
    """Step 6: Export audit records for regulatory review."""
    logger.info("=== Step 6: Export audit records ===")

    # Verify chain integrity before export
    verification = await client.ledger.verify_full_chain()
    logger.info(
        "Chain integrity: valid=%s, records=%d",
        verification.valid,
        verification.records_checked,
    )

    # Export for regulatory submission
    export_result = await client.ledger.export(
        format="jsonl",
        include_hashes=True,
    )
    logger.info("Audit export completed: %s", export_result.get("status", "unknown"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete trial coordinator workflow."""
    logger.info("Starting trial coordinator workflow for %s", COORDINATOR_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        await step_authenticate(client)
        await step_create_study(client)
        await step_enrol_patients(client)
        await step_schedule_procedures(client)
        await step_review_status(client)
        await step_export_audit(client)

    logger.info("Trial coordinator workflow completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
