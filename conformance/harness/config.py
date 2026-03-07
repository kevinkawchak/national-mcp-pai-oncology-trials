"""Harness configuration for black-box conformance testing.

Defines target server URLs/addresses, authentication credentials,
test data seeding options, profile/level selection, and output
format selection for the conformance harness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ServerTarget:
    """Configuration for a single MCP server target.

    Attributes:
        name: Server identifier (e.g., 'authz', 'fhir', 'dicom').
        transport: Transport type ('stdin', 'http', 'docker').
        address: Target address (command, URL, or container name).
        auth_token: Authentication token for test sessions.
        auth_headers: Additional authentication headers.
    """

    name: str
    transport: str = "stdin"
    address: str = ""
    auth_token: str = ""
    auth_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class SeedConfig:
    """Test data seeding configuration.

    Attributes:
        enabled: Whether to seed test data before running tests.
        patient_count: Number of synthetic patients to seed.
        study_count: Number of synthetic studies to seed.
        imaging_count: Number of synthetic imaging studies to seed.
        seed_script: Path to a custom seeding script.
    """

    enabled: bool = False
    patient_count: int = 10
    study_count: int = 2
    imaging_count: int = 5
    seed_script: str = ""


@dataclass
class HarnessConfig:
    """Top-level conformance harness configuration.

    Attributes:
        servers: Target server configurations keyed by server name.
        profile: Conformance profile to test ('base', 'clinical-read',
                 'imaging-guided-oncology', 'multi-site-federated',
                 'robot-assisted-procedure').
        level: Conformance level (1-5).
        output_format: Report output format ('json', 'junit', 'html', 'markdown').
        output_dir: Directory for test reports.
        seed: Test data seeding configuration.
        timeout: Default request timeout in seconds.
        parallel: Whether to run tests in parallel.
        verbose: Verbose output mode.
    """

    servers: dict[str, ServerTarget] = field(default_factory=dict)
    profile: str = "base"
    level: int = 1
    output_format: str = "json"
    output_dir: str = "reports"
    seed: SeedConfig = field(default_factory=SeedConfig)
    timeout: float = 30.0
    parallel: bool = False
    verbose: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HarnessConfig:
        """Create HarnessConfig from a dictionary."""
        servers = {}
        for name, srv_data in data.get("servers", {}).items():
            servers[name] = ServerTarget(
                name=name,
                transport=srv_data.get("transport", "stdin"),
                address=srv_data.get("address", ""),
                auth_token=srv_data.get("auth_token", ""),
                auth_headers=srv_data.get("auth_headers", {}),
            )

        seed_data = data.get("seed", {})
        seed = SeedConfig(
            enabled=seed_data.get("enabled", False),
            patient_count=seed_data.get("patient_count", 10),
            study_count=seed_data.get("study_count", 2),
            imaging_count=seed_data.get("imaging_count", 5),
            seed_script=seed_data.get("seed_script", ""),
        )

        return cls(
            servers=servers,
            profile=data.get("profile", "base"),
            level=data.get("level", 1),
            output_format=data.get("output_format", "json"),
            output_dir=data.get("output_dir", "reports"),
            seed=seed,
            timeout=data.get("timeout", 30.0),
            parallel=data.get("parallel", False),
            verbose=data.get("verbose", True),
        )

    @classmethod
    def from_file(cls, config_path: str | Path) -> HarnessConfig:
        """Load HarnessConfig from a JSON or YAML file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Parsed HarnessConfig instance.
        """
        path = Path(config_path)
        text = path.read_text(encoding="utf-8")

        if path.suffix == ".json":
            data = json.loads(text)
        elif path.suffix in (".yml", ".yaml"):
            try:
                import yaml

                data = yaml.safe_load(text)
            except ImportError:
                msg = "PyYAML required for YAML config files"
                raise ImportError(msg)
        else:
            msg = f"Unsupported config file format: {path.suffix}"
            raise ValueError(msg)

        return cls.from_dict(data)

    def get_server(self, name: str) -> ServerTarget:
        """Get a server target by name.

        Args:
            name: Server name (e.g., 'authz', 'fhir').

        Returns:
            ServerTarget configuration.

        Raises:
            KeyError: If the server is not configured.
        """
        if name not in self.servers:
            msg = f"Server not configured: {name}"
            raise KeyError(msg)
        return self.servers[name]


# Default server names for the 5 MCP servers
SERVER_NAMES = ["authz", "fhir", "dicom", "ledger", "provenance"]


def default_config() -> HarnessConfig:
    """Create a default HarnessConfig targeting local stdin servers."""
    servers = {}
    for name in SERVER_NAMES:
        servers[name] = ServerTarget(
            name=name,
            transport="stdin",
            address=f"trialmcp-{name}",
        )

    return HarnessConfig(servers=servers)
