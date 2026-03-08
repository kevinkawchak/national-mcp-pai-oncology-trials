"""Mock DICOM adapter with synthetic imaging metadata.

Provides a fully in-memory DICOM adapter populated with realistic
synthetic oncology imaging studies. Useful for development, testing,
and demonstration without requiring a live DICOM server.
"""

from __future__ import annotations

from typing import Any

from integrations.dicom.base_adapter import (
    BaseDicomAdapter,
    QueryLevel,
)
from integrations.dicom.modality_filter import ModalityFilter

# ---------------------------------------------------------------------------
# Synthetic study data
# ---------------------------------------------------------------------------

_SYNTHETIC_STUDIES: list[dict[str, Any]] = [
    {
        "StudyInstanceUID": "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639",
        "PatientID": "ONC-TRIAL-001",
        "PatientName": "DOE^JOHN",
        "PatientBirthDate": "19580214",
        "PatientSex": "M",
        "StudyDate": "20250115",
        "StudyDescription": "CT Chest Abdomen Pelvis with Contrast",
        "AccessionNumber": "ACC-2025-00142",
        "ReferringPhysicianName": "SMITH^JANE^MD",
        "InstitutionName": "National Oncology Center",
        "series": [
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10001"
                ),
                "Modality": "CT",
                "SeriesDescription": "Axial 3mm Soft Tissue",
                "SeriesNumber": 2,
                "NumberOfInstances": 187,
                "BodyPartExamined": "CHEST",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10002"
                ),
                "Modality": "CT",
                "SeriesDescription": "Coronal 3mm Reformat",
                "SeriesNumber": 3,
                "NumberOfInstances": 124,
                "BodyPartExamined": "CHEST",
            },
        ],
    },
    {
        "StudyInstanceUID": "1.2.826.0.1.3680043.8.1055.1.20230501090000000.12345678.11111111",
        "PatientID": "ONC-TRIAL-002",
        "PatientName": "SMITH^ALICE",
        "PatientBirthDate": "19720830",
        "PatientSex": "F",
        "StudyDate": "20250203",
        "StudyDescription": "MR Brain with and without Contrast",
        "AccessionNumber": "ACC-2025-00287",
        "ReferringPhysicianName": "CHEN^WILLIAM^MD",
        "InstitutionName": "University Medical Center",
        "series": [
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20230501090000000.12345678.20001"
                ),
                "Modality": "MR",
                "SeriesDescription": "T1 Axial Pre-Contrast",
                "SeriesNumber": 1,
                "NumberOfInstances": 42,
                "BodyPartExamined": "BRAIN",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20230501090000000.12345678.20002"
                ),
                "Modality": "MR",
                "SeriesDescription": "T1 Axial Post-Contrast",
                "SeriesNumber": 4,
                "NumberOfInstances": 42,
                "BodyPartExamined": "BRAIN",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20230501090000000.12345678.20003"
                ),
                "Modality": "MR",
                "SeriesDescription": "FLAIR Axial",
                "SeriesNumber": 2,
                "NumberOfInstances": 42,
                "BodyPartExamined": "BRAIN",
            },
        ],
    },
    {
        "StudyInstanceUID": "1.2.826.0.1.3680043.8.1055.1.20240718140000000.55555555.22222222",
        "PatientID": "ONC-TRIAL-003",
        "PatientName": "GARCIA^MARIA",
        "PatientBirthDate": "19651112",
        "PatientSex": "F",
        "StudyDate": "20250220",
        "StudyDescription": "PET-CT Whole Body FDG",
        "AccessionNumber": "ACC-2025-00391",
        "ReferringPhysicianName": "PATEL^RAJ^MD",
        "InstitutionName": "Regional Cancer Institute",
        "series": [
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20240718140000000.55555555.30001"
                ),
                "Modality": "PT",
                "SeriesDescription": "PET WB FDG Non-AC",
                "SeriesNumber": 1,
                "NumberOfInstances": 347,
                "BodyPartExamined": "WHOLEBODY",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20240718140000000.55555555.30002"
                ),
                "Modality": "CT",
                "SeriesDescription": "CT Attenuation Correction",
                "SeriesNumber": 2,
                "NumberOfInstances": 512,
                "BodyPartExamined": "WHOLEBODY",
            },
        ],
    },
    {
        "StudyInstanceUID": "1.2.826.0.1.3680043.8.1055.1.20241001080000000.99999999.33333333",
        "PatientID": "ONC-TRIAL-004",
        "PatientName": "JOHNSON^ROBERT",
        "PatientBirthDate": "19480605",
        "PatientSex": "M",
        "StudyDate": "20250301",
        "StudyDescription": "RT Planning CT with Structure Set",
        "AccessionNumber": "ACC-2025-00410",
        "ReferringPhysicianName": "LEE^SARAH^MD",
        "InstitutionName": "National Oncology Center",
        "series": [
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20241001080000000.99999999.40001"
                ),
                "Modality": "CT",
                "SeriesDescription": "Planning CT 2mm",
                "SeriesNumber": 1,
                "NumberOfInstances": 256,
                "BodyPartExamined": "LUNG",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20241001080000000.99999999.40002"
                ),
                "Modality": "RTSTRUCT",
                "SeriesDescription": "GTV PTV Structure Set",
                "SeriesNumber": 2,
                "NumberOfInstances": 1,
                "BodyPartExamined": "LUNG",
            },
            {
                "SeriesInstanceUID": (
                    "1.2.826.0.1.3680043.8.1055.1.20241001080000000.99999999.40003"
                ),
                "Modality": "RTPLAN",
                "SeriesDescription": "VMAT Treatment Plan",
                "SeriesNumber": 3,
                "NumberOfInstances": 1,
                "BodyPartExamined": "LUNG",
            },
        ],
    },
]


