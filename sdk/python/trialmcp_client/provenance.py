"""Provenance sub-client for data lineage operations.

Wraps the four Provenance server tools: ``provenance_record``,
``provenance_query_forward``, ``provenance_query_backward``, and
``provenance_verify``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .config import ServerName
from .exceptions import raise_for_error
from .models import ProvenanceRecord, ProvenanceVerification

if TYPE_CHECKING:
    from .client import TrialMCPClient

logger = logging.getLogger("trialmcp.provenance")

_SERVER = ServerName.PROVENANCE


class ProvenanceClient:
    """Sub-client for the ``trialmcp-provenance`` MCP server.

    Provides typed, async wrappers around the four provenance tools.
    The provenance server maintains a directed acyclic graph (DAG) of
    data lineage events for clinical-trial data integrity.

    Parameters
    ----------
    parent:
        The :class:`TrialMCPClient` that owns this sub-client.
    """

    def __init__(self, parent: TrialMCPClient) -> None:
        self._client = parent

    # ------------------------------------------------------------------
    # provenance_record
    # ------------------------------------------------------------------

    async def record(
        self,
        *,
        source_id: str,
        source_type: str,
        action: str,
        actor_id: str,
        actor_role: str,
        tool_call: str,
        input_hash: str | None = None,
        output_hash: str | None = None,
        origin_server: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProvenanceRecord:
        """Record a new data access or transformation event.

        Parameters
        ----------
        source_id:
            Reference to the DataSource being accessed (UUID).
        source_type:
            Category of the data source (e.g. ``"fhir_resource"``).
        action:
            Operation performed (``"read"``, ``"transform"``, etc.).
        actor_id:
            Identifier of the actor performing the action.
        actor_role:
            Role of the actor from the 6-role model.
        tool_call:
            MCP tool invocation that triggered this event.
        input_hash:
            SHA-256 fingerprint of the input data.
        output_hash:
            SHA-256 fingerprint of the output data.
        origin_server:
            MCP server that owns the data source.
        description:
            Human-readable description of the event.
        metadata:
            Additional properties specific to the source type.

        Returns
        -------
        ProvenanceRecord:
            The newly created provenance record.
        """
        params: dict[str, Any] = {
            "source_id": source_id,
            "source_type": source_type,
            "action": action,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "tool_call": tool_call,
        }
        if input_hash:
            params["input_hash"] = input_hash
        if output_hash:
            params["output_hash"] = output_hash
        if origin_server:
            params["origin_server"] = origin_server
        if description:
            params["description"] = description
        if metadata:
            params["metadata"] = metadata

        result = await self._client.call_tool(_SERVER, "provenance_record", params)
        raise_for_error(result)
        return ProvenanceRecord.from_dict(result)

    # ------------------------------------------------------------------
    # provenance_query_forward
    # ------------------------------------------------------------------

    async def query_forward(
        self,
        *,
        source_id: str,
        max_depth: int = 10,
        action_filter: str | None = None,
    ) -> list[ProvenanceRecord]:
        """Trace data lineage forward from a source (what was derived from it).

        Parameters
        ----------
        source_id:
            Starting data source ID.
        max_depth:
            Maximum DAG traversal depth.
        action_filter:
            Optional filter by action type.

        Returns
        -------
        list[ProvenanceRecord]:
            Ordered list of downstream provenance records.
        """
        params: dict[str, Any] = {
            "source_id": source_id,
            "max_depth": max_depth,
        }
        if action_filter:
            params["action_filter"] = action_filter

        result = await self._client.call_tool(_SERVER, "provenance_query_forward", params)
        raise_for_error(result)

        records_raw = result.get("records", [])
        return [ProvenanceRecord.from_dict(r) for r in records_raw]

    # ------------------------------------------------------------------
    # provenance_query_backward
    # ------------------------------------------------------------------

    async def query_backward(
        self,
        *,
        record_id: str,
        max_depth: int = 10,
        action_filter: str | None = None,
    ) -> list[ProvenanceRecord]:
        """Trace data lineage backward to its origins.

        Parameters
        ----------
        record_id:
            Starting provenance record ID.
        max_depth:
            Maximum DAG traversal depth.
        action_filter:
            Optional filter by action type.

        Returns
        -------
        list[ProvenanceRecord]:
            Ordered list of upstream provenance records.
        """
        params: dict[str, Any] = {
            "record_id": record_id,
            "max_depth": max_depth,
        }
        if action_filter:
            params["action_filter"] = action_filter

        result = await self._client.call_tool(_SERVER, "provenance_query_backward", params)
        raise_for_error(result)

        records_raw = result.get("records", [])
        return [ProvenanceRecord.from_dict(r) for r in records_raw]

    # ------------------------------------------------------------------
    # provenance_verify
    # ------------------------------------------------------------------

    async def verify(
        self,
        *,
        source_id: str | None = None,
        record_id: str | None = None,
        verify_hashes: bool = True,
    ) -> ProvenanceVerification:
        """Verify the integrity of provenance records.

        Checks SHA-256 fingerprints and DAG link consistency.

        Parameters
        ----------
        source_id:
            Verify all records for a specific data source.
        record_id:
            Verify a specific provenance record and its chain.
        verify_hashes:
            Whether to verify SHA-256 fingerprints.

        Returns
        -------
        ProvenanceVerification:
            Verification result with pass/fail details.
        """
        params: dict[str, Any] = {
            "verify_hashes": verify_hashes,
        }
        if source_id:
            params["source_id"] = source_id
        if record_id:
            params["record_id"] = record_id

        result = await self._client.call_tool(_SERVER, "provenance_verify", params)
        raise_for_error(result)

        return ProvenanceVerification(
            valid=result.get("valid", False),
            records_checked=result.get("records_checked", 0),
            broken_links=result.get("broken_links", []),
            error_message=result.get("error_message"),
        )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def record_read_access(
        self,
        *,
        source_id: str,
        source_type: str,
        actor_id: str,
        actor_role: str,
        tool_call: str,
        origin_server: str,
        output_hash: str | None = None,
        description: str | None = None,
    ) -> ProvenanceRecord:
        """Record a read-access event (common shorthand).

        Parameters
        ----------
        source_id:
            The data source being read.
        source_type:
            Category of the data source.
        actor_id:
            Actor performing the read.
        actor_role:
            Role of the actor.
        tool_call:
            MCP tool that performed the read.
        origin_server:
            Server that owns the data.
        output_hash:
            SHA-256 fingerprint of the read data.
        description:
            Human-readable description.

        Returns
        -------
        ProvenanceRecord:
            The recorded provenance event.
        """
        return await self.record(
            source_id=source_id,
            source_type=source_type,
            action="read",
            actor_id=actor_id,
            actor_role=actor_role,
            tool_call=tool_call,
            origin_server=origin_server,
            output_hash=output_hash,
            description=description,
        )

    async def full_lineage(
        self,
        *,
        source_id: str,
    ) -> dict[str, list[ProvenanceRecord]]:
        """Retrieve both forward and backward lineage for a data source.

        Parameters
        ----------
        source_id:
            The data source ID to trace.

        Returns
        -------
        dict:
            ``{"forward": [...], "backward": [...]}`` provenance chains.
        """
        import asyncio

        forward_task = self.query_forward(source_id=source_id)
        backward_task = self.query_backward(record_id=source_id)

        forward_records, backward_records = await asyncio.gather(forward_task, backward_task)

        return {
            "forward": forward_records,
            "backward": backward_records,
        }

    async def verify_source(self, source_id: str) -> ProvenanceVerification:
        """Verify all provenance records for a specific data source.

        Parameters
        ----------
        source_id:
            The data source ID.

        Returns
        -------
        ProvenanceVerification:
            Verification result.
        """
        return await self.verify(source_id=source_id)
