"""Structured JSON logging setup for MCP servers.

Configures Python's logging module to emit structured JSON log lines
suitable for production log aggregation systems.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return json.dumps(log_entry, ensure_ascii=True)


def setup_logging(
    level: str = "INFO",
    server_name: str = "trialmcp",
) -> logging.Logger:
    """Configure structured JSON logging for a server.

    Returns the root logger for the server namespace.
    """
    logger = logging.getLogger(server_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger
