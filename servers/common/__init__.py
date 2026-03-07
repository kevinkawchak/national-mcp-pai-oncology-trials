"""Shared MCP server infrastructure.

Provides transport, routing, middleware, error handling, configuration
management, structured logging, health endpoints, and schema validation
utilities used by all five domain servers.
"""

from servers.common.config import ServerConfig, load_config
from servers.common.errors import (
    AuthorizationError,
    MCPError,
    NotFoundError,
    ValidationError,
    error_response,
)
from servers.common.health import HealthChecker
from servers.common.logging import setup_logging
from servers.common.routing import RequestRouter
from servers.common.transport import MCPTransport
from servers.common.validation import SchemaValidator

__all__ = [
    "AuthorizationError",
    "HealthChecker",
    "MCPError",
    "MCPTransport",
    "NotFoundError",
    "RequestRouter",
    "SchemaValidator",
    "ServerConfig",
    "ValidationError",
    "error_response",
    "load_config",
    "setup_logging",
]
