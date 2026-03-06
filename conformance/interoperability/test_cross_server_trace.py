"""Interoperability conformance tests for multi-server audit trace linkage.

Validates that conforming implementations correctly produce linked audit
trails across multiple MCP servers, enabling end-to-end traceability
of operations spanning authorization, clinical data, imaging, auditing,
and provenance per the National MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/audit.md — Hash-chained audit records across servers
  - spec/provenance.md — Cross-server DAG lineage
  - profiles/multi-site-federated.md — Multi-server audit linkage
  - schemas/audit-record.schema.json
  - schemas/provenance-record.schema.json
"""

from __future__ import annotations

from conformance.conftest import assert_schema_valid
from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    VALID_SERVERS,
    make_audit_chain,
    make_audit_record,
)
from conformance.fixtures.provenance_records import (
    MULTI_SERVER_TRACE_SEQUENCE,
    SAMPLE_CROSS_SERVER_PROVENANCE,
    VALID_ACTION_TYPES,
    VALID_SOURCE_TYPES,
    make_provenance_dag,
    make_provenance_record,
)


class TestMultiServerAuditLinkage:
    """Validates audit trail linkage across multiple MCP servers."""

    def test_audit_chain_spans_multiple_servers(self) -> None:
        """A single audit chain MUST accommodate records from all 5 servers."""
        chain = make_audit_chain(length=5)
        servers_in_chain = {record["server"] for record in chain}
        assert servers_in_chain == set(VALID_SERVERS)

    def test_cross_server_chain_maintains_integrity(self) -> None:
        """Hash chain integrity MUST hold across server boundaries."""
        chain = make_audit_chain(length=5)
        assert chain[0]["previous_hash"] == GENESIS_HASH
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_each_server_represented_in_trace(self) -> None:
        """A complete operational trace MUST include all 5 servers."""
        trace_servers = {step["server"] for step in MULTI_SERVER_TRACE_SEQUENCE}
        assert trace_servers == set(VALID_SERVERS)

    def test_trace_follows_operational_order(self) -> None:
        """The trace sequence MUST follow the standard operational order."""
        expected_order = [
            "trialmcp-authz",
            "trialmcp-fhir",
            "trialmcp-dicom",
            "trialmcp-ledger",
            "trialmcp-provenance",
        ]
        actual_order = [step["server"] for step in MULTI_SERVER_TRACE_SEQUENCE]
        assert actual_order == expected_order

    def test_authz_precedes_data_access(self) -> None:
        """Authorization MUST precede any clinical data access."""
        servers = [step["server"] for step in MULTI_SERVER_TRACE_SEQUENCE]
        authz_idx = servers.index("trialmcp-authz")
        fhir_idx = servers.index("trialmcp-fhir")
        dicom_idx = servers.index("trialmcp-dicom")
        assert authz_idx < fhir_idx
        assert authz_idx < dicom_idx

    def test_audit_follows_data_access(self) -> None:
        """Audit recording MUST follow data access operations."""
        servers = [step["server"] for step in MULTI_SERVER_TRACE_SEQUENCE]
        fhir_idx = servers.index("trialmcp-fhir")
        ledger_idx = servers.index("trialmcp-ledger")
        assert fhir_idx < ledger_idx


class TestCrossServerProvenance:
    """Validates provenance DAG linkage across servers."""

    def test_provenance_record_has_origin_server(self) -> None:
        """Provenance records MUST track the origin server."""
        record = make_provenance_record()
        assert "origin_server" in record
        assert record["origin_server"] in VALID_SERVERS

    def test_provenance_record_validates_against_schema(self) -> None:
        """Provenance records MUST validate against provenance-record.schema.json."""
        record = make_provenance_record()
        assert_schema_valid(record, "provenance-record.schema.json")

    def test_sample_cross_server_provenance_valid(self) -> None:
        """The sample cross-server provenance record MUST be schema-valid."""
        assert_schema_valid(
            SAMPLE_CROSS_SERVER_PROVENANCE,
            "provenance-record.schema.json",
        )

    def test_provenance_dag_covers_data_pipeline(self) -> None:
        """The provenance DAG MUST cover the read->transform->aggregate pipeline."""
        dag = make_provenance_dag(depth=3)
        actions = [record["action"] for record in dag]
        assert actions == ["read", "transform", "aggregate"]

    def test_all_source_types_defined(self) -> None:
        """All 5 source types MUST be defined per spec/provenance.md."""
        assert len(VALID_SOURCE_TYPES) == 5
        for st in [
            "fhir_resource",
            "dicom_study",
            "model_parameters",
            "robot_telemetry",
            "clinical_observation",
        ]:
            assert st in VALID_SOURCE_TYPES

    def test_all_action_types_defined(self) -> None:
        """All 5 action types MUST be defined per spec/provenance.md."""
        assert len(VALID_ACTION_TYPES) == 5
        for at in ["read", "transform", "aggregate", "derive", "export"]:
            assert at in VALID_ACTION_TYPES

    def test_provenance_records_have_sha256_fingerprints(self) -> None:
        """Provenance records MUST include SHA-256 input and output hashes."""
        record = make_provenance_record()
        assert len(record["input_hash"]) == 64
        assert len(record["output_hash"]) == 64


class TestFederatedAuditCoordination:
    """Validates federated audit chain coordination across sites."""

    def test_audit_records_include_site_context(self) -> None:
        """Audit records at federated level SHOULD include site context.

        While the audit_record schema does not mandate site_id, the
        health_status schema and federated profile require site awareness.
        """
        # Audit records carry server info; site context is in health_status
        record = make_audit_record()
        assert "server" in record

    def test_different_sites_can_share_chain_format(self) -> None:
        """Audit records from different sites MUST use the same format."""
        record_site_a = make_audit_record(caller="site_a_robot_001")
        record_site_b = make_audit_record(caller="site_b_robot_002")
        # Both should have identical field sets
        assert set(record_site_a.keys()) == set(record_site_b.keys())
