"""Client configuration for the National MCP-PAI Oncology Trials SDK.

Provides structured configuration for server addresses, authentication
credentials, timeouts, and retry policies.  Configuration can be loaded
from environment variables, keyword arguments, or a combination of both.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActorRole(str, Enum):
    """The six actor roles defined by the National MCP-PAI standard."""

    ROBOT_AGENT = "robot_agent"
    TRIAL_COORDINATOR = "trial_coordinator"
    DATA_MONITOR = "data_monitor"
    AUDITOR = "auditor"
    SPONSOR = "sponsor"
    CRO = "cro"


class ServerName(str, Enum):
    """Canonical names for the five MCP servers."""

    AUTHZ = "trialmcp-authz"
    FHIR = "trialmcp-fhir"
    DICOM = "trialmcp-dicom"
    LEDGER = "trialmcp-ledger"
    PROVENANCE = "trialmcp-provenance"


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for automatic request retries.

    Parameters
    ----------
    max_retries:
        Maximum number of retry attempts before giving up.
    base_delay_seconds:
        Initial delay in seconds before the first retry.
    max_delay_seconds:
        Upper bound on the exponential backoff delay.
    exponential_base:
        Multiplier applied to the delay on each successive retry.
    retryable_codes:
        Set of error codes that are eligible for automatic retry.
    """

    max_retries: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    retryable_codes: frozenset[str] = frozenset(
        {"RATE_LIMITED", "UNAVAILABLE", "SERVER_ERROR", "INTERNAL_ERROR"}
    )


@dataclass(frozen=True)
class CircuitBreakerPolicy:
    """Configuration for the circuit breaker pattern.

    Parameters
    ----------
    failure_threshold:
        Number of consecutive failures before the circuit opens.
    recovery_timeout_seconds:
        Seconds to wait before transitioning from OPEN to HALF-OPEN.
    half_open_max_calls:
        Maximum probe calls allowed in the HALF-OPEN state.
    """

    failure_threshold: int = 5
    recovery_timeout_seconds: float = 60.0
    half_open_max_calls: int = 1


@dataclass(frozen=True)
class ServerEndpoint:
    """Connection details for a single MCP server.

    Parameters
    ----------
    host:
        Hostname or IP address.
    port:
        TCP port number.
    use_tls:
        Whether to use TLS for the connection.
    path_prefix:
        Optional URL path prefix (e.g. ``/mcp/v1``).
    """

    host: str = "localhost"
    port: int = 8000
    use_tls: bool = False
    path_prefix: str = "/mcp/v1"

    @property
    def base_url(self) -> str:
        """Construct the full base URL for this endpoint."""
        scheme = "https" if self.use_tls else "http"
        return f"{scheme}://{self.host}:{self.port}{self.path_prefix}"


@dataclass
class AuthCredentials:
    """Authentication credentials for the MCP network.

    Parameters
    ----------
    actor_id:
        Unique identifier for this actor within the trial network.
    role:
        The actor's role from the 6-role model.
    token:
        Pre-existing session token, if available.
    client_certificate_path:
        Path to a PEM-encoded client certificate for mTLS.
    client_key_path:
        Path to the client certificate's private key.
    """

    actor_id: str = ""
    role: ActorRole = ActorRole.ROBOT_AGENT
    token: str | None = None
    client_certificate_path: str | None = None
    client_key_path: str | None = None


