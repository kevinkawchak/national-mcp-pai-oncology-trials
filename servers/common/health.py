"""Health and readiness endpoint support for MCP servers.

Provides a HealthChecker that tracks server status and dependency
health, producing schema-valid health-status responses.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any


class HealthChecker:
    """Tracks server health and dependency status.

    Produces health-status responses conforming to
    schemas/health-status.schema.json.
    """

    def __init__(self, server_name: str, version: str = "0.7.0") -> None:
        self.server_name = server_name
        self.version = version
        self._start_time = time.monotonic()
        self._dependencies: list[dict[str, Any]] = []
        self._status = "healthy"

    def add_dependency(self, name: str, status: str = "healthy", latency_ms: float = 0) -> None:
        """Register or update a dependency's health status."""
        for dep in self._dependencies:
            if dep["name"] == name:
                dep["status"] = status
                dep["latency_ms"] = latency_ms
                return
        self._dependencies.append(
            {
                "name": name,
                "status": status,
                "latency_ms": latency_ms,
            }
        )

    def set_status(self, status: str) -> None:
        """Set the overall server status."""
        self._status = status

    def check(self) -> dict[str, Any]:
        """Return a schema-valid health-status response."""
        return {
            "server_name": self.server_name,
            "status": self._status,
            "version": self.version,
            "uptime_seconds": round(time.monotonic() - self._start_time, 2),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "dependencies": list(self._dependencies),
        }
