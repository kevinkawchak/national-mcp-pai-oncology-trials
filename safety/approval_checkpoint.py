"""Human-approval checkpoint patterns.

Implements mandatory human-in-the-loop approval gates for
specified oncology procedure types. Supports configurable
timeouts, escalation paths, and a full audit log.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

_DEFAULT_TIMEOUT_SECONDS: int = 300


class ApprovalStatus(Enum):
    """Status of a human-approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    TIMED_OUT = "TIMED_OUT"
    ESCALATED = "ESCALATED"


@dataclass
class ApprovalRequest:
    """A request for human-in-the-loop approval.

    Attributes:
        request_id: Unique request identifier.
        procedure_id: Procedure requiring approval.
        procedure_type: Type of oncology procedure.
        requester: Identity of the requesting system.
        reason: Why approval is needed.
        timeout_seconds: Seconds before auto-timeout.
        created_at: Timestamp of request creation.
        context: Additional context for the approver.
    """

    request_id: str
    procedure_id: str
    procedure_type: str
    requester: str
    reason: str
    timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalResponse:
    """Response from a human approver.

    Attributes:
        request_id: Matching request identifier.
        status: Final approval status.
        approver: Identity of the human approver.
        comments: Free-text approver comments.
        responded_at: Timestamp of response.
        escalation_target: Escalation recipient if needed.
    """

    request_id: str
    status: ApprovalStatus
    approver: str = ""
    comments: str = ""
    responded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    escalation_target: str = ""


class ApprovalCheckpoint:
    """Manages human-in-the-loop approval gates.

    For specified procedure types, the checkpoint creates an
    approval request, tracks its status, handles timeouts,
    and provides escalation paths when approvals are denied
    or expire.
    """

    def __init__(
        self,
        default_timeout: int = _DEFAULT_TIMEOUT_SECONDS,
        mandatory_types: list[str] | None = None,
    ) -> None:
        """Initialise the checkpoint service.

        Args:
            default_timeout: Default approval timeout in
                seconds.
            mandatory_types: Procedure types that always
                require human approval. If ``None``, all
                procedure types require approval.
        """
        self._default_timeout = default_timeout
        self._mandatory_types = mandatory_types
        self._requests: dict[str, ApprovalRequest] = {}
        self._responses: dict[str, ApprovalResponse] = {}

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def request_approval(
        self,
        procedure_id: str,
        procedure_type: str,
        requester: str,
        reason: str,
        timeout_seconds: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        """Create a new approval request.

        Args:
            procedure_id: Procedure requiring approval.
            procedure_type: Type of oncology procedure.
            requester: Requesting system identity.
            reason: Justification for the request.
            timeout_seconds: Override default timeout.
            context: Additional context payload.

        Returns:
            The created ``ApprovalRequest``.
        """
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            procedure_id=procedure_id,
            procedure_type=procedure_type,
            requester=requester,
            reason=reason,
            timeout_seconds=(
                timeout_seconds if timeout_seconds is not None else self._default_timeout
            ),
            context=context or {},
        )
        self._requests[request.request_id] = request
        return request

    def check_status(
        self,
        request_id: str,
        current_time: datetime | None = None,
    ) -> ApprovalResponse:
        """Check the status of an approval request.

        If the request has timed out and no response has been
        recorded, a ``TIMED_OUT`` response is automatically
        generated.

        Args:
            request_id: The approval request identifier.
            current_time: Override for the current time (used
                in testing).

        Returns:
            The current ``ApprovalResponse``.

        Raises:
            KeyError: If ``request_id`` is not found.
        """
        if request_id not in self._requests:
            raise KeyError(f"Unknown approval request: {request_id}")

        if request_id in self._responses:
            return self._responses[request_id]

        request = self._requests[request_id]
        now = current_time or datetime.now(timezone.utc)
        elapsed = (now - request.created_at).total_seconds()

        if elapsed >= request.timeout_seconds:
            response = ApprovalResponse(
                request_id=request_id,
                status=ApprovalStatus.TIMED_OUT,
                responded_at=now,
            )
            self._responses[request_id] = response
            return response

        return ApprovalResponse(
            request_id=request_id,
            status=ApprovalStatus.PENDING,
        )

    def respond(
        self,
        request_id: str,
        approved: bool,
        approver: str,
        comments: str = "",
    ) -> ApprovalResponse:
        """Record a human approver's decision.

        Args:
            request_id: The approval request identifier.
            approved: ``True`` to approve, ``False`` to deny.
            approver: Identity of the human approver.
            comments: Optional approver comments.

        Returns:
            The recorded ``ApprovalResponse``.

        Raises:
            KeyError: If ``request_id`` is not found.
        """
        if request_id not in self._requests:
            raise KeyError(f"Unknown approval request: {request_id}")
        status = ApprovalStatus.APPROVED if approved else ApprovalStatus.DENIED
        response = ApprovalResponse(
            request_id=request_id,
            status=status,
            approver=approver,
            comments=comments,
        )
        self._responses[request_id] = response
        return response

    def escalate(
        self,
        request_id: str,
        escalation_target: str,
        reason: str = "",
    ) -> ApprovalResponse:
        """Escalate a denied or timed-out approval.

        Args:
            request_id: The approval request identifier.
            escalation_target: Recipient of the escalation.
            reason: Justification for escalation.

        Returns:
            An ``ApprovalResponse`` with ``ESCALATED`` status.

        Raises:
            KeyError: If ``request_id`` is not found.
            ValueError: If the request has not been denied or
                timed out.
        """
        if request_id not in self._requests:
            raise KeyError(f"Unknown approval request: {request_id}")

        current = self._responses.get(request_id)
        if current is None or current.status not in (
            ApprovalStatus.DENIED,
            ApprovalStatus.TIMED_OUT,
        ):
            raise ValueError("Only denied or timed-out requests can be escalated")

        response = ApprovalResponse(
            request_id=request_id,
            status=ApprovalStatus.ESCALATED,
            comments=reason,
            escalation_target=escalation_target,
        )
        self._responses[request_id] = response
        return response

    def requires_approval(self, procedure_type: str) -> bool:
        """Check if a procedure type requires approval.

        Args:
            procedure_type: The procedure type to check.

        Returns:
            ``True`` if approval is mandatory.
        """
        if self._mandatory_types is None:
            return True
        return procedure_type in self._mandatory_types
