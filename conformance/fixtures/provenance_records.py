"""Sample provenance DAG records for conformance testing.

Extracted from schemas/provenance-record.schema.json and spec/provenance.md.
Provides valid provenance records and DAG structures for lineage testing.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

# Valid source types per spec/provenance.md
VALID_SOURCE_TYPES = [
    "fhir_resource",
    "dicom_study",
    "model_parameters",
    "robot_telemetry",
    "clinical_observation",
]

# Valid action types per spec/provenance.md
VALID_ACTION_TYPES = [
    "read",
    "transform",
    "aggregate",
    "derive",
    "export",
]

# Valid actor roles per spec/actor-model.md
VALID_ACTOR_ROLES = [
    "robot_agent",
    "trial_coordinator",
    "data_monitor",
    "auditor",
    "sponsor",
    "cro",
]


def compute_sha256(data: str) -> str:
    """Compute SHA-256 hex digest of input data."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def make_provenance_record(
    source_type: str = "fhir_resource",
    action: str = "read",
    actor_role: str = "robot_agent",
    tool_call: str = "fhir_read",
    origin_server: str = "trialmcp-fhir",
) -> dict:
    """Create a well-formed provenance record conforming to provenance-record.schema.json."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    input_data = f"input-{uuid.uuid4()}"
    output_data = f"output-{uuid.uuid4()}"
    return {
        "record_id": str(uuid.uuid4()),
        "source_id": str(uuid.uuid4()),
        "source_type": source_type,
        "action": action,
        "actor_id": f"{actor_role}_001",
        "actor_role": actor_role,
        "tool_call": tool_call,
        "input_hash": compute_sha256(input_data),
        "output_hash": compute_sha256(output_data),
        "timestamp": now,
        "origin_server": origin_server,
        "description": f"{actor_role} performed {action} on {source_type} via {tool_call}",
    }


def make_provenance_dag(depth: int = 3) -> list[dict]:
    """Build a DAG of provenance records simulating a multi-step data pipeline.

    Creates a chain: fhir_read -> transform -> aggregate, representing a
    typical national-scale data flow from FHIR resource to federated aggregate.
    """
    dag: list[dict] = []
    actions = ["read", "transform", "aggregate"]
    source_types = ["fhir_resource", "fhir_resource", "model_parameters"]
    tools = ["fhir_read", "provenance_record_access", "provenance_record_access"]

    for i in range(min(depth, len(actions))):
        record = make_provenance_record(
            source_type=source_types[i],
            action=actions[i],
            tool_call=tools[i],
        )
        dag.append(record)
    return dag


# Pre-built fixture: cross-server provenance record
SAMPLE_CROSS_SERVER_PROVENANCE = {
    "record_id": "d4e5f6a1-b2c3-7890-abcd-234567890abc",
    "source_id": "e5f6a1b2-c3d4-7890-bcde-34567890abcd",
    "source_type": "fhir_resource",
    "action": "read",
    "actor_id": "robot_agent_001",
    "actor_role": "robot_agent",
    "tool_call": "fhir_read",
    "input_hash": ("b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3"),
    "output_hash": ("c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"),
    "timestamp": "2026-03-06T14:30:00Z",
    "origin_server": "trialmcp-fhir",
    "description": "Robot agent read de-identified patient resource for procedure planning",
}

# Pre-built fixture: multi-server audit trace for interoperability testing
MULTI_SERVER_TRACE_SEQUENCE = [
    {
        "server": "trialmcp-authz",
        "tool": "authz_evaluate",
        "description": "Authorization check for robot agent",
    },
    {
        "server": "trialmcp-fhir",
        "tool": "fhir_read",
        "description": "Read de-identified patient record",
    },
    {
        "server": "trialmcp-dicom",
        "tool": "dicom_query",
        "description": "Query imaging studies for patient",
    },
    {
        "server": "trialmcp-ledger",
        "tool": "ledger_append",
        "description": "Record audit trail entry",
    },
    {
        "server": "trialmcp-provenance",
        "tool": "provenance_record_access",
        "description": "Record data lineage in provenance DAG",
    },
]