class MockDicomAdapter(BaseDicomAdapter):
    """Mock DICOM adapter backed by synthetic in-memory data.

    Provides realistic oncology imaging metadata for development
    and testing. All data is synthetic and does not represent real
    patients. Includes CT, MR, PT, RTSTRUCT, and RTPLAN modalities
    across four studies.

    Attributes:
        adapter_name: Identifier for this adapter.
    """

    adapter_name: str = "mock"

    def __init__(
        self,
        modality_filter: ModalityFilter | None = None,
    ) -> None:
        """Initialize the mock adapter.

        Args:
            modality_filter: Optional modality filter for
                role-based access enforcement.
        """
        self._studies = [dict(s) for s in _SYNTHETIC_STUDIES]
        self._modality_filter = modality_filter

    def query(
        self,
        query_level: QueryLevel,
        filters: dict[str, Any],
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query synthetic studies at the specified level.

        Args:
            query_level: The hierarchical level to query.
            filters: Key-value pairs for attribute matching.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            Matching DICOM entities as dictionaries.
        """
        if query_level == QueryLevel.STUDY:
            results = self._query_studies(filters)
        elif query_level == QueryLevel.SERIES:
            results = self._query_series(filters)
        else:
            results = self._query_images(filters)

        return results[offset : offset + limit]

    def retrieve_metadata(
        self,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve metadata for a synthetic DICOM entity.

        Args:
            study_instance_uid: The Study Instance UID.
            series_instance_uid: Optional Series Instance UID.
            sop_instance_uid: Optional SOP Instance UID.

        Returns:
            Dictionary containing DICOM metadata attributes.

        Raises:
            KeyError: If the referenced entity does not exist.
        """
        for study in self._studies:
            if study["StudyInstanceUID"] != study_instance_uid:
                continue

            if series_instance_uid is None:
                return _strip_series(study)

            for series in study.get("series", []):
                if series["SeriesInstanceUID"] == series_instance_uid:
                    return dict(series)

            raise KeyError(
                f"Series {series_instance_uid!r} not found in study {study_instance_uid!r}"
            )

        raise KeyError(f"Study {study_instance_uid!r} not found")

    def validate_modality(
        self,
        modality: str,
        role: str | None = None,
    ) -> bool:
        """Validate modality access, optionally by role.

        Args:
            modality: DICOM modality code.
            role: Optional role identifier.

        Returns:
            True if the modality is permitted.
        """
        if modality not in self.supported_modalities:
            return False

        if role and self._modality_filter:
            return self._modality_filter.is_permitted(role, modality)

        return True

    def ping(self) -> bool:
        """Mock adapter is always reachable.

        Returns:
            Always True.
        """
        return True

    # ---------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------

    def _query_studies(
        self,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Filter studies by top-level attributes."""
        results: list[dict[str, Any]] = []
        for study in self._studies:
            if _matches(study, filters):
                results.append(_strip_series(study))
        return results

    def _query_series(
        self,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Filter series across all studies."""
        results: list[dict[str, Any]] = []
        for study in self._studies:
            for series in study.get("series", []):
                merged = {
                    **_strip_series(study),
                    **series,
                }
                if _matches(merged, filters):
                    results.append(merged)
        return results

    def _query_images(
        self,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Image-level query returns series with instance count.

        Since this is a mock adapter without real instances, we
        return series metadata annotated with instance counts.
        """
        return self._query_series(filters)


def _strip_series(study: dict[str, Any]) -> dict[str, Any]:
    """Return a study dict without embedded series list."""
    return {k: v for k, v in study.items() if k != "series"}


def _matches(
    entity: dict[str, Any],
    filters: dict[str, Any],
) -> bool:
    """Check if an entity matches all filter criteria."""
    for key, value in filters.items():
        entity_value = entity.get(key)
        if entity_value is None:
            return False
        if isinstance(value, str) and value.endswith("*"):
            prefix = value[:-1]
            if not str(entity_value).startswith(prefix):
                return False
        elif str(entity_value) != str(value):
            return False
    return True
