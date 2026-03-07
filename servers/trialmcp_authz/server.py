"""Authorization MCP server entrypoint.

Provides the AuthzServer class that wires together the policy engine,
token store, transport, routing, and middleware for the trialmcp-authz
domain server.
"""

from __future__ import annotations

import logging
from typing import Any

from servers.common.config import ServerConfig, load_config
from servers.common.health import HealthChecker
from servers.common.middleware import AuditMiddleware
from servers.common.routing import RequestRouter
from servers.common.transport import MCPTransport
from servers.storage import create_storage
from servers.trialmcp_authz.policy_engine import PolicyEngine
from servers.trialmcp_authz.token_store import TokenStore

logger = logging.getLogger(__name__)


class AuthzServer:
    """MCP Authorization Server — trialmcp-authz.

    Implements deny-by-default RBAC authorization, SHA-256 token
    lifecycle, and audit emission for all authorization decisions.
    """

    SERVER_NAME = "trialmcp-authz"

    def __init__(self, config: ServerConfig | None = None) -> None:
        self.config = config or load_config(server_name=self.SERVER_NAME)
        self.storage = create_storage(
            backend=self.config.storage_backend,
            dsn=self.config.storage_dsn,
        )
        self.policy_engine = PolicyEngine(storage=self.storage)
        self.token_store = TokenStore(storage=self.storage)
        self.health = HealthChecker(self.SERVER_NAME)
        self.audit = AuditMiddleware()
        self.router = RequestRouter(self.SERVER_NAME)
        self.transport = MCPTransport()

        self._register_tools()

    def _register_tools(self) -> None:
        """Register all authz tool handlers with the router."""
        self.router.register("authz_evaluate", self.handle_evaluate)
        self.router.register("authz_issue_token", self.handle_issue_token)
        self.router.register("authz_validate_token", self.handle_validate_token)
        self.router.register("authz_revoke_token", self.handle_revoke_token)

    def handle_evaluate(self, role: str = "", tool: str = "", **kwargs: Any) -> dict[str, Any]:
        """Handle authz_evaluate tool call."""
        result = self.policy_engine.evaluate(role, tool, server=self.SERVER_NAME)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="authz_evaluate",
            caller=role,
            result_summary=result["effect"],
            parameters={"role": role, "tool": tool},
        )
        return result

    def handle_issue_token(
        self, role: str = "", expires_in: int = 3600, **kwargs: Any
    ) -> dict[str, Any]:
        """Handle authz_issue_token tool call."""
        result = self.token_store.issue(role, expires_in=expires_in)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="authz_issue_token",
            caller=role,
            result_summary="TOKEN_ISSUED",
            parameters={"role": role},
        )
        return result

    def handle_validate_token(self, token_hash: str = "", **kwargs: Any) -> dict[str, Any]:
        """Handle authz_validate_token tool call."""
        result = self.token_store.validate(token_hash)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="authz_validate_token",
            caller="system",
            result_summary="VALID" if result.get("valid") else "INVALID",
        )
        return result

    def handle_revoke_token(self, token_hash: str = "", **kwargs: Any) -> dict[str, Any]:
        """Handle authz_revoke_token tool call."""
        result = self.token_store.revoke(token_hash)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="authz_revoke_token",
            caller="system",
            result_summary="REVOKED" if result.get("revoked") else "NOT_FOUND",
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
                self.transport.write_error(request.get("id"), -32603, str(exc))


def main() -> None:
    """CLI entrypoint for trialmcp-authz server."""
    from servers.common.logging import setup_logging

    setup_logging(level="INFO", server_name="trialmcp-authz")
    server = AuthzServer()
    server.run()


if __name__ == "__main__":
    main()
