"""HTTP transport adapter for MCP conformance testing.

Connects to MCP servers exposed over HTTP endpoints, supporting
both direct HTTP MCP transport and REST-style API wrappers.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from conformance.harness.adapters.auth_adapter import AuthSession


class HttpAdapter:
    """Transport adapter for HTTP-based MCP communication.

    Sends JSON-RPC 2.0 requests to an MCP server via HTTP POST.

    Args:
        base_url: Base URL of the MCP server (e.g., 'http://localhost:8000').
        timeout: Request timeout in seconds.
        auth: Optional authentication session for authenticated requests.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        auth: AuthSession | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = auth
        self._connected = False

    def connect(self) -> None:
        """Verify connectivity to the HTTP endpoint."""
        self._connected = True

    def disconnect(self) -> None:
        """Close the HTTP connection."""
        self._connected = False

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request via HTTP POST.

        Args:
            request: JSON-RPC 2.0 request dictionary.

        Returns:
            Parsed JSON-RPC 2.0 response dictionary.

        Raises:
            ConnectionError: If not connected or the request fails.
        """
        if not self._connected:
            msg = "Not connected. Call connect() first."
            raise ConnectionError(msg)

        url = f"{self.base_url}/mcp"
        headers = {"Content-Type": "application/json"}

        # Add authentication headers
        if self.auth:
            headers.update(self.auth.get_headers())

        body = json.dumps(request).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                response_data = resp.read().decode("utf-8")
                return json.loads(response_data)
        except urllib.error.URLError as e:
            msg = f"HTTP request failed: {e}"
            raise ConnectionError(msg) from e
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response: {e}"
            raise ConnectionError(msg) from e

    def __enter__(self) -> HttpAdapter:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
