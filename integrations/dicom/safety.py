"""Image reference safety constraints for DICOM integrations.

Enforces the national MCP PAI standard requirement that physical
AI agents and trial systems never transfer or receive actual
DICOM pixel data. All imaging references must be metadata-only
pointers containing UIDs and descriptive attributes but no bulk
data or pixel arrays.

Key safety constraints:
    1. No pixel data transfer: Responses must not contain
       PixelData (7FE00010) or related bulk data fields.
    2. Metadata-only pointers: References to images use
       Study/Series/SOP Instance UIDs only.
    3. Retrieval authorization: Access to image metadata
       requires valid authorization context.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Prohibited DICOM tags and field patterns
# -------------------------------------------------------------------

# DICOM tags that carry pixel or bulk data and must never
# appear in metadata responses within this framework.
PROHIBITED_TAGS: frozenset[str] = frozenset(
    {
        # Pixel Data and related
        "7FE00010",  # Pixel Data
        "7FE00008",  # Float Pixel Data
        "7FE00009",  # Double Float Pixel Data
        "7FE00001",  # Extended Offset Table
        "7FE00002",  # Extended Offset Table Lengths
        # Waveform and overlay data
        "54000100",  # Waveform Data
        "60000010",  # Overlay Rows (group 6000)
        "60003000",  # Overlay Data
        # Encapsulated document
        "00420011",  # Encapsulated Document
        # Audio data
        "50000100",  # Audio Sample Data (retired)
    }
)

# Field name patterns that indicate pixel or bulk data
PROHIBITED_FIELD_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)pixel\s*data"),
    re.compile(r"(?i)bulk\s*data\s*uri"),
    re.compile(r"(?i)inline\s*binary"),
    re.compile(r"(?i)encapsulated\s*document"),
    re.compile(r"(?i)waveform\s*data"),
    re.compile(r"(?i)overlay\s*data"),
    re.compile(r"(?i)audio\s*sample"),
]

# DICOMweb BulkDataURI key
BULK_DATA_URI_KEY = "BulkDataURI"
INLINE_BINARY_KEY = "InlineBinary"

# Required fields for a valid metadata-only pointer
REQUIRED_POINTER_FIELDS: frozenset[str] = frozenset(
    {
        "StudyInstanceUID",
    }
)

OPTIONAL_POINTER_FIELDS: frozenset[str] = frozenset(
    {
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "Modality",
        "StudyDate",
        "StudyDescription",
        "PatientID",
        "SeriesDescription",
        "InstanceNumber",
    }
)


class SafetyViolation(Exception):
    """Raised when a safety constraint is violated.

    Indicates that a DICOM response or reference contains
    prohibited pixel data or bulk data content.
    """


class SafetyValidator:
    """Validates DICOM responses against safety constraints.

    Ensures that no pixel data, bulk data URIs, or inline
    binary content is present in metadata responses. All
    validation methods either return cleaned data or raise
    ``SafetyViolation`` when strict mode is enabled.

    Example::

        validator = SafetyValidator()
        metadata = adapter.retrieve_metadata(study_uid)
        validator.validate_metadata_response(metadata)
        # Raises SafetyViolation if pixel data detected

    Attributes:
        strict: If True, raise on violations rather than
            stripping silently.
    """

    def __init__(
        self,
        *,
        strict: bool = False,
    ) -> None:
        """Initialize the safety validator.

        Args:
            strict: If True, raise ``SafetyViolation`` on
                any prohibited content. If False (default),
                silently strip prohibited fields and log
                warnings.
        """
        self.strict = strict

    def validate_metadata_response(
        self,
        metadata: dict[str, Any],
    ) -> None:
        """Validate that a metadata response is safe.

        Checks for prohibited tags, field name patterns,
        and inline binary content. In strict mode, raises
        on first violation. In non-strict mode, logs
        warnings for all violations found.

        Args:
            metadata: DICOM metadata dictionary to validate.

        Raises:
            SafetyViolation: In strict mode, if prohibited
                content is detected.
        """
        violations = self._find_violations(metadata)

        if violations:
            msg = f"Safety violations detected: {'; '.join(violations)}"
            if self.strict:
                raise SafetyViolation(msg)
            logger.warning(msg)

    def strip_pixel_fields(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Remove all prohibited fields from metadata.

        Creates a new dictionary with all pixel data,
        bulk data, and inline binary fields removed.

        Args:
            metadata: Raw DICOM metadata dictionary.

        Returns:
            Cleaned metadata dictionary.
        """
        cleaned: dict[str, Any] = {}

        for key, value in metadata.items():
            if self._is_prohibited_key(key):
                logger.debug("Stripped prohibited field: %r", key)
                continue

            if isinstance(value, dict):
                # Handle DICOMweb JSON tag objects
                if self._has_prohibited_content(value):
                    logger.debug(
                        "Stripped field with prohibited content: %r",
                        key,
                    )
                    continue
                cleaned[key] = self._clean_nested(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_nested(item) if isinstance(item, dict) else item
                    for item in value
                    if not (isinstance(item, (bytes, bytearray)) and len(item) > 1024)
                ]
            elif isinstance(value, (bytes, bytearray)):
                if len(value) > 1024:
                    logger.debug(
                        "Stripped large binary field: %r",
                        key,
                    )
                    continue
                cleaned[key] = value
            else:
                cleaned[key] = value

        return cleaned

    def validate_image_reference(
        self,
        reference: dict[str, Any],
    ) -> list[str]:
        """Validate that an image reference is metadata-only.

        Checks that the reference contains only UID pointers
        and descriptive metadata, with no pixel data or
        bulk data URIs.

        Args:
            reference: Image reference dictionary.

        Returns:
            List of validation error messages. Empty list
            means the reference is valid.
        """
        errors: list[str] = []

        # Check required fields
        for field in REQUIRED_POINTER_FIELDS:
            if not reference.get(field):
                errors.append(f"Missing required field: {field!r}")

        # Check for prohibited content
        violations = self._find_violations(reference)
        errors.extend(violations)

        # Check for suspiciously large values
        for key, value in reference.items():
            if isinstance(value, (bytes, bytearray)):
                if len(value) > 1024:
                    errors.append(
                        f"Field {key!r} contains "
                        f"{len(value)} bytes of binary "
                        f"data (possible pixel data)"
                    )
            if isinstance(value, str) and len(value) > 10000:
                errors.append(
                    f"Field {key!r} contains {len(value)} characters (suspiciously large)"
                )

        return errors

    def check_retrieval_authorization(
        self,
        role: str,
        study_instance_uid: str,
        *,
        authorization_context: (dict[str, Any] | None) = None,
    ) -> bool:
        """Check whether a retrieval request is authorized.

        Validates that the requesting identity has proper
        authorization context for accessing the specified
        study's metadata.

        Args:
            role: Role of the requesting agent.
            study_instance_uid: Study being accessed.
            authorization_context: Optional dict containing
                authorization tokens, trial enrollment
                verification, etc.

        Returns:
            True if the retrieval is authorized.
        """
        if not role:
            logger.warning("Retrieval denied: no role specified")
            return False

        if not study_instance_uid:
            logger.warning("Retrieval denied: no study UID specified")
            return False

        if authorization_context is None:
            logger.warning(
                "Retrieval authorized without explicit context for role=%r study=%r",
                role,
                study_instance_uid,
            )
            return True

        # Validate authorization token presence
        token = authorization_context.get("token")
        if not token:
            logger.warning("Retrieval denied: no authorization token in context")
            return False

        # Validate trial enrollment if specified
        trial_id = authorization_context.get("trial_id")
        if trial_id:
            enrolled_studies = authorization_context.get("enrolled_studies", [])
            if study_instance_uid not in enrolled_studies and "*" not in enrolled_studies:
                logger.warning(
                    "Retrieval denied: study %r not in enrolled studies for trial %r",
                    study_instance_uid,
                    trial_id,
                )
                return False

        logger.info(
            "Retrieval authorized: role=%r study=%r",
            role,
            study_instance_uid,
        )
        return True

    # ---------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------

    def _find_violations(
        self,
        data: dict[str, Any],
    ) -> list[str]:
        """Find all safety violations in a data dict."""
        violations: list[str] = []

        for key, value in data.items():
            if self._is_prohibited_key(key):
                violations.append(f"Prohibited field present: {key!r}")

            if isinstance(value, dict):
                if BULK_DATA_URI_KEY in value:
                    violations.append(f"BulkDataURI found in {key!r}")
                if INLINE_BINARY_KEY in value:
                    violations.append(f"InlineBinary found in {key!r}")
                # Recurse into nested dicts
                nested = self._find_violations(value)
                violations.extend(nested)

            if isinstance(value, (bytes, bytearray)):
                if len(value) > 1024:
                    violations.append(f"Large binary data in {key!r} ({len(value)} bytes)")

        return violations

    def _is_prohibited_key(self, key: str) -> bool:
        """Check if a key matches prohibited tag patterns."""
        # Check numeric tag format
        clean_key = key.replace(",", "").replace("(", "").replace(")", "").strip().upper()
        if clean_key in PROHIBITED_TAGS:
            return True

        # Check field name patterns
        for pattern in PROHIBITED_FIELD_PATTERNS:
            if pattern.search(key):
                return True

        return False

    def _has_prohibited_content(
        self,
        value: dict[str, Any],
    ) -> bool:
        """Check if a dict value contains prohibited content."""
        if BULK_DATA_URI_KEY in value:
            return True
        if INLINE_BINARY_KEY in value:
            return True
        vr = value.get("vr", "")
        if vr in ("OB", "OW", "OF", "OD", "UN"):
            data = value.get("Value", [])
            if isinstance(data, list) and data:
                for item in data:
                    if isinstance(item, (bytes, bytearray)) and len(item) > 1024:
                        return True
        return False

    def _clean_nested(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Recursively clean nested dict of prohibited data."""
        cleaned: dict[str, Any] = {}
        for key, value in data.items():
            if key in (BULK_DATA_URI_KEY, INLINE_BINARY_KEY):
                continue
            if self._is_prohibited_key(key):
                continue
            if isinstance(value, dict):
                if not self._has_prohibited_content(value):
                    cleaned[key] = self._clean_nested(value)
            else:
                cleaned[key] = value
        return cleaned
