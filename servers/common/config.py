"""Configuration management for MCP servers.

Supports loading configuration from environment variables, YAML files,
JSON files, and programmatic defaults. Each server receives a typed
ServerConfig dataclass.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ServerConfig:
    """Configuration for an MCP server instance.

    Attributes:
        server_name: Identifier for this server instance.
        host: Bind address for network listeners.
        port: Port number for network listeners.
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR).
        storage_backend: Storage backend type (memory, sqlite, postgresql).
        storage_dsn: Connection string for persistent storage.
        config_file: Path to an optional YAML/JSON config file.
        extra: Additional server-specific configuration.
    """

    server_name: str = "trialmcp-server"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    storage_backend: str = "memory"
    storage_dsn: str = ""
    config_file: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def load_config(
    server_name: str = "trialmcp-server",
    config_file: str = "",
    env_prefix: str = "TRIALMCP_",
) -> ServerConfig:
    """Load configuration with precedence: env vars > config file > defaults."""
    cfg = ServerConfig(server_name=server_name)

    # Load from config file if provided
    config_path = config_file or os.environ.get(f"{env_prefix}CONFIG_FILE", "")
    if config_path:
        path = Path(config_path)
        if path.exists() and path.suffix == ".json":
            with open(path) as f:
                file_cfg = json.load(f)
            _apply_dict(cfg, file_cfg)
        elif path.exists() and path.suffix in (".yml", ".yaml"):
            # YAML support requires pyyaml — graceful fallback
            try:
                import yaml

                with open(path) as f:
                    file_cfg = yaml.safe_load(f)
                if isinstance(file_cfg, dict):
                    _apply_dict(cfg, file_cfg)
            except ImportError:
                pass

    # Override with environment variables
    cfg.host = os.environ.get(f"{env_prefix}HOST", cfg.host)
    cfg.port = int(os.environ.get(f"{env_prefix}PORT", str(cfg.port)))
    cfg.log_level = os.environ.get(f"{env_prefix}LOG_LEVEL", cfg.log_level)
    cfg.storage_backend = os.environ.get(f"{env_prefix}STORAGE_BACKEND", cfg.storage_backend)
    cfg.storage_dsn = os.environ.get(f"{env_prefix}STORAGE_DSN", cfg.storage_dsn)

    cfg.config_file = config_path
    return cfg


def _apply_dict(cfg: ServerConfig, d: dict[str, Any]) -> None:
    """Apply a dict of values onto a ServerConfig."""
    for key in ("server_name", "host", "log_level", "storage_backend", "storage_dsn"):
        if key in d:
            setattr(cfg, key, d[key])
    if "port" in d:
        cfg.port = int(d["port"])
    if "extra" in d and isinstance(d["extra"], dict):
        cfg.extra.update(d["extra"])
