"""Sample FHIR and DICOM resources for conformance testing.

Extracted from schemas/fhir-read.schema.json, schemas/fhir-search.schema.json,
schemas/dicom-query.schema.json, spec/privacy.md, and spec/tool-contracts.md.
"""

from __future__ import annotations

import re

# FHIR resource ID pattern per spec/security.md
FHIR_ID_PATTERN = re.compile(r"^[A-Za-z0-9\-._]+$")

# DICOM UID pattern per spec/security.md
DICOM_UID_PATTERN = re.compile(r"^[\d.]+$")

# HIPAA Safe Harbor: 18 identifiers that MUST be removed per spec/privacy.md
HIPAA_SAFE_HARBOR_IDENTIFIERS = [
    "name",
    "geographic_data",
    "dates",
    "phone_numbers",
    "fax_numbers",
    "email_addresses",
    "social_security_numbers",
    "medical_record_numbers",
    "health_plan_numbers",
    "account_numbers",
    "certificate_numbers",
    "vehicle_identifiers",
    "device_identifiers",
    "web_urls",
    "ip_addresses",
    "biometric_identifiers",
    "photographs",
    "other_unique_identifiers",
]

# FHIR fields that MUST be redacted per spec/privacy.md
FHIR_REDACTED_FIELDS = ["name", "telecom", "address"]

# Valid FHIR resource types for oncology trials
VALID_FHIR_RESOURCE_TYPES = [
    "Patient",
    "Observation",
    "Condition",
    "MedicationRequest",
    "ResearchStudy",
    "ResearchSubject",
]

# DICOM modalities: MUST support per profiles/imaging-guided-oncology.md
MUST_MODALITIES = ["CT", "MR", "PT"]
SHOULD_MODALITIES = ["RTSTRUCT", "RTPLAN"]

# DICOM query levels per schemas/dicom-query.schema.json
DICOM_QUERY_LEVELS = ["PATIENT", "STUDY", "SERIES", "IMAGE"]

# Role-based DICOM query level permissions per schemas/dicom-query.schema.json
DICOM_QUERY_PERMISSIONS: dict[str, list[str]] = {
    "trial_coordinator": ["PATIENT", "STUDY", "SERIES"],
    "robot_agent": ["STUDY", "SERIES"],
    "data_monitor": ["PATIENT", "STUDY"],
    "auditor": ["STUDY"],
}


def make_deidentified_patient() -> dict:
    """Create a de-identified FHIR Patient per spec/privacy.md."""
    return {
        "resourceType": "Patient",
        "id": "hmac_a3f8e2d1",
        "gender": "female",
        "birthDate": "1975",
        "name": "[REDACTED]",
        "address": "[REDACTED]",
    }


def make_fhir_read_response() -> dict:
    """Create a valid fhir_read response conforming to fhir-read.schema.json."""
    return {
        "resource": make_deidentified_patient(),
    }


def make_fhir_search_response(total: int = 3) -> dict:
    """Create a valid fhir_search response conforming to fhir-search.schema.json."""
    return {
        "results": [make_deidentified_patient() for _ in range(total)],
        "total": total,
        "resource_type": "Patient",
    }


def make_dicom_query_response(
    query_level: str = "STUDY",
    modality: str = "CT",
) -> dict:
    """Create a valid dicom_query response conforming to dicom-query.schema.json."""
    return {
        "results": [
            {
                "StudyInstanceUID": "1.2.840.113619.2.5.1762583153",
                "Modality": modality,
                "StudyDate": "2026",
                "NumberOfSeries": 3,
            },
        ],
        "total": 1,
        "query_level": query_level,
    }


# SSRF injection payloads that MUST be rejected per spec/security.md
SSRF_PAYLOADS = [
    "http://internal-server/admin",
    "https://evil.com/steal-data",
    "HTTP://INTERNAL/ADMIN",
    "hTtP://localhost:8080",
    "https://169.254.169.254/metadata",
    "http://[::1]/internal",
    "http://0x7f000001/admin",
]

# Invalid FHIR resource IDs that MUST be rejected
INVALID_FHIR_IDS = [
    "patient 001",  # contains space
    "patient@001",  # contains @
    "patient/001",  # contains /
    "patient<script>",  # XSS attempt
    "",  # empty string
    "http://evil.com/patient",  # URL (SSRF)
    "https://steal-data.com",  # URL (SSRF)
    "a" * 1001,  # exceeds max length (1000 chars per spec/security.md)
]

# Invalid DICOM UIDs that MUST be rejected
INVALID_DICOM_UIDS = [
    "1.2.3.abc",  # contains letters
    "1.2.3 .4",  # contains space
    "1.2.3/4",  # contains slash
    "",  # empty string
]
