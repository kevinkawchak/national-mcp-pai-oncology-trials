"""Abstract identity adapter interface.

Defines the base contract that all identity providers must
implement for authentication and authorization within the
National MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AuthResult(Enum):
    """Outcome of an authentication or authorization attempt."""

    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass(frozen=True)
class UserInfo:
    """Resolved identity information for an authenticated user."""

    subject: str
    issuer: str
    roles: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    email: str | None = None
    display_name: str | None = None


@dataclass(frozen=True)
class AuthzDecision:
    """Result of an authorization check."""

    result: AuthResult
    resource: str
    action: str
    reason: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


class IdentityAdapter(ABC):
    """Abstract base class for identity provider integrations.

    Concrete implementations wrap vendor-specific identity
    systems (OIDC, SAML, mTLS, etc.) behind a uniform interface
    used by the MCP gateway and downstream services.
    """

    @abstractmethod
    async def validate_token(
        self,
        token: str,
        *,
        expected_audience: str | None = None,
    ) -> dict[str, Any]:
        """Validate a bearer token and return its claims.

        Parameters
        ----------
        token:
            Raw bearer token (e.g. a JWT compact string).
        expected_audience:
            If provided, the token's ``aud`` claim must match.

        Returns
        -------
        dict[str, Any]
            Verified token claims.

        Raises
        ------
        ValueError
            If the token is malformed, expired, or fails
            validation.
        """

    @abstractmethod
    async def get_user_info(
        self,
        token: str,
    ) -> UserInfo:
        """Resolve identity details from a validated token.

        Parameters
        ----------
        token:
            A previously validated bearer token.

        Returns
        -------
        UserInfo
            Populated user identity record.
        """

    @abstractmethod
    async def authenticate(
        self,
        credentials: dict[str, Any],
    ) -> tuple[AuthResult, dict[str, Any]]:
        """Authenticate a principal with the given credentials.

        Parameters
        ----------
        credentials:
            Provider-specific credential payload (e.g. username
            and password, client certificate fields, API key).

        Returns
        -------
        tuple[AuthResult, dict[str, Any]]
            The authentication outcome and any supplementary
            data (e.g. issued tokens, expiry metadata).
        """

    @abstractmethod
    async def authorize(
        self,
        subject: str,
        resource: str,
        action: str,
        context: dict[str, Any] | None = None,
    ) -> AuthzDecision:
        """Evaluate whether *subject* may perform *action* on
        *resource*.

        Parameters
        ----------
        subject:
            Unique identifier of the requesting principal.
        resource:
            URI or logical name of the target resource.
        action:
            The operation being requested (e.g. ``read``,
            ``write``, ``execute``).
        context:
            Optional environmental attributes used by
            attribute-based policies.

        Returns
        -------
        AuthzDecision
            The authorization decision with audit metadata.
        """
