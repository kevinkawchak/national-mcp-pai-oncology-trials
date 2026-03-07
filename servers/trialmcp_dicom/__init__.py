"""trialmcp-dicom — DICOM Imaging MCP Server.

Implements DICOM query/retrieve with role-based modality restrictions,
DICOM UID validation, and patient name hashing.

Tools:
    dicom_query    — Query DICOM studies/series/instances
    dicom_retrieve — Retrieve DICOM metadata (pointer-based, no pixel data)
"""

from servers.trialmcp_dicom.dicom_adapter import DICOMAdapter, MockDICOMAdapter
from servers.trialmcp_dicom.server import DICOMServer

__all__ = [
    "DICOMAdapter",
    "DICOMServer",
    "MockDICOMAdapter",
]
