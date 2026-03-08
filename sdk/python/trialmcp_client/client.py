"""Unified MCP client for the National MCP-PAI Oncology Trials network.

Provides connection management, retry logic, circuit-breaker resilience,
and middleware composition for all five MCP servers.  Acts as the primary
entry-point for SDK consumers.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from .config import ClientConfig, ServerName
from .exceptions import TrialMCPError, UnavailableError, raise_for_error
from .middleware.audit_middleware import AuditMiddleware
from .middleware.auth_middleware import AuthMiddleware
from .middleware.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry
from .middleware.retry_middleware import RetryMiddleware

logger = logging.getLogger("trialmcp.client")


class MCPTransport:
    """Abstract transport layer for MCP JSON-RPC communication.

    In production this would use HTTP/2 or WebSockets.  The SDK ships with
    a stub implementation that can be replaced by concrete transports.
    """

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._connected: dict[ServerName, bool] = {}

    async def connect(self, server: ServerName) -> None:
        """Establish a connection to the given MCP server."""
        endpoint = self._config.get_endpoint(server)
        logger.info("Connecting to %s at %s", server.value, endpoint.base_url)
        self._connected[server] = True

    async def disconnect(self, server: ServerName) -> None:
        """Gracefully close the connection to the given MCP server."""
        logger.info("Disconnecting from %s", server.value)
        self._connected.pop(server, None)

    async def disconnect_all(self) -> None:
        """Disconnect from all connected servers."""
        servers = list(self._connected.keys())
        for server in servers:
            await self.disconnect(server)

    def is_connected(self, server: ServerName) -> bool:
        """Check whether we have an active connection to the server."""
        return self._connected.get(server, False)

    async def send_request(
        self,
        server: ServerName,
        tool: str,
        params: dict[str, Any],
        *,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a JSON-RPC tool call and return the parsed response.

        Parameters
        ----------
        server:
            Target MCP server.
        tool:
            Tool name to invoke on the server.
        params:
            Tool call parameters.
        request_id:
            Correlation ID for tracing.

        Returns
        -------
        dict:
            Parsed JSON response from the server.

        Raises
        ------
        UnavailableError:
            If not connected to the target server.
        """
        if not self.is_connected(server):
            raise UnavailableError(
                f"Not connected to {server.value}",
                server=server.value,
                tool=tool,
            )

        rid = request_id or str(uuid.uuid4())

        endpoint = self._config.get_endpoint(server)
        logger.debug(
            "Request %s -> %s/%s: %s",
            rid,
            endpoint.base_url,
            tool,
            json.dumps(params, default=str),
        )

        # Stub: in production, send over HTTP/WebSocket and parse the response.
        # For now, return a placeholder indicating the transport layer is ready.
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "status": "transport_stub",
                "server": server.value,
                "tool": tool,
                "params": params,
            },
        }


