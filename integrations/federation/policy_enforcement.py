"""Site-level federation policy enforcement.

Defines what data participates in federation, what computations
are allowed, result release authorization, and minimum site
count thresholds for the National MCP PAI Oncology Trials
platform.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ComputationType(Enum):
    """Types of federated computations."""

    MODEL_TRAINING = "model_training"
    AGGREGATE_STATISTICS = "aggregate_statistics"
    COHORT_DISCOVERY = "cohort_discovery"
    SURVIVAL_ANALYSIS = "survival_analysis"
    CUSTOM = "custom"


class ReleaseDecision(Enum):
    """Decision on releasing federated results."""

    APPROVED = "approved"
    DENIED = "denied"
    PENDING_REVIEW = "pending_review"


class DataParticipationScope(Enum):
    """Scope of data that may participate in federation."""

    ALL = "all"
    CONSENTED_ONLY = "consented_only"
    DEIDENTIFIED_ONLY = "deidentified_only"
    AGGREGATE_ONLY = "aggregate_only"
    NONE = "none"


@dataclass(frozen=True)
class ComputationPolicy:
    """Policy governing a type of federated computation."""

    computation_type: ComputationType
    allowed: bool = True
    max_iterations: int | None = None
    requires_approval: bool = False
    conditions: list[str] = field(default_factory=list)
    description: str = ""


@dataclass(frozen=True)
class DataParticipationPolicy:
    """Policy governing what site data enters federation."""

    site_id: str
    scope: DataParticipationScope = DataParticipationScope.DEIDENTIFIED_ONLY
    included_data_types: list[str] = field(default_factory=list)
    excluded_data_types: list[str] = field(default_factory=list)
    min_record_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultReleasePolicy:
    """Policy for releasing federated results."""

    site_id: str
    min_contributing_sites: int = 3
    require_differential_privacy: bool = True
    max_result_granularity: str = "aggregate"
    require_manual_approval: bool = False
    conditions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SiteFederationPolicy:
    """Complete federation policy for a site."""

    site_id: str
    data_participation: DataParticipationPolicy
    computation_policies: list[ComputationPolicy] = field(default_factory=list)
    result_release: ResultReleasePolicy | None = None
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Outcome of a federation policy evaluation."""

    allowed: bool
    reasons: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    evaluated_at: float = 0.0


