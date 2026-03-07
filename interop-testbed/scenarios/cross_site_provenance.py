"""Cross-site provenance trace and DAG merge scenario.

Validates that provenance records created at Site A and Site B
can be merged into a coherent DAG at the sponsor level, with
all lineage relationships preserved across site boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProvenanceTrace:
    """A cross-site provenance trace entry."""

    site: str
    record_id: str
    source_type: str
    action: str
    parent_ids: list[str] = field(default_factory=list)


def build_cross_site_dag() -> list[ProvenanceTrace]:
    """Build a cross-site provenance DAG.

    Returns:
        List of ProvenanceTrace entries spanning Site A and Site B.
    """
    traces = [
        ProvenanceTrace(
            site="site-a",
            record_id="prov-a-001",
            source_type="fhir_resource",
            action="read",
        ),
        ProvenanceTrace(
            site="site-a",
            record_id="prov-a-002",
            source_type="dicom_study",
            action="read",
            parent_ids=["prov-a-001"],
        ),
        ProvenanceTrace(
            site="site-b",
            record_id="prov-b-001",
            source_type="fhir_resource",
            action="read",
        ),
        ProvenanceTrace(
            site="sponsor",
            record_id="prov-s-001",
            source_type="model_parameters",
            action="aggregate",
            parent_ids=["prov-a-002", "prov-b-001"],
        ),
    ]
    return traces


def verify_dag_integrity(traces: list[ProvenanceTrace]) -> bool:
    """Verify that all parent references in the DAG are valid.

    Args:
        traces: List of provenance traces to verify.

    Returns:
        True if all parent references resolve to existing records.
    """
    record_ids = {t.record_id for t in traces}
    for trace in traces:
        for parent_id in trace.parent_ids:
            if parent_id not in record_ids:
                return False
    return True


def run_scenario() -> dict[str, Any]:
    """Execute the cross-site provenance scenario.

    Returns:
        Scenario result with pass/fail status and details.
    """
    dag = build_cross_site_dag()
    integrity = verify_dag_integrity(dag)

    return {
        "scenario": "cross_site_provenance",
        "passed": integrity,
        "total_traces": len(dag),
        "sites": list({t.site for t in dag}),
        "dag_valid": integrity,
    }
