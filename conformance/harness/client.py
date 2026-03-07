"""MCP conformance harness client.

Connects to MCP server implementations via pluggable transports
(stdin/stdout, HTTP, Docker, remote URL) and provides a unified
interface for invoking MCP tools and validating responses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from conformance.harness.adapters.auth_adapter import AuthSession
from conformance.harness.adapters.docker_adapter import DockerAdapter
from conformance.harness.adapters.http_adapter import HttpAdapter
from conformance.harness.adapters.stdin_adapter import StdinAdapter


@dataclass
class MCPResponse:
    """Parsed MCP JSON-RPC 2.0 response."""

    id: str
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.error is not None

    @property
    def success(self) -> bool:
        return not self.is_error


class MCPConformanceClient:
    """Client for testing MCP server conformance.

    Supports connecting to MCP servers via multiple transport mechanisms:
    - Local process (stdin/stdout MCP)
    - HTTP endpoint
    - Docker container
    - Remote staging URL
    - Any conforming MCP endpoint

    Args:
        transport: Transport type ('stdin', 'http', 'docker').
        target: Target address (command, URL, or container name).
        auth: Optional authentication session.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        transport: str = "stdin",
        target: str = "",
        auth: AuthSession | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.transport = transport
        self.target = target
        self.auth = auth
        self.timeout = timeout
        self._adapter = self._create_adapter()
        self._request_id = 0

    def _create_adapter(self) -> StdinAdapter | HttpAdapter | DockerAdapter:
        """Create the appropriate transport adapter."""
        if self.transport == "stdin":
            return StdinAdapter(command=self.target, timeout=self.timeout)
        elif self.transport == "http":
            return HttpAdapter(base_url=self.target, timeout=self.timeout, auth=self.auth)
        elif self.transport == "docker":
            return DockerAdapter(container=self.target, timeout=self.timeout)
        else:
            msg = f"Unsupported transport: {self.transport}"
            raise ValueError(msg)

    def _next_id(self) -> str:
        """Generate the next JSON-RPC request ID."""
        self._request_id += 1
        return str(self._request_id)

    def _build_request(self, method: str, params: dict[str, Any] | None = None) -> dict:
        """Build a JSON-RPC 2.0 request."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            request["params"] = params
        return request

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPResponse:
        """Invoke an MCP tool and return the parsed response.

        Args:
            tool_name: Name of the MCP tool to invoke.
            arguments: Tool arguments as a dictionary.

        Returns:
            Parsed MCPResponse with result or error.
        """
        request = self._build_request(
            "tools/call",
            {"name": tool_name, "arguments": arguments or {}},
        )
        raw = self._adapter.send(request)
        return MCPResponse(
            id=raw.get("id", ""),
            result=raw.get("result"),
            error=raw.get("error"),
            raw=raw,
        )

    def list_tools(self) -> MCPResponse:
        """List available tools on the connected server."""
        request = self._build_request("tools/list")
        raw = self._adapter.send(request)
        return MCPResponse(
            id=raw.get("id", ""),
            result=raw.get("result"),
            error=raw.get("error"),
            raw=raw,
        )

    def initialize(self) -> MCPResponse:
        """Send the MCP initialize request."""
        request = self._build_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "trialmcp-conformance-harness",
                    "version": "0.8.0",
                },
            },
        )
        raw = self._adapter.send(request)
        return MCPResponse(
            id=raw.get("id", ""),
            result=raw.get("result"),
            error=raw.get("error"),
            raw=raw,
        )

    def health_check(self) -> MCPResponse:
        """Invoke the health_status tool."""
        return self.call_tool("health_status")

    def connect(self) -> None:
        """Establish connection to the target server."""
        self._adapter.connect()

    def disconnect(self) -> None:
        """Close the connection to the target server."""
        self._adapter.disconnect()

    def __enter__(self) -> MCPConformanceClient:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()


def create_client_from_config(config: dict[str, Any]) -> MCPConformanceClient:
    """Create an MCPConformanceClient from a configuration dictionary.

    Args:
        config: Configuration with 'transport', 'target', 'auth', 'timeout' keys.

    Returns:
        Configured MCPConformanceClient instance.
    """
    auth = None
    if "auth" in config:
        auth = AuthSession(
            token=config["auth"].get("token", ""),
            token_type=config["auth"].get("token_type", "bearer"),
            headers=config["auth"].get("headers", {}),
        )

    return MCPConformanceClient(
        transport=config.get("transport", "stdin"),
        target=config.get("target", ""),
        auth=auth,
        timeout=config.get("timeout", 30.0),
    )
