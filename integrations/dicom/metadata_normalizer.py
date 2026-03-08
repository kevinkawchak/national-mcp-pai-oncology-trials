"""DICOM metadata normalization utilities.

Provides tag harmonization, encoding normalization, and value
representation handling for DICOM metadata consumed by the
national MCP PAI oncology trial framework. Ensures consistent
metadata representation regardless of the upstream DICOM source.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Tag name to standard DICOM tag mapping
# -------------------------------------------------------------------

# Maps commonly-used human-readable names and non-standard
# aliases to their canonical DICOM keyword as defined in
# PS3.6 Data Dictionary.
TAG_HARMONIZATION_MAP: dict[str, str] = {
    # Patient module
    "patient_id": "PatientID",
    "patientid": "PatientID",
    "patient_name": "PatientName",
    "patientname": "PatientName",
    "patient_birth_date": "PatientBirthDate",
    "patientbirthdate": "PatientBirthDate",
    "dob": "PatientBirthDate",
    "date_of_birth": "PatientBirthDate",
    "patient_sex": "PatientSex",
    "patientsex": "PatientSex",
    "gender": "PatientSex",
    "patient_age": "PatientAge",
    "patientage": "PatientAge",
    "patient_weight": "PatientWeight",
    "patientweight": "PatientWeight",
    # Study module
    "study_instance_uid": "StudyInstanceUID",
    "studyinstanceuid": "StudyInstanceUID",
    "study_uid": "StudyInstanceUID",
    "study_date": "StudyDate",
    "studydate": "StudyDate",
    "study_time": "StudyTime",
    "studytime": "StudyTime",
    "study_description": "StudyDescription",
    "studydescription": "StudyDescription",
    "accession_number": "AccessionNumber",
    "accessionnumber": "AccessionNumber",
    "accession": "AccessionNumber",
    "referring_physician": "ReferringPhysicianName",
    "referringphysicianname": "ReferringPhysicianName",
    # Series module
    "series_instance_uid": "SeriesInstanceUID",
    "seriesinstanceuid": "SeriesInstanceUID",
    "series_uid": "SeriesInstanceUID",
    "modality": "Modality",
    "series_description": "SeriesDescription",
    "seriesdescription": "SeriesDescription",
    "series_number": "SeriesNumber",
    "seriesnumber": "SeriesNumber",
    "body_part": "BodyPartExamined",
    "bodypartexamined": "BodyPartExamined",
    "body_part_examined": "BodyPartExamined",
    # Instance module
    "sop_instance_uid": "SOPInstanceUID",
    "sopinstanceuid": "SOPInstanceUID",
    "sop_class_uid": "SOPClassUID",
    "sopclassuid": "SOPClassUID",
    "instance_number": "InstanceNumber",
    "instancenumber": "InstanceNumber",
    # Equipment
    "manufacturer": "Manufacturer",
    "institution_name": "InstitutionName",
    "institutionname": "InstitutionName",
    "station_name": "StationName",
    "stationname": "StationName",
    # RT modules
    "rt_plan_label": "RTPlanLabel",
    "rtplanlabel": "RTPlanLabel",
    "structure_set_label": "StructureSetLabel",
    "structuresetlabel": "StructureSetLabel",
}

# Numeric DICOM tag strings (group,element) mapped to keywords
TAG_NUMBER_TO_KEYWORD: dict[str, str] = {
    "00100020": "PatientID",
    "00100010": "PatientName",
    "00100030": "PatientBirthDate",
    "00100040": "PatientSex",
    "0020000D": "StudyInstanceUID",
    "00080020": "StudyDate",
    "00080030": "StudyTime",
    "00081030": "StudyDescription",
    "00080050": "AccessionNumber",
    "00080090": "ReferringPhysicianName",
    "0020000E": "SeriesInstanceUID",
    "00080060": "Modality",
    "0008103E": "SeriesDescription",
    "00200011": "SeriesNumber",
    "00080016": "SOPClassUID",
    "00080018": "SOPInstanceUID",
    "00200013": "InstanceNumber",
    "00180015": "BodyPartExamined",
    "00080080": "InstitutionName",
    "00080070": "Manufacturer",
    "00081010": "StationName",
}

# Value Representation normalization rules
# Maps VR codes to normalization functions
_VR_NORMALIZERS: dict[str, str] = {
    "DA": "date",
    "TM": "time",
    "DT": "datetime",
    "PN": "person_name",
    "DS": "decimal_string",
    "IS": "integer_string",
    "AS": "age_string",
}


class MetadataNormalizer:
    """Normalizes DICOM metadata to a canonical form.

    Handles three normalization concerns:
    1. Tag harmonization: Maps non-standard tag names and
       numeric tag identifiers to canonical DICOM keywords.
    2. Encoding normalization: Ensures consistent UTF-8
       string representation.
    3. Value representation handling: Normalizes VR-specific
       formatting (dates, person names, etc.).

    Example::

        normalizer = MetadataNormalizer()
        raw = {"patient_id": "ONC-001", "dob": "19800101"}
        normalized = normalizer.normalize(raw)
        # {"PatientID": "ONC-001", "PatientBirthDate": "1980-01-01"}
    """

    def __init__(
        self,
        *,
        harmonize_tags: bool = True,
        normalize_encoding: bool = True,
        normalize_vr: bool = True,
        custom_tag_map: dict[str, str] | None = None,
    ) -> None:
        """Initialize the normalizer.

        Args:
            harmonize_tags: Whether to apply tag name
                harmonization.
            normalize_encoding: Whether to normalize string
                encoding to UTF-8.
            normalize_vr: Whether to apply VR-specific
                normalization.
            custom_tag_map: Additional tag name mappings to
                merge with the default map.
        """
        self._harmonize_tags = harmonize_tags
        self._normalize_encoding = normalize_encoding
        self._normalize_vr = normalize_vr
        self._tag_map = dict(TAG_HARMONIZATION_MAP)
        if custom_tag_map:
            self._tag_map.update(custom_tag_map)

    def normalize(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize a DICOM metadata dictionary.

        Applies all enabled normalization steps in order:
        tag harmonization, encoding normalization, then
        VR-specific formatting.

        Args:
            metadata: Raw DICOM metadata dictionary.

        Returns:
            Normalized metadata dictionary.
        """
        result: dict[str, Any] = {}

        for key, value in metadata.items():
            normalized_key = self._harmonize_key(key)
            normalized_value = self._normalize_value(normalized_key, value)
            result[normalized_key] = normalized_value

        return result

    def normalize_dicomweb_json(
        self,
        dataset: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize a DICOM JSON (DICOMweb) dataset.

        Converts from the numeric-tag DICOMweb JSON format
        to keyword-based format with normalized values.

        Args:
            dataset: DICOM JSON dataset with numeric tag keys
                (e.g., ``{"00100020": {"vr": "LO", ...}}``).

        Returns:
            Normalized metadata with keyword keys.
        """
        result: dict[str, Any] = {}

        for tag, tag_data in dataset.items():
            keyword = TAG_NUMBER_TO_KEYWORD.get(tag.upper(), tag)
            if not isinstance(tag_data, dict):
                result[keyword] = tag_data
                continue

            vr = tag_data.get("vr", "")
            value = tag_data.get("Value", [])

            if isinstance(value, list) and len(value) == 1:
                extracted = value[0]
            elif isinstance(value, list) and value:
                extracted = value
            else:
                extracted = None

            if extracted is not None and self._normalize_vr:
                extracted = self._apply_vr_normalization(vr, extracted)

            result[keyword] = extracted

        return result

    # ---------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------

    def _harmonize_key(self, key: str) -> str:
        """Map a tag name to its canonical DICOM keyword."""
        if not self._harmonize_tags:
            return key

        lower_key = key.lower().strip()
        if lower_key in self._tag_map:
            return self._tag_map[lower_key]

        # Check numeric tag format (e.g., "00100020")
        clean = key.replace(",", "").replace("(", "").replace(")", "").strip()
        if clean.upper() in TAG_NUMBER_TO_KEYWORD:
            return TAG_NUMBER_TO_KEYWORD[clean.upper()]

        return key

    def _normalize_value(
        self,
        key: str,
        value: Any,
    ) -> Any:
        """Normalize a single metadata value."""
        if value is None:
            return value

        if self._normalize_encoding and isinstance(value, bytes):
            value = _decode_bytes(value)

        if self._normalize_encoding and isinstance(value, str):
            value = _clean_string(value)

        return value

    def _apply_vr_normalization(
        self,
        vr: str,
        value: Any,
    ) -> Any:
        """Apply VR-specific normalization to a value."""
        if vr == "DA":
            return _normalize_date(value)
        if vr == "TM":
            return _normalize_time(value)
        if vr == "PN":
            return _normalize_person_name(value)
        if vr == "DS":
            return _normalize_decimal_string(value)
        if vr == "IS":
            return _normalize_integer_string(value)
        return value


# -------------------------------------------------------------------
# Value normalization functions
# -------------------------------------------------------------------


def _decode_bytes(value: bytes) -> str:
    """Decode bytes to UTF-8 string.

    Attempts UTF-8 first, then falls back to latin-1.

    Args:
        value: Raw byte string.

    Returns:
        Decoded string.
    """
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError:
        return value.decode("latin-1", errors="replace")


def _clean_string(value: str) -> str:
    """Clean a string value by stripping and normalizing.

    Removes null bytes and excess whitespace.

    Args:
        value: Raw string value.

    Returns:
        Cleaned string.
    """
    value = value.replace("\x00", "").strip()
    return re.sub(r"\s+", " ", value)


def _normalize_date(value: Any) -> str | Any:
    """Normalize a DICOM DA (Date) value to ISO format.

    Converts ``YYYYMMDD`` to ``YYYY-MM-DD``.

    Args:
        value: Raw date string.

    Returns:
        ISO-formatted date string, or original value if
        not parseable.
    """
    if not isinstance(value, str):
        return value
    clean = value.strip()
    if len(clean) == 8 and clean.isdigit():
        return f"{clean[:4]}-{clean[4:6]}-{clean[6:8]}"
    return clean


def _normalize_time(value: Any) -> str | Any:
    """Normalize a DICOM TM (Time) value.

    Formats to ``HH:MM:SS`` or ``HH:MM:SS.ffffff``.

    Args:
        value: Raw time string.

    Returns:
        Normalized time string.
    """
    if not isinstance(value, str):
        return value
    clean = value.strip().replace(":", "")
    if len(clean) >= 6:
        base = f"{clean[:2]}:{clean[2:4]}:{clean[4:6]}"
        if len(clean) > 6:
            base = f"{base}.{clean[6:]}"
        return base
    return value


def _normalize_person_name(value: Any) -> str | Any:
    """Normalize a DICOM PN (Person Name) value.

    Handles both string format (``LAST^FIRST^MIDDLE``)
    and DICOMweb JSON object format.

    Args:
        value: Raw person name value.

    Returns:
        Normalized person name string.
    """
    if isinstance(value, dict):
        alphabetic = value.get("Alphabetic", "")
        if alphabetic:
            return str(alphabetic)
        return str(value)
    if isinstance(value, str):
        return value.strip()
    return value


def _normalize_decimal_string(value: Any) -> float | Any:
    """Normalize a DICOM DS (Decimal String) value.

    Args:
        value: Raw decimal string.

    Returns:
        Float value, or original if not parseable.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return value
    return value


def _normalize_integer_string(value: Any) -> int | Any:
    """Normalize a DICOM IS (Integer String) value.

    Args:
        value: Raw integer string.

    Returns:
        Integer value, or original if not parseable.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return value
    return value
