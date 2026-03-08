"""Site data harmonization interfaces.

Provides schema mapping, value-set alignment, temporal
alignment (timezone and date-format normalization), and data
quality scoring for cross-site federation in the National MCP
PAI Oncology Trials platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MappingDirection(Enum):
    """Direction of a schema mapping."""

    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"
    BIDIRECTIONAL = "bidirectional"


class QualityDimension(Enum):
    """Dimensions of data quality assessment."""

    COMPLETENESS = "completeness"
    CONFORMANCE = "conformance"
    PLAUSIBILITY = "plausibility"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"


@dataclass(frozen=True)
class FieldMapping:
    """Maps a field from one schema to another."""

    source_field: str
    target_field: str
    transform: str = ""
    direction: MappingDirection = MappingDirection.SOURCE_TO_TARGET
    notes: str = ""


@dataclass(frozen=True)
class SchemaMap:
    """A complete mapping between two site schemas."""

    map_id: str
    source_site_id: str
    target_site_id: str
    field_mappings: list[FieldMapping] = field(default_factory=list)
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValueSetEntry:
    """A single entry in a value-set alignment table."""

    source_code: str
    source_display: str
    target_code: str
    target_display: str
    equivalence: str = "equivalent"


@dataclass(frozen=True)
class ValueSetAlignment:
    """Alignment between two coded value sets."""

    alignment_id: str
    source_system: str
    target_system: str
    entries: list[ValueSetEntry] = field(default_factory=list)
    unmapped_source_codes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TemporalConfig:
    """Temporal alignment configuration for a site."""

    site_id: str
    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%dT%H:%M:%S%z"
    epoch_reference: str = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class QualityScore:
    """Data quality score for a single dimension."""

    dimension: QualityDimension
    score: float
    max_score: float = 1.0
    details: str = ""


@dataclass
class DataQualityReport:
    """Comprehensive data quality report for a site."""

    site_id: str
    scores: list[QualityScore] = field(default_factory=list)
    overall_score: float = 0.0
    record_count: int = 0
    issues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def compute_overall(self) -> float:
        """Compute and store the weighted overall score.

        Uses equal weighting across all dimensions.

        Returns
        -------
        float
            The computed overall score (0.0 -- 1.0).
        """
        if not self.scores:
            self.overall_score = 0.0
            return 0.0
        total = sum(s.score / s.max_score for s in self.scores)
        self.overall_score = total / len(self.scores)
        return self.overall_score


class SiteHarmonizationAdapter(ABC):
    """Abstract adapter for cross-site data harmonization.

    Implementations bridge heterogeneous site schemas, coded
    value sets, and temporal conventions into a common
    federation-ready format.
    """

    # -- schema mapping -------------------------------------

    @abstractmethod
    async def get_schema_map(
        self,
        source_site_id: str,
        target_site_id: str,
    ) -> SchemaMap:
        """Retrieve the schema mapping between two sites.

        Raises
        ------
        KeyError
            If no mapping exists.
        """

    @abstractmethod
    async def create_schema_map(
        self,
        source_site_id: str,
        target_site_id: str,
        field_mappings: list[FieldMapping],
        *,
        version: str = "1.0",
    ) -> SchemaMap:
        """Create or update a schema mapping."""

    @abstractmethod
    async def apply_schema_map(
        self,
        schema_map: SchemaMap,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Transform records using a schema mapping.

        Returns
        -------
        list[dict[str, Any]]
            Transformed records in the target schema.
        """

    # -- value-set alignment --------------------------------

    @abstractmethod
    async def get_value_set_alignment(
        self,
        source_system: str,
        target_system: str,
    ) -> ValueSetAlignment:
        """Retrieve a value-set alignment."""

    @abstractmethod
    async def align_values(
        self,
        alignment: ValueSetAlignment,
        source_codes: list[str],
    ) -> list[str | None]:
        """Map source codes to target codes.

        Returns ``None`` for unmapped codes.
        """

    # -- temporal alignment ---------------------------------

    @abstractmethod
    async def get_temporal_config(self, site_id: str) -> TemporalConfig:
        """Retrieve temporal alignment config for a site."""

    @abstractmethod
    async def normalize_timestamps(
        self,
        site_id: str,
        timestamps: list[str],
        *,
        target_timezone: str = "UTC",
        target_format: str = "%Y-%m-%dT%H:%M:%S%z",
    ) -> list[str]:
        """Normalize timestamps to a common format.

        Parameters
        ----------
        site_id:
            Source site whose temporal config applies.
        timestamps:
            Raw timestamp strings from the source site.
        target_timezone:
            Desired output timezone.
        target_format:
            Desired output ``strftime`` format.

        Returns
        -------
        list[str]
            Normalized timestamp strings.
        """

    # -- data quality scoring -------------------------------

    @abstractmethod
    async def assess_quality(
        self,
        site_id: str,
        records: list[dict[str, Any]],
    ) -> DataQualityReport:
        """Assess data quality for a site's records.

        Returns
        -------
        DataQualityReport
            Scored quality report.
        """
