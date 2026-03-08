"""Unified de-identification pipeline.

Handles FHIR, DICOM, and free-text de-identification through
configurable pipeline stages: detect, mask, pseudonymize, and
verify.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataType(Enum):
    """Supported data types for de-identification."""

    FHIR = "fhir"
    DICOM = "dicom"
    FREE_TEXT = "free_text"


class PipelineStage(Enum):
    """Ordered stages of the de-identification pipeline."""

    DETECT = "detect"
    MASK = "mask"
    PSEUDONYMIZE = "pseudonymize"
    VERIFY = "verify"


class PHICategory(Enum):
    """Categories of Protected Health Information."""

    NAME = "name"
    DATE = "date"
    PHONE = "phone"
    EMAIL = "email"
    SSN = "ssn"
    MRN = "mrn"
    ADDRESS = "address"
    AGE = "age"
    DEVICE_ID = "device_id"
    IP_ADDRESS = "ip_address"
    BIOMETRIC = "biometric"
    PHOTO = "photo"
    OTHER = "other"


@dataclass(frozen=True)
class DetectedPHI:
    """A detected PHI element in the source data."""

    category: PHICategory
    value: str
    location: str
    confidence: float = 1.0
    context: str = ""


@dataclass(frozen=True)
class DeidentificationAction:
    """An action applied to a detected PHI element."""

    stage: PipelineStage
    original: DetectedPHI
    replacement: str
    method: str = ""


@dataclass
class PipelineResult:
    """Result of running the de-identification pipeline."""

    data_type: DataType
    input_hash: str
    output: Any = None
    actions: list[DeidentificationAction] = field(default_factory=list)
    detected_phi: list[DetectedPHI] = field(default_factory=list)
    verification_passed: bool = False
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StageConfig:
    """Configuration for a single pipeline stage."""

    stage: PipelineStage
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Per-data-type pipeline configuration."""

    data_type: DataType
    stages: list[StageConfig] = field(
        default_factory=lambda: [
            StageConfig(stage=PipelineStage.DETECT),
            StageConfig(stage=PipelineStage.MASK),
            StageConfig(stage=PipelineStage.PSEUDONYMIZE),
            StageConfig(stage=PipelineStage.VERIFY),
        ]
    )
    phi_categories: list[PHICategory] = field(default_factory=lambda: list(PHICategory))


class DeidentificationStageHandler(ABC):
    """Abstract handler for a single pipeline stage."""

    @property
    @abstractmethod
    def stage(self) -> PipelineStage:
        """The pipeline stage this handler implements."""

    @abstractmethod
    async def process(
        self,
        data: Any,
        data_type: DataType,
        context: dict[str, Any],
    ) -> tuple[Any, list[DetectedPHI | DeidentificationAction]]:
        """Process data through this stage.

        Parameters
        ----------
        data:
            The input data (raw or partially processed).
        data_type:
            The type of clinical data.
        context:
            Shared mutable context passed between stages.

        Returns
        -------
        tuple
            Transformed data and a list of findings or
            actions produced by this stage.
        """


class DeidentificationPipeline:
    """Configurable multi-stage de-identification pipeline.

    Orchestrates detect, mask, pseudonymize, and verify stages
    across FHIR, DICOM, and free-text data types.

    Parameters
    ----------
    configs:
        Per-data-type configurations. If ``None``, default
        configs for all data types are created.
    """

    def __init__(
        self,
        configs: dict[DataType, PipelineConfig] | None = None,
    ) -> None:
        if configs is None:
            configs = {dt: PipelineConfig(data_type=dt) for dt in DataType}
        self._configs = configs
        self._handlers: dict[
            tuple[DataType, PipelineStage],
            DeidentificationStageHandler,
        ] = {}

    def register_handler(
        self,
        data_type: DataType,
        handler: DeidentificationStageHandler,
    ) -> None:
        """Register a stage handler for a data type."""
        self._handlers[(data_type, handler.stage)] = handler

    def get_config(self, data_type: DataType) -> PipelineConfig:
        """Retrieve the pipeline configuration for a data
        type.
        """
        cfg = self._configs.get(data_type)
        if cfg is None:
            cfg = PipelineConfig(data_type=data_type)
            self._configs[data_type] = cfg
        return cfg

    async def run(
        self,
        data: Any,
        data_type: DataType,
        *,
        input_hash: str = "",
    ) -> PipelineResult:
        """Execute the de-identification pipeline.

        Parameters
        ----------
        data:
            Raw input data.
        data_type:
            The clinical data type.
        input_hash:
            Optional hash of the original input for
            traceability.

        Returns
        -------
        PipelineResult
            Comprehensive result including transformed data,
            detected PHI, and applied actions.
        """
        config = self.get_config(data_type)
        result = PipelineResult(
            data_type=data_type,
            input_hash=input_hash,
        )
        context: dict[str, Any] = {
            "phi_categories": config.phi_categories,
        }
        current_data = data

        for stage_cfg in config.stages:
            if not stage_cfg.enabled:
                continue
            handler = self._handlers.get((data_type, stage_cfg.stage))
            if handler is None:
                result.errors.append(f"No handler for {data_type.value}/{stage_cfg.stage.value}")
                continue

            context["stage_options"] = stage_cfg.options
            try:
                current_data, findings = await handler.process(current_data, data_type, context)
            except Exception as exc:
                result.errors.append(f"{stage_cfg.stage.value}: {exc}")
                continue

            for item in findings:
                if isinstance(item, DetectedPHI):
                    result.detected_phi.append(item)
                elif isinstance(item, DeidentificationAction):
                    result.actions.append(item)

            if stage_cfg.stage == PipelineStage.VERIFY:
                result.verification_passed = bool(current_data)

        result.output = current_data
        return result
