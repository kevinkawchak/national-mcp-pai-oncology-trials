"""Mock FHIR adapter with synthetic oncology patient data.

Provides an in-memory FHIR adapter loaded with synthetic patient,
ResearchStudy, and Observation resources for local development and
testing of the National MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

from typing import Any

from integrations.fhir.base_adapter import BaseFHIRAdapter

# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------

_PATIENTS: list[dict[str, Any]] = [
    {
        "resourceType": "Patient",
        "id": "patient-onc-001",
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]},
        "name": [{"family": "Chen", "given": ["Wei"]}],
        "birthDate": "1958-04-12",
        "gender": "male",
        "address": [
            {
                "city": "Houston",
                "state": "TX",
                "postalCode": "77030",
            }
        ],
        "identifier": [
            {
                "system": "urn:oid:2.16.840.1.113883.4.1",
                "value": "MRN-10001",
            }
        ],
    },
    {
        "resourceType": "Patient",
        "id": "patient-onc-002",
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]},
        "name": [{"family": "Okafor", "given": ["Adaeze"]}],
        "birthDate": "1971-11-03",
        "gender": "female",
        "address": [
            {
                "city": "Baltimore",
                "state": "MD",
                "postalCode": "21287",
            }
        ],
        "identifier": [
            {
                "system": "urn:oid:2.16.840.1.113883.4.1",
                "value": "MRN-10002",
            }
        ],
    },
    {
        "resourceType": "Patient",
        "id": "patient-onc-003",
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]},
        "name": [{"family": "Martinez", "given": ["Carlos", "J"]}],
        "birthDate": "1985-07-28",
        "gender": "male",
        "address": [
            {
                "city": "Rochester",
                "state": "MN",
                "postalCode": "55905",
            }
        ],
        "identifier": [
            {
                "system": "urn:oid:2.16.840.1.113883.4.1",
                "value": "MRN-10003",
            }
        ],
    },
]

_RESEARCH_STUDIES: list[dict[str, Any]] = [
    {
        "resourceType": "ResearchStudy",
        "id": "study-pai-lung-001",
        "title": (
            "Phase III Robot-Assisted Thoracoscopic Lobectomy for Non-Small Cell Lung Cancer"
        ),
        "status": "active",
        "phase": {
            "coding": [
                {
                    "system": ("http://terminology.hl7.org/CodeSystem/research-study-phase"),
                    "code": "phase-3",
                    "display": "Phase 3",
                }
            ],
        },
        "condition": [
            {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": "C34.1",
                        "display": ("Malignant neoplasm of upper lobe, bronchus or lung"),
                    }
                ],
            }
        ],
        "enrollment": [{"reference": "Group/enrolled-pai-lung-001"}],
    },
    {
        "resourceType": "ResearchStudy",
        "id": "study-pai-prostate-002",
        "title": ("Phase II Robotic Prostatectomy with AI-Guided Margin Assessment"),
        "status": "active",
        "phase": {
            "coding": [
                {
                    "system": ("http://terminology.hl7.org/CodeSystem/research-study-phase"),
                    "code": "phase-2",
                    "display": "Phase 2",
                }
            ],
        },
        "condition": [
            {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": "C61",
                        "display": "Malignant neoplasm of prostate",
                    }
                ],
            }
        ],
    },
]

_OBSERVATIONS: list[dict[str, Any]] = [
    {
        "resourceType": "Observation",
        "id": "obs-tumor-marker-001",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/CodeSystem/observation-category"),
                        "code": "laboratory",
                    }
                ],
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "2857-1",
                    "display": "Prostate specific Ag [Mass/volume] in Serum or Plasma",
                }
            ],
        },
        "subject": {"reference": "Patient/patient-onc-002"},
        "valueQuantity": {
            "value": 4.2,
            "unit": "ng/mL",
            "system": "http://unitsofmeasure.org",
            "code": "ng/mL",
        },
    },
    {
        "resourceType": "Observation",
        "id": "obs-tumor-size-002",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/CodeSystem/observation-category"),
                        "code": "imaging",
                    }
                ],
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "21889-1",
                    "display": "Size Tumor",
                }
            ],
        },
        "subject": {"reference": "Patient/patient-onc-001"},
        "valueQuantity": {
            "value": 3.1,
            "unit": "cm",
            "system": "http://unitsofmeasure.org",
            "code": "cm",
        },
    },
    {
        "resourceType": "Observation",
        "id": "obs-cea-003",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/CodeSystem/observation-category"),
                        "code": "laboratory",
                    }
                ],
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "2039-6",
                    "display": ("Carcinoembryonic Ag [Mass/volume] in Serum or Plasma"),
                }
            ],
        },
        "subject": {"reference": "Patient/patient-onc-003"},
        "valueQuantity": {
            "value": 7.8,
            "unit": "ng/mL",
            "system": "http://unitsofmeasure.org",
            "code": "ng/mL",
        },
    },
]


class MockFHIRAdapter(BaseFHIRAdapter):
    """In-memory mock FHIR adapter loaded with synthetic fixtures.

    Contains oncology-relevant Patient, ResearchStudy, and Observation
    resources for testing without a live FHIR server.
    """

    def __init__(self) -> None:
        self._resources: dict[str, dict[str, dict[str, Any]]] = {}
        self._load_fixtures()

    # ------------------------------------------------------------------
    # Fixture loading
    # ------------------------------------------------------------------

    def _load_fixtures(self) -> None:
        """Populate the in-memory store from built-in fixtures."""
        for resource_list in (
            _PATIENTS,
            _RESEARCH_STUDIES,
            _OBSERVATIONS,
        ):
            for resource in resource_list:
                rtype = resource["resourceType"]
                rid = resource["id"]
                self._resources.setdefault(rtype, {})[rid] = resource

    # ------------------------------------------------------------------
    # BaseFHIRAdapter interface
    # ------------------------------------------------------------------

    def read(
        self,
        resource_type: str,
        resource_id: str,
    ) -> dict[str, Any] | None:
        """Read a single resource by type and ID."""
        return self._resources.get(resource_type, {}).get(resource_id)

    def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Search resources with optional parameter filtering."""
        resources = list(self._resources.get(resource_type, {}).values())
        if params:
            for key, value in params.items():
                resources = [r for r in resources if str(r.get(key, "")) == value]
        resources = resources[:limit]
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(resources),
            "entry": [
                {
                    "fullUrl": (f"urn:uuid:{r['resourceType']}/{r['id']}"),
                    "resource": r,
                }
                for r in resources
            ],
        }

    def patient_lookup(
        self,
        pseudonym: str,
    ) -> dict[str, Any] | None:
        """Look up a patient by pseudonymized identifier."""
        for patient in self._resources.get("Patient", {}).values():
            if patient.get("id") == pseudonym:
                return patient
        return None

    def study_status(
        self,
        study_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve a ResearchStudy by its logical ID."""
        return self._resources.get("ResearchStudy", {}).get(study_id)
