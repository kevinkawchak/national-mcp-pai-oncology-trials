"""Procedure state machine.

Defines the canonical procedure lifecycle states, validates
transitions, persists state history, and enforces
simulation-only vs clinical-mode boundaries.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ProcedureStatus(Enum):
    """Lifecycle states for an oncology procedure."""

    SCHEDULED = "SCHEDULED"
    PRE_CHECK = "PRE_CHECK"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    POST_CHECK = "POST_CHECK"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class ProcedureMode(Enum):
    """Execution mode for a procedure."""

    SIMULATION = "SIMULATION"
    CLINICAL = "CLINICAL"


# ---------------------------------------------------------------
# Valid state transitions
# ---------------------------------------------------------------
_VALID_TRANSITIONS: dict[ProcedureStatus, set[ProcedureStatus]] = {
    ProcedureStatus.SCHEDULED: {
        ProcedureStatus.PRE_CHECK,
        ProcedureStatus.ABORTED,
    },
    ProcedureStatus.PRE_CHECK: {
        ProcedureStatus.APPROVED,
        ProcedureStatus.FAILED,
        ProcedureStatus.ABORTED,
    },
    ProcedureStatus.APPROVED: {
        ProcedureStatus.IN_PROGRESS,
        ProcedureStatus.ABORTED,
    },
    ProcedureStatus.IN_PROGRESS: {
        ProcedureStatus.POST_CHECK,
        ProcedureStatus.ABORTED,
        ProcedureStatus.FAILED,
    },
    ProcedureStatus.POST_CHECK: {
        ProcedureStatus.COMPLETED,
        ProcedureStatus.FAILED,
        ProcedureStatus.ABORTED,
    },
    ProcedureStatus.COMPLETED: set(),
    ProcedureStatus.ABORTED: set(),
    ProcedureStatus.FAILED: set(),
}


@dataclass
class StateTransition:
    """Record of a single state transition.

    Attributes:
        from_state: Previous state.
        to_state: New state.
        transitioned_at: Timestamp of the transition.
        reason: Optional reason or context.
    """

    from_state: ProcedureStatus
    to_state: ProcedureStatus
    transitioned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = ""


class ProcedureState:
    """State machine for a single procedure lifecycle.

    Enforces valid transitions, maintains a full history, and
    gates clinical-mode execution behind explicit opt-in.

    Args:
        procedure_id: Unique procedure identifier.
        mode: Execution mode (simulation or clinical).
        initial_status: Starting state.
    """

    def __init__(
        self,
        procedure_id: str,
        mode: ProcedureMode = ProcedureMode.SIMULATION,
        initial_status: ProcedureStatus = (ProcedureStatus.SCHEDULED),
    ) -> None:
        self.procedure_id = procedure_id
        self.mode = mode
        self._status = initial_status
        self._history: list[StateTransition] = []

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------

    @property
    def status(self) -> ProcedureStatus:
        """Return the current procedure status."""
        return self._status

    @property
    def is_terminal(self) -> bool:
        """Return ``True`` if the state is terminal."""
        return not _VALID_TRANSITIONS.get(self._status, set())

    @property
    def is_clinical(self) -> bool:
        """Return ``True`` if running in clinical mode."""
        return self.mode == ProcedureMode.CLINICAL

    # ----------------------------------------------------------
    # Transition API
    # ----------------------------------------------------------

    def can_transition(self, target: ProcedureStatus) -> bool:
        """Check whether a transition to *target* is valid.

        Args:
            target: The desired target state.

        Returns:
            ``True`` if the transition is allowed.
        """
        allowed = _VALID_TRANSITIONS.get(self._status, set())
        return target in allowed

    def transition(
        self,
        target: ProcedureStatus,
        reason: str = "",
    ) -> StateTransition:
        """Transition to a new state.

        Args:
            target: The desired target state.
            reason: Optional reason for the transition.

        Returns:
            The recorded ``StateTransition``.

        Raises:
            ValueError: If the transition is not allowed.
        """
        if not self.can_transition(target):
            raise ValueError(f"Invalid transition: {self._status.value} -> {target.value}")

        if target == ProcedureStatus.IN_PROGRESS and self.mode == ProcedureMode.SIMULATION:
            reason = reason or "SIMULATION mode: no physical execution"

        record = StateTransition(
            from_state=self._status,
            to_state=target,
            reason=reason,
        )
        self._history.append(record)
        self._status = target
        return record

    def get_history(self) -> list[StateTransition]:
        """Return the full transition history.

        Returns:
            Ordered list of ``StateTransition`` records.
        """
        return list(self._history)

    # ----------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------

    def serialize(self) -> dict[str, Any]:
        """Serialize the state machine for persistence.

        Returns:
            A JSON-compatible dictionary.
        """
        return {
            "procedure_id": self.procedure_id,
            "mode": self.mode.value,
            "status": self._status.value,
            "history": [
                {
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "transitioned_at": (t.transitioned_at.isoformat()),
                    "reason": t.reason,
                }
                for t in self._history
            ],
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> ProcedureState:
        """Reconstruct a state machine from serialized data.

        Args:
            data: Dictionary produced by ``serialize()``.

        Returns:
            A restored ``ProcedureState`` instance.
        """
        instance = cls(
            procedure_id=data["procedure_id"],
            mode=ProcedureMode(data["mode"]),
            initial_status=ProcedureStatus(data["status"]),
        )
        for entry in data.get("history", []):
            record = StateTransition(
                from_state=ProcedureStatus(entry["from_state"]),
                to_state=ProcedureStatus(entry["to_state"]),
                transitioned_at=datetime.fromisoformat(entry["transitioned_at"]),
                reason=entry.get("reason", ""),
            )
            instance._history.append(record)
        return instance

    def to_json(self) -> str:
        """Serialize the state machine to a JSON string.

        Returns:
            A JSON string representation.
        """
        return json.dumps(self.serialize(), indent=2)

    @classmethod
    def from_json(cls, raw: str) -> ProcedureState:
        """Reconstruct a state machine from a JSON string.

        Args:
            raw: JSON string produced by ``to_json()``.

        Returns:
            A restored ``ProcedureState`` instance.
        """
        return cls.deserialize(json.loads(raw))
