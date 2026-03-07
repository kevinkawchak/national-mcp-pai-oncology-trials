"""Mock DICOMweb server with synthetic imaging metadata.

Implements a minimal DICOMweb interface that returns
synthetic oncology imaging metadata for interoperability testing.
"""

from __future__ import annotations

import hashlib
from typing import Any


class MockPACS:
    """Mock Picture Archiving and Communication System (DICOMweb).

    Generates and serves synthetic DICOM imaging metadata
    for interoperability testing.

    Args:
        site_id: Site identifier for this PACS instance.
        study_count: Number of synthetic studies to generate.
    """

    def __init__(self, site_id: str = "site-a", study_count: int = 15) -> None:
        self.site_id = site_id
        self.study_count = study_count
        self.studies: list[dict[str, Any]] = []
        self._generate_data()

    def _generate_data(self) -> None:
        """Generate synthetic imaging study metadata."""
        modalities = ["CT", "MR", "PT", "RTSTRUCT", "RTPLAN"]
        for i in range(self.study_count):
            modality = modalities[i % len(modalities)]
            patient_index = i % 10
            patient_hash = hashlib.sha256(
                f"{self.site_id}-patient-{patient_index}".encode()
            ).hexdigest()[:12]

            self.studies.append(
                {
                    "study_instance_uid": f"1.2.840.{self.site_id}.{i}.1.{i * 7}",
                    "modality": modality,
                    "patient_name_hash": patient_hash,
                    "study_date": f"{2024 + (i % 3)}",
                    "series_count": 1 + (i % 5),
                    "instance_count": 10 + (i * 3),
                    "site_id": self.site_id,
                }
            )

    def query(
        self,
        modality: str | None = None,
        query_level: str = "STUDY",
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        """Query imaging studies.

        Args:
            modality: Filter by modality (CT, MR, PT, etc.).
            query_level: Query level (PATIENT, STUDY, SERIES, IMAGE).
            max_results: Maximum results to return.

        Returns:
            List of matching imaging study metadata.
        """
        results = self.studies
        if modality:
            results = [s for s in results if s["modality"] == modality]
        return results[:max_results]

    def retrieve_metadata(self, study_uid: str) -> dict[str, Any] | None:
        """Retrieve metadata for a specific study.

        Args:
            study_uid: Study Instance UID.

        Returns:
            Study metadata if found, None otherwise.
        """
        for study in self.studies:
            if study["study_instance_uid"] == study_uid:
                return study
        return None
