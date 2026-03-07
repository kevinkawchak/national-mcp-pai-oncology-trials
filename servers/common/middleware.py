"""Authentication, authorization, and audit middleware for MCP servers.

Provides middleware components that wrap tool handlers with
authorization checks and audit emission.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)

AuditCallback = Callable[[dict[str, Any]], None]


class AuthMiddleware:
    """Validates authorization tokens before allowing tool execution.

    Wraps tool handlers with token validation checks against the
    authorization server's token store.
    """

    def __init__(self, validate_fn: Callable[[str], dict[str, Any]] | None = None) -> None:
        self._validate = validate_fn

    def check_token(self, token_hash: str) -> dict[str, Any]:
        """Validate a token and return the validation result."""
        if self._validate is None:
            return {"valid": True, "role": "system"}
        return self._validate(token_hash)


class AuditMiddleware:
    """Emits audit records for all tool invocations.

    Captures tool name, caller, parameters, and result summary,
    then invokes the registered audit callback.
    """

    def __init__(self, callback: AuditCallback | None = None) -> None:
        self._callback = callback
        self._buffer: list[dict[str, Any]] = []

    def emit(
        self,
        server: str,
        tool: str,
        caller: str,
        result_summary: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create and emit an audit event."""
        event: dict[str, Any] = {
            "server": server,
            "tool": tool,
            "caller": caller,
            "result_summary": result_summary,
            "parameters": parameters or {},
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        }
        self._buffer.append(event)

        if self._callback is not None:
            try:
                self._callback(event)
            except Exception:
                logger.exception("Audit callback failed for %s.%s", server, tool)

        return event

    @property
    def buffer(self) -> list[dict[str, Any]]:
        """Return buffered audit events."""
        return list(self._buffer)

    def flush(self) -> list[dict[str, Any]]:
        """Return and clear buffered audit events."""
        events = list(self._buffer)
        self._buffer.clear()
        return events
