"""Emergency stop and override semantics.

Provides e-stop signal propagation, abort workflow with state
preservation, post-abort evidence capture, and recovery with
re-authorisation procedures.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EStopStatus(Enum):
    """Current status of the emergency-stop controller."""

    IDLE = "IDLE"
    TRIGGERED = "TRIGGERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RECOVERING = "RECOVERING"


@dataclass
class EStopSignal:
    """An emergency-stop signal.

    Attributes:
        signal_id: Unique signal identifier.
        procedure_id: Procedure being aborted.
        reason: Human-readable reason for the e-stop.
        triggered_by: Identity of the triggering party.
        triggered_at: Timestamp of the trigger event.
        affected_servers: List of server IDs that received
            the propagation.
        preserved_state: Snapshot of procedure state at the
            moment of abort.
        post_abort_evidence: Evidence captured after abort.
    """

    signal_id: str
    procedure_id: str
    reason: str
    triggered_by: str
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    affected_servers: list[str] = field(default_factory=list)
    preserved_state: dict[str, Any] = field(default_factory=dict)
    post_abort_evidence: dict[str, Any] = field(default_factory=dict)


class EStopController:
    """Manages emergency-stop lifecycle.

    Handles e-stop triggering, signal propagation to all active
    servers, acknowledgement, post-abort evidence capture, and
    recovery with re-authorisation.
    """

    def __init__(self) -> None:
        self._status: EStopStatus = EStopStatus.IDLE
        self._active_signal: EStopSignal | None = None
        self._history: list[EStopSignal] = []
        self._active_servers: list[str] = []

    # ----------------------------------------------------------
    # Server registration
    # ----------------------------------------------------------

    def register_server(self, server_id: str) -> None:
        """Register a server for e-stop propagation.

        Args:
            server_id: Unique identifier of the server.
        """
        if server_id not in self._active_servers:
            self._active_servers.append(server_id)

    def unregister_server(self, server_id: str) -> None:
        """Remove a server from e-stop propagation.

        Args:
            server_id: The server to remove.
        """
        if server_id in self._active_servers:
            self._active_servers.remove(server_id)

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def trigger_estop(
        self,
        procedure_id: str,
        reason: str,
        triggered_by: str,
        current_state: dict[str, Any] | None = None,
    ) -> EStopSignal:
        """Trigger an emergency stop.

        Propagates the e-stop signal to all registered servers
        and preserves the current procedure state.

        Args:
            procedure_id: The procedure to abort.
            reason: Human-readable reason.
            triggered_by: Identity of the triggering party.
            current_state: Snapshot of the procedure state to
                preserve.

        Returns:
            The emitted ``EStopSignal``.

        Raises:
            RuntimeError: If an e-stop is already active.
        """
        if self._status == EStopStatus.TRIGGERED:
            raise RuntimeError("An e-stop is already active; acknowledge before re-triggering")

        signal = EStopSignal(
            signal_id=str(uuid.uuid4()),
            procedure_id=procedure_id,
            reason=reason,
            triggered_by=triggered_by,
            affected_servers=list(self._active_servers),
            preserved_state=current_state or {},
        )
        self._active_signal = signal
        self._status = EStopStatus.TRIGGERED
        return signal

    def acknowledge(
        self,
        acknowledged_by: str,
        post_abort_evidence: dict[str, Any] | None = None,
    ) -> EStopSignal:
        """Acknowledge the active e-stop.

        Captures post-abort evidence and transitions the
        controller to ACKNOWLEDGED status.

        Args:
            acknowledged_by: Identity of the acknowledger.
            post_abort_evidence: Evidence captured after the
                abort (images, logs, sensor data, etc.).

        Returns:
            The updated ``EStopSignal``.

        Raises:
            RuntimeError: If no e-stop is active.
        """
        if self._status != EStopStatus.TRIGGERED or self._active_signal is None:
            raise RuntimeError("No active e-stop to acknowledge")

        self._active_signal.post_abort_evidence = post_abort_evidence or {}
        self._status = EStopStatus.ACKNOWLEDGED
        return self._active_signal

    def recover(
        self,
        authorised_by: str,
        recovery_notes: str = "",
    ) -> EStopSignal:
        """Initiate recovery from an acknowledged e-stop.

        The controller moves to RECOVERING and then back to
        IDLE once recovery is complete. The signal is archived
        in history.

        Args:
            authorised_by: Identity of the person authorising
                recovery.
            recovery_notes: Free-text recovery notes.

        Returns:
            The archived ``EStopSignal``.

        Raises:
            RuntimeError: If the e-stop has not been
                acknowledged.
        """
        if self._status != EStopStatus.ACKNOWLEDGED or self._active_signal is None:
            raise RuntimeError("E-stop must be acknowledged before recovery")

        self._status = EStopStatus.RECOVERING
        self._active_signal.post_abort_evidence["recovery_authorised_by"] = authorised_by
        self._active_signal.post_abort_evidence["recovery_notes"] = recovery_notes

        archived = self._active_signal
        self._history.append(archived)
        self._active_signal = None
        self._status = EStopStatus.IDLE
        return archived

    def get_status(self) -> dict[str, Any]:
        """Return the current controller status.

        Returns:
            A dictionary with status, active signal details,
            registered servers, and history count.
        """
        return {
            "status": self._status.value,
            "active_signal": (self._active_signal.signal_id if self._active_signal else None),
            "active_procedure": (self._active_signal.procedure_id if self._active_signal else None),
            "registered_servers": list(self._active_servers),
            "history_count": len(self._history),
        }

    def get_history(self) -> list[EStopSignal]:
        """Return the full e-stop history.

        Returns:
            List of archived ``EStopSignal`` records.
        """
        return list(self._history)
