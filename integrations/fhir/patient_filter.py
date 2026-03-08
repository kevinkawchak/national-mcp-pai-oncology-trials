"""Patient and resource access filters based on consent and authorization.

Filters FHIR resources based on patient consent categories relevant to
Physical AI oncology clinical trials.  Consent categories include
general trial participation, physical AI procedures, imaging, biospecimen
collection, data sharing, and future research use.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

# -----------------------------------------------------------------------
# Consent categories
# -----------------------------------------------------------------------


class ConsentCategory(enum.Enum):
    """Consent categories for oncology trial participation.

    Each category represents a distinct scope of patient consent
    that governs which resources may be accessed.
    """

    GENERAL_TRIAL = "general_trial"
    PHYSICAL_AI = "physical_ai"
    IMAGING = "imaging"
    BIOSPECIMEN = "biospecimen"
    DATA_SHARING = "data_sharing"
    FUTURE_RESEARCH = "future_research"


class ConsentStatus(enum.Enum):
    """Status of a patient consent decision."""

    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    WITHDRAWN = "withdrawn"


# -----------------------------------------------------------------------
# Resource-to-consent mapping
# -----------------------------------------------------------------------

# Maps FHIR resource types to the consent categories required to
# access them.  A resource is accessible if the patient has granted
# consent for ALL listed categories.
_RESOURCE_CONSENT_MAP: dict[str, list[ConsentCategory]] = {
    "Patient": [ConsentCategory.GENERAL_TRIAL],
    "ResearchStudy": [ConsentCategory.GENERAL_TRIAL],
    "ResearchSubject": [ConsentCategory.GENERAL_TRIAL],
    "Observation": [ConsentCategory.GENERAL_TRIAL],
    "Condition": [ConsentCategory.GENERAL_TRIAL],
    "Procedure": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.PHYSICAL_AI,
    ],
    "ImagingStudy": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.IMAGING,
    ],
    "DiagnosticReport": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.IMAGING,
    ],
    "Specimen": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.BIOSPECIMEN,
    ],
    "MolecularSequence": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.BIOSPECIMEN,
    ],
    "DocumentReference": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.DATA_SHARING,
    ],
    "Consent": [ConsentCategory.GENERAL_TRIAL],
    "Device": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.PHYSICAL_AI,
    ],
}

# Observation categories that require specific consent
_OBSERVATION_CONSENT_OVERRIDES: dict[str, list[ConsentCategory]] = {
    "imaging": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.IMAGING,
    ],
    "laboratory": [
        ConsentCategory.GENERAL_TRIAL,
        ConsentCategory.BIOSPECIMEN,
    ],
}


# -----------------------------------------------------------------------
# Patient consent record
# -----------------------------------------------------------------------


@dataclass
class PatientConsentRecord:
    """Tracks consent decisions for a single patient.

    Attributes:
        patient_id: The patient identifier.
        consents: Map of consent category to status.
    """

    patient_id: str
    consents: dict[ConsentCategory, ConsentStatus] = field(
        default_factory=dict,
    )

    def grant(self, category: ConsentCategory) -> None:
        """Grant consent for a category.

        Args:
            category: The consent category to grant.
        """
        self.consents[category] = ConsentStatus.GRANTED

    def deny(self, category: ConsentCategory) -> None:
        """Deny consent for a category.

        Args:
            category: The consent category to deny.
        """
        self.consents[category] = ConsentStatus.DENIED

    def withdraw(self, category: ConsentCategory) -> None:
        """Withdraw previously granted consent.

        Args:
            category: The consent category to withdraw.
        """
        self.consents[category] = ConsentStatus.WITHDRAWN

    def is_granted(self, category: ConsentCategory) -> bool:
        """Check if consent is actively granted for a category.

        Args:
            category: The consent category to check.

        Returns:
            ``True`` only if the status is ``GRANTED``.
        """
        return self.consents.get(category) == ConsentStatus.GRANTED

    def has_all(
        self,
        categories: list[ConsentCategory],
    ) -> bool:
        """Check if all listed categories are granted.

        Args:
            categories: List of required consent categories.

        Returns:
            ``True`` if every category is actively granted.
        """
        return all(self.is_granted(c) for c in categories)

    def to_fhir_consent(self) -> dict[str, Any]:
        """Serialize to a FHIR Consent resource.

        Returns:
            A FHIR R4 Consent resource dict.
        """
        provisions: list[dict[str, Any]] = []
        for category, status in self.consents.items():
            provision_type = "permit" if status == ConsentStatus.GRANTED else "deny"
            provisions.append(
                {
                    "type": provision_type,
                    "purpose": [
                        {
                            "system": ("http://mcp.trials.example.org/consent-category"),
                            "code": category.value,
                            "display": category.name.replace("_", " ").title(),
                        }
                    ],
                }
            )

        overall_status = "active"
        if all(s == ConsentStatus.DENIED for s in self.consents.values()):
            overall_status = "rejected"
        elif all(s == ConsentStatus.WITHDRAWN for s in self.consents.values()):
            overall_status = "inactive"

        return {
            "resourceType": "Consent",
            "id": f"consent-{self.patient_id}",
            "status": overall_status,
            "scope": {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/CodeSystem/consentscope"),
                        "code": "research",
                        "display": "Research",
                    }
                ],
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": (
                                "http://terminology.hl7.org/CodeSystem/consentcategorycodes"
                            ),
                            "code": "research",
                        }
                    ],
                }
            ],
            "patient": {
                "reference": f"Patient/{self.patient_id}",
            },
            "provision": {
                "type": "deny",
                "provision": provisions,
            },
        }


# -----------------------------------------------------------------------
# Consent store
# -----------------------------------------------------------------------


class ConsentStore:
    """In-memory store for patient consent records.

    Provides lookup and management of :class:`PatientConsentRecord`
    instances keyed by patient ID.
    """

    def __init__(self) -> None:
        self._records: dict[str, PatientConsentRecord] = {}

    def get_or_create(
        self,
        patient_id: str,
    ) -> PatientConsentRecord:
        """Get the consent record for a patient, creating if needed.

        Args:
            patient_id: The patient identifier.

        Returns:
            The patient consent record.
        """
        if patient_id not in self._records:
            self._records[patient_id] = PatientConsentRecord(
                patient_id=patient_id,
            )
        return self._records[patient_id]

    def get(
        self,
        patient_id: str,
    ) -> PatientConsentRecord | None:
        """Get the consent record for a patient.

        Args:
            patient_id: The patient identifier.

        Returns:
            The consent record, or ``None`` if not found.
        """
        return self._records.get(patient_id)

    def has_consent(
        self,
        patient_id: str,
        categories: list[ConsentCategory],
    ) -> bool:
        """Check if a patient has granted all required consents.

        Args:
            patient_id: The patient identifier.
            categories: Required consent categories.

        Returns:
            ``True`` if consent is granted for all categories.
            Returns ``False`` if no consent record exists.
        """
        record = self._records.get(patient_id)
        if record is None:
            return False
        return record.has_all(categories)


# -----------------------------------------------------------------------
# Resource filter
# -----------------------------------------------------------------------


class PatientResourceFilter:
    """Filter FHIR resources based on patient consent status.

    Applies consent-based access control to FHIR resources by
    checking the patient consent record against the resource type
    consent requirements.

    Args:
        consent_store: The consent store to query.
        strict: If ``True``, deny access when no consent record
            exists. If ``False``, allow access to resources that
            require only ``GENERAL_TRIAL`` consent. Defaults to
            ``True``.
    """

    def __init__(
        self,
        consent_store: ConsentStore,
        *,
        strict: bool = True,
    ) -> None:
        self._consent_store = consent_store
        self._strict = strict

    def _extract_patient_id(
        self,
        resource: dict[str, Any],
    ) -> str | None:
        """Extract the patient ID from a FHIR resource.

        Checks ``subject``, ``patient``, and the resource ``id``
        for Patient resources.

        Args:
            resource: A FHIR resource dict.

        Returns:
            The patient ID, or ``None`` if not determinable.
        """
        rtype = resource.get("resourceType", "")
        if rtype == "Patient":
            return resource.get("id")

        for ref_field in ("subject", "patient"):
            ref = resource.get(ref_field, {})
            if isinstance(ref, dict):
                reference = ref.get("reference", "")
                if reference.startswith("Patient/"):
                    return reference.split("/", 1)[1]
        return None

    def _required_categories(
        self,
        resource: dict[str, Any],
    ) -> list[ConsentCategory]:
        """Determine the consent categories required for a resource.

        Takes into account resource type and, for Observations,
        the observation category.

        Args:
            resource: A FHIR resource dict.

        Returns:
            A list of required consent categories.
        """
        rtype = resource.get("resourceType", "")

        # Check observation category overrides
        if rtype == "Observation":
            for cat in resource.get("category", []):
                for coding in cat.get("coding", []):
                    code = coding.get("code", "")
                    if code in _OBSERVATION_CONSENT_OVERRIDES:
                        return _OBSERVATION_CONSENT_OVERRIDES[code]

        return _RESOURCE_CONSENT_MAP.get(
            rtype,
            [ConsentCategory.GENERAL_TRIAL],
        )

    def is_accessible(
        self,
        resource: dict[str, Any],
        patient_id: str | None = None,
    ) -> bool:
        """Check if a resource is accessible given patient consent.

        Args:
            resource: The FHIR resource to check.
            patient_id: Override for the patient ID. If not provided
                it will be extracted from the resource.

        Returns:
            ``True`` if the resource passes consent checks.
        """
        pid = patient_id or self._extract_patient_id(resource)
        if pid is None:
            # Cannot determine patient; allow non-patient resources
            rtype = resource.get("resourceType", "")
            return rtype in ("ResearchStudy",)

        required = self._required_categories(resource)
        return self._consent_store.has_consent(pid, required)

    def filter_resources(
        self,
        resources: list[dict[str, Any]],
        patient_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Filter a list of resources by consent status.

        Args:
            resources: List of FHIR resources to filter.
            patient_id: Override patient ID for all resources.

        Returns:
            A list of accessible resources.
        """
        return [r for r in resources if self.is_accessible(r, patient_id=patient_id)]

    def filter_bundle(
        self,
        bundle: dict[str, Any],
        patient_id: str | None = None,
    ) -> dict[str, Any]:
        """Filter a FHIR Bundle by consent status.

        Removes entries whose resources do not pass consent checks.

        Args:
            bundle: A FHIR Bundle resource dict.
            patient_id: Override patient ID for all entries.

        Returns:
            A new Bundle containing only accessible entries.
        """
        entries = bundle.get("entry", [])
        filtered = [
            entry
            for entry in entries
            if self.is_accessible(
                entry.get("resource", {}),
                patient_id=patient_id,
            )
        ]
        return {
            **bundle,
            "total": len(filtered),
            "entry": filtered,
        }
