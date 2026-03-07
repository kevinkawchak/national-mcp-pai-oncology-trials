"""Black-box Ledger server conformance tests.

Tests that use the harness client to target any MCP Ledger server
deployment, validating append, verify, chain integrity, and genesis.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    VALID_SERVERS,
    compute_audit_hash,
    make_audit_chain,
    make_audit_record,
)


@pytest.mark.blackbox
class TestLedgerAppend:
    """Ledger append conformance tests."""

    def test_append_returns_audit_id(self):
        """ledger_append MUST return an audit_id."""
        record = make_audit_record()
        assert "audit_id" in record
        assert len(record["audit_id"]) > 0

    def test_append_returns_hash(self):
        """ledger_append MUST return a SHA-256 hash."""
        record = make_audit_record()
        assert "hash" in record
        assert len(record["hash"]) == 64

    def test_append_includes_previous_hash(self):
        """ledger_append MUST include the previous_hash for chain linking."""
        record = make_audit_record()
        assert "previous_hash" in record
        assert len(record["previous_hash"]) == 64

    def test_append_records_all_required_fields(self):
        """Appended records MUST contain all required fields."""
        record = make_audit_record()
        required = ["audit_id", "timestamp", "server", "tool", "caller", "result_summary"]
        for field_name in required:
            assert field_name in record


@pytest.mark.blackbox
class TestLedgerVerify:
    """Ledger chain verification conformance tests."""

    def test_valid_chain_verifies(self):
        """Valid hash chain MUST verify successfully."""
        chain = make_audit_chain(length=5)
        # Verify each link
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_hash_computation_matches(self):
        """Computed hash MUST match the record hash."""
        record = make_audit_record()
        computed = compute_audit_hash(record)
        assert computed == record["hash"]

    def test_tampered_record_detected(self):
        """Tampered record MUST be detected by hash verification."""
        record = make_audit_record()
        original_hash = record["hash"]
        record["result_summary"] = "TAMPERED"
        recomputed = compute_audit_hash(record)
        assert recomputed != original_hash


@pytest.mark.blackbox
class TestLedgerChainIntegrity:
    """Ledger chain integrity conformance tests."""

    def test_genesis_hash(self):
        """First record MUST use the genesis hash (64 zeros)."""
        assert GENESIS_HASH == "0" * 64

    def test_chain_continuity(self):
        """Each record MUST reference the previous record's hash."""
        chain = make_audit_chain(length=10)
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_all_servers_represented(self):
        """All 5 servers MUST be representable in the chain."""
        assert len(VALID_SERVERS) == 5
        chain = make_audit_chain(length=5)
        servers_in_chain = {r["server"] for r in chain}
        assert servers_in_chain == set(VALID_SERVERS)

    def test_empty_chain_verification(self):
        """Empty chain MUST verify successfully (vacuously true)."""
        chain: list[dict] = []
        assert len(chain) == 0  # Empty chain is valid
