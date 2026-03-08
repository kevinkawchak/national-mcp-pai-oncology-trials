"""Robot capability registry.

Manages robot platform registration, USL (Unification Standard
Level) scoring, capability validation, and procedure eligibility
matching. Tracks simulation vs clinical certification status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CertificationStatus(Enum):
    """Whether a robot is certified for simulation or clinical."""

    SIMULATION_ONLY = "SIMULATION_ONLY"
    CLINICAL = "CLINICAL"
    SUSPENDED = "SUSPENDED"


@dataclass
class RobotEntry:
    """A registered robot platform.

    Attributes:
        robot_id: Unique identifier for the robot.
        platform_name: Commercial or internal platform name.
        usl_score: Unification Standard Level score (0-100).
        capabilities: Capability descriptors conforming to
            robot-capability-profile.schema.json.
        certification: Current certification status.
        registered_at: Timestamp of initial registration.
        metadata: Additional platform metadata.
    """

    robot_id: str
    platform_name: str
    usl_score: float
    capabilities: dict[str, Any]
    certification: CertificationStatus = CertificationStatus.SIMULATION_ONLY
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------
# Required top-level keys that mirror
# robot-capability-profile.schema.json
# ---------------------------------------------------------------
_REQUIRED_CAPABILITY_KEYS: set[str] = {
    "manipulator",
    "sensors",
    "safety_systems",
    "communication",
}


class RobotRegistry:
    """Registry for robot platforms and their capabilities.

    Provides registration, lookup, capability validation, and
    procedure eligibility matching.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RobotEntry] = {}

    # ----------------------------------------------------------
    # Registration
    # ----------------------------------------------------------

    def register(self, entry: RobotEntry) -> RobotEntry:
        """Register or update a robot platform.

        Args:
            entry: The robot entry to register.

        Returns:
            The registered ``RobotEntry``.

        Raises:
            ValueError: If the capability descriptor is invalid.
        """
        errors = self.validate_capability(entry.capabilities)
        if errors:
            raise ValueError("Invalid capability descriptor: " + "; ".join(errors))
        if not 0 <= entry.usl_score <= 100:
            raise ValueError("USL score must be between 0 and 100")
        self._entries[entry.robot_id] = entry
        return entry

    # ----------------------------------------------------------
    # Lookup
    # ----------------------------------------------------------

    def lookup(self, robot_id: str) -> RobotEntry | None:
        """Look up a robot by its identifier.

        Args:
            robot_id: The robot's unique identifier.

        Returns:
            The ``RobotEntry`` if found, else ``None``.
        """
        return self._entries.get(robot_id)

    # ----------------------------------------------------------
    # Eligibility matching
    # ----------------------------------------------------------

    def match_for_procedure(
        self,
        procedure_type: str,
        required_capabilities: list[str],
        min_usl_score: float = 0.0,
        clinical_required: bool = False,
    ) -> list[RobotEntry]:
        """Find robots eligible for a given procedure.

        Args:
            procedure_type: Type of procedure requested.
            required_capabilities: Capability keys that must
                be present in the robot's profile.
            min_usl_score: Minimum USL score threshold.
            clinical_required: If ``True``, only robots with
                ``CLINICAL`` certification are returned.

        Returns:
            List of eligible ``RobotEntry`` objects sorted by
            USL score descending.
        """
        eligible: list[RobotEntry] = []
        for entry in self._entries.values():
            if entry.usl_score < min_usl_score:
                continue
            if clinical_required and (entry.certification != CertificationStatus.CLINICAL):
                continue
            if entry.certification == (CertificationStatus.SUSPENDED):
                continue
            robot_caps = set(entry.capabilities.get("supported_procedures", []))
            cap_keys = set(entry.capabilities.keys())
            has_procedures = not procedure_type or procedure_type in robot_caps
            has_capabilities = all(cap in cap_keys for cap in required_capabilities)
            if has_procedures and has_capabilities:
                eligible.append(entry)
        eligible.sort(key=lambda e: e.usl_score, reverse=True)
        return eligible

    # ----------------------------------------------------------
    # Capability validation
    # ----------------------------------------------------------

    @staticmethod
    def validate_capability(
        capabilities: dict[str, Any],
    ) -> list[str]:
        """Validate a capability descriptor.

        Checks that the descriptor contains the required
        top-level keys defined by
        robot-capability-profile.schema.json.

        Args:
            capabilities: The capability descriptor dict.

        Returns:
            A list of validation error strings. Empty if valid.
        """
        errors: list[str] = []
        for key in _REQUIRED_CAPABILITY_KEYS:
            if key not in capabilities:
                errors.append(f"Missing required key: {key}")
        return errors
