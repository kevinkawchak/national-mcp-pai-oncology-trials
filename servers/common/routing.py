"""Request routing and tool dispatching for MCP servers.

Routes incoming MCP tool-call requests to the appropriate handler
functions registered by each domain server.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

ToolHandler = Callable[..., dict[str, Any]]


class RequestRouter:
    """Routes MCP tool-call requests to registered handler functions.

    Each domain server registers its tool handlers with the router,
    which then dispatches incoming requests based on the tool name.
    """

    def __init__(self, server_name: str) -> None:
        self.server_name = server_name
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, tool_name: str, handler: ToolHandler) -> None:
        """Register a handler function for a tool name."""
        self._handlers[tool_name] = handler
        logger.debug("Registered tool %s on %s", tool_name, self.server_name)

    def list_tools(self) -> list[str]:
        """Return the list of registered tool names."""
        return sorted(self._handlers.keys())

    def has_tool(self, tool_name: str) -> bool:
        """Check whether a tool is registered."""
        return tool_name in self._handlers

    def dispatch(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a request to the registered handler.

        Raises KeyError if the tool is not registered.
        """
        handler = self._handlers.get(tool_name)
        if handler is None:
            raise KeyError(f"Unknown tool: {tool_name}")
        return handler(**params)

    def route_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Route a full MCP request dict to the appropriate handler.

        Expects ``request`` to have ``method`` and optional ``params`` keys.
        Returns a result dict or raises on unknown tools.
        """
        method = request.get("method", "")
        params = request.get("params", {})

        # MCP tool calls use "tools/call" method with tool name in params
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            return self.dispatch(tool_name, arguments)

        # Direct tool name as method
        if self.has_tool(method):
            return self.dispatch(method, params)

        raise KeyError(f"Unsupported method: {method}")
