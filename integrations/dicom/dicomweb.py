"""DICOMweb protocol support for QIDO-RS, WADO-RS, and STOW-RS.

Provides URL construction, request building, and response parsing
utilities for the DICOMweb standard (DICOM PS3.18). Handles
multipart MIME responses for WADO-RS bulk data retrieval.
"""

from __future__ import annotations

import io
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# DICOM media types
# -------------------------------------------------------------------

MEDIA_TYPE_DICOM_JSON = "application/dicom+json"
MEDIA_TYPE_MULTIPART_RELATED = "multipart/related"
MEDIA_TYPE_OCTET_STREAM = "application/octet-stream"


# -------------------------------------------------------------------
# URL builders
# -------------------------------------------------------------------


def build_qido_url(
    base_url: str,
    resource: str,
    study_instance_uid: str | None = None,
    series_instance_uid: str | None = None,
    params: dict[str, str] | None = None,
) -> str:
    """Build a QIDO-RS query URL.

    Constructs a URL conforming to DICOM PS3.18 Section 10.6
    for Query based on ID for DICOM Objects (QIDO-RS).

    Args:
        base_url: DICOMweb service root URL.
        resource: Resource type: ``studies``, ``series``,
            or ``instances``.
        study_instance_uid: Optional study UID for scoping
            series or instance queries.
        series_instance_uid: Optional series UID for scoping
            instance queries.
        params: Additional query parameters (filters, limit,
            offset, includefield, etc.).

    Returns:
        Fully-constructed QIDO-RS URL string.
    """
    parts = [base_url.rstrip("/")]

    if study_instance_uid:
        parts.append(f"studies/{study_instance_uid}")
        if series_instance_uid and resource == "instances":
            parts.append(f"series/{series_instance_uid}")
        if resource != "studies":
            parts.append(resource)
    else:
        parts.append(resource)

    url = "/".join(parts)

    if params:
        query_string = urllib.parse.urlencode(params, doseq=True)
        url = f"{url}?{query_string}"

    return url


def build_wado_metadata_url(
    base_url: str,
    study_instance_uid: str,
    series_instance_uid: str | None = None,
    sop_instance_uid: str | None = None,
) -> str:
    """Build a WADO-RS metadata retrieval URL.

    Constructs a URL for retrieving DICOM JSON metadata via
    WADO-RS (PS3.18 Section 10.4). Appends ``/metadata`` to
    ensure only metadata is returned, not bulk data.

    Args:
        base_url: DICOMweb service root URL.
        study_instance_uid: Study Instance UID.
        series_instance_uid: Optional Series Instance UID.
        sop_instance_uid: Optional SOP Instance UID.

    Returns:
        WADO-RS metadata URL string.
    """
    parts = [
        base_url.rstrip("/"),
        f"studies/{study_instance_uid}",
    ]

    if series_instance_uid:
        parts.append(f"series/{series_instance_uid}")

    if sop_instance_uid:
        parts.append(f"instances/{sop_instance_uid}")

    parts.append("metadata")
    return "/".join(parts)


def build_stow_url(
    base_url: str,
    study_instance_uid: str | None = None,
) -> str:
    """Build a STOW-RS store URL.

    Constructs a URL for storing DICOM objects via STOW-RS
    (PS3.18 Section 10.5).

    Args:
        base_url: DICOMweb service root URL.
        study_instance_uid: Optional study UID to scope the
            store operation.

    Returns:
        STOW-RS URL string.
    """
    parts = [base_url.rstrip("/"), "studies"]
    if study_instance_uid:
        parts[-1] = f"studies/{study_instance_uid}"
    return "/".join(parts)


# -------------------------------------------------------------------
# Response parsing
# -------------------------------------------------------------------