class FederationPolicyEnforcer:
    """Enforces site-level federation policies.

    Evaluates whether a site's data may participate in a
    computation, whether the computation type is permitted,
    and whether aggregated results may be released.
    """

    def __init__(self) -> None:
        self._policies: dict[str, SiteFederationPolicy] = {}

    # -- policy management ----------------------------------

    def register_policy(self, policy: SiteFederationPolicy) -> None:
        """Register or replace a site federation policy."""
        self._policies[policy.site_id] = policy

    def get_policy(self, site_id: str) -> SiteFederationPolicy:
        """Retrieve the federation policy for a site.

        Raises
        ------
        KeyError
            If no policy is registered for the site.
        """
        policy = self._policies.get(site_id)
        if policy is None:
            raise KeyError(f"No federation policy for site {site_id!r}")
        return policy

    def list_policies(
        self,
    ) -> list[SiteFederationPolicy]:
        """List all registered federation policies."""
        return list(self._policies.values())

    # -- data participation ---------------------------------

    def check_data_participation(
        self,
        site_id: str,
        data_type: str,
    ) -> PolicyEvaluationResult:
        """Check whether a site may contribute data.

        Parameters
        ----------
        site_id:
            The participating site.
        data_type:
            The type of data to contribute.

        Returns
        -------
        PolicyEvaluationResult
            Whether participation is allowed.
        """
        reasons: list[str] = []
        policy = self.get_policy(site_id)

        if not policy.enabled:
            reasons.append("Site federation is disabled")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        dp = policy.data_participation
        if dp.scope == DataParticipationScope.NONE:
            reasons.append("Data participation scope is NONE")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if dp.excluded_data_types and data_type in dp.excluded_data_types:
            reasons.append(f"Data type {data_type!r} is excluded")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if dp.included_data_types and data_type not in dp.included_data_types:
            reasons.append(f"Data type {data_type!r} not in included types")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        reasons.append(f"Data participation allowed under scope {dp.scope.value}")
        return PolicyEvaluationResult(
            allowed=True,
            reasons=reasons,
            evaluated_at=time.time(),
        )

    # -- computation policies -------------------------------

    def check_computation(
        self,
        site_id: str,
        computation_type: ComputationType,
    ) -> PolicyEvaluationResult:
        """Check whether a computation type is allowed.

        Returns
        -------
        PolicyEvaluationResult
            Whether the computation is permitted.
        """
        reasons: list[str] = []
        conditions: list[str] = []
        policy = self.get_policy(site_id)

        if not policy.enabled:
            reasons.append("Site federation is disabled")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        for cp in policy.computation_policies:
            if cp.computation_type != computation_type:
                continue
            if not cp.allowed:
                reasons.append(f"Computation {computation_type.value} is explicitly disallowed")
                return PolicyEvaluationResult(
                    allowed=False,
                    reasons=reasons,
                    evaluated_at=time.time(),
                )
            if cp.requires_approval:
                conditions.append("Requires manual approval")
            conditions.extend(cp.conditions)
            reasons.append(f"Computation {computation_type.value} allowed")
            return PolicyEvaluationResult(
                allowed=True,
                reasons=reasons,
                conditions=conditions,
                evaluated_at=time.time(),
            )

        reasons.append(f"No policy for computation {computation_type.value}; denied by default")
        return PolicyEvaluationResult(
            allowed=False,
            reasons=reasons,
            evaluated_at=time.time(),
        )

    # -- result release -------------------------------------

    def authorize_result_release(
        self,
        site_id: str,
        contributing_site_count: int,
        *,
        has_differential_privacy: bool = False,
    ) -> PolicyEvaluationResult:
        """Authorize the release of federated results.

        Parameters
        ----------
        site_id:
            The site requesting result release.
        contributing_site_count:
            Number of sites whose data contributed.
        has_differential_privacy:
            Whether differential privacy was applied.

        Returns
        -------
        PolicyEvaluationResult
            Whether the release is authorized.
        """
        reasons: list[str] = []
        conditions: list[str] = []
        policy = self.get_policy(site_id)

        rp = policy.result_release
        if rp is None:
            reasons.append("No result release policy configured; denied by default")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if contributing_site_count < rp.min_contributing_sites:
            reasons.append(
                f"Minimum {rp.min_contributing_sites} "
                f"contributing sites required; got "
                f"{contributing_site_count}"
            )
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if rp.require_differential_privacy and not has_differential_privacy:
            reasons.append("Differential privacy is required but not applied")
            return PolicyEvaluationResult(
                allowed=False,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if rp.require_manual_approval:
            conditions.append("Manual approval required before release")

        conditions.extend(rp.conditions)
        reasons.append("Result release authorized")
        return PolicyEvaluationResult(
            allowed=True,
            reasons=reasons,
            conditions=conditions,
            evaluated_at=time.time(),
        )

    # -- minimum site thresholds ----------------------------

    def check_minimum_sites(
        self,
        site_ids: list[str],
    ) -> PolicyEvaluationResult:
        """Verify that enough sites participate.

        Uses the maximum ``min_contributing_sites`` across
        all participating sites' release policies.

        Returns
        -------
        PolicyEvaluationResult
            Whether the minimum threshold is met.
        """
        min_required = 0
        for sid in site_ids:
            try:
                policy = self.get_policy(sid)
            except KeyError:
                continue
            rp = policy.result_release
            if rp is not None:
                min_required = max(
                    min_required,
                    rp.min_contributing_sites,
                )

        if min_required == 0:
            min_required = 2  # sensible default

        if len(site_ids) >= min_required:
            return PolicyEvaluationResult(
                allowed=True,
                reasons=[f"Site count {len(site_ids)} meets minimum threshold {min_required}"],
                evaluated_at=time.time(),
            )
        return PolicyEvaluationResult(
            allowed=False,
            reasons=[f"Site count {len(site_ids)} below minimum threshold {min_required}"],
            evaluated_at=time.time(),
        )
