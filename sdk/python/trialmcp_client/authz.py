"""AuthZ sub-client for authorization operations.

Wraps the four AuthZ server tools: ``authz_evaluate``, ``authz_issue_token``,
``authz_validate_token``, and ``authz_revoke_token``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .config import ServerName
from .exceptions import raise_for_error
from .models import AuthzDecision, SessionToken

if TYPE_CHECKING:
    from .client import TrialMCPClient

logger = logging.getLogger("trialmcp.authz")

_SERVER = ServerName.AUTHZ


class AuthzClient:
    """Sub-client for the ``trialmcp-authz`` MCP server.

    Provides typed, async wrappers around the four authorization tools.

    Parameters
    ----------
    parent:
        The :class:`TrialMCPClient` that owns this sub-client.
    """

    def __init__(self, parent: TrialMCPClient) -> None:
        self._client = parent

    # ------------------------------------------------------------------
    # authz_evaluate
    # ------------------------------------------------------------------

    async def evaluate(
        self,
        *,
        role: str,
        server: str,
        tool: str,
        context: dict[str, Any] | None = None,
    ) -> AuthzDecision:
        """Evaluate an authorization request against the RBAC policy engine.

        Parameters
        ----------
        role:
            Actor role from the 6-role model (e.g. ``"robot_agent"``).
        server:
            Target MCP server name (e.g. ``"trialmcp-fhir"``).
        tool:
            Target MCP tool name (e.g. ``"fhir_read"``).
        context:
            Optional additional context for policy evaluation.

        Returns
        -------
        AuthzDecision:
            The policy evaluation result.

        Raises
        ------
        AuthzDeniedError:
            If the policy explicitly denies access.
        """
        params: dict[str, Any] = {
            "role": role,
            "server": server,
            "tool": tool,
        }
        if context:
            params["context"] = context

        result = await self._client.call_tool(_SERVER, "authz_evaluate", params)
        raise_for_error(result)
        return AuthzDecision.from_dict(result)

    # ------------------------------------------------------------------
    # authz_issue_token
    # ------------------------------------------------------------------

    async def issue_token(
        self,
        *,
        subject: str,
        role: str,
        ttl_seconds: int = 3600,
        scope: list[str] | None = None,
    ) -> SessionToken:
        """Request a new session token from the AuthZ server.

        Parameters
        ----------
        subject:
            Actor identifier (e.g. ``"robot_agent_001"``).
        role:
            Actor role.
        ttl_seconds:
            Requested token time-to-live in seconds.
        scope:
            Optional list of permitted tool patterns.

        Returns
        -------
        SessionToken:
            The issued session token with metadata.
        """
        params: dict[str, Any] = {
            "subject": subject,
            "role": role,
            "ttl_seconds": ttl_seconds,
        }
        if scope:
            params["scope"] = scope

        result = await self._client.call_tool(_SERVER, "authz_issue_token", params, skip_auth=True)
        raise_for_error(result)
        return SessionToken.from_dict(result)

    # ------------------------------------------------------------------
    # authz_validate_token
    # ------------------------------------------------------------------

    async def validate_token(
        self,
        *,
        token: str,
    ) -> dict[str, Any]:
        """Validate an existing session token.

        Parameters
        ----------
        token:
            The raw session token to validate.

        Returns
        -------
        dict:
            Validation result including subject, role, and expiry.

        Raises
        ------
        AuthzExpiredError:
            If the token has expired.
        """
        result = await self._client.call_tool(
            _SERVER,
            "authz_validate_token",
            {"token": token},
            skip_auth=True,
        )
        raise_for_error(result)
        return result

    # ------------------------------------------------------------------
    # authz_revoke_token
    # ------------------------------------------------------------------

    async def revoke_token(
        self,
        *,
        token: str,
        reason: str = "",
    ) -> dict[str, Any]:
        """Revoke an active session token.

        Parameters
        ----------
        token:
            The raw session token to revoke.
        reason:
            Human-readable reason for revocation.

        Returns
        -------
        dict:
            Confirmation of the revocation.
        """
        params: dict[str, Any] = {"token": token}
        if reason:
            params["reason"] = reason

        result = await self._client.call_tool(_SERVER, "authz_revoke_token", params)
        raise_for_error(result)
        return result

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def check_access(
        self,
        *,
        role: str,
        server: str,
        tool: str,
    ) -> bool:
        """Quick boolean check: is this access allowed?

        Unlike :meth:`evaluate`, this method catches denial errors and
        returns ``False`` instead of raising.

        Parameters
        ----------
        role:
            Actor role.
        server:
            Target server.
        tool:
            Target tool.

        Returns
        -------
        bool:
            ``True`` if access is allowed.
        """
        try:
            decision = await self.evaluate(role=role, server=server, tool=tool)
            return decision.allowed
        except Exception:
            return False

    async def batch_evaluate(
        self,
        requests: list[dict[str, str]],
    ) -> list[AuthzDecision]:
        """Evaluate multiple authorization requests in parallel.

        Parameters
        ----------
        requests:
            List of dicts each containing ``role``, ``server``, ``tool``.

        Returns
        -------
        list[AuthzDecision]:
            Corresponding list of authorization decisions.
        """
        import asyncio

        tasks = [
            self.evaluate(
                role=req["role"],
                server=req["server"],
                tool=req["tool"],
            )
            for req in requests
        ]
        return list(await asyncio.gather(*tasks))


# Alias for CI compatibility (CI imports AuthZClient with capital Z)
AuthZClient = AuthzClient
