"""DICOM integration adapters for National MCP PAI Oncology Trials.

This package provides production-grade DICOM integration adapters
for physical AI oncology clinical trials operating under the
national MCP standard. Adapters support metadata-only access
patterns with strict safety constraints prohibiting pixel data
transfer.

Modules:
    base_adapter: Abstract DICOM adapter interface.
    mock_adapter: Mock adapter with synthetic imaging metadata.
    orthanc_adapter: Orthanc DICOM server adapter.
    dcm4chee_adapter: dcm4chee DICOM archive adapter.
    dicomweb: DICOMweb (QIDO-RS, WADO-RS, STOW-RS) support.
    metadata_normalizer: DICOM metadata normalization utilities.
    modality_filter: Role-based modality restriction enforcement.
    recist: RECIST 1.1 measurement validation and examples.
    safety: Image reference safety constraints enforcement.
"""

from __future__ import annotations

from integrations.dicom.base_adapter import (
    BaseDicomAdapter,
    QueryLevel,
)
from integrations.dicom.mock_adapter import MockDicomAdapter
from integrations.dicom.modality_filter import ModalityFilter
from integrations.dicom.safety import SafetyValidator

__all__ = [
    "BaseDicomAdapter",
    "MockDicomAdapter",
    "ModalityFilter",
    "QueryLevel",
    "SafetyValidator",
]
