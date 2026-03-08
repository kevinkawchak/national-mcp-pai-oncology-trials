"""FHIR CapabilityStatement generation and ingestion.

Provides utilities to generate FHIR R4 CapabilityStatement resources
for the National MCP PAI Oncology Trials platform and to parse
incoming CapabilityStatements to discover server capabilities.
"""

from __future__ import annotations

import datetime
from typing import Any

# Default resource types supported by the oncology trials platform
_DEFAULT_RESOURCE_TYPES: list[dict[str, Any]] = [
    {
        "type": "Patient",
        "profile": ("http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"),
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
        ],
        "searchParam": [
            {"name": "_id", "type": "token"},
            {"name": "identifier", "type": "token"},
            {"name": "name", "type": "string"},
            {"name": "gender", "type": "token"},
            {"name": "birthdate", "type": "date"},
        ],
    },
    {
        "type": "ResearchStudy",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
        ],
        "searchParam": [
            {"name": "_id", "type": "token"},
            {"name": "status", "type": "token"},
            {"name": "title", "type": "string"},
            {"name": "phase", "type": "token"},
        ],
    },
    {
        "type": "ResearchSubject",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
        ],
        "searchParam": [
            {"name": "study", "type": "reference"},
            {"name": "individual", "type": "reference"},
            {"name": "status", "type": "token"},
        ],
    },
    {
        "type": "Observation",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
        ],
        "searchParam": [
            {"name": "subject", "type": "reference"},
            {"name": "code", "type": "token"},
            {"name": "category", "type": "token"},
            {"name": "date", "type": "date"},
        ],
    },
    {
        "type": "Condition",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
        ],
        "searchParam": [
            {"name": "subject", "type": "reference"},
            {"name": "code", "type": "token"},
            {"name": "clinical-status", "type": "token"},
        ],
    },
    {
        "type": "Consent",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"},
            {"code": "create"},
            {"code": "update"},
        ],
        "searchParam": [
            {"name": "patient", "type": "reference"},
            {"name": "status", "type": "token"},
            {"name": "category", "type": "token"},
        ],
    },
]


def generate_capability_statement(
    *,
    server_url: str = "https://mcp.trials.example.org/fhir",
    software_name: str = "National MCP PAI Oncology Trials",
    software_version: str = "1.0.0",
    publisher: str = "National MCP Consortium",
    resource_types: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate a FHIR R4 CapabilityStatement resource.

    Args:
        server_url: The base URL of the FHIR server.
        software_name: Name of the software system.
        software_version: Version of the software system.
        publisher: Organization publishing the statement.
        resource_types: List of resource type capability dicts.
            Defaults to the standard oncology trial resources.

    Returns:
        A complete CapabilityStatement resource dict.
    """
    resources = resource_types or _DEFAULT_RESOURCE_TYPES
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return {
        "resourceType": "CapabilityStatement",
        "id": "national-mcp-pai-oncology",
        "url": f"{server_url}/metadata",
        "version": software_version,
        "name": "NationalMCPPAIOncologyCapabilityStatement",
        "title": ("National MCP PAI Oncology Trials Capability Statement"),
        "status": "active",
        "experimental": False,
        "date": now,
        "publisher": publisher,
        "description": (
            "FHIR R4 capabilities for the National MCP Physical AI "
            "Oncology Clinical Trials platform."
        ),
        "kind": "instance",
        "software": {
            "name": software_name,
            "version": software_version,
        },
        "implementation": {
            "description": software_name,
            "url": server_url,
        },
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "security": {
                    "cors": True,
                    "service": [
                        {
                            "coding": [
                                {
                                    "system": (
                                        "http://terminology.hl7.org/"
                                        "CodeSystem/"
                                        "restful-security-service"
                                    ),
                                    "code": "SMART-on-FHIR",
                                }
                            ],
                        }
                    ],
                    "description": ("OAuth2 via SMART-on-FHIR with system-level scopes."),
                },
                "resource": resources,
                "interaction": [
                    {"code": "transaction"},
                    {"code": "batch"},
                    {"code": "search-system"},
                ],
            }
        ],
    }


class CapabilityParser:
    """Parse a FHIR CapabilityStatement to discover server features.

    Provides query methods to determine which resource types,
    interactions, and search parameters a server supports.
    """

    def __init__(
        self,
        capability_statement: dict[str, Any],
    ) -> None:
        self._statement = capability_statement
        self._rest = self._extract_rest()

    def _extract_rest(self) -> dict[str, Any]:
        """Extract the first server-mode REST entry."""
        for rest in self._statement.get("rest", []):
            if rest.get("mode") == "server":
                return rest
        return {}

    # ---------------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------------

    @property
    def fhir_version(self) -> str:
        """Return the FHIR version advertised by the server."""
        return self._statement.get("fhirVersion", "unknown")

    @property
    def software_name(self) -> str:
        """Return the server software name."""
        sw = self._statement.get("software", {})
        return sw.get("name", "unknown")

    @property
    def status(self) -> str:
        """Return the publication status of the statement."""
        return self._statement.get("status", "unknown")

    @property
    def formats(self) -> list[str]:
        """Return the list of supported content formats."""
        return self._statement.get("format", [])

    # ---------------------------------------------------------------
    # Resource capabilities
    # ---------------------------------------------------------------

    def supported_resource_types(self) -> list[str]:
        """Return all resource types the server supports.

        Returns:
            A sorted list of FHIR resource type names.
        """
        resources = self._rest.get("resource", [])
        return sorted(r.get("type", "") for r in resources)

    def supports_resource(self, resource_type: str) -> bool:
        """Check if the server supports a specific resource type.

        Args:
            resource_type: The FHIR resource type to check.

        Returns:
            ``True`` if the resource type is supported.
        """
        return resource_type in self.supported_resource_types()

    def interactions_for(
        self,
        resource_type: str,
    ) -> list[str]:
        """Return the supported interactions for a resource type.

        Args:
            resource_type: The FHIR resource type.

        Returns:
            A list of interaction codes (e.g. ``["read",
            "search-type"]``).
        """
        for res in self._rest.get("resource", []):
            if res.get("type") == resource_type:
                return [ix.get("code", "") for ix in res.get("interaction", [])]
        return []

    def search_params_for(
        self,
        resource_type: str,
    ) -> list[dict[str, str]]:
        """Return the search parameters for a resource type.

        Args:
            resource_type: The FHIR resource type.

        Returns:
            A list of search parameter dicts with ``name`` and
            ``type`` keys.
        """
        for res in self._rest.get("resource", []):
            if res.get("type") == resource_type:
                return res.get("searchParam", [])
        return []

    def supports_interaction(
        self,
        resource_type: str,
        interaction: str,
    ) -> bool:
        """Check if a specific interaction is supported.

        Args:
            resource_type: The FHIR resource type.
            interaction: The interaction code to check.

        Returns:
            ``True`` if the interaction is supported for that type.
        """
        return interaction in self.interactions_for(resource_type)

    def system_interactions(self) -> list[str]:
        """Return system-level interactions the server supports.

        Returns:
            A list of system interaction codes (e.g.
            ``["transaction", "batch"]``).
        """
        return [ix.get("code", "") for ix in self._rest.get("interaction", [])]

    def has_smart_security(self) -> bool:
        """Check if the server advertises SMART-on-FHIR security.

        Returns:
            ``True`` if SMART-on-FHIR is listed in the security
            services.
        """
        security = self._rest.get("security", {})
        for svc in security.get("service", []):
            for coding in svc.get("coding", []):
                if coding.get("code") == "SMART-on-FHIR":
                    return True
        return False
