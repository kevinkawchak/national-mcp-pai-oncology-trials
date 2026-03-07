"""Provenance MCP server entrypoint.

Provides the ProvenanceServer class that wires together the provenance
DAG, transport, routing, and middleware.
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
from servers.trialmcp_provenance.dag import ProvenanceDAG

logger = logging.getLogger(__name__)


class ProvenanceServer:
    """MCP Provenance Server — trialmcp-provenance.

    Implements DAG-based data lineage tracking with SHA-256 fingerprinting,
    W3C PROV alignment, and cross-site trace merging support.
    """

    SERVER_NAME = "trialmcp-provenance"

    def __init__(self, config: ServerConfig | None = None) -> None:
        self.config = config or load_config(server_name=self.SERVER_NAME)
        self.storage = create_storage(
            backend=self.config.storage_backend,
            dsn=self.config.storage_dsn,
        )
        self.dag = ProvenanceDAG(storage=self.storage)
        self.health = HealthChecker(self.SERVER_NAME)
        self.audit = AuditMiddleware()
        self.router = RequestRouter(self.SERVER_NAME)
        self.transport = MCPTransport()

        self._register_tools()

    def _register_tools(self) -> None:
        self.router.register("provenance_record", self.handle_record)
        self.router.register("provenance_query_forward", self.handle_query_forward)
        self.router.register("provenance_query_backward", self.handle_query_backward)
        self.router.register("provenance_verify", self.handle_verify)

    def handle_record(
        self,
        source_id: str = "",
        action: str = "read",
        actor_id: str = "",
        actor_role: str = "",
        tool_call: str = "",
        source_type: str = "fhir",
        origin_server: str = "",
        description: str = "",
        parent_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle provenance_record tool call."""
        record = self.dag.record(
            source_id=source_id,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            tool_call=tool_call,
            source_type=source_type,
            origin_server=origin_server,
            description=description,
            parent_ids=parent_ids,
        )
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="provenance_record",
            caller=actor_id,
            result_summary="RECORDED",
            parameters={"source_id": source_id, "action": action},
        )
        return record

    def handle_query_forward(
        self, record_id: str = "", depth: int = 10, **kwargs: Any
    ) -> dict[str, Any]:
        """Handle provenance_query_forward tool call."""
        records = self.dag.query_forward(record_id, depth=depth)
        return {"records": records, "total": len(records), "direction": "forward"}

    def handle_query_backward(
        self, record_id: str = "", depth: int = 10, **kwargs: Any
    ) -> dict[str, Any]:
        """Handle provenance_query_backward tool call."""
        records = self.dag.query_backward(record_id, depth=depth)
        return {"records": records, "total": len(records), "direction": "backward"}

    def handle_verify(self, record_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Handle provenance_verify tool call."""
        result = self.dag.verify(record_id=record_id)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="provenance_verify",
            caller=kwargs.get("caller", "system"),
            result_summary="VALID" if result.get("valid") else "INVALID",
        )
        return result

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
    """CLI entrypoint for trialmcp-provenance server."""
    from servers.common.logging import setup_logging

    setup_logging(level="INFO", server_name="trialmcp-provenance")
    server = ProvenanceServer()
    server.run()


if __name__ == "__main__":
    main()
