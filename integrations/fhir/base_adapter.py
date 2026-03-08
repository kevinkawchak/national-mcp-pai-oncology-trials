"""Abstract FHIR adapter interface for oncology trial data access.

Defines the contract that all FHIR backend adapters must implement,
including resource read/search, patient lookup, study status, and
capability statement generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseFHIRAdapter(ABC):
    """Abstract base class for FHIR R4 backend adapters.

    All concrete adapters (mock, HAPI, SMART-on-FHIR) must implement
    the abstract methods defined here to provide a uniform interface
    for oncology trial data access.
    """

    @abstractmethod
    def read(
        self,
        resource_type: str,
        resource_id: str,
    ) -> dict[str, Any] | None:
        """Read a single FHIR resource by type and ID.

        Args:
            resource_type: FHIR resource type (e.g. "Patient").
            resource_id: Logical ID of the resource.

        Returns:
            The FHIR resource dict, or ``None`` if not found.
        """

    @abstractmethod
    def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Search for FHIR resources matching the given parameters.

        Args:
            resource_type: FHIR resource type to search.
            params: Optional search parameter key/value pairs.
            limit: Maximum number of results to return.

        Returns:
            A FHIR Bundle of type ``searchset``.
        """

    @abstractmethod
    def patient_lookup(
        self,
        pseudonym: str,
    ) -> dict[str, Any] | None:
        """Look up a patient by pseudonymized identifier.

        Args:
            pseudonym: The pseudonymized patient ID.

        Returns:
            The Patient resource dict, or ``None`` if not found.
        """

    @abstractmethod
    def study_status(
        self,
        study_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve the current status of a clinical research study.

        Args:
            study_id: Logical ID of the ResearchStudy resource.

        Returns:
            The ResearchStudy resource dict, or ``None`` if not found.
        """

    def capability_statement(self) -> dict[str, Any]:
        """Return a FHIR R4 CapabilityStatement for this adapter.

        Subclasses may override to advertise additional capabilities.

        Returns:
            A CapabilityStatement resource dict.
        """
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
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"},
                            ],
                        },
                        {
                            "type": "ResearchStudy",
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"},
                            ],
                        },
                        {
                            "type": "Observation",
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"},
                            ],
                        },
                    ],
                }
            ],
        }
