"""Authentication middleware for automatic token management and refresh.

Handles session-token lifecycle: issuance, injection into outbound requests,
expiry detection, and transparent re-authentication.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..config import AuthCredentials

logger = logging.getLogger("trialmcp.middleware.auth")

# Refresh the token when it has less than this many seconds remaining
_TOKEN_REFRESH_MARGIN_SECONDS = 60


@dataclass
class _TokenState:
    """Internal mutable state tracking the current session token."""

    token: str = ""
    expires_at_epoch: float = 0.0
    refreshing: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @property
    def is_valid(self) -> bool:
        """True if we have a token that has not yet expired."""
        if not self.token:
            return False
        return time.time() < (self.expires_at_epoch - _TOKEN_REFRESH_MARGIN_SECONDS)

    @property
    def is_expired(self) -> bool:
        """True if the current token is past its expiry time."""
        return bool(self.token) and time.time() >= self.expires_at_epoch


class AuthMiddleware:
    """Middleware that injects and refreshes session tokens transparently.

    On each outbound request the middleware:

    1. Checks whether a valid token exists.
    2. If not, acquires a new token via the AuthZ ``issue_token`` tool.
    3. Injects the token into the request parameters.

    Thread-safety is ensured via an :class:`asyncio.Lock` so that concurrent
    requests share a single token-refresh operation.

    Parameters
    ----------
    credentials:
        The :class:`AuthCredentials` from the client configuration.
    transport:
        The raw MCP transport used to call ``issue_token`` on the AuthZ server.
    """

    def __init__(self, credentials: AuthCredentials, transport: Any) -> None:
        self._credentials = credentials
        self._transport = transport
        self._state = _TokenState()

        # Seed with a pre-existing token if one was provided
        if credentials.token:
            self._state.token = credentials.token
            # Assume a 1-hour expiry when we don't know the real value
            self._state.expires_at_epoch = time.time() + 3600

    async def inject_credentials(
        self,
        server: Any,
        tool: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Inject authentication credentials into outbound tool-call params.

        Parameters
        ----------
        server:
            Target :class:`ServerName`.
        tool:
            Tool being invoked (used for logging).
        params:
            Original request parameters.

        Returns
        -------
        dict:
            A copy of *params* augmented with authentication fields.
        """
        token = await self._ensure_token()
        enriched = dict(params)
        if token:
            enriched["_auth"] = {
                "token": token,
                "actor_id": self._credentials.actor_id,
                "role": self._credentials.role.value,
            }
        return enriched

    async def invalidate(self) -> None:
        """Force-invalidate the current token, triggering a refresh on the
        next request.
        """
        async with self._state.lock:
            self._state.token = ""
            self._state.expires_at_epoch = 0.0
            logger.info("Token invalidated; will re-authenticate on next request")

    async def _ensure_token(self) -> str:
        """Return a valid token, refreshing if necessary."""
        if self._state.is_valid:
            return self._state.token

        async with self._state.lock:
            # Double-check after acquiring the lock
            if self._state.is_valid:
                return self._state.token

            logger.info(
                "Token %s; requesting new token for %s (%s)",
                "expired" if self._state.is_expired else "missing",
                self._credentials.actor_id,
                self._credentials.role.value,
            )

            try:
                self._state.refreshing = True
                new_token = await self._request_token()
                self._state.token = new_token
                # Default 1-hour expiry; real implementation would parse the
                # response's ``expires_at`` field.
                self._state.expires_at_epoch = time.time() + 3600
                logger.info("Token refreshed for %s", self._credentials.actor_id)
            except Exception:
                logger.exception("Failed to refresh token")
                # Return whatever we have; the server will reject if invalid
            finally:
                self._state.refreshing = False

        return self._state.token

    async def _request_token(self) -> str:
        """Call the AuthZ server's ``issue_token`` tool to get a new token.

        Returns
        -------
        str:
            The raw session token string.
        """
        from ..config import ServerName

        response = await self._transport.send_request(
            ServerName.AUTHZ,
            "issue_token",
            {
                "subject": self._credentials.actor_id,
                "role": self._credentials.role.value,
            },
        )
        result = response.get("result", {})
        return result.get("token", "")
