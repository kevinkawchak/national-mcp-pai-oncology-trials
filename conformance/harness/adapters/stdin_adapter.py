"""Stdin/stdout MCP transport adapter.

Manages a subprocess running an MCP server and communicates via
JSON-RPC 2.0 over stdin/stdout, the standard MCP transport mechanism.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


class StdinAdapter:
    """Transport adapter for stdin/stdout MCP communication.

    Launches an MCP server as a subprocess and sends/receives
    JSON-RPC 2.0 messages via its stdin and stdout streams.

    Args:
        command: Shell command to launch the MCP server process.
        timeout: Read timeout in seconds.
    """

    def __init__(self, command: str = "", timeout: float = 30.0) -> None:
        self.command = command
        self.timeout = timeout
        self._process: subprocess.Popen | None = None

    def connect(self) -> None:
        """Launch the MCP server subprocess."""
        if self._process is not None:
            return

        args = self.command.split() if isinstance(self.command, str) else self.command
        self._process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def disconnect(self) -> None:
        """Terminate the MCP server subprocess."""
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request and read the response.

        Args:
            request: JSON-RPC 2.0 request dictionary.

        Returns:
            Parsed JSON-RPC 2.0 response dictionary.

        Raises:
            ConnectionError: If the process is not connected.
            TimeoutError: If reading the response times out.
        """
        if self._process is None or self._process.stdin is None:
            msg = "Not connected. Call connect() first."
            raise ConnectionError(msg)

        # Write request as a single line of JSON
        request_line = json.dumps(request) + "\n"
        self._process.stdin.write(request_line)
        self._process.stdin.flush()

        # Read response line
        if self._process.stdout is None:
            msg = "Process stdout is not available"
            raise ConnectionError(msg)

        response_line = self._process.stdout.readline()
        if not response_line:
            msg = "No response received from server"
            raise ConnectionError(msg)

        return json.loads(response_line)

    def __enter__(self) -> StdinAdapter:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
