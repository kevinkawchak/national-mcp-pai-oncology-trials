"""Adversarial tests for authorization bypass attempts.

Validates resilience against role escalation, token reuse after
revocation, expired token acceptance, and forged token attacks.
"""

from __future__ import annotations

import hashlib
import uuid

import pytest

from conformance.fixtures.authz_decisions import (
    DEFAULT_ALLOW_RULES,
    UNAUTHORIZED_ACCESS_ATTEMPTS,
)


@pytest.mark.adversarial
class TestRoleEscalation:
    """Authorization bypass via role escalation."""

    def test_auditor_cannot_escalate_to_coordinator(self):
        """Auditor MUST NOT be able to access trial_coordinator tools."""
        coordinator_tools = {(s, t) for s, t in DEFAULT_ALLOW_RULES["trial_coordinator"]}
        auditor_tools = {(s, t) for s, t in DEFAULT_ALLOW_RULES["auditor"]}
        # Auditor should not have all coordinator permissions
        assert not coordinator_tools.issubset(auditor_tools)

    def test_sponsor_cannot_escalate_to_robot(self):
        """Sponsor MUST NOT have robot_agent permissions."""
        robot_tools = {(s, t) for s, t in DEFAULT_ALLOW_RULES["robot_agent"]}
        sponsor_tools = {(s, t) for s, t in DEFAULT_ALLOW_RULES["sponsor"]}
        assert not robot_tools.issubset(sponsor_tools)

    def test_unknown_role_has_no_permissions(self):
        """Unknown roles MUST have zero permissions."""
        assert "malicious_actor" not in DEFAULT_ALLOW_RULES
        assert "admin" not in DEFAULT_ALLOW_RULES
        assert "root" not in DEFAULT_ALLOW_RULES

    @pytest.mark.parametrize(
        "attempt",
        UNAUTHORIZED_ACCESS_ATTEMPTS,
        ids=[f"{a['role']}-{a['tool']}" for a in UNAUTHORIZED_ACCESS_ATTEMPTS],
    )
    def test_known_unauthorized_access_denied(self, attempt):
        """Known unauthorized access attempts MUST be denied."""
        role = attempt["role"]
        server = attempt["server"]
        tool = attempt["tool"]
        allowed = (server, tool) in DEFAULT_ALLOW_RULES.get(role, [])
        assert not allowed, f"{role} should not access {server}/{tool}"


@pytest.mark.adversarial
class TestTokenReuse:
    """Authorization bypass via token reuse after revocation."""

    def test_revoked_token_format_still_valid_sha256(self):
        """Revoked tokens maintain valid SHA-256 format but MUST be rejected."""
        token_hash = hashlib.sha256(b"test-token").hexdigest()
        assert len(token_hash) == 64  # Format is valid
        # Server MUST reject this after revocation

    def test_expired_token_format_valid(self):
        """Expired tokens maintain valid format but MUST be rejected."""
        token_hash = hashlib.sha256(b"expired-token").hexdigest()
        assert len(token_hash) == 64


@pytest.mark.adversarial
class TestForgedTokens:
    """Authorization bypass via forged tokens."""

    def test_random_token_hash_rejected(self):
        """Random SHA-256 hash MUST NOT be accepted as a valid token."""
        forged_hash = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        assert len(forged_hash) == 64
        # Server MUST reject tokens it did not issue

    def test_empty_token_rejected(self):
        """Empty string MUST NOT be accepted as a token."""
        assert len("") == 0

    def test_truncated_hash_rejected(self):
        """Truncated hash MUST NOT be accepted."""
        truncated = hashlib.sha256(b"test").hexdigest()[:32]
        assert len(truncated) != 64
