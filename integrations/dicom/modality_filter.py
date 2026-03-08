"""Role-based modality restriction enforcement.

Defines which clinical trial roles may access which DICOM
modalities. Enforces the national MCP PAI standard access
matrix for oncology imaging modalities.

Modality tiers:
    MUST: CT, MR, PT -- core imaging modalities required
        for oncology trial assessments.
    SHOULD: RTSTRUCT, RTPLAN -- radiation therapy objects
        that carry treatment-sensitive data.

Roles:
    robot_agent: Physical AI agent performing autonomous
        imaging analysis.
    trial_coordinator: Clinical trial coordinator managing
        study operations.
    data_monitor: Data safety monitoring board member.
    auditor: Regulatory or quality auditor.
    sponsor: Trial sponsor representative.
    cro: Contract research organization representative.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Modality tiers
# -------------------------------------------------------------------

MUST_MODALITIES: frozenset[str] = frozenset(
    {
        "CT",
        "MR",
        "PT",
    }
)

SHOULD_MODALITIES: frozenset[str] = frozenset(
    {
        "RTSTRUCT",
        "RTPLAN",
    }
)

ALL_MODALITIES: frozenset[str] = MUST_MODALITIES | SHOULD_MODALITIES

# -------------------------------------------------------------------
# Role definitions and access matrix
# -------------------------------------------------------------------

VALID_ROLES: frozenset[str] = frozenset(
    {
        "robot_agent",
        "trial_coordinator",
        "data_monitor",
        "auditor",
        "sponsor",
        "cro",
    }
)

# Default access matrix: maps role to permitted modalities.
# Each role gets a frozenset of modality codes.
DEFAULT_ACCESS_MATRIX: dict[str, frozenset[str]] = {
    "robot_agent": MUST_MODALITIES,
    "trial_coordinator": ALL_MODALITIES,
    "data_monitor": MUST_MODALITIES,
    "auditor": ALL_MODALITIES,
    "sponsor": MUST_MODALITIES,
    "cro": MUST_MODALITIES | frozenset({"RTSTRUCT"}),
}


class ModalityFilter:
    """Role-based DICOM modality access filter.

    Enforces restrictions on which DICOM modalities a given
    role is permitted to access. The filter can be configured
    with a custom access matrix or will use the national MCP
    PAI standard defaults.

    Example::

        filt = ModalityFilter()
        filt.is_permitted("robot_agent", "CT")       # True
        filt.is_permitted("robot_agent", "RTPLAN")    # False
        filt.is_permitted("auditor", "RTPLAN")        # True

    Attributes:
        access_matrix: Current role-to-modality access map.
    """

    def __init__(
        self,
        access_matrix: (dict[str, frozenset[str]] | None) = None,
    ) -> None:
        """Initialize the modality filter.

        Args:
            access_matrix: Optional custom access matrix
                mapping role names to permitted modality
                frozensets. Defaults to the national MCP PAI
                standard matrix.
        """
        if access_matrix is not None:
            self.access_matrix = dict(access_matrix)
        else:
            self.access_matrix = dict(DEFAULT_ACCESS_MATRIX)

    def is_permitted(
        self,
        role: str,
        modality: str,
    ) -> bool:
        """Check if a role is permitted to access a modality.

        Args:
            role: Role identifier (e.g., ``robot_agent``).
            modality: DICOM modality code (e.g., ``CT``).

        Returns:
            True if the role may access the modality.

        Raises:
            ValueError: If the role is not recognized.
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Unknown role: {role!r}. Valid roles: {sorted(VALID_ROLES)}")

        permitted = self.access_matrix.get(role, frozenset())
        allowed = modality.upper() in permitted

        if not allowed:
            logger.warning(
                "Modality access denied: role=%r modality=%r",
                role,
                modality,
            )

        return allowed

    def filter_results(
        self,
        role: str,
        results: list[dict[str, Any]],
        modality_key: str = "Modality",
    ) -> list[dict[str, Any]]:
        """Filter query results by role modality permissions.

        Removes any result whose modality is not permitted
        for the given role.

        Args:
            role: Role identifier.
            results: List of DICOM metadata dictionaries.
            modality_key: Key name for the modality field
                in result dictionaries.

        Returns:
            Filtered list containing only permitted results.
        """
        filtered: list[dict[str, Any]] = []
        for result in results:
            modality = result.get(modality_key, "")
            if isinstance(modality, str) and modality:
                if self.is_permitted(role, modality):
                    filtered.append(result)
            else:
                # If no modality specified, include by
                # default (e.g., study-level results)
                filtered.append(result)
        return filtered

    def get_permitted_modalities(
        self,
        role: str,
    ) -> frozenset[str]:
        """Get the set of modalities permitted for a role.

        Args:
            role: Role identifier.

        Returns:
            Frozenset of permitted modality codes.

        Raises:
            ValueError: If the role is not recognized.
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Unknown role: {role!r}. Valid roles: {sorted(VALID_ROLES)}")
        return self.access_matrix.get(role, frozenset())

    def grant_modality(
        self,
        role: str,
        modality: str,
    ) -> None:
        """Grant a role access to an additional modality.

        Args:
            role: Role identifier.
            modality: DICOM modality code to grant.

        Raises:
            ValueError: If the role is not recognized.
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Unknown role: {role!r}. Valid roles: {sorted(VALID_ROLES)}")
        current = self.access_matrix.get(role, frozenset())
        self.access_matrix[role] = current | {modality.upper()}
        logger.info(
            "Granted modality %r to role %r",
            modality,
            role,
        )

    def revoke_modality(
        self,
        role: str,
        modality: str,
    ) -> None:
        """Revoke a role's access to a modality.

        Args:
            role: Role identifier.
            modality: DICOM modality code to revoke.

        Raises:
            ValueError: If the role is not recognized.
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Unknown role: {role!r}. Valid roles: {sorted(VALID_ROLES)}")
        current = self.access_matrix.get(role, frozenset())
        self.access_matrix[role] = current - {modality.upper()}
        logger.info(
            "Revoked modality %r from role %r",
            modality,
            role,
        )
