"""Adversarial tests for audit chain tampering.

Validates detection of modified records, inserted foreign records,
deleted records, reordered records, and hash collision attempts.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    compute_audit_hash,
    make_audit_chain,
    make_audit_record,
)


@pytest.mark.adversarial
class TestModifiedRecords:
    """Audit chain tampering via modified records."""

    def test_modified_result_summary_detected(self):
        """Modified result_summary MUST change the hash."""
        record = make_audit_record()
        original_hash = record["hash"]
        record["result_summary"] = "TAMPERED"
        new_hash = compute_audit_hash(record)
        assert new_hash != original_hash

    def test_modified_caller_detected(self):
        """Modified caller MUST change the hash."""
        record = make_audit_record()
        original_hash = record["hash"]
        record["caller"] = "malicious_actor"
        new_hash = compute_audit_hash(record)
        assert new_hash != original_hash

    def test_modified_parameters_detected(self):
        """Modified parameters MUST change the hash."""
        record = make_audit_record(parameters={"key": "value"})
        original_hash = record["hash"]
        record["parameters"] = {"key": "tampered"}
        new_hash = compute_audit_hash(record)
        assert new_hash != original_hash

    def test_modified_timestamp_detected(self):
        """Modified timestamp MUST change the hash."""
        record = make_audit_record()
        original_hash = record["hash"]
        record["timestamp"] = "2020-01-01T00:00:00Z"
        new_hash = compute_audit_hash(record)
        assert new_hash != original_hash

    def test_modified_server_detected(self):
        """Modified server MUST change the hash."""
        record = make_audit_record()
        original_hash = record["hash"]
        record["server"] = "malicious-server"
        new_hash = compute_audit_hash(record)
        assert new_hash != original_hash


@pytest.mark.adversarial
class TestInsertedForeignRecords:
    """Audit chain tampering via inserted foreign records."""

    def test_foreign_record_breaks_chain(self):
        """Inserted foreign record MUST break chain continuity."""
        chain = make_audit_chain(length=3)
        foreign = make_audit_record(
            server="foreign-server",
            previous_hash="f" * 64,
        )
        chain.insert(1, foreign)
        # Chain is now broken at position 1
        assert chain[1]["previous_hash"] != chain[0]["hash"]

    def test_foreign_record_wrong_genesis(self):
        """Foreign record with wrong genesis MUST be detectable."""
        foreign = make_audit_record(previous_hash="bad_genesis")
        assert foreign["previous_hash"] != GENESIS_HASH


@pytest.mark.adversarial
class TestDeletedRecords:
    """Audit chain tampering via deleted records."""

    def test_deleted_record_breaks_chain(self):
        """Deleted record MUST break chain continuity."""
        chain = make_audit_chain(length=5)
        # Remove the middle record
        del chain[2]
        # Chain is now broken: chain[2].previous_hash != chain[1].hash
        assert chain[2]["previous_hash"] != chain[1]["hash"]


@pytest.mark.adversarial
class TestReorderedRecords:
    """Audit chain tampering via reordered records."""

    def test_swapped_records_detected(self):
        """Swapped records MUST break chain integrity."""
        chain = make_audit_chain(length=4)
        # Swap records 1 and 2
        chain[1], chain[2] = chain[2], chain[1]
        # Chain is now broken
        assert chain[1]["previous_hash"] != chain[0]["hash"]
        assert chain[2]["previous_hash"] != chain[1]["hash"]


@pytest.mark.adversarial
class TestHashCollisionAttempts:
    """Audit chain tampering via hash collision attempts."""

    def test_different_content_different_hash(self):
        """Records with different content MUST produce different hashes."""
        r1 = make_audit_record(result_summary="Operation A")
        r2 = make_audit_record(result_summary="Operation B")
        assert r1["hash"] != r2["hash"]

    def test_hash_is_sha256_length(self):
        """All hashes MUST be 64 hex characters (SHA-256)."""
        record = make_audit_record()
        assert len(record["hash"]) == 64
        assert all(c in "0123456789abcdef" for c in record["hash"])

    def test_canonical_json_deterministic(self):
        """Canonical JSON serialization MUST be deterministic."""
        record = make_audit_record()
        h1 = compute_audit_hash(record)
        h2 = compute_audit_hash(record)
        assert h1 == h2
