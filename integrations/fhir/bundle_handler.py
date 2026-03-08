"""FHIR Bundle handling for transaction, batch, and search results.

Provides utilities to parse, create, and validate FHIR R4 Bundle
resources including transaction bundles, batch bundles, and search
result bundles with proper ``fullUrl``, ``request``, and ``response``
fields.
"""

from __future__ import annotations

import uuid
from typing import Any

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

BUNDLE_TYPES = frozenset(
    {
        "document",
        "message",
        "transaction",
        "transaction-response",
        "batch",
        "batch-response",
        "history",
        "searchset",
        "collection",
    }
)

_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "DELETE", "PATCH"})


# -----------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------


class BundleValidationError(ValueError):
    """Raised when a FHIR Bundle fails structural validation."""


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Validate a FHIR Bundle for structural correctness.

    Checks resource type, bundle type, entry structure, and
    request/response fields appropriate to the bundle type.

    Args:
        bundle: A FHIR Bundle resource dict.

    Returns:
        A list of validation error messages. An empty list means
        the bundle is valid.
    """
    errors: list[str] = []

    if bundle.get("resourceType") != "Bundle":
        errors.append(f"resourceType must be 'Bundle', got '{bundle.get('resourceType')}'")

    bundle_type = bundle.get("type")
    if bundle_type not in BUNDLE_TYPES:
        errors.append(
            f"Invalid bundle type: '{bundle_type}'. Must be one of {sorted(BUNDLE_TYPES)}"
        )

    entries = bundle.get("entry", [])
    for idx, entry in enumerate(entries):
        prefix = f"entry[{idx}]"

        # Every entry should have a resource or a request
        if "resource" not in entry and "request" not in entry:
            errors.append(f"{prefix}: must contain 'resource' or 'request'")

        # Transaction and batch entries require request
        if bundle_type in ("transaction", "batch"):
            if "request" not in entry:
                errors.append(f"{prefix}: '{bundle_type}' entries must include 'request'")
            else:
                req = entry["request"]
                method = req.get("method")
                if method not in _HTTP_METHODS:
                    errors.append(f"{prefix}.request.method: invalid method '{method}'")
                if not req.get("url"):
                    errors.append(f"{prefix}.request.url: required")

        # Response entries require response
        if bundle_type in (
            "transaction-response",
            "batch-response",
        ):
            if "response" not in entry:
                errors.append(f"{prefix}: response entries must include 'response'")
            elif not entry["response"].get("status"):
                errors.append(f"{prefix}.response.status: required")

    return errors


# -----------------------------------------------------------------------
# Bundle entry builders
# -----------------------------------------------------------------------


def _generate_full_url(
    resource: dict[str, Any] | None = None,
) -> str:
    """Generate a fullUrl for a bundle entry.

    Uses the resource type and ID if available, otherwise falls back
    to a URN UUID.

    Args:
        resource: Optional FHIR resource dict.

    Returns:
        A fullUrl string.
    """
    if resource:
        rtype = resource.get("resourceType", "")
        rid = resource.get("id", "")
        if rtype and rid:
            return f"urn:uuid:{rtype}/{rid}"
    return f"urn:uuid:{uuid.uuid4()}"


def make_entry(
    resource: dict[str, Any],
    *,
    method: str | None = None,
    url: str | None = None,
    full_url: str | None = None,
    if_match: str | None = None,
) -> dict[str, Any]:
    """Create a single Bundle entry dict.

    Args:
        resource: The FHIR resource for this entry.
        method: HTTP method for transaction/batch entries.
        url: Request URL for transaction/batch entries.
        full_url: Override for the fullUrl field.
        if_match: Optional If-Match header value for conditional
            updates.

    Returns:
        A properly structured Bundle entry dict.
    """
    entry: dict[str, Any] = {
        "fullUrl": full_url or _generate_full_url(resource),
        "resource": resource,
    }
    if method and url:
        request: dict[str, str] = {
            "method": method,
            "url": url,
        }
        if if_match:
            request["ifMatch"] = if_match
        entry["request"] = request
    return entry


def make_response_entry(
    status: str,
    *,
    location: str | None = None,
    etag: str | None = None,
    last_modified: str | None = None,
    resource: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a response entry for transaction/batch responses.

    Args:
        status: HTTP status code as a string (e.g. ``"201 Created"``).
        location: Optional Location header value.
        etag: Optional ETag header value.
        last_modified: Optional Last-Modified header value.
        resource: Optional resource returned in the response.

    Returns:
        A Bundle response entry dict.
    """
    response: dict[str, str] = {"status": status}
    if location:
        response["location"] = location
    if etag:
        response["etag"] = etag
    if last_modified:
        response["lastModified"] = last_modified

    entry: dict[str, Any] = {"response": response}
    if resource:
        entry["fullUrl"] = _generate_full_url(resource)
        entry["resource"] = resource
    return entry


