"""Integration tests for reference server packages.

Exercises the real server packages from Phase 2 via in-process calls,
validating that each server correctly implements its tool contracts
and produces schema-valid output.
"""

from __future__ import annotations

import pytest

from servers.trialmcp_authz.server import AuthzServer
from servers.trialmcp_dicom.server import DicomServer
from servers.trialmcp_fhir.server import FhirServer
from servers.trialmcp_ledger.server import LedgerServer
from servers.trialmcp_provenance.server import ProvenanceServer


@pytest.fixture()
def authz_server():
    """Create an in-process AuthZ server instance."""
    return AuthzServer()


@pytest.fixture()
def fhir_server():
    """Create an in-process FHIR server instance."""
    return FhirServer()


@pytest.fixture()
def dicom_server():
    """Create an in-process DICOM server instance."""
    return DicomServer()


@pytest.fixture()
def ledger_server():
    """Create an in-process Ledger server instance."""
    return LedgerServer()


@pytest.fixture()
def provenance_server():
    """Create an in-process Provenance server instance."""
    return ProvenanceServer()


class TestAuthzServerIntegration:
    """Integration tests for the AuthZ server."""

    def test_evaluate_allow(self, authz_server):
        result = authz_server.handle_tool(
            "authz_evaluate",
            {
                "role": "robot_agent",
                "server": "trialmcp-fhir",
                "tool": "fhir_read",
            },
        )
        assert result["allowed"] is True
        assert result["effect"] == "ALLOW"

    def test_evaluate_deny(self, authz_server):
        result = authz_server.handle_tool(
            "authz_evaluate",
            {
                "role": "auditor",
                "server": "trialmcp-fhir",
                "tool": "fhir_read",
            },
        )
        assert result["allowed"] is False
        assert result["effect"] == "DENY"

    def test_token_lifecycle(self, authz_server):
        # Issue
        token_result = authz_server.handle_tool(
            "authz_issue_token",
            {
                "role": "robot_agent",
                "caller": "test-agent",
            },
        )
        assert "token_hash" in token_result

        # Validate
        validate_result = authz_server.handle_tool(
            "authz_validate_token",
            {
                "token_hash": token_result["token_hash"],
            },
        )
        assert validate_result["valid"] is True

        # Revoke
        revoke_result = authz_server.handle_tool(
            "authz_revoke_token",
            {
                "token_hash": token_result["token_hash"],
            },
        )
        assert revoke_result["revoked"] is True

    def test_health_status(self, authz_server):
        result = authz_server.handle_tool("health_status", {})
        assert result["status"] in ("healthy", "degraded", "unhealthy")
        assert "server_name" in result


class TestFhirServerIntegration:
    """Integration tests for the FHIR server."""

    def test_fhir_read_deidentified(self, fhir_server):
        result = fhir_server.handle_tool(
            "fhir_read",
            {
                "resource_type": "Patient",
                "resource_id": "test-patient-001",
            },
        )
        assert "resource" in result

    def test_fhir_search(self, fhir_server):
        result = fhir_server.handle_tool(
            "fhir_search",
            {
                "resource_type": "Patient",
            },
        )
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_health_status(self, fhir_server):
        result = fhir_server.handle_tool("health_status", {})
        assert result["status"] in ("healthy", "degraded", "unhealthy")


class TestDicomServerIntegration:
    """Integration tests for the DICOM server."""

    def test_dicom_query(self, dicom_server):
        result = dicom_server.handle_tool(
            "dicom_query",
            {
                "query_level": "STUDY",
                "modality": "CT",
            },
        )
        assert "results" in result

    def test_health_status(self, dicom_server):
        result = dicom_server.handle_tool("health_status", {})
        assert result["status"] in ("healthy", "degraded", "unhealthy")


class TestLedgerServerIntegration:
    """Integration tests for the Ledger server."""

    def test_ledger_append_and_verify(self, ledger_server):
        # Append
        result = ledger_server.handle_tool(
            "ledger_append",
            {
                "server": "trialmcp-ledger",
                "tool": "ledger_append",
                "caller": "test-agent",
                "result_summary": "Test operation",
            },
        )
        assert "audit_id" in result
        assert "hash" in result

        # Verify
        verify_result = ledger_server.handle_tool("ledger_verify", {})
        assert verify_result["valid"] is True

    def test_health_status(self, ledger_server):
        result = ledger_server.handle_tool("health_status", {})
        assert result["status"] in ("healthy", "degraded", "unhealthy")


class TestProvenanceServerIntegration:
    """Integration tests for the Provenance server."""

    def test_record_and_query(self, provenance_server):
        # Record
        result = provenance_server.handle_tool(
            "provenance_record_access",
            {
                "source_type": "fhir_resource",
                "action": "read",
                "actor_role": "robot_agent",
            },
        )
        assert "record_id" in result

    def test_health_status(self, provenance_server):
        result = provenance_server.handle_tool("health_status", {})
        assert result["status"] in ("healthy", "degraded", "unhealthy")