@dataclass
class ClientConfig:
    """Top-level configuration for the TrialMCP client SDK.

    Combines server endpoints, authentication, timeouts, retry, and
    circuit-breaker settings into a single configuration object.

    Parameters
    ----------
    servers:
        Mapping of :class:`ServerName` to :class:`ServerEndpoint`.
    auth:
        Authentication credentials.
    request_timeout_seconds:
        Per-request timeout in seconds.
    connect_timeout_seconds:
        TCP connect timeout in seconds.
    retry_policy:
        Retry behaviour configuration.
    circuit_breaker_policy:
        Circuit breaker configuration.
    enable_audit_logging:
        Whether the audit middleware should log all requests locally.
    audit_log_path:
        Filesystem path for the local audit log.
    site_id:
        Clinical site identifier for multi-site deployments.
    environment:
        Deployment environment label (e.g. ``production``, ``staging``).
    extra:
        Arbitrary additional configuration values.
    """

    servers: dict[ServerName, ServerEndpoint] = field(default_factory=dict)
    auth: AuthCredentials = field(default_factory=AuthCredentials)
    request_timeout_seconds: float = 30.0
    connect_timeout_seconds: float = 10.0
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    circuit_breaker_policy: CircuitBreakerPolicy = field(default_factory=CircuitBreakerPolicy)
    enable_audit_logging: bool = True
    audit_log_path: str = "/var/log/trialmcp/sdk_audit.jsonl"
    site_id: str = ""
    environment: str = "production"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Populate default server endpoints if none were provided."""
        if not self.servers:
            self.servers = _default_server_map()

    def get_endpoint(self, server: ServerName) -> ServerEndpoint:
        """Return the endpoint for the given server, or a sensible default."""
        return self.servers.get(server, ServerEndpoint())


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

_DEFAULT_PORTS: dict[ServerName, int] = {
    ServerName.AUTHZ: 8100,
    ServerName.FHIR: 8200,
    ServerName.DICOM: 8300,
    ServerName.LEDGER: 8400,
    ServerName.PROVENANCE: 8500,
}


def _default_server_map() -> dict[ServerName, ServerEndpoint]:
    """Build the default server endpoint map using standard ports."""
    return {name: ServerEndpoint(port=port) for name, port in _DEFAULT_PORTS.items()}


def _env_or(key: str, default: str) -> str:
    """Return the environment variable *key* if set, else *default*."""
    return os.environ.get(key, default)


def config_from_env(
    *,
    prefix: str = "TRIALMCP",
    actor_id: str | None = None,
    role: ActorRole | None = None,
) -> ClientConfig:
    """Create a :class:`ClientConfig` from environment variables.

    Environment variable names follow the pattern
    ``<PREFIX>_<SERVER>_HOST``, ``<PREFIX>_<SERVER>_PORT``, etc.

    Parameters
    ----------
    prefix:
        Common prefix for all environment variables.
    actor_id:
        Override the actor ID (falls back to ``<PREFIX>_ACTOR_ID``).
    role:
        Override the actor role (falls back to ``<PREFIX>_ACTOR_ROLE``).

    Returns
    -------
    ClientConfig:
        A fully populated configuration object.
    """
    server_keys = {
        ServerName.AUTHZ: "AUTHZ",
        ServerName.FHIR: "FHIR",
        ServerName.DICOM: "DICOM",
        ServerName.LEDGER: "LEDGER",
        ServerName.PROVENANCE: "PROVENANCE",
    }

    servers: dict[ServerName, ServerEndpoint] = {}
    for sname, skey in server_keys.items():
        host = _env_or(f"{prefix}_{skey}_HOST", "localhost")
        port = int(_env_or(f"{prefix}_{skey}_PORT", str(_DEFAULT_PORTS[sname])))
        use_tls = _env_or(f"{prefix}_{skey}_TLS", "false").lower() in ("1", "true", "yes")
        servers[sname] = ServerEndpoint(host=host, port=port, use_tls=use_tls)

    resolved_actor_id = actor_id or _env_or(f"{prefix}_ACTOR_ID", "sdk-default")
    resolved_role_str = (role.value if role else None) or _env_or(
        f"{prefix}_ACTOR_ROLE", ActorRole.ROBOT_AGENT.value
    )
    resolved_role = ActorRole(resolved_role_str)

    auth = AuthCredentials(
        actor_id=resolved_actor_id,
        role=resolved_role,
        token=os.environ.get(f"{prefix}_TOKEN"),
        client_certificate_path=os.environ.get(f"{prefix}_CLIENT_CERT"),
        client_key_path=os.environ.get(f"{prefix}_CLIENT_KEY"),
    )

    timeout = float(_env_or(f"{prefix}_REQUEST_TIMEOUT", "30.0"))
    connect_timeout = float(_env_or(f"{prefix}_CONNECT_TIMEOUT", "10.0"))
    site_id = _env_or(f"{prefix}_SITE_ID", "")
    environment = _env_or(f"{prefix}_ENVIRONMENT", "production")
    audit_log_path = _env_or(f"{prefix}_AUDIT_LOG", "/var/log/trialmcp/sdk_audit.jsonl")

    return ClientConfig(
        servers=servers,
        auth=auth,
        request_timeout_seconds=timeout,
        connect_timeout_seconds=connect_timeout,
        enable_audit_logging=True,
        audit_log_path=audit_log_path,
        site_id=site_id,
        environment=environment,
    )