# -----------------------------------------------------------------------
# Bundle builders
# -----------------------------------------------------------------------


def create_searchset_bundle(
    resources: list[dict[str, Any]],
    *,
    total: int | None = None,
    link_self: str | None = None,
    link_next: str | None = None,
) -> dict[str, Any]:
    """Create a searchset Bundle from a list of resources.

    Args:
        resources: List of FHIR resources to include.
        total: Total number of matching resources (may differ from
            the number of entries if paginated).
        link_self: Self link URL for the search.
        link_next: Next page link URL, if applicable.

    Returns:
        A FHIR Bundle of type ``searchset``.
    """
    bundle: dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": total if total is not None else len(resources),
        "entry": [
            {
                "fullUrl": _generate_full_url(r),
                "resource": r,
                "search": {"mode": "match"},
            }
            for r in resources
        ],
    }

    links: list[dict[str, str]] = []
    if link_self:
        links.append({"relation": "self", "url": link_self})
    if link_next:
        links.append({"relation": "next", "url": link_next})
    if links:
        bundle["link"] = links

    return bundle


def create_transaction_bundle(
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a transaction Bundle.

    All entries are expected to have ``request`` fields. The server
    must process them atomically.

    Args:
        entries: List of Bundle entry dicts with ``request`` fields.

    Returns:
        A FHIR Bundle of type ``transaction``.
    """
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": entries,
    }


def create_batch_bundle(
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a batch Bundle.

    Similar to a transaction bundle but entries are processed
    independently (no atomicity guarantee).

    Args:
        entries: List of Bundle entry dicts with ``request`` fields.

    Returns:
        A FHIR Bundle of type ``batch``.
    """
    return {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": entries,
    }


def create_transaction_response(
    response_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a transaction-response Bundle.

    Args:
        response_entries: List of response entry dicts.

    Returns:
        A FHIR Bundle of type ``transaction-response``.
    """
    return {
        "resourceType": "Bundle",
        "type": "transaction-response",
        "entry": response_entries,
    }


# -----------------------------------------------------------------------
# Bundle parser
# -----------------------------------------------------------------------


class BundleParser:
    """Parse and extract data from FHIR Bundles.

    Provides convenience methods for iterating over entries,
    extracting resources by type, and accessing pagination links.
    """

    def __init__(self, bundle: dict[str, Any]) -> None:
        if bundle.get("resourceType") != "Bundle":
            raise BundleValidationError(
                f"Expected resourceType 'Bundle', got '{bundle.get('resourceType')}'"
            )
        self._bundle = bundle

    @property
    def bundle_type(self) -> str:
        """Return the bundle type."""
        return self._bundle.get("type", "")

    @property
    def total(self) -> int | None:
        """Return the total count, if present."""
        return self._bundle.get("total")

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Return all bundle entries."""
        return self._bundle.get("entry", [])

    def resources(self) -> list[dict[str, Any]]:
        """Extract all resources from the bundle entries.

        Returns:
            A list of FHIR resource dicts.
        """
        return [entry["resource"] for entry in self.entries if "resource" in entry]

    def resources_by_type(
        self,
        resource_type: str,
    ) -> list[dict[str, Any]]:
        """Extract resources of a specific type.

        Args:
            resource_type: The FHIR resource type to filter for.

        Returns:
            A list of matching resource dicts.
        """
        return [r for r in self.resources() if r.get("resourceType") == resource_type]

    def link(self, relation: str) -> str | None:
        """Get a link URL by relation name.

        Args:
            relation: The link relation (e.g. ``"self"``,
                ``"next"``).

        Returns:
            The link URL, or ``None`` if not present.
        """
        for lnk in self._bundle.get("link", []):
            if lnk.get("relation") == relation:
                return lnk.get("url")
        return None

    @property
    def next_link(self) -> str | None:
        """Return the ``next`` pagination link, if present."""
        return self.link("next")

    @property
    def self_link(self) -> str | None:
        """Return the ``self`` link, if present."""
        return self.link("self")

    def validate(self) -> list[str]:
        """Validate the bundle structure.

        Returns:
            A list of validation error messages.
        """
        return validate_bundle(self._bundle)
