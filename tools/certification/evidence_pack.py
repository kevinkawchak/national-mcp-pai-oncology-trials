"""Evidence bundle export for conformance certification.

Creates reproducible evidence bundles containing conformance test
results, schema validation results, audit chain verification,
environment snapshots, and certification manifests.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EvidenceArtifact:
    """A single evidence artifact.

    Attributes:
        name: Artifact name.
        artifact_type: Type of artifact (test_results, schema_validation, etc.).
        content: Artifact content (serializable).
        sha256: SHA-256 hash of the artifact content.
    """

    name: str
    artifact_type: str
    content: Any = None
    sha256: str = ""

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the artifact content."""
        serialized = json.dumps(self.content, sort_keys=True, default=str)
        self.sha256 = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return self.sha256


@dataclass
class EvidencePack:
    """Complete evidence bundle for certification.

    Attributes:
        pack_id: Unique identifier for this evidence pack.
        timestamp: Generation timestamp.
        site_id: Site identifier.
        profile: Conformance profile tested.
        level: Conformance level.
        artifacts: List of evidence artifacts.
        environment: Environment configuration snapshot.
    """

    pack_id: str = ""
    timestamp: str = ""
    site_id: str = ""
    profile: str = "base"
    level: int = 1
    artifacts: list[EvidenceArtifact] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.pack_id:
            self.pack_id = hashlib.sha256(f"{self.site_id}-{self.timestamp}".encode()).hexdigest()[
                :16
            ]
        if not self.environment:
            self.environment = {
                "python_version": (
                    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                ),
                "platform": sys.platform,
            }

    def add_artifact(
        self,
        name: str,
        artifact_type: str,
        content: Any,
    ) -> EvidenceArtifact:
        """Add an evidence artifact to the pack.

        Args:
            name: Artifact name.
            artifact_type: Type of artifact.
            content: Artifact content.

        Returns:
            The created EvidenceArtifact.
        """
        artifact = EvidenceArtifact(
            name=name,
            artifact_type=artifact_type,
            content=content,
        )
        artifact.compute_hash()
        self.artifacts.append(artifact)
        return artifact

    def generate_manifest(self) -> dict[str, Any]:
        """Generate a reproducible certification manifest.

        Returns:
            Manifest dictionary with hashes of all evidence artifacts.
        """
        artifact_hashes = []
        for artifact in self.artifacts:
            if not artifact.sha256:
                artifact.compute_hash()
            artifact_hashes.append(
                {
                    "name": artifact.name,
                    "type": artifact.artifact_type,
                    "sha256": artifact.sha256,
                }
            )

        manifest_content = json.dumps(artifact_hashes, sort_keys=True)
        manifest_hash = hashlib.sha256(manifest_content.encode("utf-8")).hexdigest()

        return {
            "pack_id": self.pack_id,
            "timestamp": self.timestamp,
            "site_id": self.site_id,
            "profile": self.profile,
            "level": self.level,
            "artifact_count": len(self.artifacts),
            "artifacts": artifact_hashes,
            "manifest_hash": manifest_hash,
            "environment": self.environment,
        }

    def export(self, output_dir: str | Path) -> Path:
        """Export the evidence pack to a directory.

        Args:
            output_dir: Output directory.

        Returns:
            Path to the manifest file.
        """
        out = Path(output_dir) / f"evidence-{self.pack_id}"
        out.mkdir(parents=True, exist_ok=True)

        # Write each artifact
        for artifact in self.artifacts:
            artifact_path = out / f"{artifact.name}.json"
            artifact_path.write_text(
                json.dumps(artifact.content, indent=2, default=str),
                encoding="utf-8",
            )

        # Write manifest
        manifest_path = out / "manifest.json"
        manifest_path.write_text(
            json.dumps(self.generate_manifest(), indent=2),
            encoding="utf-8",
        )

        return manifest_path
