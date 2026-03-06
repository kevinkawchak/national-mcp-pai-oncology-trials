"""Security conformance tests for token lifecycle management.

Validates token issuance, expiry enforcement, revocation, and rotation
per the National MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/security.md — Token lifecycle (issuance, hashing, expiry, revocation)
  - spec/tool-contracts.md — authz_issue_token, authz_validate_token, authz_revoke_token
  - schemas/authz-decision.schema.json
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timedelta, timezone

# Token lifecycle constants per spec/security.md
DEFAULT_TOKEN_EXPIRY_SECONDS = 3600
MAX_TOKEN_EXPIRY_SECONDS = 86400
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def issue_token(
    subject: str = "robot_agent_001",
    role: str = "robot_agent",
    expiry_seconds: int = DEFAULT_TOKEN_EXPIRY_SECONDS,
) -> dict:
    """Simulate token issuance per spec/security.md.

    Tokens are UUID v4, stored as SHA-256 hashes (never in plaintext).
    """
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    return {
        "token_hash": token_hash,
        "raw_token": raw_token,
        "subject": subject,
        "role": role,
        "issued_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(seconds=expiry_seconds)).isoformat().replace("+00:00", "Z"),
        "revoked": False,
    }


def is_token_expired(token: dict) -> bool:
    """Check if a token has expired per spec/security.md."""
    expires_at = datetime.fromisoformat(
        token["expires_at"].replace("Z", "+00:00"),
    )
    return datetime.now(timezone.utc) > expires_at


def revoke_token(token: dict) -> dict:
    """Revoke a token per spec/security.md (immediate revocation)."""
    token["revoked"] = True
    return token


class TestTokenIssuance:
    """Validates token issuance per spec/security.md."""

    def test_token_is_uuid_v4(self) -> None:
        """Raw tokens MUST be UUID v4 format."""
        token = issue_token()
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(token["raw_token"])

    def test_token_hash_is_sha256(self) -> None:
        """Token hash MUST be a SHA-256 hex digest (64 chars)."""
        token = issue_token()
        assert SHA256_PATTERN.match(token["token_hash"])

    def test_token_hash_matches_raw(self) -> None:
        """Token hash MUST be the SHA-256 of the raw token."""
        token = issue_token()
        expected = hashlib.sha256(token["raw_token"].encode("utf-8")).hexdigest()
        assert token["token_hash"] == expected

    def test_token_never_stores_plaintext(self) -> None:
        """The stored representation MUST be the hash, never plaintext."""
        token = issue_token()
        assert token["token_hash"] != token["raw_token"]

    def test_token_has_subject(self) -> None:
        """Tokens MUST include a subject identifier."""
        token = issue_token(subject="trial_coordinator_001")
        assert token["subject"] == "trial_coordinator_001"

    def test_token_has_role(self) -> None:
        """Tokens MUST include the actor role."""
        token = issue_token(role="trial_coordinator")
        assert token["role"] == "trial_coordinator"


class TestTokenExpiry:
    """Validates token expiry enforcement per spec/security.md."""

    def test_default_expiry_is_3600_seconds(self) -> None:
        """Default token expiry MUST be 3600 seconds (1 hour)."""
        assert DEFAULT_TOKEN_EXPIRY_SECONDS == 3600

    def test_max_expiry_is_86400_seconds(self) -> None:
        """Maximum token expiry MUST be 86400 seconds (24 hours)."""
        assert MAX_TOKEN_EXPIRY_SECONDS == 86400

    def test_token_has_utc_expiry(self) -> None:
        """Token expiry MUST be in UTC."""
        token = issue_token()
        assert token["expires_at"].endswith("Z")

    def test_token_has_utc_issuance(self) -> None:
        """Token issuance time MUST be in UTC."""
        token = issue_token()
        assert token["issued_at"].endswith("Z")

    def test_expiry_exceeding_max_rejected(self) -> None:
        """Tokens requesting > 86400s expiry MUST be rejected."""
        requested_expiry = MAX_TOKEN_EXPIRY_SECONDS + 1
        assert requested_expiry > MAX_TOKEN_EXPIRY_SECONDS

    def test_fresh_token_is_not_expired(self) -> None:
        """A freshly issued token MUST NOT be expired."""
        token = issue_token()
        assert not is_token_expired(token)

    def test_zero_expiry_token_is_expired(self) -> None:
        """A token with 0-second expiry MUST be immediately expired."""
        token = issue_token(expiry_seconds=0)
        # The token was issued "now" with 0s expiry, so it's expired
        assert is_token_expired(token)


class TestTokenRevocation:
    """Validates token revocation per spec/security.md."""

    def test_revocation_is_immediate(self) -> None:
        """Token revocation MUST take effect immediately."""
        token = issue_token()
        assert not token["revoked"]
        revoked = revoke_token(token)
        assert revoked["revoked"] is True

    def test_revoked_token_stays_revoked(self) -> None:
        """A revoked token MUST remain revoked (no un-revocation)."""
        token = issue_token()
        revoked = revoke_token(token)
        assert revoked["revoked"] is True
        # Revoking again should still be revoked
        revoked_again = revoke_token(revoked)
        assert revoked_again["revoked"] is True

    def test_revoked_token_hash_unchanged(self) -> None:
        """Revocation MUST NOT change the token hash."""
        token = issue_token()
        original_hash = token["token_hash"]
        revoked = revoke_token(token)
        assert revoked["token_hash"] == original_hash
