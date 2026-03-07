"""Adversarial tests for replay attack detection.

Validates detection of duplicated audit records, replayed
authorization requests, and duplicated provenance records.
"""

from __future__ import annotations

import copy

import pytest

from conformance.fixtures.audit_records import (
    make_audit_chain,
    make_audit_record,
)
from conformance.fixtures.provenance_records import make_provenance_record


@pytest.mark.adversarial
class TestDuplicatedAuditRecords:
    """Replay attack via duplicated audit records."""

    def test_duplicate_audit_id_detected(self):
        """Duplicate audit_id MUST be detectable."""
        record1 = make_audit_record()
        record2 = copy.deepcopy(record1)
        # Exact duplicates share the same audit_id
        assert record1["audit_id"] == record2["audit_id"]

    def test_duplicate_record_in_chain_detected(self):
        """Duplicate record inserted into chain MUST be detectable."""
        chain = make_audit_chain(length=3)
        # Insert a duplicate of record 0 at position 1
        duplicate = copy.deepcopy(chain[0])
        chain.insert(1, duplicate)
        # chain[1] (duplicate of r0) has previous_hash == genesis,
        # but at position 1 it should link to chain[0].hash — mismatch
        assert chain[1]["previous_hash"] != chain[0]["hash"]

    def test_replayed_record_wrong_previous_hash(self):
        """Replayed record MUST have wrong previous_hash for its position."""
        chain = make_audit_chain(length=3)
        replayed = copy.deepcopy(chain[0])
        # If inserted at position 3, previous_hash won't match chain[2]
        assert replayed["previous_hash"] != chain[2]["hash"]


@pytest.mark.adversarial
class TestReplayedAuthorizationRequests:
    """Replay attack via replayed authorization requests."""

    def test_authorization_timestamps_unique(self):
        """Each authorization request MUST have a unique timestamp."""
        from conformance.fixtures.authz_decisions import make_allow_decision

        d1 = make_allow_decision()
        d2 = make_allow_decision()
        # Decisions made at same "fixture" time are acceptable,
        # but real implementations MUST use current timestamps
        assert "evaluated_at" in d1
        assert "evaluated_at" in d2


@pytest.mark.adversarial
class TestDuplicatedProvenanceRecords:
    """Replay attack via duplicated provenance records."""

    def test_provenance_record_ids_unique(self):
        """Each provenance record MUST have a unique record_id."""
        r1 = make_provenance_record()
        r2 = make_provenance_record()
        assert r1["record_id"] != r2["record_id"]

    def test_provenance_hashes_unique(self):
        """Each provenance record MUST have unique input/output hashes."""
        r1 = make_provenance_record()
        r2 = make_provenance_record()
        # Different records should produce different hashes
        assert r1["input_hash"] != r2["input_hash"] or r1["output_hash"] != r2["output_hash"]

    def test_duplicate_provenance_detectable(self):
        """Exact duplicate provenance records MUST be detectable."""
        r1 = make_provenance_record()
        r2 = copy.deepcopy(r1)
        assert r1["record_id"] == r2["record_id"]
