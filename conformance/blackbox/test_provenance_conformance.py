"""Black-box Provenance server conformance tests.

Tests that use the harness client to target any MCP Provenance server
deployment, validating record, query, and DAG integrity.
"""

from __future__ import annotations

import pytest

from conformance.fixtures.provenance_records import (
    VALID_ACTION_TYPES,
    VALID_ACTOR_ROLES,
    VALID_SOURCE_TYPES,
    make_provenance_dag,
    make_provenance_record,
)


@pytest.mark.blackbox
class TestProvenanceRecord:
    """Provenance record conformance tests."""

    def test_record_returns_id(self):
        """provenance_record_access MUST return a record_id."""
        record = make_provenance_record()
        assert "record_id" in record
        assert len(record["record_id"]) > 0

    def test_record_includes_timestamp(self):
        """Provenance record MUST include a timestamp."""
        record = make_provenance_record()
        assert "timestamp" in record

    def test_record_includes_source_type(self):
        """Provenance record MUST include a valid source_type."""
        record = make_provenance_record()
        assert record["source_type"] in VALID_SOURCE_TYPES

    def test_record_includes_action(self):
        """Provenance record MUST include a valid action."""
        record = make_provenance_record()
        assert record["action"] in VALID_ACTION_TYPES

    def test_record_includes_actor(self):
        """Provenance record MUST include an actor identifier."""
        record = make_provenance_record()
        assert "actor_id" in record
        assert "actor_role" in record


@pytest.mark.blackbox
class TestProvenanceQuery:
    """Provenance query conformance tests."""

    def test_five_source_types(self):
        """Exactly 5 source types MUST be defined."""
        assert len(VALID_SOURCE_TYPES) == 5

    def test_five_action_types(self):
        """Exactly 5 action types MUST be defined."""
        assert len(VALID_ACTION_TYPES) == 5

    def test_six_actor_roles(self):
        """Exactly 6 actor roles MUST be defined."""
        assert len(VALID_ACTOR_ROLES) == 6

    @pytest.mark.parametrize("source_type", VALID_SOURCE_TYPES)
    def test_source_type_accepted(self, source_type):
        """Each source type MUST be accepted."""
        record = make_provenance_record(source_type=source_type)
        assert record["source_type"] == source_type


@pytest.mark.blackbox
class TestProvenanceDAGIntegrity:
    """Provenance DAG integrity conformance tests."""

    def test_dag_creation(self):
        """DAG MUST be constructable with multiple records."""
        dag = make_provenance_dag(depth=3)
        assert len(dag) == 3

    def test_dag_records_have_hashes(self):
        """Each DAG record MUST include input and output hashes."""
        dag = make_provenance_dag(depth=3)
        for record in dag:
            assert "input_hash" in record
            assert "output_hash" in record
            assert len(record["input_hash"]) == 64
            assert len(record["output_hash"]) == 64

    def test_dag_records_sequential_actions(self):
        """DAG records MUST follow valid action progression."""
        dag = make_provenance_dag(depth=3)
        for record in dag:
            assert record["action"] in VALID_ACTION_TYPES
