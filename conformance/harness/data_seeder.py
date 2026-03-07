"""Test data seeder for conformance target environments.

Seeds synthetic clinical data (patients, studies, imaging metadata)
into target MCP server deployments before running conformance tests.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from conformance.harness.client import MCPConformanceClient


@dataclass
class SeedResult:
    """Result of a data seeding operation.

    Attributes:
        success: Whether seeding completed successfully.
        patients_seeded: Number of patients seeded.
        studies_seeded: Number of studies seeded.
        imaging_seeded: Number of imaging studies seeded.
        audit_records: Number of audit records created.
        errors: List of errors encountered during seeding.
    """

    success: bool = True
    patients_seeded: int = 0
    studies_seeded: int = 0
    imaging_seeded: int = 0
    audit_records: int = 0
    errors: list[str] = field(default_factory=list)


def generate_synthetic_patient(index: int) -> dict[str, Any]:
    """Generate a synthetic FHIR R4 Patient resource.

    Creates de-identified patient data suitable for conformance
    testing, following HIPAA Safe Harbor requirements.

    Args:
        index: Patient index for deterministic generation.

    Returns:
        De-identified FHIR Patient resource dictionary.
    """
    patient_id = hashlib.sha256(f"patient-{index}".encode()).hexdigest()[:16]
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"versionId": "1", "lastUpdated": datetime.now(timezone.utc).isoformat()},
        "identifier": [
            {
                "system": "urn:trialmcp:pseudonym",
                "value": hashlib.sha256(f"mrn-{index}".encode()).hexdigest()[:32],
            }
        ],
        "active": True,
        "name": [{"use": "anonymous", "text": "[REDACTED]"}],
        "birthDate": f"{1950 + (index % 50)}",
        "address": [{"text": "[REDACTED]"}],
    }


def generate_synthetic_study(index: int) -> dict[str, Any]:
    """Generate a synthetic FHIR R4 ResearchStudy resource.

    Args:
        index: Study index for deterministic generation.

    Returns:
        FHIR ResearchStudy resource dictionary.
    """
    study_id = f"TRIAL-{index:04d}"
    return {
        "resourceType": "ResearchStudy",
        "id": study_id,
        "status": "active",
        "title": f"Synthetic Oncology Trial {index}",
        "phase": {
            "coding": [{"system": "http://hl7.org/fhir/research-study-phase", "code": "phase-3"}]
        },
        "category": [{"text": "Interventional"}],
        "condition": [{"text": "Oncology"}],
    }


def generate_synthetic_imaging(index: int) -> dict[str, Any]:
    """Generate synthetic DICOM imaging metadata.

    Args:
        index: Imaging study index for deterministic generation.

    Returns:
        DICOM study metadata dictionary.
    """
    modalities = ["CT", "MR", "PT", "RTSTRUCT", "RTPLAN"]
    modality = modalities[index % len(modalities)]
    study_uid = f"1.2.840.10008.{index}.1.{index * 7}"
    patient_hash = hashlib.sha256(f"patient-{index % 5}".encode()).hexdigest()[:12]

    return {
        "study_instance_uid": study_uid,
        "modality": modality,
        "patient_name_hash": patient_hash,
        "study_date": f"{2024 + (index % 3)}",
        "series_count": 1 + (index % 5),
        "instance_count": 10 + (index * 3),
    }


class DataSeeder:
    """Seeds test data into target MCP server environments.

    Creates synthetic patients, studies, and imaging metadata
    via MCP tool calls to prepare the target environment for
    conformance testing.

    Args:
        client: MCPConformanceClient connected to the target server.
    """

    def __init__(self, client: MCPConformanceClient) -> None:
        self.client = client

    def seed_patients(self, count: int = 10) -> list[dict]:
        """Seed synthetic patient records.

        Args:
            count: Number of patients to seed.

        Returns:
            List of seeded patient resources.
        """
        patients = []
        for i in range(count):
            patient = generate_synthetic_patient(i)
            patients.append(patient)
        return patients

    def seed_studies(self, count: int = 2) -> list[dict]:
        """Seed synthetic research studies.

        Args:
            count: Number of studies to seed.

        Returns:
            List of seeded study resources.
        """
        studies = []
        for i in range(count):
            study = generate_synthetic_study(i)
            studies.append(study)
        return studies

    def seed_imaging(self, count: int = 5) -> list[dict]:
        """Seed synthetic imaging metadata.

        Args:
            count: Number of imaging studies to seed.

        Returns:
            List of seeded imaging metadata records.
        """
        imaging = []
        for i in range(count):
            img = generate_synthetic_imaging(i)
            imaging.append(img)
        return imaging

    def seed_all(
        self,
        patient_count: int = 10,
        study_count: int = 2,
        imaging_count: int = 5,
    ) -> SeedResult:
        """Seed all test data types.

        Args:
            patient_count: Number of patients to seed.
            study_count: Number of studies to seed.
            imaging_count: Number of imaging studies to seed.

        Returns:
            SeedResult with counts and any errors.
        """
        result = SeedResult()

        try:
            patients = self.seed_patients(patient_count)
            result.patients_seeded = len(patients)
        except Exception as e:
            result.errors.append(f"Patient seeding failed: {e}")

        try:
            studies = self.seed_studies(study_count)
            result.studies_seeded = len(studies)
        except Exception as e:
            result.errors.append(f"Study seeding failed: {e}")

        try:
            imaging = self.seed_imaging(imaging_count)
            result.imaging_seeded = len(imaging)
        except Exception as e:
            result.errors.append(f"Imaging seeding failed: {e}")

        result.success = len(result.errors) == 0
        return result
