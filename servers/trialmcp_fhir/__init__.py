"""trialmcp-fhir — FHIR Clinical Data MCP Server.

Implements FHIR R4 clinical data access with mandatory HIPAA Safe Harbor
de-identification, HMAC-SHA256 pseudonymization, and role-based access.

Tools:
    fhir_read          — Read a single de-identified FHIR resource
    fhir_search        — Search for de-identified FHIR resources
    fhir_patient_lookup — Look up a pseudonymized patient
    fhir_study_status  — Get trial study status
"""

from servers.trialmcp_fhir.deid_pipeline import DeidentificationPipeline
from servers.trialmcp_fhir.fhir_adapter import FHIRAdapter, MockFHIRAdapter
from servers.trialmcp_fhir.server import FHIRServer

__all__ = [
    "DeidentificationPipeline",
    "FHIRAdapter",
    "FHIRServer",
    "MockFHIRAdapter",
]
