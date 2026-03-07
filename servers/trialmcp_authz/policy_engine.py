"""Deny-by-default RBAC policy engine with 6-actor policy matrix.

Implements the authorization policy evaluation logic defined in
spec/actor-model.md and spec/security.md.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from servers.storage.base import BaseStorage

# Default deny-by-default policy matrix aligned with spec/actor-model.md
DEFAULT_POLICY: dict[str, list[str]] = {
    "robot_agent": [
        "fhir_read",
        "dicom_query",
        "dicom_retrieve_pointer",
        "ledger_append",
        "provenance_record_access",
    ],
    "trial_coordinator": [
        "fhir_read",
        "fhir_search",
        "fhir_patient_lookup",
        "fhir_study_status",
        "dicom_query",
        "dicom_retrieve_pointer",
        "dicom_study_metadata",
        "authz_list_policies",
    ],
    "data_monitor": [
        "fhir_read",
        "fhir_search",
        "dicom_query",
        "dicom_study_metadata",
    ],
    "auditor": [
        "ledger_query",
        "ledger_verify",
        "ledger_replay",
        "ledger_chain_status",
    ],
    "sponsor": [
        "authz_list_policies",
    ],
    "cro": [
        "authz_list_policies",
        "fhir_study_status",
    ],
}


class PolicyEngine:
    """Deny-by-default RBAC policy engine.

    Evaluates authorization requests against a policy matrix.
    Supports persistent policy storage via the storage adapter interface.
    """

    def __init__(self, storage: BaseStorage | None = None) -> None:
        self._storage = storage
        self._policy = dict(DEFAULT_POLICY)
        if storage:
            self._load_policies()

    def _load_policies(self) -> None:
        """Load policies from persistent storage."""
        if self._storage is None:
            return
        stored = self._storage.query("policies")
        for record in stored:
            role = record.get("role", "")
            tools = record.get("tools", [])
            if role and isinstance(tools, list):
                self._policy[role] = tools

    def evaluate(
        self,
        role: str,
        tool: str,
        server: str = "trialmcp-authz",
    ) -> dict[str, Any]:
        """Evaluate an authorization request.

        Returns a schema-valid authz-decision per
        schemas/authz-decision.schema.json.
        """
        allowed_tools = self._policy.get(role, [])
        effect = "ALLOW" if tool in allowed_tools else "DENY"
        allowed = effect == "ALLOW"

        result: dict[str, Any] = {
            "allowed": allowed,
            "effect": effect,
            "role": role,
            "server": server,
            "tool": tool,
            "matching_rules": (
                [{"role": role, "server": server, "tool": tool, "effect": "ALLOW"}]
                if allowed
                else []
            ),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
        if not allowed:
            result["deny_reason"] = (
                f"Role '{role}' is denied access to tool '{tool}' by default policy."
            )
        return result

    def get_role_permissions(self, role: str) -> list[str]:
        """Get the list of allowed tools for a role."""
        return list(self._policy.get(role, []))

    def list_roles(self) -> list[str]:
        """List all roles in the policy matrix."""
        return sorted(self._policy.keys())

    def update_policy(self, role: str, tools: list[str]) -> None:
        """Update the policy for a role and persist if storage available."""
        self._policy[role] = tools
        if self._storage:
            self._storage.put("policies", role, {"role": role, "tools": tools})