class TrialMCPClient:
    """Unified async client for all National MCP-PAI Oncology Trials servers.

    Composes transport, middleware (auth, audit, retry, circuit-breaker), and
    per-server sub-clients into a single entry-point.

    Usage::

        config = ClientConfig(...)
        async with TrialMCPClient(config) as client:
            decision = await client.authz.evaluate(
                role="robot_agent",
                server="trialmcp-fhir",
                tool="fhir_read",
            )

    """

    def __init__(self, config: ClientConfig | None = None) -> None:
        self._config = config or ClientConfig()
        self._transport = MCPTransport(self._config)
        self._closed = False

        # Middleware stack
        self._circuit_breakers = CircuitBreakerRegistry(self._config.circuit_breaker_policy)
        self._retry = RetryMiddleware(self._config.retry_policy)
        self._auth = AuthMiddleware(self._config.auth, self._transport)
        self._audit = AuditMiddleware(
            enabled=self._config.enable_audit_logging,
            log_path=self._config.audit_log_path,
            actor_id=self._config.auth.actor_id,
            site_id=self._config.site_id,
        )

        # Lazily-initialised sub-clients
        self._authz_client: Any = None
        self._fhir_client: Any = None
        self._dicom_client: Any = None
        self._ledger_client: Any = None
        self._provenance_client: Any = None

    # ------------------------------------------------------------------
    # Sub-client accessors (lazy import to avoid circular deps)
    # ------------------------------------------------------------------

    @property
    def authz(self) -> Any:
        """AuthZ sub-client for authorization operations."""
        if self._authz_client is None:
            from .authz import AuthzClient

            self._authz_client = AuthzClient(self)
        return self._authz_client

    @property
    def fhir(self) -> Any:
        """FHIR sub-client for clinical data operations."""
        if self._fhir_client is None:
            from .fhir import FHIRClient

            self._fhir_client = FHIRClient(self)
        return self._fhir_client

    @property
    def dicom(self) -> Any:
        """DICOM sub-client for imaging operations."""
        if self._dicom_client is None:
            from .dicom import DICOMClient

            self._dicom_client = DICOMClient(self)
        return self._dicom_client

    @property
    def ledger(self) -> Any:
        """Ledger sub-client for audit chain operations."""
        if self._ledger_client is None:
            from .ledger import LedgerClient

            self._ledger_client = LedgerClient(self)
        return self._ledger_client

    @property
    def provenance(self) -> Any:
        """Provenance sub-client for data lineage operations."""
        if self._provenance_client is None:
            from .provenance import ProvenanceClient

            self._provenance_client = ProvenanceClient(self)
        return self._provenance_client

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self, servers: list[ServerName] | None = None) -> None:
        """Connect to the specified MCP servers (or all by default).

        Parameters
        ----------
        servers:
            Explicit list of servers to connect to.  If ``None``, connects
            to all five servers.
        """
        targets = servers or list(ServerName)
        connect_tasks = [self._transport.connect(s) for s in targets]
        await asyncio.gather(*connect_tasks)
        logger.info("Connected to %d server(s)", len(targets))

    async def close(self) -> None:
        """Gracefully disconnect from all servers and release resources."""
        if self._closed:
            return
        self._closed = True
        await self._transport.disconnect_all()
        await self._audit.flush()
        logger.info("TrialMCPClient closed")

    async def __aenter__(self) -> TrialMCPClient:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Core request pipeline
    # ------------------------------------------------------------------

    async def call_tool(
        self,
        server: ServerName,
        tool: str,
        params: dict[str, Any] | None = None,
        *,
        request_id: str | None = None,
        skip_auth: bool = False,
    ) -> dict[str, Any]:
        """Execute a tool call through the full middleware pipeline.

        The pipeline order is:
        1. Circuit breaker check
        2. Auth middleware (token injection)
        3. Retry middleware (with exponential backoff)
        4. Transport send
        5. Error parsing
        6. Audit logging

        Parameters
        ----------
        server:
            Target MCP server.
        tool:
            Tool name to invoke.
        params:
            Tool call parameters.
        request_id:
            Optional correlation ID.
        skip_auth:
            If ``True``, skip automatic token injection (used for the
            ``issue_token`` call itself).

        Returns
        -------
        dict:
            The ``result`` field from the JSON-RPC response.

        Raises
        ------
        TrialMCPError:
            Any error from the 9-code taxonomy.
        UnavailableError:
            If the circuit breaker is open for this server.
        """
        rid = request_id or str(uuid.uuid4())
        call_params = params or {}

        # 1. Circuit breaker gate
        breaker = self._circuit_breakers.get(server)
        breaker.check()

        # 2. Auth middleware
        if not skip_auth:
            call_params = await self._auth.inject_credentials(server, tool, call_params)

        # 3. Retry wrapper around transport call
        async def _do_call() -> dict[str, Any]:
            response = await self._transport.send_request(server, tool, call_params, request_id=rid)
            # Parse error responses
            result = response.get("result", response)
            raise_for_error(result)
            return result

        try:
            result = await self._retry.execute(_do_call, server_name=server.value)
            breaker.record_success()
        except TrialMCPError:
            breaker.record_failure()
            raise
        except Exception as exc:
            breaker.record_failure()
            raise UnavailableError(
                f"Transport error communicating with {server.value}: {exc}",
                server=server.value,
                tool=tool,
                request_id=rid,
            ) from exc

        # 4. Audit logging
        await self._audit.log_call(
            server=server.value,
            tool=tool,
            params=call_params,
            result_summary=_summarise(result),
            request_id=rid,
        )

        return result

    # ------------------------------------------------------------------
    # Health / diagnostics
    # ------------------------------------------------------------------

    async def health_check(self, server: ServerName) -> dict[str, Any]:
        """Check the health of a specific MCP server.

        Returns
        -------
        dict:
            Health status payload from the server.
        """
        return await self.call_tool(server, "health", {}, skip_auth=True)

    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Check the health of all connected servers.

        Returns
        -------
        dict:
            Mapping of server name to health status.
        """
        results: dict[str, dict[str, Any]] = {}

        async def _check(s: ServerName) -> None:
            try:
                results[s.value] = await self.health_check(s)
            except Exception as exc:
                results[s.value] = {"status": "unreachable", "error": str(exc)}

        await asyncio.gather(*[_check(s) for s in ServerName])
        return results

    @property
    def config(self) -> ClientConfig:
        """Return the active client configuration."""
        return self._config

    @property
    def circuit_breakers(self) -> CircuitBreakerRegistry:
        """Access the circuit breaker registry for diagnostics."""
        return self._circuit_breakers

    def get_circuit_breaker(self, server: ServerName) -> CircuitBreaker:
        """Return the circuit breaker for a specific server."""
        return self._circuit_breakers.get(server)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _summarise(result: dict[str, Any], max_length: int = 200) -> str:
    """Create a brief, PHI-safe summary of a tool result for audit logging."""
    status = result.get("status", "ok")
    resource_type = result.get("resource_type", "")
    total = result.get("total")
    parts = [f"status={status}"]
    if resource_type:
        parts.append(f"type={resource_type}")
    if total is not None:
        parts.append(f"total={total}")
    summary = ", ".join(parts)
    return summary[:max_length]
