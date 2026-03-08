"""Ledger sub-client for audit chain operations.

Wraps the four Ledger server tools: ``ledger_append``, ``ledger_verify``,
``ledger_query``, and ``ledger_export``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .config import ServerName
from .exceptions import raise_for_error
from .models import AuditRecord, ChainVerification

if TYPE_CHECKING:
    from .client import TrialMCPClient

logger = logging.getLogger("trialmcp.ledger")

_SERVER = ServerName.LEDGER


class LedgerClient:
    """Sub-client for the ``trialmcp-ledger`` MCP server.

    Provides typed, async wrappers around the four audit ledger tools.
    The ledger maintains a SHA-256 hash-chained, append-only log of all
    MCP tool invocations for 21 CFR Part 11 compliance.

    Parameters
    ----------
    parent:
        The :class:`TrialMCPClient` that owns this sub-client.
    """

    def __init__(self, parent: TrialMCPClient) -> None:
        self._client = parent

    # ------------------------------------------------------------------
    # ledger_append
    # ------------------------------------------------------------------

    async def append(
        self,
        *,
        server: str,
        tool: str,
        caller: str,
        parameters: dict[str, Any],
        result_summary: str,
    ) -> AuditRecord:
        """Append a new record to the audit ledger.

        The server automatically computes the SHA-256 hash and links
        the new record to the previous one.

        Parameters
        ----------
        server:
            MCP server that generated the event.
        tool:
            MCP tool that was invoked.
        caller:
            Pseudonymised actor identifier.
        parameters:
            De-identified tool call parameters.
        result_summary:
            Brief outcome description (must not contain PHI).

        Returns
        -------
        AuditRecord:
            The newly created audit record with its hash.
        """
        params: dict[str, Any] = {
            "server": server,
            "tool": tool,
            "caller": caller,
            "parameters": parameters,
            "result_summary": result_summary,
        }

        result = await self._client.call_tool(_SERVER, "ledger_append", params)
        raise_for_error(result)
        return AuditRecord.from_dict(result)

    # ------------------------------------------------------------------
    # ledger_verify
    # ------------------------------------------------------------------

    async def verify(
        self,
        *,
        start_id: str | None = None,
        end_id: str | None = None,
        full_chain: bool = False,
    ) -> ChainVerification:
        """Verify the integrity of the audit chain.

        Checks that each record's hash correctly links to the previous
        record, detecting any tampering or corruption.

        Parameters
        ----------
        start_id:
            Audit record ID to start verification from.
        end_id:
            Audit record ID to stop verification at.
        full_chain:
            If ``True``, verify the entire chain from genesis.

        Returns
        -------
        ChainVerification:
            Verification result with pass/fail and broken-link details.

        Raises
        ------
        ChainBrokenError:
            If a hash-chain integrity violation is detected.
        """
        params: dict[str, Any] = {}
        if start_id:
            params["start_id"] = start_id
        if end_id:
            params["end_id"] = end_id
        if full_chain:
            params["full_chain"] = True

        result = await self._client.call_tool(_SERVER, "ledger_verify", params)
        raise_for_error(result)

        return ChainVerification(
            valid=result.get("valid", False),
            records_checked=result.get("records_checked", 0),
            first_record_id=result.get("first_record_id"),
            last_record_id=result.get("last_record_id"),
            broken_at_id=result.get("broken_at_id"),
            error_message=result.get("error_message"),
        )

    # ------------------------------------------------------------------
    # ledger_query
    # ------------------------------------------------------------------

    async def query(
        self,
        *,
        server: str | None = None,
        tool: str | None = None,
        caller: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditRecord]:
        """Query audit records by various criteria.

        Parameters
        ----------
        server:
            Filter by originating MCP server.
        tool:
            Filter by tool name.
        caller:
            Filter by actor identifier.
        start_time:
            Earliest timestamp (ISO 8601).
        end_time:
            Latest timestamp (ISO 8601).
        limit:
            Maximum number of records to return.
        offset:
            Number of records to skip (for pagination).

        Returns
        -------
        list[AuditRecord]:
            Matching audit records.
        """
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if server:
            params["server"] = server
        if tool:
            params["tool"] = tool
        if caller:
            params["caller"] = caller
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        result = await self._client.call_tool(_SERVER, "ledger_query", params)
        raise_for_error(result)

        records_raw = result.get("records", [])
        return [AuditRecord.from_dict(r) for r in records_raw]

    # ------------------------------------------------------------------
    # ledger_export
    # ------------------------------------------------------------------

    async def export(
        self,
        *,
        format: str = "jsonl",
        start_time: str | None = None,
        end_time: str | None = None,
        server: str | None = None,
        include_hashes: bool = True,
    ) -> dict[str, Any]:
        """Export audit records for external compliance review.

        Parameters
        ----------
        format:
            Export format (``"jsonl"``, ``"csv"``, ``"xml"``).
        start_time:
            Earliest timestamp for export window.
        end_time:
            Latest timestamp for export window.
        server:
            Optional filter by originating server.
        include_hashes:
            Whether to include hash chain values in the export.

        Returns
        -------
        dict:
            Export result including the data payload or download reference.
        """
        params: dict[str, Any] = {
            "format": format,
            "include_hashes": include_hashes,
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if server:
            params["server"] = server

        result = await self._client.call_tool(_SERVER, "ledger_export", params)
        raise_for_error(result)
        return result

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def verify_full_chain(self) -> ChainVerification:
        """Verify the entire audit chain from genesis.

        Returns
        -------
        ChainVerification:
            Full chain verification result.
        """
        return await self.verify(full_chain=True)

    async def query_by_caller(
        self,
        caller: str,
        *,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Query all audit records for a specific actor.

        Parameters
        ----------
        caller:
            The pseudonymised actor identifier.
        limit:
            Maximum records to return.

        Returns
        -------
        list[AuditRecord]:
            Matching audit records.
        """
        return await self.query(caller=caller, limit=limit)

    async def query_by_server(
        self,
        server: str,
        *,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Query all audit records for a specific MCP server.

        Parameters
        ----------
        server:
            The MCP server name.
        limit:
            Maximum records to return.

        Returns
        -------
        list[AuditRecord]:
            Matching audit records.
        """
        return await self.query(server=server, limit=limit)

    async def get_latest_records(
        self,
        count: int = 10,
    ) -> list[AuditRecord]:
        """Retrieve the most recent audit records.

        Parameters
        ----------
        count:
            Number of recent records to retrieve.

        Returns
        -------
        list[AuditRecord]:
            The most recent audit records.
        """
        return await self.query(limit=count)
