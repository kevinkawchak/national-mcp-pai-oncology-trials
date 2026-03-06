"""Security conformance tests for audit hash chain integrity.

Validates that conforming implementations detect hash chain tampering,
enforce genesis hash requirements, and correctly verify chain continuity
per the National MCP-PAI Oncology Trials Standard.

Specification references:
  - spec/audit.md — Hash chain verification, genesis hash, tampering detection
  - spec/tool-contracts.md — ledger_verify, ledger_chain_status
  - schemas/audit-record.schema.json
"""

from __future__ import annotations

import hashlib
import json

from conformance.fixtures.audit_records import (
    GENESIS_HASH,
    compute_audit_hash,
    make_audit_chain,
    make_audit_record,
)


def verify_chain(chain: list[dict]) -> tuple[bool, str]:
    """Verify a hash chain per spec/audit.md.

    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    """
    if not chain:
        return False, "Chain is empty"

    # Genesis check
    if chain[0]["previous_hash"] != GENESIS_HASH:
        return False, "Genesis record does not use the genesis hash"

    for i, record in enumerate(chain):
        # Recompute hash
        expected_hash = compute_audit_hash(record)
        if record["hash"] != expected_hash:
            return False, f"Record {i}: hash mismatch (tampered)"

        # Chain continuity (skip first record, already checked genesis)
        if i > 0 and record["previous_hash"] != chain[i - 1]["hash"]:
            return False, f"Record {i}: chain link broken"

    return True, ""


class TestGenesisHash:
    """Validates genesis hash requirements per spec/audit.md."""

    def test_genesis_hash_is_64_zeros(self) -> None:
        """Genesis hash MUST be '0' repeated 64 times."""
        assert GENESIS_HASH == "0" * 64
        assert len(GENESIS_HASH) == 64

    def test_genesis_record_previous_hash(self) -> None:
        """First record in chain MUST have previous_hash = genesis hash."""
        chain = make_audit_chain(length=1)
        assert chain[0]["previous_hash"] == GENESIS_HASH

    def test_non_genesis_first_record_detected(self) -> None:
        """A chain whose first record does not use genesis hash MUST fail."""
        chain = make_audit_chain(length=3)
        chain[0]["previous_hash"] = "a" * 64
        is_valid, error = verify_chain(chain)
        assert not is_valid
        assert "genesis" in error.lower()


class TestChainVerification:
    """Validates hash chain verification per spec/audit.md."""

    def test_valid_chain_passes_verification(self) -> None:
        """A correctly constructed chain MUST pass verification."""
        chain = make_audit_chain(length=5)
        is_valid, error = verify_chain(chain)
        assert is_valid, f"Valid chain should pass: {error}"

    def test_single_record_chain_is_valid(self) -> None:
        """A chain with a single genesis record MUST be valid."""
        chain = make_audit_chain(length=1)
        is_valid, error = verify_chain(chain)
        assert is_valid, f"Single record chain should pass: {error}"

    def test_empty_chain_is_invalid(self) -> None:
        """An empty chain MUST fail verification."""
        is_valid, error = verify_chain([])
        assert not is_valid


class TestHashTampering:
    """Validates detection of hash chain tampering per spec/audit.md."""

    def test_modified_result_summary_detected(self) -> None:
        """Modifying result_summary MUST cause hash mismatch."""
        chain = make_audit_chain(length=3)
        # Tamper with the middle record's result_summary
        chain[1]["result_summary"] = "TAMPERED RESULT"
        is_valid, error = verify_chain(chain)
        assert not is_valid
        assert "tampered" in error.lower() or "mismatch" in error.lower()

    def test_modified_caller_detected(self) -> None:
        """Modifying caller MUST cause hash mismatch."""
        chain = make_audit_chain(length=3)
        chain[1]["caller"] = "evil_actor"
        is_valid, error = verify_chain(chain)
        assert not is_valid

    def test_modified_parameters_detected(self) -> None:
        """Modifying parameters MUST cause hash mismatch."""
        chain = make_audit_chain(length=3)
        chain[1]["parameters"] = {"injected": "malicious_data"}
        is_valid, error = verify_chain(chain)
        assert not is_valid

    def test_modified_timestamp_detected(self) -> None:
        """Modifying timestamp MUST cause hash mismatch."""
        chain = make_audit_chain(length=3)
        chain[1]["timestamp"] = "2000-01-01T00:00:00Z"
        is_valid, error = verify_chain(chain)
        assert not is_valid

    def test_swapped_records_detected(self) -> None:
        """Swapping two records in the chain MUST break verification."""
        chain = make_audit_chain(length=4)
        chain[1], chain[2] = chain[2], chain[1]
        is_valid, error = verify_chain(chain)
        assert not is_valid

    def test_deleted_record_detected(self) -> None:
        """Removing a record from the chain MUST break verification."""
        chain = make_audit_chain(length=4)
        del chain[2]  # Remove middle record
        is_valid, error = verify_chain(chain)
        assert not is_valid

    def test_inserted_record_detected(self) -> None:
        """Inserting a foreign record MUST break verification."""
        chain = make_audit_chain(length=3)
        foreign = make_audit_record(
            server="trialmcp-authz",
            tool="authz_evaluate",
            previous_hash="f" * 64,
        )
        chain.insert(1, foreign)
        is_valid, error = verify_chain(chain)
        assert not is_valid


class TestCanonicalSerialization:
    """Validates canonical JSON serialization per spec/audit.md."""

    def test_hash_uses_alphabetical_key_order(self) -> None:
        """Hash computation MUST use alphabetical key order."""
        record = make_audit_record()
        # Compute manually with sorted keys
        hashable = {k: v for k, v in sorted(record.items()) if k != "hash"}
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert record["hash"] == expected

    def test_hash_excludes_hash_field(self) -> None:
        """Hash computation MUST exclude the hash field itself."""
        record = make_audit_record()
        # Including hash field should produce different result
        with_hash = dict(sorted(record.items()))
        canonical_with = json.dumps(with_hash, sort_keys=True, separators=(",", ":"))
        hash_with = hashlib.sha256(canonical_with.encode("utf-8")).hexdigest()
        assert hash_with != record["hash"]

    def test_hash_uses_utf8_encoding(self) -> None:
        """Hash computation MUST use UTF-8 encoding."""
        record = make_audit_record()
        hashable = {k: v for k, v in sorted(record.items()) if k != "hash"}
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        # Explicitly use UTF-8
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert digest == record["hash"]
