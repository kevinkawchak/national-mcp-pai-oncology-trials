"""Client-side audit logging middleware.

Records every MCP tool invocation to a local append-only JSONL file for
offline compliance review.  The log intentionally omits PHI; only tool names,
parameters keys, timestamps, and result summaries are recorded.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("trialmcp.middleware.audit")

# Maximum number of records buffered before an automatic flush
_BUFFER_FLUSH_SIZE = 50


@dataclass
class AuditEntry:
    """A single client-side audit log entry.

    Fields are intentionally kept free of PHI.  The ``params_keys`` field
    records only the *names* of the parameters passed, not their values.
    """

    entry_id: str
    timestamp: str
    actor_id: str
    site_id: str
    server: str
    tool: str
    params_keys: list[str]
    result_summary: str
    request_id: str
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict suitable for JSON encoding."""
        return asdict(self)


class AuditMiddleware:
    """Middleware that logs every tool call to a local JSONL audit file.

    The log is append-only and never contains PHI.  It is designed to
    complement the server-side audit ledger with a client-side record
    for independent verification.

    Parameters
    ----------
    enabled:
        Whether audit logging is active.
    log_path:
        Filesystem path for the JSONL audit log.
    actor_id:
        Identifier of the calling actor.
    site_id:
        Clinical site identifier.
    """

    def __init__(
        self,
        *,
        enabled: bool = True,
        log_path: str = "/var/log/trialmcp/sdk_audit.jsonl",
        actor_id: str = "",
        site_id: str = "",
    ) -> None:
        self._enabled = enabled
        self._log_path = log_path
        self._actor_id = actor_id
        self._site_id = site_id
        self._buffer: list[AuditEntry] = []
        self._lock = asyncio.Lock()
        self._initialised = False

    async def log_call(
        self,
        *,
        server: str,
        tool: str,
        params: dict[str, Any],
        result_summary: str,
        request_id: str,
        duration_ms: float = 0.0,
    ) -> None:
        """Record a single tool invocation.

        Parameters
        ----------
        server:
            Name of the MCP server that handled the call.
        tool:
            Tool name that was invoked.
        params:
            Tool call parameters (only keys are recorded).
        result_summary:
            Brief, PHI-safe summary of the result.
        request_id:
            Correlation ID for cross-referencing with server logs.
        duration_ms:
            Round-trip latency in milliseconds.
        """
        if not self._enabled:
            return

        # Strip auth metadata and record only param key names
        safe_keys = [k for k in params if not k.startswith("_")]

        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            actor_id=self._actor_id,
            site_id=self._site_id,
            server=server,
            tool=tool,
            params_keys=safe_keys,
            result_summary=result_summary,
            request_id=request_id,
            duration_ms=duration_ms,
        )

        async with self._lock:
            self._buffer.append(entry)
            if len(self._buffer) >= _BUFFER_FLUSH_SIZE:
                await self._flush_buffer()

    async def flush(self) -> None:
        """Force-flush all buffered audit entries to disk."""
        async with self._lock:
            await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Write buffered entries to the JSONL log file.

        Called internally with the lock already held.
        """
        if not self._buffer:
            return

        entries = list(self._buffer)
        self._buffer.clear()

        try:
            await self._ensure_log_directory()
            lines = [json.dumps(e.to_dict(), default=str) + "\n" for e in entries]
            # Use sync file I/O in a thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._write_lines, lines)
            logger.debug("Flushed %d audit entries to %s", len(entries), self._log_path)
        except Exception:
            # Re-buffer on failure so entries are not lost
            async with self._lock:
                self._buffer = entries + self._buffer
            logger.exception("Failed to flush audit log to %s", self._log_path)

    def _write_lines(self, lines: list[str]) -> None:
        """Synchronous helper to append lines to the log file."""
        with open(self._log_path, "a", encoding="utf-8") as fh:
            fh.writelines(lines)

    async def _ensure_log_directory(self) -> None:
        """Create the log directory if it does not exist."""
        if self._initialised:
            return
        log_dir = os.path.dirname(self._log_path)
        if log_dir:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, os.makedirs, log_dir, 0o755, True)
        self._initialised = True

    async def read_entries(
        self,
        *,
        limit: int = 100,
        server: str | None = None,
        tool: str | None = None,
    ) -> list[AuditEntry]:
        """Read recent entries from the audit log for local review.

        Parameters
        ----------
        limit:
            Maximum number of entries to return.
        server:
            Optional filter by server name.
        tool:
            Optional filter by tool name.

        Returns
        -------
        list[AuditEntry]:
            Matching entries, most-recent first.
        """
        await self.flush()

        entries: list[AuditEntry] = []
        try:
            loop = asyncio.get_running_loop()
            raw_lines: list[str] = await loop.run_in_executor(None, self._read_lines)
        except FileNotFoundError:
            return entries

        for line in reversed(raw_lines):
            if len(entries) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if server and data.get("server") != server:
                continue
            if tool and data.get("tool") != tool:
                continue

            entries.append(
                AuditEntry(
                    entry_id=data.get("entry_id", ""),
                    timestamp=data.get("timestamp", ""),
                    actor_id=data.get("actor_id", ""),
                    site_id=data.get("site_id", ""),
                    server=data.get("server", ""),
                    tool=data.get("tool", ""),
                    params_keys=data.get("params_keys", []),
                    result_summary=data.get("result_summary", ""),
                    request_id=data.get("request_id", ""),
                    duration_ms=data.get("duration_ms", 0.0),
                )
            )

        return entries

    def _read_lines(self) -> list[str]:
        """Synchronous helper to read all lines from the log file."""
        with open(self._log_path, encoding="utf-8") as fh:
            return fh.readlines()
