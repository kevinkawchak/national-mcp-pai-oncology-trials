"""DICOM backend adapter interfaces.

Provides abstract and concrete adapters for backend DICOM data sources
including a mock adapter for testing, with interfaces for Orthanc
and dcm4chee backends.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Any

# Role-based modality restrictions per spec/tool-contracts.md
# MUST modalities: CT, MR, PT
# SHOULD modalities: RTSTRUCT, RTPLAN
MUST_MODALITIES = {"CT", "MR", "PT"}
SHOULD_MODALITIES = {"RTSTRUCT", "RTPLAN"}
ALL_SUPPORTED_MODALITIES = MUST_MODALITIES | SHOULD_MODALITIES

# Role-based query level permissions per spec/tool-contracts.md
ROLE_QUERY_LEVELS: dict[str, list[str]] = {
    "robot_agent": ["STUDY", "SERIES"],
    "trial_coordinator": ["STUDY", "SERIES", "IMAGE"],
    "data_monitor": ["STUDY"],
    "auditor": [],
    "sponsor": [],
    "cro": [],
}


def hash_patient_name(name: str) -> str:
    """Hash a patient name to a 12-character SHA-256 prefix."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:12]


def generalize_study_date(date_str: str) -> str:
    """Generalize a DICOM StudyDate to year-only format."""
    if len(date_str) >= 4:
        return date_str[:4]
    return date_str


class DICOMAdapter(ABC):
    """Abstract base class for DICOM backend adapters."""

    @abstractmethod
    def query(
        self,
        query_level: str,
        modality: str | None = None,
        patient_id: str | None = None,
        study_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query DICOM studies/series/instances."""

    @abstractmethod
    def retrieve(self, study_uid: str) -> dict[str, Any] | None:
        """Retrieve DICOM study metadata (pointer, no pixel data)."""


class MockDICOMAdapter(DICOMAdapter):
    """Mock DICOM adapter for testing and local development."""

    def __init__(self) -> None:
        self._studies: list[dict[str, Any]] = [
            {
                "StudyInstanceUID": "1.2.840.113619.2.55.3.604688119.969.1234567890.1",
                "PatientName": "Smith^John",
                "PatientID": "patient-001",
                "StudyDate": "20250115",
                "Modality": "CT",
                "StudyDescription": "CT Chest with contrast",
                "NumberOfSeries": 3,
                "NumberOfInstances": 245,
            },
            {
                "StudyInstanceUID": "1.2.840.113619.2.55.3.604688119.969.1234567890.2",
                "PatientName": "Johnson^Maria",
                "PatientID": "patient-002",
                "StudyDate": "20250220",
                "Modality": "MR",
                "StudyDescription": "MR Brain without contrast",
                "NumberOfSeries": 5,
                "NumberOfInstances": 380,
            },
            {
                "StudyInstanceUID": "1.2.840.113619.2.55.3.604688119.969.1234567890.3",
                "PatientName": "Smith^John",
                "PatientID": "patient-001",
                "StudyDate": "20250301",
                "Modality": "PT",
                "StudyDescription": "PET/CT FDG whole body",
                "NumberOfSeries": 2,
                "NumberOfInstances": 512,
            },
        ]

    def query(
        self,
        query_level: str,
        modality: str | None = None,
        patient_id: str | None = None,
        study_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        results = list(self._studies)

        if modality:
            results = [s for s in results if s["Modality"] == modality]
        if patient_id:
            results = [s for s in results if s["PatientID"] == patient_id]
        if study_uid:
            results = [s for s in results if s["StudyInstanceUID"] == study_uid]

        # Apply de-identification: hash patient names, generalize dates
        deidentified = []
        for study in results:
            entry = dict(study)
            entry["PatientName"] = hash_patient_name(entry["PatientName"])
            entry["StudyDate"] = generalize_study_date(entry["StudyDate"])
            deidentified.append(entry)

        return deidentified

    def retrieve(self, study_uid: str) -> dict[str, Any] | None:
        for study in self._studies:
            if study["StudyInstanceUID"] == study_uid:
                return {
                    "StudyInstanceUID": study_uid,
                    "Modality": study["Modality"],
                    "StudyDescription": study["StudyDescription"],
                    "NumberOfSeries": study["NumberOfSeries"],
                    "NumberOfInstances": study["NumberOfInstances"],
                    "retrieval_pointer": f"dicom://{study_uid}",
                    "pixel_data_included": False,
                }
        return None
