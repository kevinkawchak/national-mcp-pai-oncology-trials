"""DICOM sub-client for imaging operations.

Wraps the two DICOM server tools: ``dicom_query`` and ``dicom_retrieve``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .config import ServerName
from .exceptions import raise_for_error
from .models import DICOMQueryResult, DICOMRetrieveResult, DICOMStudy

if TYPE_CHECKING:
    from .client import TrialMCPClient

logger = logging.getLogger("trialmcp.dicom")

_SERVER = ServerName.DICOM


class DICOMClient:
    """Sub-client for the ``trialmcp-dicom`` MCP server.

    Provides typed, async wrappers around DICOM query and retrieve
    operations.  All patient identifiers in results are pseudonymised
    by the server.

    Parameters
    ----------
    parent:
        The :class:`TrialMCPClient` that owns this sub-client.
    """

    def __init__(self, parent: TrialMCPClient) -> None:
        self._client = parent

    # ------------------------------------------------------------------
    # dicom_query
    # ------------------------------------------------------------------

    async def query(
        self,
        *,
        patient_pseudonym: str | None = None,
        study_instance_uid: str | None = None,
        modality: str | None = None,
        study_date_from: str | None = None,
        study_date_to: str | None = None,
        accession_number: str | None = None,
        limit: int = 50,
    ) -> DICOMQueryResult:
        """Query for DICOM studies matching the given criteria.

        At least one filter parameter must be provided.

        Parameters
        ----------
        patient_pseudonym:
            HMAC-SHA256 pseudonymised patient identifier.
        study_instance_uid:
            Specific DICOM Study Instance UID to look up.
        modality:
            Imaging modality filter (e.g. ``"CT"``, ``"MR"``, ``"PT"``).
        study_date_from:
            Earliest study date (ISO 8601 date string).
        study_date_to:
            Latest study date (ISO 8601 date string).
        accession_number:
            Accession number filter.
        limit:
            Maximum number of studies to return.

        Returns
        -------
        DICOMQueryResult:
            Matching DICOM studies.

        Raises
        ------
        InvalidInputError:
            If no filter parameters are provided.
        """
        params: dict[str, Any] = {"limit": limit}
        if patient_pseudonym:
            params["patient_pseudonym"] = patient_pseudonym
        if study_instance_uid:
            params["study_instance_uid"] = study_instance_uid
        if modality:
            params["modality"] = modality
        if study_date_from:
            params["study_date_from"] = study_date_from
        if study_date_to:
            params["study_date_to"] = study_date_to
        if accession_number:
            params["accession_number"] = accession_number

        result = await self._client.call_tool(_SERVER, "dicom_query", params)
        raise_for_error(result)
        return DICOMQueryResult.from_dict(result)

    # ------------------------------------------------------------------
    # dicom_retrieve
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        *,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
        transfer_syntax: str | None = None,
        destination: str | None = None,
    ) -> DICOMRetrieveResult:
        """Retrieve DICOM objects from the imaging archive.

        Parameters
        ----------
        study_instance_uid:
            The Study Instance UID to retrieve.
        series_instance_uid:
            Optional filter to retrieve a specific series.
        sop_instance_uid:
            Optional filter to retrieve a specific SOP instance.
        transfer_syntax:
            Requested DICOM transfer syntax UID.
        destination:
            Optional storage destination path or identifier.

        Returns
        -------
        DICOMRetrieveResult:
            Result including counts and storage path.

        Raises
        ------
        NotFoundError:
            If the study does not exist.
        """
        params: dict[str, Any] = {
            "study_instance_uid": study_instance_uid,
        }
        if series_instance_uid:
            params["series_instance_uid"] = series_instance_uid
        if sop_instance_uid:
            params["sop_instance_uid"] = sop_instance_uid
        if transfer_syntax:
            params["transfer_syntax"] = transfer_syntax
        if destination:
            params["destination"] = destination

        result = await self._client.call_tool(_SERVER, "dicom_retrieve", params)
        raise_for_error(result)
        return DICOMRetrieveResult.from_dict(result)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def query_by_patient(
        self,
        patient_pseudonym: str,
        *,
        modality: str | None = None,
    ) -> list[DICOMStudy]:
        """Query all studies for a pseudonymised patient.

        Parameters
        ----------
        patient_pseudonym:
            The HMAC-SHA256 pseudonymised patient identifier.
        modality:
            Optional modality filter.

        Returns
        -------
        list[DICOMStudy]:
            All matching DICOM studies.
        """
        result = await self.query(
            patient_pseudonym=patient_pseudonym,
            modality=modality,
        )
        return result.studies

    async def retrieve_study(
        self,
        study_instance_uid: str,
    ) -> DICOMRetrieveResult:
        """Retrieve all series and instances for a complete study.

        Parameters
        ----------
        study_instance_uid:
            The Study Instance UID.

        Returns
        -------
        DICOMRetrieveResult:
            Retrieval result with counts and storage location.
        """
        return await self.retrieve(study_instance_uid=study_instance_uid)

    async def query_and_retrieve(
        self,
        *,
        patient_pseudonym: str,
        modality: str | None = None,
    ) -> list[DICOMRetrieveResult]:
        """Query for studies and retrieve all matching ones.

        Combines ``dicom_query`` and ``dicom_retrieve`` into a single
        workflow.

        Parameters
        ----------
        patient_pseudonym:
            The pseudonymised patient identifier.
        modality:
            Optional modality filter.

        Returns
        -------
        list[DICOMRetrieveResult]:
            Retrieval results for each matching study.
        """
        import asyncio

        query_result = await self.query(
            patient_pseudonym=patient_pseudonym,
            modality=modality,
        )

        if not query_result.studies:
            return []

        retrieve_tasks = [
            self.retrieve(study_instance_uid=study.study_instance_uid)
            for study in query_result.studies
        ]
        return list(await asyncio.gather(*retrieve_tasks))

    async def find_study_by_uid(
        self,
        study_instance_uid: str,
    ) -> DICOMStudy | None:
        """Look up a single study by its UID.

        Parameters
        ----------
        study_instance_uid:
            The Study Instance UID.

        Returns
        -------
        DICOMStudy | None:
            The study if found, or ``None``.
        """
        result = await self.query(study_instance_uid=study_instance_uid)
        if result.studies:
            return result.studies[0]
        return None
