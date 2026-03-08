"""Site capability verification.

Validates site capability profiles against
site-capability-profile.schema.json, checks required
infrastructure, and determines procedure eligibility based
on site capabilities and regulatory overlay compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SiteStatus(Enum):
    """Verification status of a site."""

    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    CONDITIONALLY_VERIFIED = "CONDITIONALLY_VERIFIED"


@dataclass
class SiteVerificationResult:
    """Result of site capability verification.

    Attributes:
        site_id: Unique site identifier.
        status: Overall verification status.
        infrastructure_errors: Missing infrastructure items.
        regulatory_errors: Regulatory compliance issues.
        eligible_procedures: Procedures the site may host.
        verified_at: Timestamp of verification.
        details: Additional verification context.
    """

    site_id: str
    status: SiteStatus
    infrastructure_errors: list[str] = field(default_factory=list)
    regulatory_errors: list[str] = field(default_factory=list)
    eligible_procedures: list[str] = field(default_factory=list)
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def is_verified(self) -> bool:
        """Return ``True`` if the site is fully verified."""
        return self.status == SiteStatus.VERIFIED


# ---------------------------------------------------------------
# Required infrastructure keys matching
# site-capability-profile.schema.json
# ---------------------------------------------------------------
_REQUIRED_INFRASTRUCTURE: dict[str, str] = {
    "servers": ("MCP-compliant server infrastructure required"),
    "storage": ("Encrypted clinical data storage required"),
    "network": ("Low-latency network connectivity required"),
    "regulatory_overlay": ("Regulatory overlay configuration required"),
}

_REQUIRED_PROFILE_KEYS: set[str] = {
    "site_id",
    "site_name",
    "infrastructure",
    "supported_procedures",
    "regulatory_status",
}


class SiteVerifier:
    """Verifies site capability profiles.

    Validates infrastructure, checks regulatory compliance,
    and determines which procedures a site is eligible to
    host.
    """

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def verify_site(
        self,
        profile: dict[str, Any],
    ) -> SiteVerificationResult:
        """Run full site verification.

        Args:
            profile: Site capability profile payload
                conforming to
                site-capability-profile.schema.json.

        Returns:
            A ``SiteVerificationResult`` with itemised errors
            and eligible procedures.
        """
        site_id = profile.get("site_id", "unknown")

        schema_errors = self._validate_profile_schema(profile)
        infra_errors = self._check_infrastructure(profile.get("infrastructure", {}))
        reg_errors = self.validate_regulatory_compliance(profile.get("regulatory_status", {}))

        all_errors = schema_errors + infra_errors + reg_errors
        eligible = profile.get("supported_procedures", []) if not all_errors else []

        if all_errors:
            status = (
                SiteStatus.CONDITIONALLY_VERIFIED
                if not reg_errors and not schema_errors
                else SiteStatus.NOT_VERIFIED
            )
        else:
            status = SiteStatus.VERIFIED

        return SiteVerificationResult(
            site_id=site_id,
            status=status,
            infrastructure_errors=infra_errors,
            regulatory_errors=reg_errors,
            eligible_procedures=eligible,
            details={
                "schema_errors": schema_errors,
            },
        )

    def check_procedure_eligibility(
        self,
        profile: dict[str, Any],
        procedure_type: str,
    ) -> bool:
        """Check if a site can host a specific procedure.

        Args:
            profile: Site capability profile payload.
            procedure_type: The procedure type to check.

        Returns:
            ``True`` if the site is verified and the procedure
            is in the site's supported list.
        """
        result = self.verify_site(profile)
        if not result.is_verified:
            return False
        return procedure_type in result.eligible_procedures

    @staticmethod
    def validate_regulatory_compliance(
        regulatory_status: dict[str, Any],
    ) -> list[str]:
        """Validate regulatory overlay compliance.

        Args:
            regulatory_status: Regulatory status section of
                the site profile.

        Returns:
            List of regulatory error strings. Empty if
            compliant.
        """
        errors: list[str] = []

        if not regulatory_status.get("irb_approved"):
            errors.append("IRB approval is required")

        if not regulatory_status.get("fda_cleared"):
            errors.append("FDA clearance is required")

        if not regulatory_status.get("data_governance_compliant"):
            errors.append("Data governance compliance is required")

        expiry = regulatory_status.get("certification_expiry")
        if expiry:
            try:
                expiry_dt = datetime.fromisoformat(expiry)
                if expiry_dt < datetime.now(timezone.utc):
                    errors.append("Site certification has expired")
            except (ValueError, TypeError):
                errors.append("Invalid certification expiry date")

        return errors

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    @staticmethod
    def _validate_profile_schema(
        profile: dict[str, Any],
    ) -> list[str]:
        """Check required top-level keys."""
        errors: list[str] = []
        for key in _REQUIRED_PROFILE_KEYS:
            if key not in profile:
                errors.append(f"Missing required field: {key}")
        return errors

    @staticmethod
    def _check_infrastructure(
        infrastructure: dict[str, Any],
    ) -> list[str]:
        """Verify required infrastructure components."""
        errors: list[str] = []
        for key, message in _REQUIRED_INFRASTRUCTURE.items():
            if key not in infrastructure:
                errors.append(message)
        return errors
