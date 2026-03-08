"""Task-order validator with safety constraints.

Validates task orders against the task-order.schema.json
structure, enforces precondition and post-procedure evidence
contracts, and checks trial protocol constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ValidationStatus(Enum):
    """Overall validation result status."""

    VALID = "VALID"
    INVALID = "INVALID"


@dataclass
class TaskValidationResult:
    """Result of validating a task order.

    Attributes:
        task_order_id: The task order being validated.
        status: Overall validation status.
        precondition_errors: Failed precondition checks.
        postcondition_errors: Failed postcondition checks.
        schema_errors: Structural schema violations.
        protocol_errors: Trial protocol constraint violations.
        validated_at: Timestamp of the validation.
    """

    task_order_id: str
    status: ValidationStatus
    precondition_errors: list[str] = field(default_factory=list)
    postcondition_errors: list[str] = field(default_factory=list)
    schema_errors: list[str] = field(default_factory=list)
    protocol_errors: list[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_valid(self) -> bool:
        """Return ``True`` when no errors are present."""
        return self.status == ValidationStatus.VALID


# ---------------------------------------------------------------
# Required fields mirroring task-order.schema.json
# ---------------------------------------------------------------
_REQUIRED_TASK_ORDER_KEYS: set[str] = {
    "task_order_id",
    "procedure_type",
    "patient_id",
    "site_id",
    "robot_id",
    "protocol_id",
}

# ---------------------------------------------------------------
# Precondition contract keys
# ---------------------------------------------------------------
_REQUIRED_PRECONDITIONS: dict[str, str] = {
    "patient_identity_confirmed": ("Patient identity must be confirmed"),
    "consent_valid": ("Valid patient consent must be on file"),
    "site_cleared": ("Site must be cleared for procedure"),
    "robot_calibrated": ("Robot must be calibrated and ready"),
}

# ---------------------------------------------------------------
# Post-procedure evidence keys
# ---------------------------------------------------------------
_REQUIRED_POSTCONDITIONS: set[str] = {
    "completion_status",
    "measurements",
    "adverse_events",
}


class TaskValidator:
    """Validates task orders and enforces safety contracts.

    Checks structural conformance to task-order.schema.json,
    verifies precondition contracts, post-procedure evidence
    capture contracts, and trial protocol constraints.
    """

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def validate(
        self,
        task_order: dict[str, Any],
        preconditions: dict[str, Any] | None = None,
        postconditions: dict[str, Any] | None = None,
        protocol_constraints: dict[str, Any] | None = None,
    ) -> TaskValidationResult:
        """Validate a task order end-to-end.

        Args:
            task_order: The task-order payload.
            preconditions: Pre-procedure condition values.
            postconditions: Post-procedure evidence values.
            protocol_constraints: Trial protocol constraints.

        Returns:
            A ``TaskValidationResult`` with itemised errors.
        """
        task_order_id = task_order.get("task_order_id", "unknown")

        schema_errors = self._validate_schema(task_order)
        precondition_errors = self._validate_preconditions(preconditions or {})
        postcondition_errors = self._validate_postconditions(postconditions or {})
        protocol_errors = self._validate_protocol(
            task_order,
            protocol_constraints or {},
        )

        all_errors = schema_errors + precondition_errors + postcondition_errors + protocol_errors
        status = ValidationStatus.VALID if not all_errors else ValidationStatus.INVALID

        return TaskValidationResult(
            task_order_id=task_order_id,
            status=status,
            precondition_errors=precondition_errors,
            postcondition_errors=postcondition_errors,
            schema_errors=schema_errors,
            protocol_errors=protocol_errors,
        )

    def validate_preconditions(
        self,
        preconditions: dict[str, Any],
    ) -> list[str]:
        """Validate only the precondition contract.

        Args:
            preconditions: Mapping of condition name to value.

        Returns:
            List of error strings. Empty if all pass.
        """
        return self._validate_preconditions(preconditions)

    def validate_postconditions(
        self,
        postconditions: dict[str, Any],
    ) -> list[str]:
        """Validate only the postcondition evidence contract.

        Args:
            postconditions: Evidence capture payload.

        Returns:
            List of error strings. Empty if all pass.
        """
        return self._validate_postconditions(postconditions)

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    @staticmethod
    def _validate_schema(
        task_order: dict[str, Any],
    ) -> list[str]:
        """Check required top-level keys."""
        errors: list[str] = []
        for key in _REQUIRED_TASK_ORDER_KEYS:
            if key not in task_order:
                errors.append(f"Missing required field: {key}")
        return errors

    @staticmethod
    def _validate_preconditions(
        preconditions: dict[str, Any],
    ) -> list[str]:
        """Verify each precondition contract entry."""
        errors: list[str] = []
        for key, message in _REQUIRED_PRECONDITIONS.items():
            value = preconditions.get(key)
            if not value:
                errors.append(message)
        return errors

    @staticmethod
    def _validate_postconditions(
        postconditions: dict[str, Any],
    ) -> list[str]:
        """Verify post-procedure evidence capture."""
        errors: list[str] = []
        for key in _REQUIRED_POSTCONDITIONS:
            if key not in postconditions:
                errors.append(f"Missing post-procedure evidence: {key}")
        return errors

    @staticmethod
    def _validate_protocol(
        task_order: dict[str, Any],
        constraints: dict[str, Any],
    ) -> list[str]:
        """Enforce trial protocol constraints."""
        errors: list[str] = []

        allowed_procedures = constraints.get("allowed_procedures")
        procedure = task_order.get("procedure_type")
        if allowed_procedures and procedure and procedure not in allowed_procedures:
            errors.append(f"Procedure '{procedure}' not allowed by protocol")

        max_duration = constraints.get("max_duration_minutes")
        order_duration = task_order.get("duration_minutes")
        if (
            max_duration is not None
            and order_duration is not None
            and order_duration > max_duration
        ):
            errors.append(f"Duration {order_duration}m exceeds protocol limit {max_duration}m")

        excluded_sites = constraints.get("excluded_sites", [])
        site_id = task_order.get("site_id")
        if site_id and site_id in excluded_sites:
            errors.append(f"Site '{site_id}' excluded by protocol")

        return errors
