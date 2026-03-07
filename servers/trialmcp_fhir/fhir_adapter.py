"""FHIR backend adapter interfaces.

Provides abstract and concrete adapters for backend FHIR data sources
including a mock adapter for testing, with interfaces for HAPI FHIR
and SMART-on-FHIR backends.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class FHIRAdapter(ABC):
    """Abstract base class for FHIR backend adapters."""

    @abstractmethod
    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        """Read a single FHIR resource by type and ID."""

    @abstractmethod
    def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Search for FHIR resources. Returns a Bundle."""

    @abstractmethod
    def patient_lookup(self, pseudonym: str) -> dict[str, Any] | None:
        """Look up a patient by pseudonymized ID."""

    @abstractmethod
    def study_status(self, study_id: str) -> dict[str, Any] | None:
        """Get the status of a clinical study."""

    def capability_statement(self) -> dict[str, Any]:
        """Return a FHIR CapabilityStatement for this adapter."""
        return {
            "resourceType": "CapabilityStatement",
            "status": "active",
            "kind": "instance",
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [
                {
                    "mode": "server",
                    "resource": [
                        {
                            "type": "Patient",
                            "interaction": [{"code": "read"}, {"code": "search-type"}],
                        },
                        {"type": "ResearchStudy", "interaction": [{"code": "read"}]},
                    ],
                }
            ],
        }


class MockFHIRAdapter(FHIRAdapter):
    """Mock FHIR adapter for testing and local development.

    Loads synthetic FHIR data from JSON files or in-memory fixtures.
    """

    def __init__(self, data_dir: str | Path | None = None) -> None:
        self._resources: dict[str, dict[str, dict[str, Any]]] = {}
        if data_dir:
            self._load_data(Path(data_dir))
        else:
            self._load_synthetic_data()

    def _load_data(self, data_dir: Path) -> None:
        """Load FHIR resources from JSON files in a directory."""
        for json_file in data_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    bundle = json.load(f)
                for entry in bundle.get("entry", []):
                    resource = entry.get("resource", {})
                    rtype = resource.get("resourceType", "")
                    rid = resource.get("id", "")
                    if rtype and rid:
                        if rtype not in self._resources:
                            self._resources[rtype] = {}
                        self._resources[rtype][rid] = resource
            except (json.JSONDecodeError, OSError):
                continue

    def _load_synthetic_data(self) -> None:
        """Load built-in synthetic FHIR data."""
        patients = [
            {
                "resourceType": "Patient",
                "id": "patient-001",
                "name": [{"family": "Smith", "given": ["John"]}],
                "birthDate": "1965-03-15",
                "gender": "male",
            },
            {
                "resourceType": "Patient",
                "id": "patient-002",
                "name": [{"family": "Johnson", "given": ["Maria"]}],
                "birthDate": "1972-08-22",
                "gender": "female",
            },
        ]
        self._resources["Patient"] = {p["id"]: p for p in patients}

        studies = [
            {
                "resourceType": "ResearchStudy",
                "id": "study-onc-001",
                "title": "Phase III Robot-Assisted Oncology Trial",
                "status": "active",
                "phase": {"text": "Phase 3"},
            },
        ]
        self._resources["ResearchStudy"] = {s["id"]: s for s in studies}

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        return self._resources.get(resource_type, {}).get(resource_id)

    def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        resources = list(self._resources.get(resource_type, {}).values())
        if params:
            for key, value in params.items():
                resources = [r for r in resources if str(r.get(key, "")) == value]
        resources = resources[:limit]
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(resources),
            "entry": [{"resource": r} for r in resources],
        }

    def patient_lookup(self, pseudonym: str) -> dict[str, Any] | None:
        for patient in self._resources.get("Patient", {}).values():
            if patient.get("id") == pseudonym:
                return patient
        return None

    def study_status(self, study_id: str) -> dict[str, Any] | None:
        return self._resources.get("ResearchStudy", {}).get(study_id)
