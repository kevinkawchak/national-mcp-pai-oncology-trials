"""Terminology mapping hooks for oncology code systems.

Provides lookup interfaces and cross-system mapping for ICD-10-CM,
SNOMED CT, LOINC, and RxNorm code systems.  Includes sample
oncology-relevant codes for lung cancer, breast cancer, prostate
cancer, common tumor markers, and chemotherapy agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# -----------------------------------------------------------------------
# Data model
# -----------------------------------------------------------------------


@dataclass(frozen=True)
class CodeEntry:
    """A single code in a terminology system.

    Attributes:
        system: The code system URI.
        code: The code value.
        display: Human-readable display text.
    """

    system: str
    code: str
    display: str


@dataclass
class CodeMapping:
    """A mapping between codes in different systems.

    Attributes:
        source: The source code entry.
        target: The target code entry.
        equivalence: FHIR ConceptMap equivalence value.
    """

    source: CodeEntry
    target: CodeEntry
    equivalence: str = "equivalent"


# -----------------------------------------------------------------------
# Code system URIs
# -----------------------------------------------------------------------

ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"
SNOMED_SYSTEM = "http://snomed.info/sct"
LOINC_SYSTEM = "http://loinc.org"
RXNORM_SYSTEM = "http://www.nlm.nih.gov/research/umls/rxnorm"


# -----------------------------------------------------------------------
# Sample oncology codes
# -----------------------------------------------------------------------

_ICD10_CODES: dict[str, CodeEntry] = {
    "C34.0": CodeEntry(
        ICD10_SYSTEM,
        "C34.0",
        "Malignant neoplasm of main bronchus",
    ),
    "C34.1": CodeEntry(
        ICD10_SYSTEM,
        "C34.1",
        "Malignant neoplasm of upper lobe, bronchus or lung",
    ),
    "C34.2": CodeEntry(
        ICD10_SYSTEM,
        "C34.2",
        "Malignant neoplasm of middle lobe, bronchus or lung",
    ),
    "C34.3": CodeEntry(
        ICD10_SYSTEM,
        "C34.3",
        "Malignant neoplasm of lower lobe, bronchus or lung",
    ),
    "C34.9": CodeEntry(
        ICD10_SYSTEM,
        "C34.9",
        "Malignant neoplasm of unspecified part of bronchus or lung",
    ),
    "C50.9": CodeEntry(
        ICD10_SYSTEM,
        "C50.9",
        "Malignant neoplasm of breast, unspecified",
    ),
    "C61": CodeEntry(
        ICD10_SYSTEM,
        "C61",
        "Malignant neoplasm of prostate",
    ),
    "C18.9": CodeEntry(
        ICD10_SYSTEM,
        "C18.9",
        "Malignant neoplasm of colon, unspecified",
    ),
    "C71.9": CodeEntry(
        ICD10_SYSTEM,
        "C71.9",
        "Malignant neoplasm of brain, unspecified",
    ),
}

_SNOMED_CODES: dict[str, CodeEntry] = {
    "254637007": CodeEntry(
        SNOMED_SYSTEM,
        "254637007",
        "Non-small cell lung cancer (disorder)",
    ),
    "254632001": CodeEntry(
        SNOMED_SYSTEM,
        "254632001",
        "Small cell carcinoma of lung (disorder)",
    ),
    "399068003": CodeEntry(
        SNOMED_SYSTEM,
        "399068003",
        "Malignant tumor of prostate (disorder)",
    ),
    "254837009": CodeEntry(
        SNOMED_SYSTEM,
        "254837009",
        "Malignant neoplasm of breast (disorder)",
    ),
    "363406005": CodeEntry(
        SNOMED_SYSTEM,
        "363406005",
        "Malignant neoplasm of colon (disorder)",
    ),
    "367336001": CodeEntry(
        SNOMED_SYSTEM,
        "367336001",
        "Chemotherapy (procedure)",
    ),
    "108290001": CodeEntry(
        SNOMED_SYSTEM,
        "108290001",
        "Radiation oncology AND/OR radiotherapy (procedure)",
    ),
    "387713003": CodeEntry(
        SNOMED_SYSTEM,
        "387713003",
        "Surgical procedure (procedure)",
    ),
}

_LOINC_CODES: dict[str, CodeEntry] = {
    "2857-1": CodeEntry(
        LOINC_SYSTEM,
        "2857-1",
        "Prostate specific Ag [Mass/volume] in Serum or Plasma",
    ),
    "2039-6": CodeEntry(
        LOINC_SYSTEM,
        "2039-6",
        "Carcinoembryonic Ag [Mass/volume] in Serum or Plasma",
    ),
    "21889-1": CodeEntry(
        LOINC_SYSTEM,
        "21889-1",
        "Size Tumor",
    ),
    "85319-2": CodeEntry(
        LOINC_SYSTEM,
        "85319-2",
        "HER2 [Presence] in Breast cancer specimen",
    ),
    "85337-4": CodeEntry(
        LOINC_SYSTEM,
        "85337-4",
        "Estrogen receptor Ag [Presence] in Breast cancer specimen",
    ),
    "10524-7": CodeEntry(
        LOINC_SYSTEM,
        "10524-7",
        "Microscopic observation in Tissue by Cyto stain",
    ),
    "33717-0": CodeEntry(
        LOINC_SYSTEM,
        "33717-0",
        "WhiteBloodCell count in Body fluid",
    ),
    "26499-4": CodeEntry(
        LOINC_SYSTEM,
        "26499-4",
        "Neutrophils [#/volume] in Blood",
    ),
}

_RXNORM_CODES: dict[str, CodeEntry] = {
    "51499": CodeEntry(
        RXNORM_SYSTEM,
        "51499",
        "Cisplatin",
    ),
    "4492": CodeEntry(
        RXNORM_SYSTEM,
        "4492",
        "Carboplatin",
    ),
    "56946": CodeEntry(
        RXNORM_SYSTEM,
        "56946",
        "Paclitaxel",
    ),
    "72962": CodeEntry(
        RXNORM_SYSTEM,
        "72962",
        "Docetaxel",
    ),
    "194000": CodeEntry(
        RXNORM_SYSTEM,
        "194000",
        "Pembrolizumab",
    ),
    "1313988": CodeEntry(
        RXNORM_SYSTEM,
        "1313988",
        "Nivolumab",
    ),
    "258494": CodeEntry(
        RXNORM_SYSTEM,
        "258494",
        "Bevacizumab",
    ),
    "6851": CodeEntry(
        RXNORM_SYSTEM,
        "6851",
        "Methotrexate",
    ),
}

# ICD-10 to SNOMED mappings
_ICD10_TO_SNOMED: list[CodeMapping] = [
    CodeMapping(
        _ICD10_CODES["C34.1"],
        _SNOMED_CODES["254637007"],
    ),
    CodeMapping(
        _ICD10_CODES["C61"],
        _SNOMED_CODES["399068003"],
    ),
    CodeMapping(
        _ICD10_CODES["C50.9"],
        _SNOMED_CODES["254837009"],
    ),
    CodeMapping(
        _ICD10_CODES["C18.9"],
        _SNOMED_CODES["363406005"],
    ),
]


# -----------------------------------------------------------------------
# Registry
# -----------------------------------------------------------------------


@dataclass
class TerminologyRegistry:
    """Registry of terminology code systems and cross-system mappings.

    Provides lookup and mapping interfaces for ICD-10-CM, SNOMED CT,
    LOINC, and RxNorm with pre-loaded oncology-relevant codes.
    """

    _code_systems: dict[str, dict[str, CodeEntry]] = field(
        default_factory=dict,
    )
    _mappings: list[CodeMapping] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Load default code systems and mappings."""
        if not self._code_systems:
            self._code_systems = {
                ICD10_SYSTEM: dict(_ICD10_CODES),
                SNOMED_SYSTEM: dict(_SNOMED_CODES),
                LOINC_SYSTEM: dict(_LOINC_CODES),
                RXNORM_SYSTEM: dict(_RXNORM_CODES),
            }
        if not self._mappings:
            self._mappings = list(_ICD10_TO_SNOMED)

    # ---------------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------------

    def lookup(
        self,
        system: str,
        code: str,
    ) -> CodeEntry | None:
        """Look up a code in a specific code system.

        Args:
            system: The code system URI.
            code: The code value to look up.

        Returns:
            The matching :class:`CodeEntry`, or ``None``.
        """
        return self._code_systems.get(system, {}).get(code)

    def lookup_display(
        self,
        system: str,
        code: str,
    ) -> str:
        """Return the display text for a code, or the code itself.

        Args:
            system: The code system URI.
            code: The code value.

        Returns:
            The display string, or the raw code if not found.
        """
        entry = self.lookup(system, code)
        return entry.display if entry else code

    def codes_in_system(self, system: str) -> list[CodeEntry]:
        """Return all known codes in a code system.

        Args:
            system: The code system URI.

        Returns:
            A list of :class:`CodeEntry` instances.
        """
        return list(self._code_systems.get(system, {}).values())

    # ---------------------------------------------------------------
    # Cross-system mapping
    # ---------------------------------------------------------------

    def map_code(
        self,
        source_system: str,
        source_code: str,
        target_system: str,
    ) -> list[CodeEntry]:
        """Map a code from one system to another.

        Args:
            source_system: URI of the source code system.
            source_code: The source code value.
            target_system: URI of the target code system.

        Returns:
            A list of matching target :class:`CodeEntry` instances.
        """
        results: list[CodeEntry] = []
        for mapping in self._mappings:
            src = mapping.source
            tgt = mapping.target
            if (
                src.system == source_system
                and src.code == source_code
                and tgt.system == target_system
            ):
                results.append(tgt)
            elif (
                tgt.system == source_system
                and tgt.code == source_code
                and src.system == target_system
            ):
                results.append(src)
        return results

    def add_code(
        self,
        system: str,
        code: str,
        display: str,
    ) -> CodeEntry:
        """Register a new code in a code system.

        Args:
            system: The code system URI.
            code: The code value.
            display: Human-readable display text.

        Returns:
            The newly created :class:`CodeEntry`.
        """
        entry = CodeEntry(system, code, display)
        self._code_systems.setdefault(system, {})[code] = entry
        return entry

    def add_mapping(
        self,
        source: CodeEntry,
        target: CodeEntry,
        equivalence: str = "equivalent",
    ) -> CodeMapping:
        """Register a cross-system code mapping.

        Args:
            source: The source code entry.
            target: The target code entry.
            equivalence: FHIR ConceptMap equivalence value.

        Returns:
            The newly created :class:`CodeMapping`.
        """
        mapping = CodeMapping(source, target, equivalence)
        self._mappings.append(mapping)
        return mapping

    # ---------------------------------------------------------------
    # FHIR coding helpers
    # ---------------------------------------------------------------

    def to_fhir_coding(
        self,
        system: str,
        code: str,
    ) -> dict[str, str] | None:
        """Convert a code to a FHIR Coding dict.

        Args:
            system: The code system URI.
            code: The code value.

        Returns:
            A FHIR Coding dict, or ``None`` if the code is unknown.
        """
        entry = self.lookup(system, code)
        if entry is None:
            return None
        return {
            "system": entry.system,
            "code": entry.code,
            "display": entry.display,
        }

    def to_fhir_codeable_concept(
        self,
        system: str,
        code: str,
    ) -> dict[str, Any] | None:
        """Convert a code to a FHIR CodeableConcept dict.

        Args:
            system: The code system URI.
            code: The code value.

        Returns:
            A FHIR CodeableConcept dict, or ``None`` if unknown.
        """
        coding = self.to_fhir_coding(system, code)
        if coding is None:
            return None
        return {
            "coding": [coding],
            "text": coding["display"],
        }
