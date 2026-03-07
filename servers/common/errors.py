"""Structured error responses for MCP servers.

Implements the 9-code error taxonomy defined in
schemas/error-response.schema.json and provides exception classes
for common error conditions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# 9-code error taxonomy per spec/tool-contracts.md
ERROR_CODES = {
    "AUTHZ_DENIED",
    "AUTHZ_TOKEN_INVALID",
    "AUTHZ_TOKEN_EXPIRED",
    "VALIDATION_ERROR",
    "RESOURCE_NOT_FOUND",
    "RATE_LIMITED",
    "INTERNAL_ERROR",
    "CHAIN_INTEGRITY_ERROR",
    "PRIVACY_VIOLATION",
}


class MCPError(Exception):
    """Base exception for MCP server errors."""

    def __init__(self, code: str, message: str, **kwargs: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = kwargs


class AuthorizationError(MCPError):
    """Raised when an authorization check fails."""

    def __init__(self, message: str = "Authorization denied") -> None:
        super().__init__("AUTHZ_DENIED", message)


class ValidationError(MCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__("VALIDATION_ERROR", message)


class NotFoundError(MCPError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__("RESOURCE_NOT_FOUND", message)


def error_response(
    code: str,
    message: str,
    tool: str = "",
    server: str = "",
    request_id: str = "",
) -> dict[str, Any]:
    """Build a schema-valid error response per error-response.schema.json."""
    resp: dict[str, Any] = {
        "error": True,
        "code": code,
        "message": message,
    }
    if server:
        resp["server"] = server
    if tool:
        resp["tool"] = tool
    if request_id:
        resp["request_id"] = request_id
    resp["timestamp"] = datetime.now(timezone.utc).isoformat()
    return resp
