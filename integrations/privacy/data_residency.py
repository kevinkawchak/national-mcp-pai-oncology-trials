"""Data residency enforcement.

Enforces site-level data-boundary policies, authorizes
cross-site transfers, and applies jurisdiction-specific
retention rules (US federal, California CCPA, New York PHL).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Jurisdiction(Enum):
    """Supported legal jurisdictions."""

    US_FEDERAL = "us_federal"
    CALIFORNIA_CCPA = "california_ccpa"
    NEW_YORK_PHL = "new_york_phl"


class TransferDecision(Enum):
    """Outcome of a cross-site transfer request."""

    APPROVED = "approved"
    DENIED = "denied"
    PENDING_REVIEW = "pending_review"


class DataCategory(Enum):
    """Categories of regulated data."""

    PHI = "phi"
    PII = "pii"
    GENOMIC = "genomic"
    IMAGING = "imaging"
    MODEL_WEIGHTS = "model_weights"
    AGGREGATE_STATS = "aggregate_stats"


@dataclass(frozen=True)
class RetentionRule:
    """A jurisdiction-specific data retention rule."""

    jurisdiction: Jurisdiction
    data_category: DataCategory
    min_retention_days: int
    max_retention_days: int | None = None
    requires_deletion_proof: bool = False
    description: str = ""


@dataclass(frozen=True)
class SiteBoundaryPolicy:
    """Data boundary policy for a single site."""

    site_id: str
    jurisdiction: Jurisdiction
    allowed_data_categories: list[DataCategory] = field(default_factory=lambda: list(DataCategory))
    allow_outbound_transfer: bool = False
    allowed_destination_sites: list[str] = field(default_factory=list)
    retention_rules: list[RetentionRule] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransferRequest:
    """A request to move data across site boundaries."""

    request_id: str
    source_site_id: str
    destination_site_id: str
    data_category: DataCategory
    justification: str
    requested_at: float = 0.0
    requested_by: str = ""


@dataclass(frozen=True)
class TransferAuthorizationResult:
    """Result of evaluating a cross-site transfer request."""

    request_id: str
    decision: TransferDecision
    reasons: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    evaluated_at: float = 0.0


# -- default retention rules --------------------------------

_DEFAULT_RETENTION_RULES: list[RetentionRule] = [
    # US Federal (HIPAA: 6 years from creation/last use)
    RetentionRule(
        jurisdiction=Jurisdiction.US_FEDERAL,
        data_category=DataCategory.PHI,
        min_retention_days=2190,
        description=("HIPAA requires PHI retention for 6 years"),
    ),
    RetentionRule(
        jurisdiction=Jurisdiction.US_FEDERAL,
        data_category=DataCategory.PII,
        min_retention_days=2190,
        description=("HIPAA requires PII retention for 6 years"),
    ),
    # California CCPA
    RetentionRule(
        jurisdiction=Jurisdiction.CALIFORNIA_CCPA,
        data_category=DataCategory.PII,
        min_retention_days=365,
        requires_deletion_proof=True,
        description=("CCPA: retain PII records of requests for 24 months; deletion upon request"),
    ),
    RetentionRule(
        jurisdiction=Jurisdiction.CALIFORNIA_CCPA,
        data_category=DataCategory.PHI,
        min_retention_days=2190,
        requires_deletion_proof=True,
        description=("CCPA + HIPAA: PHI retention 6 years with deletion proof"),
    ),
    # New York PHL
    RetentionRule(
        jurisdiction=Jurisdiction.NEW_YORK_PHL,
        data_category=DataCategory.PHI,
        min_retention_days=2190,
        description=("NY PHL: retain PHI for minimum 6 years"),
    ),
    RetentionRule(
        jurisdiction=Jurisdiction.NEW_YORK_PHL,
        data_category=DataCategory.GENOMIC,
        min_retention_days=3650,
        description=("NY PHL: retain genomic data for 10 years"),
    ),
]


def get_default_retention_rules(
    jurisdiction: Jurisdiction,
) -> list[RetentionRule]:
    """Return default retention rules for a jurisdiction.

    Parameters
    ----------
    jurisdiction:
        The target legal jurisdiction.

    Returns
    -------
    list[RetentionRule]
        Applicable default rules.
    """
    return [r for r in _DEFAULT_RETENTION_RULES if r.jurisdiction == jurisdiction]


class DataResidencyManager:
    """Enforces data residency and retention policies.

    Manages per-site boundary policies, evaluates cross-site
    transfer requests, and provides retention rule lookups.
    """

    def __init__(self) -> None:
        self._policies: dict[str, SiteBoundaryPolicy] = {}

    # -- policy management ----------------------------------

    def register_site_policy(self, policy: SiteBoundaryPolicy) -> None:
        """Register or replace a site boundary policy."""
        self._policies[policy.site_id] = policy

    def get_site_policy(self, site_id: str) -> SiteBoundaryPolicy:
        """Retrieve the boundary policy for a site.

        Raises
        ------
        KeyError
            If no policy is registered for the site.
        """
        policy = self._policies.get(site_id)
        if policy is None:
            raise KeyError(f"No residency policy for site {site_id!r}")
        return policy

    def list_site_policies(
        self,
    ) -> list[SiteBoundaryPolicy]:
        """List all registered site policies."""
        return list(self._policies.values())

    # -- transfer authorization -----------------------------

    def authorize_transfer(self, request: TransferRequest) -> TransferAuthorizationResult:
        """Evaluate a cross-site data transfer request.

        Checks:
        1. Source site allows outbound transfers.
        2. Destination is in the allowed list.
        3. Data category is permitted at both sites.

        Returns
        -------
        TransferAuthorizationResult
            The authorization decision.
        """
        reasons: list[str] = []
        conditions: list[str] = []

        # Source policy
        try:
            src = self.get_site_policy(request.source_site_id)
        except KeyError:
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=["No residency policy for source site"],
                evaluated_at=time.time(),
            )

        if not src.allow_outbound_transfer:
            reasons.append("Source site prohibits outbound transfers")
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if (
            src.allowed_destination_sites
            and request.destination_site_id not in src.allowed_destination_sites
        ):
            reasons.append("Destination site not in allowed list")
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        if request.data_category not in src.allowed_data_categories:
            reasons.append(
                f"Data category {request.data_category.value} not permitted at source site"
            )
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        # Destination policy
        try:
            dst = self.get_site_policy(request.destination_site_id)
        except KeyError:
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=["No residency policy for destination"],
                evaluated_at=time.time(),
            )

        if request.data_category not in dst.allowed_data_categories:
            reasons.append(
                f"Data category {request.data_category.value} not permitted at destination site"
            )
            return TransferAuthorizationResult(
                request_id=request.request_id,
                decision=TransferDecision.DENIED,
                reasons=reasons,
                evaluated_at=time.time(),
            )

        # Cross-jurisdiction conditions
        if src.jurisdiction != dst.jurisdiction:
            conditions.append(
                "Cross-jurisdiction transfer: verify "
                "compliance with both "
                f"{src.jurisdiction.value} and "
                f"{dst.jurisdiction.value}"
            )

        reasons.append("Transfer authorized")
        return TransferAuthorizationResult(
            request_id=request.request_id,
            decision=TransferDecision.APPROVED,
            reasons=reasons,
            conditions=conditions,
            evaluated_at=time.time(),
        )

    # -- retention rules ------------------------------------

    def get_retention_rules(self, site_id: str) -> list[RetentionRule]:
        """Get retention rules for a site.

        Returns site-specific rules if configured, otherwise
        falls back to jurisdiction defaults.
        """
        policy = self.get_site_policy(site_id)
        if policy.retention_rules:
            return list(policy.retention_rules)
        return get_default_retention_rules(policy.jurisdiction)

    def check_retention_compliance(
        self,
        site_id: str,
        data_category: DataCategory,
        data_age_days: int,
    ) -> tuple[bool, str]:
        """Check whether data meets retention requirements.

        Parameters
        ----------
        site_id:
            The site holding the data.
        data_category:
            Category of the data.
        data_age_days:
            Age of the data in days.

        Returns
        -------
        tuple[bool, str]
            ``(compliant, reason)`` -- ``True`` when the data
            meets all applicable retention rules.
        """
        rules = self.get_retention_rules(site_id)
        applicable = [r for r in rules if r.data_category == data_category]
        if not applicable:
            return True, "No retention rules apply"

        for rule in applicable:
            if data_age_days < rule.min_retention_days:
                return True, (f"Within minimum retention of {rule.min_retention_days} days")
            if rule.max_retention_days is not None and data_age_days > rule.max_retention_days:
                return False, (
                    f"Exceeds maximum retention of "
                    f"{rule.max_retention_days} days "
                    f"({rule.description})"
                )
        return True, "Retention requirements satisfied"
