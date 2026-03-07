"""Audit Ledger MCP server entrypoint.

Provides the LedgerServer class that wires together the audit chain,
transport, routing, and middleware.
"""

from __future__ import annotations

import logging
from typing import Any

from servers.common.config import ServerConfig, load_config
from servers.common.errors import error_response
from servers.common.health import HealthChecker
from servers.common.middleware import AuditMiddleware
from servers.common.routing import RequestRouter
from servers.common.transport import MCPTransport
from servers.storage import create_storage
from servers.trialmcp_ledger.chain import AuditChain

logger = logging.getLogger(__name__)


class LedgerServer:
    """MCP Audit Ledger Server — trialmcp-ledger.

    Implements hash-chained immutable audit ledger with genesis block
    initialization, chain verification, and audit record management.
    """

    SERVER_NAME = "trialmcp-ledger"

    def __init__(self, config: ServerConfig | None = None) -> None:
        self.config = config or load_config(server_name=self.SERVER_NAME)
        self.storage = create_storage(
            backend=self.config.storage_backend,
            dsn=self.config.storage_dsn,
        )
        self.chain = AuditChain(storage=self.storage)
        self.health = HealthChecker(self.SERVER_NAME)
        self.audit = AuditMiddleware()
        self.router = RequestRouter(self.SERVER_NAME)
        self.transport = MCPTransport()

        self._register_tools()

    def _register_tools(self) -> None:
        self.router.register("ledger_append", self.handle_append)
        self.router.register("ledger_verify", self.handle_verify)
        self.router.register("ledger_query", self.handle_query)
        self.router.register("ledger_export", self.handle_export)

    def handle_append(
        self,
        server: str = "",
        tool: str = "",
        caller: str = "",
        result_summary: str = "",
        parameters: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle ledger_append tool call."""
        record = self.chain.append(
            server=server,
            tool=tool,
            caller=caller,
            result_summary=result_summary,
            parameters=parameters,
        )
        return record

    def handle_verify(self, **kwargs: Any) -> dict[str, Any]:
        """Handle ledger_verify tool call."""
        result = self.chain.verify()
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="ledger_verify",
            caller=kwargs.get("caller", "system"),
            result_summary="VALID" if result.get("valid") else "INVALID",
        )
        return result

    def handle_query(
        self,
        server: str | None = None,
        tool: str | None = None,
        caller: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle ledger_query tool call."""
        records = self.chain.query(server=server, tool=tool, caller=caller, limit=limit)
        return {"records": records, "total": len(records)}

    def handle_export(self, format: str = "json", **kwargs: Any) -> dict[str, Any]:
        """Handle ledger_export tool call."""
        records = self.chain.export(format=format)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="ledger_export",
            caller=kwargs.get("caller", "system"),
            result_summary=f"EXPORTED ({len(records)} records)",
        )
        return {"records": records, "total": len(records), "format": format}

    def run(self) -> None:
        """Start the server transport loop."""
        logger.info("Starting %s", self.SERVER_NAME)
        self.transport.start()
        while self.transport.is_running:
            request = self.transport.read_request()
            if request is None:
                break
            try:
                request_id = request.get("id")
                result = self.router.route_request(request)
                self.transport.write_result(request_id, result)
            except KeyError as exc:
                self.transport.write_error(request.get("id"), -32601, str(exc))
            except Exception as exc:
                logger.exception("Error processing request")
                resp = error_response("INTERNAL_ERROR", str(exc), server=self.SERVER_NAME)
                self.transport.write_result(request.get("id"), resp)


def main() -> None:
    """CLI entrypoint for trialmcp-ledger server."""
    from servers.common.logging import setup_logging

    setup_logging(level="INFO", server_name="trialmcp-ledger")
    server = LedgerServer()
    server.run()


if __name__ == "__main__":
    main()
