"""External policy engine integration (OPA-compatible).

Implements an Open Policy Agent (OPA)-compatible interface for
policy evaluation with deny-by-default semantics, decision
caching, and policy bundle loading.
"""

from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(Enum):
    """Policy evaluation outcome."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyInput:
    """Structured input for a policy evaluation request."""

    subject: str
    resource: str
    action: str
    environment: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyResult:
    """Outcome produced by the policy engine."""

    decision: Decision
    reasons: list[str] = field(default_factory=list)
    obligations: dict[str, Any] = field(default_factory=dict)
    evaluated_at: float = 0.0
    policy_version: str = ""


@dataclass
class CacheEntry:
    """A cached policy decision with TTL."""

    result: PolicyResult
    expires_at: float


class PolicyBundleLoader(ABC):
    """Abstract interface for loading policy bundles.

    A *bundle* is a versioned collection of policy rules
    (e.g. a Rego bundle in OPA).
    """

    @abstractmethod
    async def load_bundle(self, bundle_id: str) -> dict[str, Any]:
        """Fetch a policy bundle by identifier.

        Returns
        -------
        dict[str, Any]
            Bundle metadata and rules payload.
        """

    @abstractmethod
    async def list_bundles(self) -> list[dict[str, Any]]:
        """List available policy bundles."""


class PolicyEngine:
    """OPA-compatible policy evaluation engine.

    Applies **deny-by-default** semantics: a request is denied
    unless at least one policy rule explicitly allows it and no
    rule explicitly denies it.

    Parameters
    ----------
    cache_ttl_seconds:
        How long cached decisions remain valid.
    """

    def __init__(self, *, cache_ttl_seconds: int = 60) -> None:
        self._rules: list[dict[str, Any]] = []
        self._cache: dict[str, CacheEntry] = {}
        self._cache_ttl = cache_ttl_seconds
        self._policy_version = "0.0.0"

    # -- cache helpers --------------------------------------

    @staticmethod
    def _cache_key(policy_input: PolicyInput) -> str:
        """Produce a deterministic cache key."""
        blob = json.dumps(
            {
                "sub": policy_input.subject,
                "res": policy_input.resource,
                "act": policy_input.action,
                "env": policy_input.environment,
                "ctx": policy_input.context,
            },
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode()).hexdigest()

    def _get_cached(self, key: str) -> PolicyResult | None:
        """Return a cached result if still valid."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.result

    def _put_cache(self, key: str, result: PolicyResult) -> None:
        """Store a result in the decision cache."""
        self._cache[key] = CacheEntry(
            result=result,
            expires_at=time.time() + self._cache_ttl,
        )

    def clear_cache(self) -> None:
        """Flush all cached decisions."""
        self._cache.clear()

    # -- rule management ------------------------------------

    def add_rule(self, rule: dict[str, Any]) -> None:
        """Register a policy rule.

        A rule is a dict with at least ``"effect"`` (``allow``
        or ``deny``) and a ``"match"`` predicate dict whose
        keys are compared against the :class:`PolicyInput`.
        """
        if rule.get("effect") not in ("allow", "deny"):
            raise ValueError("Rule must have effect 'allow' or 'deny'")
        self._rules.append(rule)
        self.clear_cache()

    def load_rules(self, rules: list[dict[str, Any]]) -> None:
        """Bulk-load rules, replacing any existing set."""
        self._rules.clear()
        for rule in rules:
            self.add_rule(rule)

    def set_policy_version(self, version: str) -> None:
        """Record the active policy bundle version."""
        self._policy_version = version
        self.clear_cache()

    # -- evaluation -----------------------------------------

    def _match_rule(
        self,
        rule: dict[str, Any],
        policy_input: PolicyInput,
    ) -> bool:
        """Return ``True`` when a rule's match predicate
        applies to *policy_input*.
        """
        match = rule.get("match", {})
        if "subject" in match:
            if match["subject"] != policy_input.subject:
                return False
        if "resource" in match:
            if match["resource"] != policy_input.resource:
                return False
        if "action" in match:
            if match["action"] != policy_input.action:
                return False
        return True

    async def evaluate(self, policy_input: PolicyInput) -> PolicyResult:
        """Evaluate policies against *policy_input*.

        Uses deny-by-default: the result is ``ALLOW`` only when
        at least one ``allow`` rule matches **and** no ``deny``
        rule matches.

        Returns
        -------
        PolicyResult
            The evaluation outcome.
        """
        key = self._cache_key(policy_input)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        reasons: list[str] = []
        has_allow = False
        has_deny = False

        for rule in self._rules:
            if not self._match_rule(rule, policy_input):
                continue
            effect = rule["effect"]
            description = rule.get("description", "unnamed rule")
            if effect == "deny":
                has_deny = True
                reasons.append(f"deny: {description}")
            elif effect == "allow":
                has_allow = True
                reasons.append(f"allow: {description}")

        if has_deny or not has_allow:
            decision = Decision.DENY
            if not has_allow and not has_deny:
                reasons.append("deny-by-default: no matching allow rule")
        else:
            decision = Decision.ALLOW

        result = PolicyResult(
            decision=decision,
            reasons=reasons,
            evaluated_at=time.time(),
            policy_version=self._policy_version,
        )
        self._put_cache(key, result)
        return result
