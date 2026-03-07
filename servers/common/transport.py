"""MCP transport layer — stdin/stdout JSON-RPC protocol handling.

Implements the Model Context Protocol transport for reading requests
from stdin and writing responses to stdout in JSON-RPC 2.0 format.
"""

from __future__ import annotations

import json
import sys
from typing import Any


class MCPTransport:
    """Handles MCP protocol communication over stdin/stdout.

    Reads JSON-RPC 2.0 requests from stdin and writes responses to stdout,
    implementing the core MCP transport layer for all five domain servers.
    """

    def __init__(self, input_stream: Any = None, output_stream: Any = None) -> None:
        self._input = input_stream or sys.stdin
        self._output = output_stream or sys.stdout
        self._running = False

    def read_request(self) -> dict[str, Any] | None:
        """Read a single JSON-RPC request from the input stream."""
        try:
            line = self._input.readline()
            if not line:
                return None
            return json.loads(line.strip())
        except (json.JSONDecodeError, OSError):
            return None

    def write_response(self, response: dict[str, Any]) -> None:
        """Write a JSON-RPC response to the output stream."""
        try:
            self._output.write(json.dumps(response, ensure_ascii=True) + "\n")
            self._output.flush()
        except OSError:
            pass

    def write_error(
        self,
        request_id: str | int | None,
        code: int,
        message: str,
        data: Any = None,
    ) -> None:
        """Write a JSON-RPC error response."""
        error_obj: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error_obj["data"] = data
        response: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error_obj,
        }
        self.write_response(response)

    def write_result(self, request_id: str | int | None, result: Any) -> None:
        """Write a JSON-RPC success response."""
        response: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
        self.write_response(response)

    def start(self) -> None:
        """Start the transport loop (blocking)."""
        self._running = True

    def stop(self) -> None:
        """Signal the transport to stop."""
        self._running = False

    @property
    def is_running(self) -> bool:
        """Whether the transport loop is active."""
        return self._running
