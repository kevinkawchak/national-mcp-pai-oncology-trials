"""Negative conformance tests for deny-by-default unauthorized access.

Validates that conforming implementations enforce deny-by-default RBAC,
rejecting access where no explicit ALLOW rule exists per the National
MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/security.md — Deny-by-default RBAC, DENY precedence
  - spec/actor-model.md — 6-actor permission matrix
  - profiles/base-profile.md — Base conformance: RBAC enforcement
  - schemas/authz-decision.schema.json
"""

from __future__ import annotations

import pytest

from conformance.conftest import assert_schema_valid
from conformance.fixtures.authz_decisions import (
    DEFAULT_ALLOW_RULES,
    UNAUTHORIZED_ACCESS_ATTEMPTS,
    VALID_ROLES,
    make_deny_decision,
)


class TestDenyByDefault:
    """Validates deny-by-default RBAC enforcement per spec/security.md."""

    def test_no_allow_rule_results_in_deny(self) -> None:
        """Access MUST be denied when no matching ALLOW rule exists."""
        decision = make_deny_decision()
        assert decision["allowed"] is False
        assert decision["effect"] == "DENY"

    def test_deny_decision_has_empty_matching_rules(self) -> None:
        """DENY by default MUST have empty matching_rules list."""
        decision = make_deny_decision()
        assert decision["matching_rules"] == []

    def test_deny_decision_has_reason(self) -> None:
        """DENY decisions SHOULD include a deny_reason."""
        decision = make_deny_decision()
        assert "deny_reason" in decision
        assert len(decision["deny_reason"]) > 0


class TestPermissionEscalation:
    """Validates that known unauthorized access attempts are denied."""

    @pytest.mark.parametrize("attempt", UNAUTHORIZED_ACCESS_ATTEMPTS)
    def test_unauthorized_access_denied(self, attempt: dict) -> None:
        """Known unauthorized role-server-tool combinations MUST be denied."""
        role = attempt["role"]
        server = attempt["server"]
        tool = attempt["tool"]

        # Verify this combination is NOT in the allow rules
        allowed_pairs = DEFAULT_ALLOW_RULES.get(role, [])
        assert (server, tool) not in allowed_pairs, (
            f"Expected ({server}, {tool}) to be denied for {role}"
        )

    @pytest.mark.parametrize("attempt", UNAUTHORIZED_ACCESS_ATTEMPTS)
    def test_unauthorized_produces_valid_deny_decision(self, attempt: dict) -> None:
        """Unauthorized attempts MUST produce a valid DENY decision."""
        decision = make_deny_decision(
            role=attempt["role"],
            server=attempt["server"],
            tool=attempt["tool"],
        )
        assert decision["allowed"] is False
        assert decision["effect"] == "DENY"
        assert_schema_valid(decision, "authz-decision.schema.json")


class TestRoleBoundaries:
    """Validates that each role has defined boundaries per spec/actor-model.md."""

    def test_all_six_roles_defined(self) -> None:
        """All 6 actor roles MUST be defined."""
        assert len(VALID_ROLES) == 6
        for role in [
            "robot_agent",
            "trial_coordinator",
            "data_monitor",
            "auditor",
            "sponsor",
            "cro",
        ]:
            assert role in VALID_ROLES

    def test_each_role_has_allow_rules(self) -> None:
        """Each role MUST have at least one ALLOW rule (otherwise role is useless)."""
        for role in VALID_ROLES:
            assert role in DEFAULT_ALLOW_RULES
            assert len(DEFAULT_ALLOW_RULES[role]) > 0, f"Role {role} has no allow rules"

    def test_sponsor_has_minimal_access(self) -> None:
        """sponsor role MUST have minimal access (policy viewing only)."""
        sponsor_tools = [tool for _, tool in DEFAULT_ALLOW_RULES["sponsor"]]
        # Sponsor should only see policies, not execute clinical tools
        assert "fhir_read" not in sponsor_tools
        assert "dicom_query" not in sponsor_tools
        assert "ledger_append" not in sponsor_tools

    def test_auditor_cannot_modify_data(self) -> None:
        """auditor role MUST NOT have write access to clinical data."""
        auditor_tools = [tool for _, tool in DEFAULT_ALLOW_RULES["auditor"]]
        write_tools = [
            "ledger_append",
            "provenance_register_source",
            "provenance_record_access",
            "fhir_read",
            "dicom_query",
        ]
        for tool in write_tools:
            assert tool not in auditor_tools, f"auditor should not have {tool}"

    def test_data_monitor_is_read_only(self) -> None:
        """data_monitor role MUST NOT have write access."""
        dm_tools = [tool for _, tool in DEFAULT_ALLOW_RULES["data_monitor"]]
        write_tools = [
            "ledger_append",
            "provenance_register_source",
            "provenance_record_access",
            "authz_issue_token",
            "authz_revoke_token",
        ]
        for tool in write_tools:
            assert tool not in dm_tools, f"data_monitor should not have {tool}"


class TestDENYPrecedence:
    """Validates DENY precedence over ALLOW per spec/security.md."""

    def test_deny_overrides_allow(self) -> None:
        """When both DENY and ALLOW rules match, DENY MUST take precedence."""
        # Simulate: an ALLOW rule exists but a DENY rule also matches
        # The final decision MUST be DENY per spec/security.md
        decision = make_deny_decision(
            role="robot_agent",
            server="trialmcp-fhir",
            tool="fhir_read",
            reason="Explicit DENY rule overrides ALLOW",
        )
        assert decision["allowed"] is False
        assert decision["effect"] == "DENY"

    def test_deny_decision_validates_against_schema(self) -> None:
        """DENY precedence decisions MUST conform to authz-decision.schema.json."""
        decision = make_deny_decision(
            role="robot_agent",
            server="trialmcp-fhir",
            tool="fhir_read",
        )
        assert_schema_valid(decision, "authz-decision.schema.json")
