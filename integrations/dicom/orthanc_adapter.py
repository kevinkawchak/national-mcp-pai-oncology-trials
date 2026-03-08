"""Orthanc DICOM server adapter.

Implements the BaseDicomAdapter interface for Orthanc DICOM
servers using the Orthanc REST API via urllib. Supports study
and series queries, metadata retrieval, and patient search
with configurable base URL.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from integrations.dicom.base_adapter import (
    BaseDicomAdapter,
    QueryLevel,
)
from integrations.dicom.modality_filter import ModalityFilter
from integrations.dicom.safety import SafetyValidator

logger = logging.getLogger(__name__)


class OrthancAdapter(BaseDicomAdapter):
    """DICOM adapter for Orthanc servers.

    Communicates with an Orthanc server via its REST API using
    only stdlib ``urllib``. All responses are validated through
    the safety layer to ensure no pixel data is returned.

    Attributes:
        adapter_name: Identifier for this adapter.
        base_url: Root URL of the Orthanc REST API.
    """

    adapter_name: str = "orthanc"

    def __init__(
        self,
        base_url: str = "http://localhost:8042",
        *,
        username: str | None = None,
        password: str | None = None,
        modality_filter: ModalityFilter | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the Orthanc adapter.

        Args:
            base_url: Root URL of the Orthanc server
                (e.g., ``http://localhost:8042``).
            username: Optional HTTP basic auth username.
            password: Optional HTTP basic auth password.
            modality_filter: Optional role-based modality filter.
            timeout: HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._modality_filter = modality_filter
        self._timeout = timeout
        self._safety = SafetyValidator()

    # ---------------------------------------------------------------
    # Public interface
    # ---------------------------------------------------------------

    def query(
        self,
        query_level: QueryLevel,
        filters: dict[str, Any],
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query the Orthanc server at the specified level.

        Args:
            query_level: STUDY, SERIES, or IMAGE level.
            filters: DICOM attribute filters.
            limit: Maximum number of results.
            offset: Pagination offset.

        Returns:
            List of matching DICOM entity metadata dicts.

        Raises:
            ConnectionError: If the server is unreachable.
            ValueError: If the query level is unsupported.
        """
        if query_level == QueryLevel.STUDY:
            return self._query_studies(filters, limit, offset)
        if query_level == QueryLevel.SERIES:
            return self._query_series(filters, limit, offset)
        if query_level == QueryLevel.IMAGE:
            return self._query_instances(filters, limit, offset)
        raise ValueError(f"Unsupported query level: {query_level!r}")

    def retrieve_metadata(
        self,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve metadata from Orthanc for a DICOM entity.

        Args:
            study_instance_uid: Study Instance UID.
            series_instance_uid: Optional Series Instance UID.
            sop_instance_uid: Optional SOP Instance UID.

        Returns:
            Metadata dictionary with pixel data stripped.

        Raises:
            ConnectionError: If the server is unreachable.
            KeyError: If the entity is not found.
        """
        if sop_instance_uid:
            orthanc_id = self._lookup_instance(sop_instance_uid)
            metadata = self._get_json(f"/instances/{orthanc_id}/simplified-tags")
        elif series_instance_uid:
            orthanc_id = self._lookup_series(series_instance_uid)
            metadata = self._get_json(f"/series/{orthanc_id}")
        else:
            orthanc_id = self._lookup_study(study_instance_uid)
            metadata = self._get_json(f"/studies/{orthanc_id}")

        self._safety.validate_metadata_response(metadata)
        return metadata

    def validate_modality(
        self,
        modality: str,
        role: str | None = None,
    ) -> bool:
        """Validate modality access permission.

        Args:
            modality: DICOM modality code.
            role: Optional role for RBAC check.

        Returns:
            True if the modality is permitted.
        """
        if modality not in self.supported_modalities:
            return False
        if role and self._modality_filter:
            return self._modality_filter.is_permitted(role, modality)
        return True

    def ping(self) -> bool:
        """Check Orthanc server connectivity.

        Returns:
            True if the server responds to /system.
        """
        try:
            self._get_json("/system")
            return True
        except (ConnectionError, urllib.error.URLError):
            return False

    def search_patients(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """Search patients by name or ID pattern.

        Uses the Orthanc ``/tools/find`` endpoint.

        Args:
            query: Patient name or ID search pattern.
                Supports ``*`` wildcards.

        Returns:
            List of matching patient metadata dicts.
        """
        payload = {
            "Level": "Patient",
            "Query": {"PatientName": query},
            "Expand": True,
        }
        results = self._post_json("/tools/find", payload)
        if not isinstance(results, list):
            return []
        return [self._safety.strip_pixel_fields(r) for r in results]

    # ---------------------------------------------------------------
    # Private query helpers
    # ---------------------------------------------------------------

    def _query_studies(
        self,
        filters: dict[str, Any],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Query studies via Orthanc /tools/find."""
        payload = {
            "Level": "Study",
            "Query": filters,
            "Expand": True,
            "Limit": limit,
            "Since": offset,
        }
        results = self._post_json("/tools/find", payload)
        return self._sanitize_results(results)

    def _query_series(
        self,
        filters: dict[str, Any],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Query series via Orthanc /tools/find."""
        payload = {
            "Level": "Series",
            "Query": filters,
            "Expand": True,
            "Limit": limit,
            "Since": offset,
        }
        results = self._post_json("/tools/find", payload)
        return self._sanitize_results(results)

    def _query_instances(
        self,
        filters: dict[str, Any],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Query instances via Orthanc /tools/find."""
        payload = {
            "Level": "Instance",
            "Query": filters,
            "Expand": True,
            "Limit": limit,
            "Since": offset,
        }
        results = self._post_json("/tools/find", payload)
        return self._sanitize_results(results)

    # ---------------------------------------------------------------
    # Lookup helpers
    # ---------------------------------------------------------------

    def _lookup_study(self, uid: str) -> str:
        """Resolve Study Instance UID to Orthanc ID."""
        return self._lookup("study", uid)

    def _lookup_series(self, uid: str) -> str:
        """Resolve Series Instance UID to Orthanc ID."""
        return self._lookup("series", uid)

    def _lookup_instance(self, uid: str) -> str:
        """Resolve SOP Instance UID to Orthanc ID."""
        return self._lookup("instance", uid)

    def _lookup(self, level: str, uid: str) -> str:
        """Resolve a DICOM UID to an Orthanc internal ID.

        Args:
            level: One of study, series, instance.
            uid: The DICOM UID to look up.

        Returns:
            The Orthanc internal identifier string.

        Raises:
            KeyError: If the UID cannot be resolved.
        """
        payload = {
            "Level": level.capitalize(),
            "Query": {
                f"{level.capitalize()}InstanceUID": uid,
            },
        }
        try:
            results = self._post_json("/tools/find", payload)
        except ConnectionError:
            raise

        if not results:
            raise KeyError(f"{level.capitalize()} UID {uid!r} not found in Orthanc")
        return results[0] if isinstance(results[0], str) else results[0].get("ID", "")

    # ---------------------------------------------------------------
    # HTTP helpers
    # ---------------------------------------------------------------

    def _build_request(
        self,
        path: str,
        data: bytes | None = None,
        method: str = "GET",
    ) -> urllib.request.Request:
        """Build an urllib Request for the Orthanc API.

        Args:
            path: API path (e.g., ``/studies``).
            data: Optional request body bytes.
            method: HTTP method.

        Returns:
            Configured urllib Request object.
        """
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if self._username and self._password:
            import base64

            credentials = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
            req.add_header("Authorization", f"Basic {credentials}")
        return req

    def _get_json(self, path: str) -> Any:
        """Perform a GET request and parse JSON response.

        Args:
            path: API endpoint path.

        Returns:
            Parsed JSON response.

        Raises:
            ConnectionError: On network or HTTP errors.
        """
        req = self._build_request(path)
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise ConnectionError(f"Orthanc request failed: {exc}") from exc

    def _post_json(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        """Perform a POST request with JSON body.

        Args:
            path: API endpoint path.
            payload: Request body as a dictionary.

        Returns:
            Parsed JSON response.

        Raises:
            ConnectionError: On network or HTTP errors.
        """
        data = json.dumps(payload).encode()
        req = self._build_request(path, data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise ConnectionError(f"Orthanc POST failed: {exc}") from exc

    def _sanitize_results(
        self,
        results: Any,
    ) -> list[dict[str, Any]]:
        """Strip pixel data from a list of result dicts."""
        if not isinstance(results, list):
            return []
        return [self._safety.strip_pixel_fields(r) for r in results if isinstance(r, dict)]
