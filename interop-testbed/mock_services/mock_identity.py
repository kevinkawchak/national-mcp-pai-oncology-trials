"""Mock OIDC/JWT identity provider for interoperability testing.

Implements a minimal OIDC-compatible identity provider that issues
JWT tokens for authentication during interoperability testing.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from base64 import urlsafe_b64encode
from typing import Any


class MockIdentityProvider:
    """Mock OpenID Connect / JWT Identity Provider.

    Issues JWT-like tokens for testing authentication flows
    across the national interoperability testbed.

    Args:
        issuer: OIDC issuer URL.
    """

    def __init__(self, issuer: str = "https://identity.trialmcp.example.com") -> None:
        self.issuer = issuer
        self._tokens: dict[str, dict[str, Any]] = {}
        self._signing_key = hashlib.sha256(b"mock-signing-key").hexdigest()

    def issue_token(
        self,
        subject: str,
        role: str,
        audience: str = "trialmcp",
        expiry_seconds: int = 3600,
    ) -> dict[str, Any]:
        """Issue a JWT-like token.

        Args:
            subject: Token subject (user/agent identifier).
            role: Actor role.
            audience: Token audience.
            expiry_seconds: Token lifetime in seconds.

        Returns:
            Token metadata including encoded token and hash.
        """
        now = int(time.time())
        claims = {
            "iss": self.issuer,
            "sub": subject,
            "aud": audience,
            "role": role,
            "iat": now,
            "exp": now + expiry_seconds,
            "jti": str(uuid.uuid4()),
        }

        # Simple mock JWT encoding (NOT real JWT — for testing only)
        header = urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
        payload = urlsafe_b64encode(json.dumps(claims).encode()).decode()
        signature = hashlib.sha256(f"{header}.{payload}.{self._signing_key}".encode()).hexdigest()[
            :32
        ]

        token = f"{header}.{payload}.{signature}"
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        self._tokens[token_hash] = {
            "token": token,
            "claims": claims,
            "revoked": False,
        }

        return {
            "token": token,
            "token_hash": token_hash,
            "expires_at": claims["exp"],
            "role": role,
        }

    def validate_token(self, token_hash: str) -> dict[str, Any]:
        """Validate a token by its hash.

        Args:
            token_hash: SHA-256 hash of the token.

        Returns:
            Validation result with claims if valid.
        """
        if token_hash not in self._tokens:
            return {"valid": False, "reason": "Token not found"}

        token_data = self._tokens[token_hash]
        if token_data["revoked"]:
            return {"valid": False, "reason": "Token revoked"}

        now = int(time.time())
        if token_data["claims"]["exp"] < now:
            return {"valid": False, "reason": "Token expired"}

        return {
            "valid": True,
            "claims": token_data["claims"],
        }

    def revoke_token(self, token_hash: str) -> bool:
        """Revoke a token.

        Args:
            token_hash: SHA-256 hash of the token to revoke.

        Returns:
            True if the token was revoked, False if not found.
        """
        if token_hash in self._tokens:
            self._tokens[token_hash]["revoked"] = True
            return True
        return False

    def get_openid_configuration(self) -> dict[str, Any]:
        """Return the OIDC discovery document.

        Returns:
            OIDC configuration metadata.
        """
        return {
            "issuer": self.issuer,
            "authorization_endpoint": f"{self.issuer}/authorize",
            "token_endpoint": f"{self.issuer}/token",
            "jwks_uri": f"{self.issuer}/.well-known/jwks.json",
            "response_types_supported": ["code", "token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["HS256"],
        }
