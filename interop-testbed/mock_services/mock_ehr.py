"""Mock FHIR R4 server with synthetic patient data.

Implements a minimal FHIR R4 server interface that returns
synthetic oncology patient data for interoperability testing.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


class MockEHR:
    """Mock Electronic Health Record (FHIR R4 server).

    Generates and serves synthetic oncology patient data
    for interoperability testing.

    Args:
        site_id: Site identifier for this EHR instance.
        patient_count: Number of synthetic patients to generate.
    """

    def __init__(self, site_id: str = "site-a", patient_count: int = 20) -> None:
        self.site_id = site_id
        self.patient_count = patient_count
        self.patients: list[dict[str, Any]] = []
        self.studies: list[dict[str, Any]] = []
        self._generate_data()

    def _generate_data(self) -> None:
        """Generate synthetic patient and study data."""
        for i in range(self.patient_count):
            self.patients.append(self._make_patient(i))
        # Generate 2 research studies per site
        for i in range(2):
            self.studies.append(self._make_study(i))

    def _make_patient(self, index: int) -> dict[str, Any]:
        """Generate a synthetic FHIR Patient resource."""
        patient_id = hashlib.sha256(f"{self.site_id}-patient-{index}".encode()).hexdigest()[:16]
        return {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
            },
            "identifier": [
                {
                    "system": "urn:trialmcp:pseudonym",
                    "value": hashlib.sha256(f"{self.site_id}-mrn-{index}".encode()).hexdigest()[
                        :32
                    ],
                }
            ],
            "active": True,
            "name": [{"use": "anonymous", "text": "[REDACTED]"}],
            "gender": ["male", "female"][index % 2],
            "birthDate": f"{1940 + (index % 60)}",
            "address": [{"text": "[REDACTED]"}],
        }

    def _make_study(self, index: int) -> dict[str, Any]:
        """Generate a synthetic FHIR ResearchStudy resource."""
        return {
            "resourceType": "ResearchStudy",
            "id": f"{self.site_id}-TRIAL-{index:04d}",
            "status": "active",
            "title": f"Oncology Trial {index} at {self.site_id}",
            "phase": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/research-study-phase",
                        "code": "phase-3",
                    }
                ]
            },
        }

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        """Read a FHIR resource by type and ID.

        Args:
            resource_type: FHIR resource type.
            resource_id: Resource identifier.

        Returns:
            FHIR resource if found, None otherwise.
        """
        if resource_type == "Patient":
            for patient in self.patients:
                if patient["id"] == resource_id:
                    return patient
        elif resource_type == "ResearchStudy":
            for study in self.studies:
                if study["id"] == resource_id:
                    return study
        return None

    def search(self, resource_type: str, max_results: int = 100) -> list[dict[str, Any]]:
        """Search for FHIR resources by type.

        Args:
            resource_type: FHIR resource type to search.
            max_results: Maximum results to return (capped at 100).

        Returns:
            List of matching FHIR resources.
        """
        cap = min(max_results, 100)
        if resource_type == "Patient":
            return self.patients[:cap]
        elif resource_type == "ResearchStudy":
            return self.studies[:cap]
        return []
