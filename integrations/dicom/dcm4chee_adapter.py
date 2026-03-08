"""dcm4chee DICOM archive adapter.

Implements the BaseDicomAdapter interface for dcm4chee-arc
DICOM archive servers using the DICOMweb REST API. Supports
QIDO-RS queries and WADO-RS metadata retrieval via dcm4chee-
specific endpoints.
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
from integrations.dicom.dicomweb import (
    DICOMwebClient,
    build_qido_url,
    build_wado_metadata_url,
)
from integrations.dicom.modality_filter import ModalityFilter
from integrations.dicom.safety import SafetyValidator

logger = logging.getLogger(__name__)

# dcm4chee default AE title path segment
_DEFAULT_AE_TITLE = "DCM4CHEE"


class Dcm4cheeAdapter(BaseDicomAdapter):
    """DICOM adapter for dcm4chee-arc servers.

    Uses DICOMweb (QIDO-RS, WADO-RS) endpoints exposed by
    dcm4chee-arc. The adapter constructs dcm4chee-specific
    URL paths that include the AE title segment.

    Attributes:
        adapter_name: Identifier for this adapter.
        base_url: Root URL of the dcm4chee-arc DICOMweb API.
        ae_title: Application Entity title for URL routing.
    """

    adapter_name: str = "dcm4chee"

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        *,
        ae_title: str = _DEFAULT_AE_TITLE,
        username: str | None = None,
        password: str | None = None,
        modality_filter: ModalityFilter | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the dcm4chee adapter.

        Args:
            base_url: Root URL of the dcm4chee-arc server.
            ae_title: DICOM Application Entity title used in
                the DICOMweb URL path.
            username: Optional HTTP basic auth username.
            password: Optional HTTP basic auth password.
            modality_filter: Optional role-based modality filter.
            timeout: HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.ae_title = ae_title
        self._username = username
        self._password = password
        self._modality_filter = modality_filter
        self._timeout = timeout
        self._safety = SafetyValidator()
        self._dicomweb = DICOMwebClient(
            base_url=self._service_url,
            username=username,
            password=password,
            timeout=timeout,
        )

    @property
    def _service_url(self) -> str:
        """Build the dcm4chee DICOMweb service root URL."""
        return f"{self.base_url}/dcm4chee-arc/aets/{self.ae_title}/rs"

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
        """Query dcm4chee via QIDO-RS at the specified level.

        Args:
            query_level: STUDY, SERIES, or IMAGE level.
            filters: DICOM attribute filters as keyword-value
                pairs.
            limit: Maximum number of results.
            offset: Pagination offset.

        Returns:
            List of matching DICOM entity metadata dicts.

        Raises:
            ConnectionError: If the server is unreachable.
        """
        level_map = {
            QueryLevel.STUDY: "studies",
            QueryLevel.SERIES: "series",
            QueryLevel.IMAGE: "instances",
        }
        resource = level_map.get(query_level)
        if resource is None:
            raise ValueError(f"Unsupported query level: {query_level!r}")

        study_uid = filters.pop("StudyInstanceUID", None)

        url = build_qido_url(
            base_url=self._service_url,
            resource=resource,
            study_instance_uid=study_uid,
            params={
                **filters,
                "limit": str(limit),
                "offset": str(offset),
            },
        )

        results = self._get_json(url)
        return self._sanitize_results(results)

    def retrieve_metadata(
        self,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve metadata via WADO-RS from dcm4chee.

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
        url = build_wado_metadata_url(
            base_url=self._service_url,
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            sop_instance_uid=sop_instance_uid,
        )

        try:
            result = self._get_json(url)
        except ConnectionError:
            raise
        except KeyError:
            raise

        if isinstance(result, list) and result:
            metadata = result[0]
        elif isinstance(result, dict):
            metadata = result
        else:
            raise KeyError(f"No metadata found for study {study_instance_uid!r}")

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
        """Check dcm4chee server connectivity.

        Uses the dcm4chee-arc monitoring endpoint.

        Returns:
            True if the server responds successfully.
        """
        url = f"{self.base_url}/dcm4chee-arc/ctrl/status"
        try:
            self._get_json(url)
            return True
        except (ConnectionError, urllib.error.URLError):
            return False

    # ---------------------------------------------------------------
    # HTTP helpers
    # ---------------------------------------------------------------

    def _get_json(self, url: str) -> Any:
        """Perform a GET request and parse JSON response.

        Args:
            url: Full URL to request.

        Returns:
            Parsed JSON response.

        Raises:
            ConnectionError: On network or HTTP errors.
            KeyError: On 404 responses.
        """
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/dicom+json")
        if self._username and self._password:
            import base64

            credentials = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
            req.add_header("Authorization", f"Basic {credentials}")

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise KeyError(f"Resource not found: {url}") from exc
            raise ConnectionError(f"dcm4chee request failed (HTTP {exc.code}): {exc}") from exc
        except urllib.error.URLError as exc:
            raise ConnectionError(f"dcm4chee request failed: {exc}") from exc

    def _sanitize_results(
        self,
        results: Any,
    ) -> list[dict[str, Any]]:
        """Strip pixel data from a list of result dicts."""
        if not isinstance(results, list):
            return []
        return [self._safety.strip_pixel_fields(r) for r in results if isinstance(r, dict)]
