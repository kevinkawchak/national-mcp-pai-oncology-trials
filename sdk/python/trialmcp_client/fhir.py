"""FHIR sub-client for clinical data operations.

Wraps the four FHIR server tools: ``fhir_read``, ``fhir_search``,
``fhir_patient_lookup``, and ``fhir_study_status``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .config import ServerName
from .exceptions import raise_for_error
from .models import FHIRResource, FHIRSearchResult, StudyStatusResult

if TYPE_CHECKING:
    from .client import TrialMCPClient

logger = logging.getLogger("trialmcp.fhir")

_SERVER = ServerName.FHIR


class FHIRClient:
    """Sub-client for the ``trialmcp-fhir`` MCP server.

    All returned patient data is de-identified by the server.  The SDK
    never stores or logs raw patient identifiers.

    Parameters
    ----------
    parent:
        The :class:`TrialMCPClient` that owns this sub-client.
    """

    def __init__(self, parent: TrialMCPClient) -> None:
        self._client = parent

    # ------------------------------------------------------------------
    # fhir_read
    # ------------------------------------------------------------------

    async def read(
        self,
        *,
        resource_type: str,
        resource_id: str,
        version: str | None = None,
    ) -> FHIRResource:
        """Read a single FHIR resource by type and ID.

        Parameters
        ----------
        resource_type:
            FHIR resource type (e.g. ``"Patient"``, ``"ResearchStudy"``).
        resource_id:
            The pseudonymised resource identifier.
        version:
            Optional specific version to retrieve.

        Returns
        -------
        FHIRResource:
            The de-identified FHIR resource.

        Raises
        ------
        NotFoundError:
            If the resource does not exist.
        InvalidInputError:
            If the resource type or ID is invalid.
        """
        params: dict[str, Any] = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }
        if version:
            params["version"] = version

        result = await self._client.call_tool(_SERVER, "fhir_read", params)
        raise_for_error(result)
        return FHIRResource.from_dict(result)

    # ------------------------------------------------------------------
    # fhir_search
    # ------------------------------------------------------------------

    async def search(
        self,
        *,
        resource_type: str,
        query_params: dict[str, str] | None = None,
        max_results: int = 100,
        page_token: str | None = None,
    ) -> FHIRSearchResult:
        """Search for FHIR resources matching the given criteria.

        Parameters
        ----------
        resource_type:
            FHIR resource type to search.
        query_params:
            Search parameters as key-value pairs.
        max_results:
            Maximum number of results to return.
        page_token:
            Continuation token for paginated results.

        Returns
        -------
        FHIRSearchResult:
            The matching resources and pagination metadata.
        """
        params: dict[str, Any] = {
            "resource_type": resource_type,
            "max_results": max_results,
        }
        if query_params:
            params["query_params"] = query_params
        if page_token:
            params["page_token"] = page_token

        result = await self._client.call_tool(_SERVER, "fhir_search", params)
        raise_for_error(result)
        return FHIRSearchResult.from_dict(result)

    # ------------------------------------------------------------------
    # fhir_patient_lookup
    # ------------------------------------------------------------------

    async def patient_lookup(
        self,
        *,
        patient_pseudonym: str,
        include_observations: bool = False,
        include_conditions: bool = False,
    ) -> FHIRResource:
        """Look up a de-identified patient by pseudonymised identifier.

        Parameters
        ----------
        patient_pseudonym:
            The HMAC-SHA256 pseudonymised patient identifier.
        include_observations:
            Whether to include clinical observations in the bundle.
        include_conditions:
            Whether to include diagnosed conditions.

        Returns
        -------
        FHIRResource:
            The de-identified patient resource (possibly a Bundle).
        """
        params: dict[str, Any] = {
            "patient_pseudonym": patient_pseudonym,
        }
        if include_observations:
            params["include_observations"] = True
        if include_conditions:
            params["include_conditions"] = True

        result = await self._client.call_tool(_SERVER, "fhir_patient_lookup", params)
        raise_for_error(result)
        return FHIRResource.from_dict(result)

    # ------------------------------------------------------------------
    # fhir_study_status
    # ------------------------------------------------------------------

    async def study_status(
        self,
        *,
        study_id: str,
    ) -> StudyStatusResult:
        """Retrieve the current status of a clinical study.

        Parameters
        ----------
        study_id:
            The clinical study identifier (e.g. NCT number).

        Returns
        -------
        StudyStatusResult:
            Current study status, enrolment, and site information.
        """
        result = await self._client.call_tool(
            _SERVER,
            "fhir_study_status",
            {"study_id": study_id},
        )
        raise_for_error(result)
        return StudyStatusResult.from_dict(result)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def search_all(
        self,
        *,
        resource_type: str,
        query_params: dict[str, str] | None = None,
        max_total: int = 1000,
    ) -> list[FHIRResource]:
        """Auto-paginate through all matching FHIR resources.

        Parameters
        ----------
        resource_type:
            FHIR resource type to search.
        query_params:
            Search parameters.
        max_total:
            Safety limit on total resources fetched.

        Returns
        -------
        list[FHIRResource]:
            All matching resources up to *max_total*.
        """
        all_resources: list[FHIRResource] = []
        page_token: str | None = None

        while len(all_resources) < max_total:
            batch_size = min(100, max_total - len(all_resources))
            result = await self.search(
                resource_type=resource_type,
                query_params=query_params,
                max_results=batch_size,
                page_token=page_token,
            )
            all_resources.extend(result.resources)

            if not result.next_page_token:
                break
            page_token = result.next_page_token

        return all_resources

    async def read_research_study(self, study_id: str) -> FHIRResource:
        """Convenience wrapper to read a ResearchStudy resource.

        Parameters
        ----------
        study_id:
            The study resource identifier.

        Returns
        -------
        FHIRResource:
            The ResearchStudy FHIR resource.
        """
        return await self.read(resource_type="ResearchStudy", resource_id=study_id)

    async def search_research_subjects(
        self,
        *,
        study_id: str,
        status: str | None = None,
    ) -> FHIRSearchResult:
        """Search for research subjects enrolled in a study.

        Parameters
        ----------
        study_id:
            The study identifier to filter by.
        status:
            Optional subject status filter.

        Returns
        -------
        FHIRSearchResult:
            Matching research subject resources.
        """
        query: dict[str, str] = {"study": study_id}
        if status:
            query["status"] = status
        return await self.search(
            resource_type="ResearchSubject",
            query_params=query,
        )
