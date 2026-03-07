"""Authenticated session management for MCP conformance testing.

Provides authentication session handling for connecting to
secured MCP server deployments during conformance testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AuthSession:
    """Authenticated session for MCP server access.

    Manages authentication tokens and headers required for
    connecting to secured MCP server deployments.

    Attributes:
        token: Bearer or API token for authentication.
        token_type: Token type ('bearer', 'api-key', 'jwt').
        headers: Additional authentication headers.
        username: Username for basic auth (if applicable).
        password: Password for basic auth (if applicable).
        expires_at: Token expiration timestamp (ISO 8601).
    """

    token: str = ""
    token_type: str = "bearer"
    headers: dict[str, str] = field(default_factory=dict)
    username: str = ""
    password: str = ""
    expires_at: str = ""

    def get_headers(self) -> dict[str, str]:
        """Build HTTP headers for authenticated requests.

        Returns:
            Dictionary of authentication headers.
        """
        auth_headers = dict(self.headers)

        if self.token:
            if self.token_type == "bearer":
                auth_headers["Authorization"] = f"Bearer {self.token}"
            elif self.token_type == "api-key":
                auth_headers["X-API-Key"] = self.token
            elif self.token_type == "jwt":
                auth_headers["Authorization"] = f"Bearer {self.token}"

        return auth_headers

    @property
    def is_authenticated(self) -> bool:
        """Check if the session has valid credentials."""
        return bool(self.token or (self.username and self.password))


class AuthManager:
    """Manages authentication sessions for conformance testing.

    Handles token acquisition, refresh, and revocation for
    testing authentication-related conformance requirements.

    Args:
        auth_server_url: URL of the authorization server.
        client_id: Client identifier for token requests.
        client_secret: Client secret for token requests.
    """

    def __init__(
        self,
        auth_server_url: str = "",
        client_id: str = "",
        client_secret: str = "",
    ) -> None:
        self.auth_server_url = auth_server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._sessions: dict[str, AuthSession] = {}

    def create_session(
        self,
        role: str,
        token: str = "",
        token_type: str = "bearer",
    ) -> AuthSession:
        """Create an authentication session for a specific role.

        Args:
            role: Actor role (e.g., 'robot_agent', 'auditor').
            token: Pre-existing token (if available).
            token_type: Token type.

        Returns:
            Configured AuthSession.
        """
        session = AuthSession(token=token, token_type=token_type)
        self._sessions[role] = session
        return session

    def get_session(self, role: str) -> AuthSession | None:
        """Retrieve an existing session for a role.

        Args:
            role: Actor role name.

        Returns:
            AuthSession if exists, None otherwise.
        """
        return self._sessions.get(role)

    def revoke_session(self, role: str) -> bool:
        """Revoke and remove a session for a role.

        Args:
            role: Actor role name.

        Returns:
            True if a session was revoked, False if no session existed.
        """
        if role in self._sessions:
            del self._sessions[role]
            return True
        return False

    def clear_all_sessions(self) -> None:
        """Revoke all active sessions."""
        self._sessions.clear()
