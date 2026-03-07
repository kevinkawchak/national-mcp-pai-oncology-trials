"""Black-box end-to-end workflow conformance tests.

Tests that validate the complete robot agent workflow across all 5
MCP servers: authorization → FHIR → DICOM → ledger → provenance.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.audit_records import VALID_SERVERS, make_audit_chain
from conformance.fixtures.authz_decisions import DEFAULT_ALLOW_RULES, make_allow_decision
from conformance.fixtures.clinical_resources import (
    make_deidentified_patient,
)
from conformance.fixtures.provenance_records import (
    MULTI_SERVER_TRACE_SEQUENCE,
)


@pytest.mark.blackbox
class TestCrossServerWorkflow:
    """End-to-end cross-server workflow conformance tests."""

    def test_five_server_workflow_order(self):
        """Workflow MUST follow: authz → fhir → dicom → ledger → provenance."""
        expected_order = [
            "trialmcp-authz",
            "trialmcp-fhir",
            "trialmcp-dicom",
            "trialmcp-ledger",
            "trialmcp-provenance",
        ]
        actual_order = [step["server"] for step in MULTI_SERVER_TRACE_SEQUENCE]
        assert actual_order == expected_order

    def test_robot_agent_authorized_for_workflow(self):
        """Robot agent MUST be authorized for workflow tools."""
        robot_perms = DEFAULT_ALLOW_RULES["robot_agent"]
        required_tools = [
            ("trialmcp-fhir", "fhir_read"),
            ("trialmcp-dicom", "dicom_query"),
            ("trialmcp-ledger", "ledger_append"),
            ("trialmcp-provenance", "provenance_record_access"),
        ]
        for server, tool in required_tools:
            assert (server, tool) in robot_perms, f"Robot agent missing permission: {server}/{tool}"

    def test_audit_chain_spans_all_servers(self):
        """Audit chain MUST span all 5 servers."""
        chain = make_audit_chain(length=5)
        servers = {r["server"] for r in chain}
        assert servers == set(VALID_SERVERS)

    def test_workflow_produces_deidentified_data(self):
        """FHIR step MUST produce de-identified data."""
        patient = make_deidentified_patient()
        assert patient["name"] == "[REDACTED]"

    def test_workflow_produces_provenance_trace(self):
        """Each workflow step MUST produce a provenance record."""
        for step in MULTI_SERVER_TRACE_SEQUENCE:
            assert "server" in step
            assert "tool" in step
            assert "description" in step


@pytest.mark.blackbox
class TestTokenExchangeWorkflow:
    """Token-based workflow conformance tests."""

    def test_robot_token_enables_fhir_access(self):
        """Robot token MUST enable FHIR read access."""
        decision = make_allow_decision(
            role="robot_agent",
            server="trialmcp-fhir",
            tool="fhir_read",
        )
        assert decision["allowed"] is True

    def test_robot_token_enables_dicom_access(self):
        """Robot token MUST enable DICOM query access."""
        decision = make_allow_decision(
            role="robot_agent",
            server="trialmcp-dicom",
            tool="dicom_query",
        )
        assert decision["allowed"] is True

    def test_robot_token_enables_ledger_access(self):
        """Robot token MUST enable ledger append access."""
        decision = make_allow_decision(
            role="robot_agent",
            server="trialmcp-ledger",
            tool="ledger_append",
        )
        assert decision["allowed"] is True
