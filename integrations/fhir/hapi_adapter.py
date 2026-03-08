"""HAPI FHIR server adapter using stdlib HTTP.

Connects to a HAPI FHIR R4 server over HTTP/HTTPS using only
``urllib`` (no external dependencies). Provides resource read, search,
patient lookup, and study status operations with graceful error
handling for the National MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from integrations.fhir.base_adapter import BaseFHIRAdapter

logger = logging.getLogger(__name__)


class HAPIFHIRAdapter(BaseFHIRAdapter):
    """Adapter for a HAPI FHIR R4 server.

    Uses :mod:`urllib` for all HTTP communication so the adapter has
    zero third-party runtime dependencies.

    Args:
        base_url: Root URL of the HAPI FHIR server
            (e.g. ``"http://hapi.fhir.org/baseR4"``).
        timeout: HTTP request timeout in seconds.
        default_headers: Extra headers sent with every request.
    """

    def __init__(
        self,
        base_url: str = "http://hapi.fhir.org/baseR4",
        timeout: int = 30,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._headers: dict[str, str] = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }
        if default_headers:
            self._headers.update(default_headers)

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _build_url(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> str:
        """Construct a full URL from a relative path and query params."""
        url = f"{self._base_url}/{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        return url

    def _request(
        self,
        url: str,
        method: str = "GET",
        body: bytes | None = None,
    ) -> dict[str, Any] | None:
        """Execute an HTTP request and return parsed JSON.

        Returns ``None`` on 404. Raises on other HTTP errors after
        logging the details.
        """
        req = urllib.request.Request(
            url,
            data=body,
            headers=self._headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                logger.debug("Resource not found: %s", url)
                return None
            logger.error(
                "HAPI FHIR HTTP %s error for %s: %s",
                exc.code,
                url,
                exc.reason,
            )
            raise
        except urllib.error.URLError as exc:
            logger.error(
                "HAPI FHIR connection error for %s: %s",
                url,
                exc.reason,
            )
            raise
        except (json.JSONDecodeError, OSError) as exc:
            logger.error(
                "HAPI FHIR response parse error for %s: %s",
                url,
                exc,
            )
            raise

    # ------------------------------------------------------------------
    # BaseFHIRAdapter interface
    # ------------------------------------------------------------------

    def read(
        self,
        resource_type: str,
        resource_id: str,
    ) -> dict[str, Any] | None:
        """Read a single FHIR resource from the HAPI server."""
        url = self._build_url(f"{resource_type}/{resource_id}")
        return self._request(url)

    def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Search for FHIR resources on the HAPI server."""
        search_params = dict(params or {})
        search_params["_count"] = str(limit)
        url = self._build_url(resource_type, search_params)
        result = self._request(url)
        if result is None:
            return {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 0,
                "entry": [],
            }
        return result

    def patient_lookup(
        self,
        pseudonym: str,
    ) -> dict[str, Any] | None:
        """Look up a patient by pseudonymized ID."""
        return self.read("Patient", pseudonym)

    def study_status(
        self,
        study_id: str,
    ) -> dict[str, Any] | None:
        """Get the current status of a ResearchStudy."""
        return self.read("ResearchStudy", study_id)

    def capability_statement(self) -> dict[str, Any]:
        """Fetch the CapabilityStatement from the HAPI server."""
        url = self._build_url("metadata")
        result = self._request(url)
        if result is not None:
            return result
        return super().capability_statement()
