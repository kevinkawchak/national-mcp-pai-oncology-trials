"""SMART-on-FHIR / OAuth2 adapter with token management.

Extends the HAPI FHIR adapter with OAuth2 client-credentials token
handling, automatic token refresh, and expiry tracking for secure
access to SMART-enabled FHIR servers.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from integrations.fhir.hapi_adapter import HAPIFHIRAdapter

logger = logging.getLogger(__name__)


class TokenStore:
    """In-memory OAuth2 token store with expiry tracking.

    Tracks the access token, refresh token, and expiration timestamp
    so that callers can determine when a token refresh is needed.
    """

    def __init__(self) -> None:
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.expires_at: float = 0.0
        self.token_type: str = "Bearer"
        self.scope: str = ""

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the access token has expired.

        Includes a 30-second buffer to avoid using a token that is
        about to expire mid-request.
        """
        return time.time() >= (self.expires_at - 30.0)

    def update(self, token_response: dict[str, Any]) -> None:
        """Update the store from an OAuth2 token response.

        Args:
            token_response: Parsed JSON from the token endpoint.
        """
        self.access_token = token_response.get("access_token")
        self.refresh_token = token_response.get("refresh_token", self.refresh_token)
        self.token_type = token_response.get("token_type", "Bearer")
        self.scope = token_response.get("scope", self.scope)
        expires_in = int(token_response.get("expires_in", 3600))
        self.expires_at = time.time() + expires_in

    def clear(self) -> None:
        """Clear all stored tokens."""
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0.0


class SMARTFHIRAdapter(HAPIFHIRAdapter):
    """SMART-on-FHIR adapter with OAuth2 client-credentials flow.

    Extends :class:`HAPIFHIRAdapter` to automatically acquire and
    refresh OAuth2 tokens before each request.  Supports both the
    initial client-credentials grant and refresh-token grant.

    Args:
        base_url: Root URL of the FHIR server.
        token_url: OAuth2 token endpoint URL.
        client_id: OAuth2 client identifier.
        client_secret: OAuth2 client secret.
        scopes: Space-separated list of requested scopes.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: str = "system/*.read",
        timeout: int = 30,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout)
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._token_store = TokenStore()

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    @property
    def token_store(self) -> TokenStore:
        """Expose the token store for inspection or testing."""
        return self._token_store

    def _acquire_token(self) -> None:
        """Acquire a new access token via client-credentials grant."""
        payload = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": self._scopes,
            }
        ).encode("utf-8")
        self._post_token(payload)

    def _refresh_existing_token(self) -> None:
        """Refresh the access token using a stored refresh token."""
        if not self._token_store.refresh_token:
            self._acquire_token()
            return
        payload = urllib.parse.urlencode(
            {
                "grant_type": "refresh_token",
                "refresh_token": self._token_store.refresh_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
        ).encode("utf-8")
        try:
            self._post_token(payload)
        except (urllib.error.HTTPError, urllib.error.URLError):
            logger.warning("Refresh token grant failed; falling back to client-credentials grant.")
            self._acquire_token()

    def _post_token(self, payload: bytes) -> None:
        """POST to the token endpoint and update the token store."""
        req = urllib.request.Request(
            self._token_url,
            data=payload,
            headers={
                "Content-Type": ("application/x-www-form-urlencoded"),
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                token_response = json.loads(resp.read().decode("utf-8"))
                self._token_store.update(token_response)
                logger.debug("OAuth2 token acquired successfully.")
        except urllib.error.HTTPError as exc:
            logger.error("Token endpoint HTTP %s: %s", exc.code, exc.reason)
            raise
        except urllib.error.URLError as exc:
            logger.error("Token endpoint connection error: %s", exc.reason)
            raise

    def _ensure_valid_token(self) -> None:
        """Ensure a valid access token is available.

        Acquires a new token or refreshes the existing one as needed.
        """
        if self._token_store.access_token is None:
            self._acquire_token()
        elif self._token_store.is_expired:
            self._refresh_existing_token()

    # ------------------------------------------------------------------
    # Override HTTP layer to inject Authorization header
    # ------------------------------------------------------------------

    def _request(
        self,
        url: str,
        method: str = "GET",
        body: bytes | None = None,
    ) -> dict[str, Any] | None:
        """Execute an authenticated HTTP request.

        Ensures a valid OAuth2 token is present before delegating
        to the parent :class:`HAPIFHIRAdapter` HTTP implementation.
        """
        self._ensure_valid_token()
        token = self._token_store.access_token
        if token:
            self._headers["Authorization"] = f"{self._token_store.token_type} {token}"
        return super()._request(url, method=method, body=body)
