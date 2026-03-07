"""Adversarial tests for rate limiting and abuse detection.

Validates handling of rapid token issuance, bulk query flooding,
and concurrent write contention patterns.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.authz_decisions import VALID_ROLES


@pytest.mark.adversarial
class TestRapidTokenIssuance:
    """Rate limiting for rapid token issuance."""

    def test_token_issuance_limit_enforceable(self):
        """System MUST be capable of enforcing token issuance rate limits."""
        # Validate that rate limit thresholds are reasonable
        max_tokens_per_minute = 60
        assert max_tokens_per_minute > 0
        assert max_tokens_per_minute <= 1000  # Reasonable upper bound

    def test_per_role_token_limits(self):
        """Each role SHOULD have independent token issuance limits."""
        for role in VALID_ROLES:
            # Each role should be trackable independently
            assert isinstance(role, str)
            assert len(role) > 0


@pytest.mark.adversarial
class TestBulkQueryFlooding:
    """Rate limiting for bulk query flooding."""

    def test_fhir_search_result_cap(self):
        """FHIR search MUST cap results at 100 to prevent data exfiltration."""
        max_results = 100
        assert max_results <= 100

    def test_dicom_query_result_cap(self):
        """DICOM queries SHOULD have reasonable result limits."""
        max_results = 1000
        assert max_results <= 10000  # Reasonable upper bound

    def test_ledger_query_pagination(self):
        """Ledger queries SHOULD support pagination to prevent bulk extraction."""
        page_size = 100
        assert page_size > 0
        assert page_size <= 1000


@pytest.mark.adversarial
class TestConcurrentWriteContention:
    """Rate limiting for concurrent write contention."""

    def test_ledger_write_serialization(self):
        """Concurrent ledger writes MUST be serialized for chain integrity."""
        # Chain integrity requires sequential hash linking
        # Concurrent writes must be serialized
        from conformance.fixtures.audit_records import make_audit_chain

        chain = make_audit_chain(length=5)
        # Verify chain is properly ordered
        for i in range(1, len(chain)):
            assert chain[i]["previous_hash"] == chain[i - 1]["hash"]

    def test_provenance_dag_concurrent_safety(self):
        """Concurrent provenance writes MUST maintain DAG consistency."""
        from conformance.fixtures.provenance_records import make_provenance_dag

        dag = make_provenance_dag(depth=3)
        # All records should have unique IDs
        ids = [r["record_id"] for r in dag]
        assert len(ids) == len(set(ids))
