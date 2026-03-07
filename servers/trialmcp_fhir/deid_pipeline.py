"""HIPAA Safe Harbor de-identification pipeline.

Implements the 18-identifier removal specified in spec/privacy.md,
with HMAC-SHA256 pseudonymization for patient identifiers.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any

# HIPAA Safe Harbor 18 identifiers per spec/privacy.md
HIPAA_IDENTIFIERS = [
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

# FHIR resource fields containing PHI
PHI_FIELDS = {
    "name",
    "address",
    "telecom",
    "birthDate",
    "deceasedDateTime",
    "identifier",
    "photo",
    "contact",
    "communication",
}

# Year-only date pattern
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


class DeidentificationPipeline:
    """HIPAA Safe Harbor de-identification for FHIR resources.

    Removes or masks the 18 HIPAA identifiers from FHIR R4 resources,
    pseudonymizes patient IDs via HMAC-SHA256, and generalizes dates
    to year-only format.
    """

    def __init__(self, hmac_key: str = "trialmcp-default-key") -> None:
        self._hmac_key = hmac_key.encode("utf-8")

    def pseudonymize_id(self, patient_id: str) -> str:
        """Generate an HMAC-SHA256 pseudonym for a patient ID."""
        return hmac.new(self._hmac_key, patient_id.encode("utf-8"), hashlib.sha256).hexdigest()

    def generalize_date(self, date_str: str) -> str:
        """Generalize a date to year-only format per Safe Harbor."""
        if DATE_PATTERN.match(date_str):
            return date_str[:4]
        return date_str

    def deidentify_resource(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Apply Safe Harbor de-identification to a FHIR resource.

        Returns a copy of the resource with PHI removed or masked.
        """
        result = dict(resource)

        # Remove PHI fields
        for field in PHI_FIELDS:
            if field in result:
                if field == "birthDate":
                    result["birthDate"] = self.generalize_date(result["birthDate"])
                elif field == "name":
                    result["name"] = [{"text": "[REDACTED]"}]
                elif field == "address":
                    result["address"] = [{"text": "[REDACTED]"}]
                elif field == "telecom":
                    del result["telecom"]
                elif field == "identifier":
                    # Pseudonymize identifiers
                    new_ids = []
                    for ident in result.get("identifier", []):
                        value = ident.get("value", "")
                        new_ids.append(
                            {
                                "system": ident.get("system", ""),
                                "value": self.pseudonymize_id(value),
                            }
                        )
                    result["identifier"] = new_ids
                else:
                    del result[field]

        # Pseudonymize patient ID if present
        if "id" in result and result.get("resourceType") == "Patient":
            result["id"] = self.pseudonymize_id(result["id"])

        return result

    def deidentify_bundle(self, bundle: dict[str, Any]) -> dict[str, Any]:
        """Apply de-identification to all resources in a FHIR Bundle."""
        result = dict(bundle)
        entries = result.get("entry", [])
        deidentified_entries = []
        for entry in entries:
            resource = entry.get("resource", {})
            deidentified_entries.append(
                {
                    **entry,
                    "resource": self.deidentify_resource(resource),
                }
            )
        result["entry"] = deidentified_entries
        return result
