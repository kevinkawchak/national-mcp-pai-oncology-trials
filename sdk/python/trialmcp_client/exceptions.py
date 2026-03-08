"""Typed exception hierarchy for the National MCP-PAI Oncology Trials SDK.

Maps the 9-code error taxonomy defined in the standard error-response schema
to concrete Python exceptions, enabling structured error handling across all
five MCP servers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ErrorDetails:
    """Additional context attached to an MCP error response.

    Mirrors the ``details`` object in error-response.schema.json.
    """

    field_name: str | None = None
    expected_pattern: str | None = None
    retry_after_seconds: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class TrialMCPError(Exception):
    """Base exception for all MCP-PAI SDK errors.

    Every concrete error carries the machine-readable ``code``, the originating
    ``server`` and ``tool``, a human-readable ``message``, and optional
    :class:`ErrorDetails`.
    """

    code: str = "UNKNOWN"

    def __init__(
        self,
        message: str,
        *,
        server: str | None = None,
        tool: str | None = None,
        request_id: str | None = None,
        timestamp: str | None = None,
        details: ErrorDetails | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.server = server
        self.tool = tool
        self.request_id = request_id
        self.timestamp = timestamp
        self.details = details

    def __repr__(self) -> str:
        parts = [f"code={self.code!r}", f"message={self.message!r}"]
        if self.server:
            parts.append(f"server={self.server!r}")
        if self.tool:
            parts.append(f"tool={self.tool!r}")
        if self.request_id:
            parts.append(f"request_id={self.request_id!r}")
        return f"{type(self).__name__}({', '.join(parts)})"


# ---------------------------------------------------------------------------
# Authorization errors
# ---------------------------------------------------------------------------


class AuthzDeniedError(TrialMCPError):
    """Access denied by the RBAC policy engine (AUTHZ_DENIED).

    Raised when no matching ALLOW rule exists or an explicit DENY rule matched.
    """

    code = "AUTHZ_DENIED"


class AuthzExpiredError(TrialMCPError):
    """Session token has expired (TOKEN_EXPIRED).

    The caller should re-authenticate before retrying.
    """

    code = "AUTHZ_EXPIRED"


class PermissionDeniedError(TrialMCPError):
    """Authenticated but insufficient permissions (PERMISSION_DENIED)."""

    code = "PERMISSION_DENIED"


# ---------------------------------------------------------------------------
# Input / resource errors
# ---------------------------------------------------------------------------


class InvalidInputError(TrialMCPError):
    """Request payload failed validation (INVALID_INPUT / VALIDATION_FAILED).

    The ``details`` field typically carries ``field_name`` and
    ``expected_pattern``.
    """

    code = "INVALID_INPUT"


class NotFoundError(TrialMCPError):
    """Requested resource does not exist (NOT_FOUND)."""

    code = "NOT_FOUND"


# ---------------------------------------------------------------------------
# Integrity errors
# ---------------------------------------------------------------------------


class ChainBrokenError(TrialMCPError):
    """Audit ledger hash-chain integrity violation detected (CHAIN_BROKEN).

    This is a critical clinical-safety event that must halt further processing
    and trigger an immediate investigation per 21 CFR Part 11.
    """

    code = "CHAIN_BROKEN"


class PHILeakError(TrialMCPError):
    """Protected Health Information detected in a non-safe channel (PHI_LEAK).

    Raised when the SDK detects potential PHI in logging, error messages, or
    outbound payloads that should be de-identified.
    """

    code = "PHI_LEAK"


# ---------------------------------------------------------------------------
# Availability errors
# ---------------------------------------------------------------------------


class RateLimitedError(TrialMCPError):
    """Request throttled by the server (RATE_LIMITED).

    ``details.retry_after_seconds`` indicates the minimum wait before retry.
    """

    code = "RATE_LIMITED"

    @property
    def retry_after(self) -> int | None:
        """Seconds to wait before retrying, if provided by the server."""
        if self.details:
            return self.details.retry_after_seconds
        return None


class ServerError(TrialMCPError):
    """Internal server error (INTERNAL_ERROR / SERVER_ERROR)."""

    code = "SERVER_ERROR"


class UnavailableError(TrialMCPError):
    """Server is temporarily unavailable (UNAVAILABLE).

    Raised when the circuit breaker trips or the server cannot be reached.
    """

    code = "UNAVAILABLE"


# ---------------------------------------------------------------------------
# Mapping helper
# ---------------------------------------------------------------------------

_CODE_TO_EXCEPTION: dict[str, type[TrialMCPError]] = {
    "AUTHZ_DENIED": AuthzDeniedError,
    "TOKEN_EXPIRED": AuthzExpiredError,
    "TOKEN_REVOKED": AuthzExpiredError,
    "PERMISSION_DENIED": PermissionDeniedError,
    "INVALID_INPUT": InvalidInputError,
    "VALIDATION_FAILED": InvalidInputError,
    "NOT_FOUND": NotFoundError,
    "CHAIN_BROKEN": ChainBrokenError,
    "PHI_LEAK": PHILeakError,
    "RATE_LIMITED": RateLimitedError,
    "INTERNAL_ERROR": ServerError,
    "SERVER_ERROR": ServerError,
    "UNAVAILABLE": UnavailableError,
}


def raise_for_error(response: dict[str, Any]) -> None:
    """Inspect an MCP response and raise the appropriate typed exception.

    If the response does not have ``"error": true``, this function is a no-op.

    Parameters
    ----------
    response:
        The raw JSON-decoded response dict from any MCP server.

    Raises
    ------
    TrialMCPError:
        A subclass matching the response's ``code`` field.
    """
    if not response.get("error"):
        return

    code = response.get("code", "UNKNOWN")
    message = response.get("message", "Unknown error")
    raw_details = response.get("details")

    details: ErrorDetails | None = None
    if isinstance(raw_details, dict):
        details = ErrorDetails(
            field_name=raw_details.get("field"),
            expected_pattern=raw_details.get("expected_pattern"),
            retry_after_seconds=raw_details.get("retry_after_seconds"),
            extra={
                k: v
                for k, v in raw_details.items()
                if k not in ("field", "expected_pattern", "retry_after_seconds")
            },
        )

    exc_cls = _CODE_TO_EXCEPTION.get(code, TrialMCPError)
    raise exc_cls(
        message,
        server=response.get("server"),
        tool=response.get("tool"),
        request_id=response.get("request_id"),
        timestamp=response.get("timestamp"),
        details=details,
    )
