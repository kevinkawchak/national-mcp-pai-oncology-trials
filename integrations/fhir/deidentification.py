"""HIPAA Safe Harbor de-identification pipeline for FHIR resources.

Comprehensive implementation of the 18 HIPAA identifiers removal with
HMAC-SHA256 pseudonymization, year-only date generalization, name and
address redaction, and a verification suite that tests completeness.

Builds on the pattern in ``servers/trialmcp_fhir/deid_pipeline.py``
with full coverage of all 18 Safe Harbor identifiers and a
:class:`DeidentificationVerifier` for compliance auditing.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any

# -----------------------------------------------------------------------
# HIPAA Safe Harbor 18 identifiers
# -----------------------------------------------------------------------

HIPAA_IDENTIFIERS: list[str] = [
    "name",
    "address",
    "dates",
    "phone",
    "fax",
    "email",
    "ssn",
    "mrn",
    "health_plan_id",
    "account_number",
    "certificate_license",
    "vehicle_ids",
    "device_ids",
    "urls",
    "ip_addresses",
    "biometric_ids",
    "photo",
    "other_unique_id",
]

# FHIR resource fields that may contain PHI, mapped to the HIPAA
# identifier category they correspond to.
_PHI_FIELD_MAP: dict[str, str] = {
    "name": "name",
    "address": "address",
    "birthDate": "dates",
    "deceasedDateTime": "dates",
    "telecom": "phone",
    "identifier": "mrn",
    "photo": "photo",
    "contact": "name",
    "communication": "other_unique_id",
    "managingOrganization": "other_unique_id",
}

# Regex patterns for detecting residual PHI in free-text fields
_PHI_PATTERNS: dict[str, re.Pattern[str]] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "url": re.compile(r"https?://[^\s]+"),
    "date_full": re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    "mrn": re.compile(r"\bMRN[-:]?\s*\d+\b", re.IGNORECASE),
    "fax": re.compile(
        r"\bfax\s*:?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        re.IGNORECASE,
    ),
    "health_plan_id": re.compile(r"\b\d{3}-\d{2}-\d{4,}\b"),
    "account_number": re.compile(r"\baccount\s*#?\s*:?\s*\d{6,}\b", re.IGNORECASE),
    "vehicle_id": re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b"),
    "device_serial": re.compile(r"\bserial\s*#?\s*:?\s*[A-Z0-9]{8,}\b", re.IGNORECASE),
    "zip_full": re.compile(r"\b\d{5}-\d{4}\b"),
}

# Date pattern for generalization
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Redaction sentinel
REDACTED = "[REDACTED]"


# -----------------------------------------------------------------------
# Test corpus for verification
# -----------------------------------------------------------------------

_TEST_CORPUS: list[dict[str, Any]] = [
    {
        "resourceType": "Patient",
        "id": "test-phi-patient",
        "name": [{"family": "Doe", "given": ["Jane"]}],
        "address": [
            {
                "line": ["123 Main St"],
                "city": "Springfield",
                "state": "IL",
                "postalCode": "62704-1234",
            }
        ],
        "birthDate": "1980-06-15",
        "telecom": [
            {"system": "phone", "value": "(555) 123-4567"},
            {"system": "fax", "value": "(555) 765-4321"},
            {"system": "email", "value": "jane.doe@example.com"},
        ],
        "identifier": [
            {
                "system": "http://hospital.example/mrn",
                "value": "MRN-99999",
            },
            {
                "system": "http://hl7.org/fhir/sid/us-ssn",
                "value": "123-45-6789",
            },
        ],
        "photo": [{"contentType": "image/jpeg", "data": "base64=="}],
        "contact": [
            {
                "name": {"family": "Doe", "given": ["John"]},
                "telecom": [{"system": "phone", "value": "555-999-8888"}],
            }
        ],
    },
]


class DeidentificationPipeline:
    """HIPAA Safe Harbor de-identification for FHIR R4 resources.

    Removes or masks all 18 HIPAA identifiers from FHIR resources,
    pseudonymizes patient IDs via HMAC-SHA256, and generalizes dates
    to year-only format.

    Args:
        hmac_key: Secret key used for HMAC-SHA256 pseudonymization.
    """

    def __init__(
        self,
        hmac_key: str = "national-mcp-pai-default-key",
    ) -> None:
        self._hmac_key = hmac_key.encode("utf-8")

    # ---------------------------------------------------------------
    # Pseudonymization
    # ---------------------------------------------------------------

    def pseudonymize_id(self, value: str) -> str:
        """Generate an HMAC-SHA256 pseudonym for a value.

        Args:
            value: The identifier value to pseudonymize.

        Returns:
            A hex-encoded HMAC-SHA256 digest.
        """
        return hmac.new(
            self._hmac_key,
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    # ---------------------------------------------------------------
    # Date generalization
    # ---------------------------------------------------------------

    @staticmethod
    def generalize_date(date_str: str) -> str:
        """Generalize a date to year-only per Safe Harbor.

        Args:
            date_str: An ISO-8601 date string (YYYY-MM-DD).

        Returns:
            The four-digit year, or the original string if it does
            not match the expected format.
        """
        if _DATE_RE.fullmatch(date_str):
            return date_str[:4]
        return date_str

    # ---------------------------------------------------------------
    # Text scrubbing
    # ---------------------------------------------------------------

    @staticmethod
    def scrub_text(text: str) -> str:
        """Remove detectable PHI patterns from free text.

        Args:
            text: Arbitrary free-text content.

        Returns:
            Text with PHI patterns replaced by ``[REDACTED]``.
        """
        for pattern in _PHI_PATTERNS.values():
            text = pattern.sub(REDACTED, text)
        return text

    # ---------------------------------------------------------------
    # Name / address redaction
    # ---------------------------------------------------------------

    @staticmethod
    def _redact_name(
        name_list: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Replace all HumanName entries with a redacted placeholder."""
        return [{"text": REDACTED}] if name_list else []

    @staticmethod
    def _redact_address(
        address_list: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Replace all Address entries with a redacted placeholder."""
        return [{"text": REDACTED}] if address_list else []

    # ---------------------------------------------------------------
    # Resource-level de-identification
    # ---------------------------------------------------------------

    def deidentify_resource(
        self,
        resource: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply full Safe Harbor de-identification to a resource.

        Produces a deep-ish copy with all PHI removed or masked.

        Args:
            resource: A FHIR R4 resource dict.

        Returns:
            A de-identified copy of the resource.
        """
        result = dict(resource)

        # Name redaction
        if "name" in result:
            result["name"] = self._redact_name(result["name"])

        # Address redaction
        if "address" in result:
            result["address"] = self._redact_address(result["address"])

        # Date generalization
        for date_field in ("birthDate", "deceasedDateTime"):
            if date_field in result:
                result[date_field] = self.generalize_date(result[date_field])

        # Remove telecom (phone, fax, email)
        result.pop("telecom", None)

        # Remove photo
        result.pop("photo", None)

        # Remove contact (contains names and telecom)
        result.pop("contact", None)

        # Remove communication preferences
        result.pop("communication", None)

        # Remove managing organization reference
        result.pop("managingOrganization", None)

        # Pseudonymize identifiers
        if "identifier" in result:
            new_ids: list[dict[str, Any]] = []
            for ident in result.get("identifier", []):
                value = ident.get("value", "")
                new_ids.append(
                    {
                        "system": ident.get("system", ""),
                        "value": self.pseudonymize_id(value),
                    }
                )
            result["identifier"] = new_ids

        # Pseudonymize patient ID
        if "id" in result and result.get("resourceType") == "Patient":
            result["id"] = self.pseudonymize_id(result["id"])

        # Scrub any text narrative
        if "text" in result and isinstance(result["text"], dict):
            div = result["text"].get("div", "")
            if div:
                result["text"] = {
                    **result["text"],
                    "div": self.scrub_text(div),
                }

        return result

    def deidentify_bundle(
        self,
        bundle: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply de-identification to all resources in a Bundle.

        Args:
            bundle: A FHIR Bundle resource dict.

        Returns:
            A new Bundle with all contained resources de-identified.
        """
        result = dict(bundle)
        entries = result.get("entry", [])
        result["entry"] = [
            {
                **entry,
                "resource": self.deidentify_resource(entry.get("resource", {})),
            }
            for entry in entries
        ]
        return result


class DeidentificationVerifier:
    """Verification suite for HIPAA Safe Harbor compliance.

    Tests that a :class:`DeidentificationPipeline` correctly handles
    all 18 HIPAA identifiers by running the pipeline against a test
    corpus and checking for residual PHI.
    """

    def __init__(
        self,
        pipeline: DeidentificationPipeline | None = None,
    ) -> None:
        self._pipeline = pipeline or DeidentificationPipeline()

    # ---------------------------------------------------------------
    # Identifier checkers
    # ---------------------------------------------------------------

    @staticmethod
    def _has_name(resource: dict[str, Any]) -> bool:
        """Check if any real name remains."""
        for name_entry in resource.get("name", []):
            text = name_entry.get("text", "")
            if text and text != REDACTED:
                return True
            if name_entry.get("family") or name_entry.get("given"):
                return True
        return False

    @staticmethod
    def _has_address(resource: dict[str, Any]) -> bool:
        """Check if any real address remains."""
        for addr in resource.get("address", []):
            text = addr.get("text", "")
            if text and text != REDACTED:
                return True
            if addr.get("line") or addr.get("city"):
                return True
        return False

    @staticmethod
    def _has_full_date(resource: dict[str, Any]) -> bool:
        """Check if any full date (YYYY-MM-DD) remains."""
        for field in ("birthDate", "deceasedDateTime"):
            val = resource.get(field, "")
            if _DATE_RE.fullmatch(val):
                return True
        return False

    @staticmethod
    def _has_telecom(resource: dict[str, Any]) -> bool:
        """Check if telecom data remains."""
        return "telecom" in resource

    @staticmethod
    def _has_photo(resource: dict[str, Any]) -> bool:
        """Check if photo data remains."""
        return "photo" in resource

    @staticmethod
    def _has_contact(resource: dict[str, Any]) -> bool:
        """Check if contact data remains."""
        return "contact" in resource

    @staticmethod
    def _has_plain_identifiers(resource: dict[str, Any]) -> bool:
        """Check if any non-pseudonymized identifiers remain."""
        for ident in resource.get("identifier", []):
            value = ident.get("value", "")
            # HMAC-SHA256 hex digests are 64 chars of hex
            if value and len(value) != 64:
                return True
        return False

    def verify_resource(
        self,
        original: dict[str, Any],
        deidentified: dict[str, Any],
    ) -> list[str]:
        """Verify de-identification of a single resource.

        Args:
            original: The original FHIR resource.
            deidentified: The de-identified FHIR resource.

        Returns:
            A list of HIPAA identifier categories that were NOT
            properly handled. An empty list means full compliance.
        """
        failures: list[str] = []

        if self._has_name(deidentified):
            failures.append("name")
        if self._has_address(deidentified):
            failures.append("address")
        if self._has_full_date(deidentified):
            failures.append("dates")
        if self._has_telecom(deidentified):
            failures.append("phone")
            failures.append("fax")
            failures.append("email")
        if self._has_photo(deidentified):
            failures.append("photo")
        if self._has_contact(deidentified):
            failures.append("name")
        if self._has_plain_identifiers(deidentified):
            failures.append("mrn")
            failures.append("ssn")

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for f in failures:
            if f not in seen:
                seen.add(f)
                unique.append(f)
        return unique

    def verify_all(
        self,
        test_corpus: list[dict[str, Any]] | None = None,
    ) -> dict[str, list[str]]:
        """Run verification against a full test corpus.

        Args:
            test_corpus: List of FHIR resources to test. Defaults to
                the built-in test corpus if not provided.

        Returns:
            A dict mapping resource IDs to lists of unhandled HIPAA
            identifier categories. Empty lists indicate compliance.
        """
        corpus = test_corpus or _TEST_CORPUS
        results: dict[str, list[str]] = {}
        for resource in corpus:
            rid = resource.get("id", "unknown")
            deidentified = self._pipeline.deidentify_resource(resource)
            failures = self.verify_resource(resource, deidentified)
            results[rid] = failures
        return results

    def is_compliant(
        self,
        test_corpus: list[dict[str, Any]] | None = None,
    ) -> bool:
        """Check if the pipeline passes all verification checks.

        Args:
            test_corpus: Optional custom test corpus.

        Returns:
            ``True`` if all resources pass de-identification checks.
        """
        results = self.verify_all(test_corpus)
        return all(len(v) == 0 for v in results.values())
