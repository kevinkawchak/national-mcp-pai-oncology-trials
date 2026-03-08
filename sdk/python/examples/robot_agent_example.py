"""Robot agent workflow example for the National MCP-PAI Oncology Trials SDK.

Demonstrates a complete Physical AI robot agent workflow:
1. Authenticate and obtain a session token
2. Check authorized capabilities
3. Read patient data and imaging for procedure planning
4. Submit a task order for biopsy needle placement
5. Monitor the procedure lifecycle
6. Record provenance and verify the audit trail
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
logger = logging.getLogger("example.robot_agent")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROBOT_ID = "robot_agent_001"
TRIAL_ID = "NCT00000001"
SITE_ID = "site-east-001"
PATIENT_PSEUDONYM = "hmac_a3f8e2d1b4c5"
ROBOT_UUID = "b7e4f3a2-1c9d-4e8f-a5b6-7d2e3f4a5b6c"


def build_config() -> ClientConfig:
    """Build the client configuration for the robot agent."""
    config = ClientConfig(
        auth=AuthCredentials(
            actor_id=ROBOT_ID,
            role=ActorRole.ROBOT_AGENT,
        ),
        site_id=SITE_ID,
        environment="staging",
    )
    return config


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


async def step_authenticate(client: TrialMCPClient) -> str:
    """Step 1: Authenticate and obtain a session token."""
    logger.info("=== Step 1: Authentication ===")
    token = await client.authz.issue_token(
        subject=ROBOT_ID,
        role=ActorRole.ROBOT_AGENT.value,
        ttl_seconds=7200,
        scope=["fhir_read", "dicom_query", "dicom_retrieve", "ledger_append"],
    )
    logger.info("Session token issued, expires at: %s", token.expires_at)
    return token.token


async def step_check_capabilities(client: TrialMCPClient) -> None:
    """Step 2: Check which tools this robot agent is authorised to use."""
    logger.info("=== Step 2: Capability check ===")

    tools_to_check = [
        ("trialmcp-fhir", "fhir_read"),
        ("trialmcp-fhir", "fhir_search"),
        ("trialmcp-dicom", "dicom_query"),
        ("trialmcp-dicom", "dicom_retrieve"),
        ("trialmcp-ledger", "ledger_append"),
        ("trialmcp-provenance", "provenance_record"),
    ]

    requests = [
        {"role": ActorRole.ROBOT_AGENT.value, "server": srv, "tool": tool}
        for srv, tool in tools_to_check
    ]
    decisions = await client.authz.batch_evaluate(requests)

    for (srv, tool), decision in zip(tools_to_check, decisions):
        status = "ALLOWED" if decision.allowed else "DENIED"
        logger.info("  %s/%s: %s", srv, tool, status)


async def step_read_patient_data(client: TrialMCPClient) -> None:
    """Step 3: Read de-identified patient data for procedure planning."""
    logger.info("=== Step 3: Read patient data ===")

    # Look up the patient by pseudonym
    patient = await client.fhir.patient_lookup(
        patient_pseudonym=PATIENT_PSEUDONYM,
        include_observations=True,
        include_conditions=True,
    )
    logger.info(
        "Patient resource type: %s, ID: %s",
        patient.resource_type,
        patient.resource_id,
    )

    # Query imaging studies for procedure planning
    imaging = await client.dicom.query(
        patient_pseudonym=PATIENT_PSEUDONYM,
        modality="CT",
    )
    logger.info("Found %d CT studies for procedure planning", imaging.total)

    for study in imaging.studies:
        logger.info(
            "  Study %s: %s (%d series, %d instances)",
            study.study_instance_uid,
            study.description,
            study.series_count,
            study.instance_count,
        )


async def step_submit_task_order(client: TrialMCPClient) -> str:
    """Step 4: Submit a task order for biopsy needle placement."""
    logger.info("=== Step 4: Submit task order ===")

    task_id = str(uuid.uuid4())

    # Record the task submission in the audit ledger
    audit_record = await client.ledger.append(
        server="trialmcp-fhir",
        tool="task_order_submit",
        caller=ROBOT_ID,
        parameters={
            "task_id": task_id,
            "trial_id": TRIAL_ID,
            "site_id": SITE_ID,
            "procedure_type": "biopsy_needle_placement",
            "robot_id": ROBOT_UUID,
            "patient_pseudonym": PATIENT_PSEUDONYM,
        },
        result_summary="Task order submitted for biopsy needle placement",
    )
    logger.info("Task order %s recorded in audit ledger: %s", task_id, audit_record.audit_id)
    return task_id


async def step_monitor_procedure(client: TrialMCPClient, task_id: str) -> None:
    """Step 5: Monitor procedure lifecycle events."""
    logger.info("=== Step 5: Monitor procedure ===")

    # Simulate monitoring by recording lifecycle events
    lifecycle_events = [
        ("safety_check", "All safety prerequisites verified"),
        ("in_progress", "Biopsy needle placement procedure started"),
        ("completed", "Procedure completed successfully"),
    ]

    for status, summary in lifecycle_events:
        await client.ledger.append(
            server="trialmcp-fhir",
            tool="task_order_update",
            caller=ROBOT_ID,
            parameters={"task_id": task_id, "status": status},
            result_summary=summary,
        )
        logger.info("  Task %s -> %s: %s", task_id, status, summary)


async def step_record_provenance(client: TrialMCPClient) -> None:
    """Step 6: Record provenance for data access during the procedure."""
    logger.info("=== Step 6: Record provenance ===")

    source_id = str(uuid.uuid4())

    # Record read access to patient data
    prov_record = await client.provenance.record_read_access(
        source_id=source_id,
        source_type="fhir_resource",
        actor_id=ROBOT_ID,
        actor_role=ActorRole.ROBOT_AGENT.value,
        tool_call="fhir_read",
        origin_server="trialmcp-fhir",
        description="Robot agent read de-identified patient resource for biopsy planning",
    )
    logger.info("Provenance recorded: %s", prov_record.record_id)

    # Verify provenance integrity
    verification = await client.provenance.verify(source_id=source_id)
    logger.info(
        "Provenance verification: valid=%s, records_checked=%d",
        verification.valid,
        verification.records_checked,
    )


async def step_verify_audit_trail(client: TrialMCPClient) -> None:
    """Step 7: Verify the audit trail integrity."""
    logger.info("=== Step 7: Verify audit trail ===")

    # Query recent audit records for this robot
    records = await client.ledger.query(caller=ROBOT_ID, limit=10)
    logger.info("Found %d recent audit records for %s", len(records), ROBOT_ID)

    # Verify the chain integrity
    chain_check = await client.ledger.verify_full_chain()
    logger.info(
        "Chain verification: valid=%s, records_checked=%d",
        chain_check.valid,
        chain_check.records_checked,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the complete robot agent workflow."""
    logger.info("Starting robot agent workflow for %s", ROBOT_ID)
    config = build_config()

    async with TrialMCPClient(config) as client:
        # Execute workflow steps sequentially
        token = await step_authenticate(client)
        logger.info("Token acquired (length=%d)", len(token))

        await step_check_capabilities(client)
        await step_read_patient_data(client)
        task_id = await step_submit_task_order(client)
        await step_monitor_procedure(client, task_id)
        await step_record_provenance(client)
        await step_verify_audit_trail(client)

    logger.info("Robot agent workflow completed successfully")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))  # type: ignore[arg-type]