def parse_qido_response(
    response_body: bytes,
) -> list[dict[str, Any]]:
    """Parse a QIDO-RS JSON response body.

    Args:
        response_body: Raw response bytes in
            ``application/dicom+json`` format.

    Returns:
        List of DICOM JSON dataset dictionaries.

    Raises:
        ValueError: If the response is not valid JSON or
            not a JSON array.
    """
    try:
        data = json.loads(response_body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid QIDO-RS response: {exc}") from exc

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise ValueError("QIDO-RS response must be a JSON array or object")


def parse_multipart_response(
    response_body: bytes,
    boundary: str,
) -> list[bytes]:
    """Parse a multipart/related WADO-RS response.

    Splits a multipart MIME response into individual parts,
    stripping MIME headers from each part. Used for WADO-RS
    bulk data retrieval responses.

    Args:
        response_body: Raw multipart response body.
        boundary: MIME boundary string (without leading
            dashes).

    Returns:
        List of part bodies as bytes.
    """
    delimiter = f"--{boundary}".encode("ascii")

    parts: list[bytes] = []
    raw_parts = response_body.split(delimiter)

    for raw_part in raw_parts:
        stripped = raw_part.strip()
        if not stripped or stripped == b"--":
            continue
        if stripped.endswith(b"--"):
            stripped = stripped[:-2].strip()
        if not stripped:
            continue

        # Separate headers from body at double CRLF
        header_end = stripped.find(b"\r\n\r\n")
        if header_end == -1:
            header_end = stripped.find(b"\n\n")
            if header_end == -1:
                parts.append(stripped)
                continue
            body = stripped[header_end + 2 :]
        else:
            body = stripped[header_end + 4 :]

        if body:
            parts.append(body)

    return parts


def extract_boundary(content_type: str) -> str:
    """Extract the boundary parameter from a Content-Type.

    Args:
        content_type: Full Content-Type header value.

    Returns:
        The boundary string.

    Raises:
        ValueError: If no boundary parameter is found.
    """
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("boundary="):
            boundary = part.split("=", 1)[1].strip()
            return boundary.strip('"')
    raise ValueError(f"No boundary in Content-Type: {content_type!r}")


# -------------------------------------------------------------------
# DICOMweb client
# -------------------------------------------------------------------


class DICOMwebClient:
    """Lightweight DICOMweb HTTP client using urllib.

    Provides methods for QIDO-RS queries, WADO-RS metadata
    retrieval, and STOW-RS store operations.

    Attributes:
        base_url: DICOMweb service root URL.
    """

    def __init__(
        self,
        base_url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the DICOMweb client.

        Args:
            base_url: DICOMweb service root URL.
            username: Optional HTTP basic auth username.
            password: Optional HTTP basic auth password.
            timeout: HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout

    def qido_query(
        self,
        resource: str,
        params: dict[str, str] | None = None,
        study_instance_uid: str | None = None,
        series_instance_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a QIDO-RS query.

        Args:
            resource: ``studies``, ``series``, or
                ``instances``.
            params: Query filter parameters.
            study_instance_uid: Optional study scope.
            series_instance_uid: Optional series scope.

        Returns:
            List of matching DICOM JSON datasets.
        """
        url = build_qido_url(
            self.base_url,
            resource,
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            params=params,
        )
        body = self._get(url, accept=MEDIA_TYPE_DICOM_JSON)
        return parse_qido_response(body)

    def wado_metadata(
        self,
        study_instance_uid: str,
        series_instance_uid: str | None = None,
        sop_instance_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve DICOM JSON metadata via WADO-RS.

        Args:
            study_instance_uid: Study Instance UID.
            series_instance_uid: Optional Series Instance UID.
            sop_instance_uid: Optional SOP Instance UID.

        Returns:
            List of DICOM JSON metadata datasets.
        """
        url = build_wado_metadata_url(
            self.base_url,
            study_instance_uid,
            series_instance_uid=series_instance_uid,
            sop_instance_uid=sop_instance_uid,
        )
        body = self._get(url, accept=MEDIA_TYPE_DICOM_JSON)
        return parse_qido_response(body)

    def stow_store(
        self,
        dicom_data: bytes,
        study_instance_uid: str | None = None,
    ) -> dict[str, Any]:
        """Store a DICOM object via STOW-RS.

        Args:
            dicom_data: Raw DICOM Part-10 file bytes.
            study_instance_uid: Optional study UID to scope
                the store operation.

        Returns:
            STOW-RS response as a dictionary.
        """
        url = build_stow_url(
            self.base_url,
            study_instance_uid=study_instance_uid,
        )
        boundary = "----DICOMwebBoundary"
        body = self._build_multipart_body(dicom_data, boundary)
        content_type = (
            f'{MEDIA_TYPE_MULTIPART_RELATED}; type="application/dicom"; boundary={boundary}'
        )

        resp_body = self._post(
            url,
            body,
            content_type=content_type,
            accept=MEDIA_TYPE_DICOM_JSON,
        )
        try:
            return json.loads(resp_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"status": "stored", "raw": len(body)}

    # ---------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------

    def _build_auth_header(self) -> str | None:
        """Build HTTP Basic Authorization header value."""
        if not self._username or not self._password:
            return None
        import base64

        credentials = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
        return f"Basic {credentials}"

    def _get(
        self,
        url: str,
        accept: str = MEDIA_TYPE_DICOM_JSON,
    ) -> bytes:
        """Perform an HTTP GET request.

        Args:
            url: Full URL to request.
            accept: Accept header media type.

        Returns:
            Response body as bytes.

        Raises:
            ConnectionError: On network or HTTP errors.
        """
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", accept)
        auth = self._build_auth_header()
        if auth:
            req.add_header("Authorization", auth)

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return resp.read()
        except urllib.error.URLError as exc:
            raise ConnectionError(f"DICOMweb GET failed: {exc}") from exc

    def _post(
        self,
        url: str,
        body: bytes,
        content_type: str,
        accept: str = MEDIA_TYPE_DICOM_JSON,
    ) -> bytes:
        """Perform an HTTP POST request.

        Args:
            url: Full URL to post to.
            body: Request body bytes.
            content_type: Content-Type header value.
            accept: Accept header media type.

        Returns:
            Response body as bytes.

        Raises:
            ConnectionError: On network or HTTP errors.
        """
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", content_type)
        req.add_header("Accept", accept)
        auth = self._build_auth_header()
        if auth:
            req.add_header("Authorization", auth)

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return resp.read()
        except urllib.error.URLError as exc:
            raise ConnectionError(f"DICOMweb POST failed: {exc}") from exc

    @staticmethod
    def _build_multipart_body(
        dicom_data: bytes,
        boundary: str,
    ) -> bytes:
        """Build a multipart/related request body for STOW-RS.

        Args:
            dicom_data: Raw DICOM Part-10 bytes.
            boundary: MIME boundary string.

        Returns:
            Multipart body as bytes.
        """
        buf = io.BytesIO()
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(b"Content-Type: application/dicom\r\n")
        buf.write(b"\r\n")
        buf.write(dicom_data)
        buf.write(b"\r\n")
        buf.write(f"--{boundary}--\r\n".encode())
        return buf.getvalue()
