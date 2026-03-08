"""Reusable access control manager.

Provides role-based (RBAC) and attribute-based (ABAC) access
control with data-classification enforcement for the National
MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataClassification(Enum):
    """Sensitivity classification levels (ascending)."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


_CLASSIFICATION_RANK: dict[DataClassification, int] = {
    DataClassification.PUBLIC: 0,
    DataClassification.INTERNAL: 1,
    DataClassification.CONFIDENTIAL: 2,
    DataClassification.RESTRICTED: 3,
}


class PermissionEffect(Enum):
    """Outcome of a permission evaluation."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class Permission:
    """A single permission entry."""

    resource: str
    action: str
    effect: PermissionEffect = PermissionEffect.ALLOW
    conditions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Role:
    """A named role carrying a set of permissions."""

    name: str
    permissions: list[Permission] = field(default_factory=list)
    max_classification: DataClassification = DataClassification.INTERNAL
    description: str = ""


@dataclass(frozen=True)
class AccessSubject:
    """A principal requesting access."""

    subject_id: str
    roles: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    clearance: DataClassification = DataClassification.PUBLIC


@dataclass(frozen=True)
class AccessRequest:
    """A structured access request."""

    subject: AccessSubject
    resource: str
    action: str
    resource_classification: DataClassification = DataClassification.INTERNAL
    environment: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AccessDecision:
    """Result of an access control evaluation."""

    effect: PermissionEffect
    reasons: list[str] = field(default_factory=list)
    matched_roles: list[str] = field(default_factory=list)
    matched_permissions: list[Permission] = field(default_factory=list)


class AccessControlManager:
    """Unified RBAC + ABAC access control manager.

    Combines role-based permission lookups with attribute-based
    condition evaluation and data-classification enforcement.
    Deny-by-default: access is denied unless an explicit allow
    is found and no deny rule matches.
    """

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        self._abac_policies: list[dict[str, Any]] = []

    # -- role management ------------------------------------

    def register_role(self, role: Role) -> None:
        """Register or replace a named role."""
        self._roles[role.name] = role

    def get_role(self, name: str) -> Role | None:
        """Retrieve a role by name."""
        return self._roles.get(name)

    def list_roles(self) -> list[Role]:
        """Return all registered roles."""
        return list(self._roles.values())

    # -- ABAC policy management -----------------------------

    def add_abac_policy(self, policy: dict[str, Any]) -> None:
        """Add an attribute-based policy rule.

        A policy dict must contain:
        - ``effect``: ``"allow"`` or ``"deny"``
        - ``condition``: a dict of attribute requirements
        """
        if policy.get("effect") not in ("allow", "deny"):
            raise ValueError("ABAC policy must have effect 'allow' or 'deny'")
        self._abac_policies.append(policy)

    # -- classification enforcement -------------------------

    @staticmethod
    def check_classification(
        subject_clearance: DataClassification,
        resource_classification: DataClassification,
    ) -> bool:
        """Return ``True`` when subject clearance meets or
        exceeds the resource classification.
        """
        return (
            _CLASSIFICATION_RANK[subject_clearance] >= _CLASSIFICATION_RANK[resource_classification]
        )

    # -- ABAC condition matching ----------------------------

    @staticmethod
    def _match_condition(
        condition: dict[str, Any],
        request: AccessRequest,
    ) -> bool:
        """Evaluate a simple attribute condition."""
        attrs = request.subject.attributes
        env = request.environment
        for key, expected in condition.items():
            if key.startswith("env."):
                actual = env.get(key[4:])
            else:
                actual = attrs.get(key)
            if actual != expected:
                return False
        return True

    # -- evaluation -----------------------------------------

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        """Evaluate an access request.

        Processing order:
        1. Data classification check.
        2. ABAC deny rules.
        3. RBAC permission matching.
        4. ABAC allow rules.

        Returns
        -------
        AccessDecision
            The final access decision.
        """
        reasons: list[str] = []
        matched_roles: list[str] = []
        matched_perms: list[Permission] = []

        # 1 -- classification gate
        if not self.check_classification(
            request.subject.clearance,
            request.resource_classification,
        ):
            reasons.append(
                "Insufficient clearance for resource "
                "classification "
                f"{request.resource_classification.value}"
            )
            return AccessDecision(
                effect=PermissionEffect.DENY,
                reasons=reasons,
            )

        # 2 -- ABAC deny rules
        for policy in self._abac_policies:
            if policy["effect"] != "deny":
                continue
            condition = policy.get("condition", {})
            if self._match_condition(condition, request):
                reasons.append("Denied by ABAC policy: " + policy.get("description", "unnamed"))
                return AccessDecision(
                    effect=PermissionEffect.DENY,
                    reasons=reasons,
                )

        # 3 -- RBAC
        for role_name in request.subject.roles:
            role = self._roles.get(role_name)
            if role is None:
                continue
            for perm in role.permissions:
                resource_match = perm.resource == "*" or perm.resource == request.resource
                action_match = perm.action == "*" or perm.action == request.action
                if resource_match and action_match:
                    if perm.effect == PermissionEffect.DENY:
                        reasons.append(f"Denied by role {role_name}")
                        return AccessDecision(
                            effect=PermissionEffect.DENY,
                            reasons=reasons,
                            matched_roles=[role_name],
                            matched_permissions=[perm],
                        )
                    matched_roles.append(role_name)
                    matched_perms.append(perm)

        if matched_perms:
            reasons.append("Allowed by RBAC")
            return AccessDecision(
                effect=PermissionEffect.ALLOW,
                reasons=reasons,
                matched_roles=matched_roles,
                matched_permissions=matched_perms,
            )

        # 4 -- ABAC allow rules
        for policy in self._abac_policies:
            if policy["effect"] != "allow":
                continue
            condition = policy.get("condition", {})
            if self._match_condition(condition, request):
                reasons.append("Allowed by ABAC policy: " + policy.get("description", "unnamed"))
                return AccessDecision(
                    effect=PermissionEffect.ALLOW,
                    reasons=reasons,
                )

        reasons.append("Deny-by-default: no matching allow rule")
        return AccessDecision(
            effect=PermissionEffect.DENY,
            reasons=reasons,
        )
