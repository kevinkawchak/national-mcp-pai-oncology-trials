"""SHA-256 token lifecycle management with configurable expiry.

Implements token issuance, validation, and revocation as specified
in spec/security.md.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from servers.storage.base import BaseStorage

DEFAULT_EXPIRY = 3600  # 1 hour
MAX_EXPIRY = 86400  # 24 hours


class TokenStore:
    """Manages SHA-256 hashed bearer tokens with lifecycle support.

    Tokens are stored by their SHA-256 hash (never in plaintext).
    Supports configurable expiry with a hard maximum of 24 hours.
    """

    def __init__(self, storage: BaseStorage | None = None) -> None:
        self._storage = storage
        self._tokens: dict[str, dict[str, Any]] = {}

    def issue(self, role: str, expires_in: int = DEFAULT_EXPIRY) -> dict[str, Any]:
        """Issue a new bearer token for the given role.

        Returns token metadata including the SHA-256 hash.
        The raw token value is returned only at issuance time.
        """
        if expires_in > MAX_EXPIRY:
            expires_in = MAX_EXPIRY

        raw = uuid.uuid4().hex
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(now.timestamp() + expires_in, tz=timezone.utc)

        meta: dict[str, Any] = {
            "role": role,
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "revoked": False,
        }

        self._tokens[token_hash] = meta
        if self._storage:
            self._storage.put("tokens", token_hash, meta)

        return {
            "token_hash": token_hash,
            "role": role,
            "issued_at": meta["issued_at"],
            "expires_at": meta["expires_at"],
        }

    def validate(self, token_hash: str) -> dict[str, Any]:
        """Validate a previously issued token."""
        meta = self._get_token(token_hash)
        if meta is None:
            return {"valid": False, "reason": "TOKEN_NOT_FOUND"}
        if meta.get("revoked"):
            return {"valid": False, "reason": "TOKEN_REVOKED"}

        expires = datetime.fromisoformat(meta["expires_at"])
        if datetime.now(timezone.utc) > expires:
            return {"valid": False, "reason": "TOKEN_EXPIRED"}

        return {"valid": True, "role": meta["role"]}

    def revoke(self, token_hash: str) -> dict[str, Any]:
        """Immediately revoke a token."""
        meta = self._get_token(token_hash)
        if meta is None:
            return {"revoked": False, "reason": "TOKEN_NOT_FOUND"}

        meta["revoked"] = True
        self._tokens[token_hash] = meta
        if self._storage:
            self._storage.put("tokens", token_hash, meta)

        return {"revoked": True, "token_hash": token_hash}

    def _get_token(self, token_hash: str) -> dict[str, Any] | None:
        """Look up token metadata from memory or storage."""
        if token_hash in self._tokens:
            return self._tokens[token_hash]
        if self._storage:
            meta = self._storage.get("tokens", token_hash)
            if meta:
                self._tokens[token_hash] = meta
                return meta
        return None
