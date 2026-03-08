"""Abstract DICOM adapter interface for oncology trial integrations.

Defines the contract that all DICOM adapters must implement,
including query, metadata retrieval, and modality validation
operations. Supports STUDY, SERIES, and IMAGE query levels
per DICOM Query/Retrieve specification.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from typing import Any


class QueryLevel(enum.Enum):
    """DICOM query/retrieve level.

    Corresponds to the hierarchical levels defined in the DICOM
    Query/Retrieve Service Class (PS3.4 Annex C).
    """

    STUDY = "STUDY"
    SERIES = "SERIES"
    IMAGE = "IMAGE"


class BaseDicomAdapter(ABC):
    """Abstract base class for DICOM integration adapters.

    All DICOM adapters used within the national MCP PAI oncology
    trial framework must implement this interface. Adapters are
    expected to operate in metadata-only mode; pixel data transfer
    is explicitly prohibited by the safety module.

    Attributes:
        adapter_name: Human-readable name for this adapter.
        supported_modalities: Set of DICOM modality codes this
            adapter is configured to handle.
    """

    adapter_name: str = "base"
    supported_modalities: set[str] = {
        "CT",
        "MR",
        "PT",
        "RTSTRUCT",
        "RTPLAN",
    }

    @abstractmethod
    def query(
        self,
        query_level: QueryLevel,
        filters: dict[str, Any],
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query the DICOM source at the specified level.

        Args:
            query_level: The hierarchical level to query
                (STUDY, SERIES, or IMAGE).
            filters: Key-value pairs for DICOM attribute matching.
                Keys should be standard DICOM keyword names
                (e.g., ``PatientID``, ``Modality``).
            limit: Maximum number of results to return.
            offset: Number of results to skip for pagination.

        Returns:
            A list of dictionaries, each representing a matched
            DICOM entity with its metadata attributes.

        Raises:
            ConnectionError: If the DICOM source is unreachable.
            ValueError: If the query_level or filters are invalid.
        """

    @abstractmethod
    def retrieve_metadata(
        self,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve DICOM metadata for a specific entity.

        Returns metadata only; pixel data is never included per
        safety constraints. The level of detail depends on which
        UIDs are provided.

        Args:
            study_instance_uid: The Study Instance UID.
            series_instance_uid: Optional Series Instance UID to
                narrow retrieval to a specific series.
            sop_instance_uid: Optional SOP Instance UID to narrow
                retrieval to a specific instance.

        Returns:
            A dictionary containing DICOM metadata attributes.
            Pixel data fields are stripped by the safety layer.

        Raises:
            ConnectionError: If the DICOM source is unreachable.
            KeyError: If the referenced entity does not exist.
        """

    @abstractmethod
    def validate_modality(
        self,
        modality: str,
        role: str | None = None,
    ) -> bool:
        """Check whether a modality is permitted for access.

        Validates that the given DICOM modality code is within
        the set of supported modalities and, optionally, that
        the requesting role has permission to access it.

        Args:
            modality: DICOM modality code (e.g., ``CT``, ``MR``).
            role: Optional role identifier for role-based access
                control checks.

        Returns:
            True if the modality is permitted, False otherwise.
        """

    def ping(self) -> bool:
        """Check connectivity to the DICOM source.

        Returns:
            True if the source is reachable, False otherwise.
        """
        return False

    def __repr__(self) -> str:
        """Return a string representation of the adapter."""
        return f"<{self.__class__.__name__} adapter_name={self.adapter_name!r}>"
