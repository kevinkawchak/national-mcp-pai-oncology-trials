"""OIDC/JWT token validation adapter.

Implements JWT parsing and validation using only the Python
standard library (``json``, ``base64``).  Signature verification
is delegated to a pluggable verifier callback so that the adapter
remains independent of any specific cryptography library.
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from integrations.identity.base_adapter import (
    AuthResult,
    AuthzDecision,
    IdentityAdapter,
    UserInfo,
)


@dataclass(frozen=True)
class TokenClaims:
    """Parsed and validated JWT claims."""

    header: dict[str, Any]
    payload: dict[str, Any]
    signature_bytes: bytes


SignatureVerifier = Callable[[bytes, bytes, dict[str, Any]], Awaitable[bool]]
"""Async callback that verifies a JWT signature.

Parameters are (signing_input, signature, header).  Must return
``True`` when the signature is valid.
"""


def _b64url_decode(data: str) -> bytes:
    """Decode a Base64-URL encoded string with padding fix."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def _decode_jwt_parts(token: str) -> TokenClaims:
    """Split and decode a compact JWT without verification.

    Raises
    ------
    ValueError
        If the token is not a valid three-part JWT.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT must contain exactly three Base64-URL parts")
    header = json.loads(_b64url_decode(parts[0]))
    payload = json.loads(_b64url_decode(parts[1]))
    signature_bytes = _b64url_decode(parts[2])
    return TokenClaims(
        header=header,
        payload=payload,
        signature_bytes=signature_bytes,
    )


class OIDCAdapter(IdentityAdapter):
    """OIDC-compatible identity adapter with JWT validation.

    Parameters
    ----------
    issuer:
        Expected ``iss`` claim value.
    audience:
        Default expected ``aud`` claim value.
    signature_verifier:
        Async callback for cryptographic signature checks.
    clock_skew_seconds:
        Permitted clock-skew tolerance for ``exp``/``nbf``
        checks.
    """

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        signature_verifier: SignatureVerifier,
        clock_skew_seconds: int = 30,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._verifier = signature_verifier
        self._clock_skew = clock_skew_seconds

    # -- internal helpers ------------------------------------

    def _validate_issuer(self, payload: dict[str, Any]) -> None:
        """Raise if ``iss`` does not match expected issuer."""
        iss = payload.get("iss")
        if iss != self._issuer:
            raise ValueError(f"Issuer mismatch: expected {self._issuer!r}, got {iss!r}")

    def _validate_audience(
        self,
        payload: dict[str, Any],
        expected: str | None = None,
    ) -> None:
        """Raise if ``aud`` does not match."""
        expected = expected or self._audience
        aud = payload.get("aud")
        if isinstance(aud, list):
            if expected not in aud:
                raise ValueError(f"Audience {expected!r} not in {aud!r}")
        elif aud != expected:
            raise ValueError(f"Audience mismatch: expected {expected!r}, got {aud!r}")

    def _validate_expiry(self, payload: dict[str, Any]) -> None:
        """Raise if the token has expired or is not yet valid."""
        now = time.time()
        exp = payload.get("exp")
        if exp is not None and now > exp + self._clock_skew:
            raise ValueError("Token has expired")
        nbf = payload.get("nbf")
        if nbf is not None and now < nbf - self._clock_skew:
            raise ValueError("Token is not yet valid")

    def _extract_roles(self, payload: dict[str, Any]) -> list[str]:
        """Extract roles from common claim locations."""
        roles: list[str] = []
        realm = payload.get("realm_access", {}).get("roles", [])
        roles.extend(realm)
        resource = payload.get("resource_access", {})
        for client_roles in resource.values():
            roles.extend(client_roles.get("roles", []))
        explicit = payload.get("roles", [])
        if isinstance(explicit, list):
            roles.extend(explicit)
        return list(dict.fromkeys(roles))

    # -- public interface ------------------------------------

    async def validate_token(
        self,
        token: str,
        *,
        expected_audience: str | None = None,
    ) -> dict[str, Any]:
        """Validate a JWT and return verified claims."""
        claims = _decode_jwt_parts(token)
        signing_input = token.rsplit(".", 1)[0].encode("ascii")

        sig_ok = await self._verifier(
            signing_input,
            claims.signature_bytes,
            claims.header,
        )
        if not sig_ok:
            raise ValueError("JWT signature verification failed")

        self._validate_issuer(claims.payload)
        self._validate_audience(claims.payload, expected_audience)
        self._validate_expiry(claims.payload)
        return claims.payload

    async def get_user_info(self, token: str) -> UserInfo:
        """Resolve user info from JWT claims."""
        payload = await self.validate_token(token)
        return UserInfo(
            subject=payload.get("sub", ""),
            issuer=payload.get("iss", ""),
            roles=self._extract_roles(payload),
            attributes=payload,
            email=payload.get("email"),
            display_name=payload.get("name"),
        )

    async def authenticate(
        self,
        credentials: dict[str, Any],
    ) -> tuple[AuthResult, dict[str, Any]]:
        """Authenticate by validating a presented JWT.

        Expects ``credentials["token"]`` to contain the JWT.
        """
        token = credentials.get("token")
        if not token:
            return AuthResult.INVALID, {"error": "No token provided"}
        try:
            claims = await self.validate_token(token)
            return AuthResult.GRANTED, {"claims": claims}
        except ValueError as exc:
            if "expired" in str(exc).lower():
                return AuthResult.EXPIRED, {"error": str(exc)}
            return AuthResult.INVALID, {"error": str(exc)}

    async def authorize(
        self,
        subject: str,
        resource: str,
        action: str,
        context: dict[str, Any] | None = None,
    ) -> AuthzDecision:
        """Stub authorization -- delegate to policy engine."""
        return AuthzDecision(
            result=AuthResult.DENIED,
            resource=resource,
            action=action,
            reason=("OIDC adapter defers authorization to the policy engine"),
        )
