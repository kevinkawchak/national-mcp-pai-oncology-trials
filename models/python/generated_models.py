"""Auto-generated typed models from /schemas/*.schema.json.

DO NOT EDIT — regenerate with: python scripts/generate_models.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AuditRecord:
    """Audit Record.

    Defines a single hash-chained audit ledger record as specified by the National MCP-PAI
    Oncology Trials Standard. Derived from the ledger_server.py AuditRecord dataclass.
    Each record is linked to its predecessor via SHA-256 hashing for 21 CFR Part 11
    compliance.
    """

    audit_id: str
    timestamp: str
    server: str
    tool: str
    caller: str
    parameters: dict[str, Any]
    result_summary: str
    hash: str
    previous_hash: str


@dataclass
class AuthzDecision:
    """Authorization Decision.

    Represents the result of an authorization evaluation from the AuthZ server's policy
    engine. Derived from authz_server.py evaluate return shape. Implements deny-by-default
    RBAC with explicit DENY precedence over ALLOW.
    """

    allowed: bool
    effect: str
    role: str
    server: str
    tool: str
    evaluated_at: str
    matching_rules: list[dict[str, Any]] | None = None
    deny_reason: str | None = None
    token_info: dict[str, Any] | None = None


@dataclass
class CapabilityDescriptor:
    """MCP Server Capability Descriptor.

    Describes the capabilities advertised by a conforming MCP server in the National MCP-
    PAI Oncology Trials network, including the server name, version, supported tools, and
    conformance level.
    """

    server_name: str
    version: str
    conformance_level: int
    tools: list[str]
    vendor_extensions: list[str] | None = None
    regulatory_certifications: list[str] | None = None
    contact: dict[str, Any] | None = None


@dataclass
class ConsentStatus:
    """Consent Status.

    Represents the consent state machine for a patient participating in a Physical AI
    oncology clinical trial. Tracks informed consent for robotic procedure involvement,
    data sharing, and federated learning participation.
    """

    consent_id: str
    patient_pseudonym: str
    trial_id: str
    consent_state: str
    consent_categories: list[dict[str, Any]]
    recorded_at: str
    recorded_by: str | None = None
    site_id: str | None = None
    irb_protocol_version: str | None = None
    electronic_signature: dict[str, Any] | None = None
    state_history: list[dict[str, Any]] | None = None


@dataclass
class DicomQuery:
    """DICOM Query.

    Defines the input parameters and output shape for the dicom_query MCP tool. Derived
    from dicom_server.py dicom_query handler. Supports hierarchical DICOM query levels
    with role-based access control and patient-name hashing.
    """

    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    permissions: dict[str, Any] | None = None
    errors: list[str] | None = None


@dataclass
class ErrorResponse:
    """Error Response.

    Standardized error response format for all MCP servers in the National MCP-PAI
    Oncology Trials network. Derived from servers/common/__init__.py error_response()
    helper. All conforming servers MUST use this format for error responses.
    """

    error: bool
    code: str
    message: str
    server: str | None = None
    tool: str | None = None
    timestamp: str | None = None
    request_id: str | None = None
    details: dict[str, Any] | None = None


@dataclass
class FhirRead:
    """FHIR Read.

    Defines the input parameters and output shape for the fhir_read MCP tool. Derived from
    fhir_server.py fhir_read handler. Returns a single de-identified FHIR R4 resource with
    HIPAA Safe Harbor applied.
    """

    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    errors: list[str] | None = None


@dataclass
class FhirSearch:
    """FHIR Search.

    Defines the input parameters and output shape for the fhir_search MCP tool. Derived
    from fhir_server.py fhir_search handler. Returns a collection of de-identified FHIR R4
    resources matching the search criteria, capped at 100 results.
    """

    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    errors: list[str] | None = None


@dataclass
class HealthStatus:
    """Health Status.

    Standardized health check response for MCP servers in the National MCP-PAI Oncology
    Trials network. Derived from servers/common/__init__.py health_status() helper. Used
    by monitoring systems and the federated coordination layer to track server
    availability across all national sites.
    """

    server_name: str
    status: str
    version: str
    uptime_seconds: float
    checked_at: str
    conformance_level: int | None = None
    dependencies: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None
    site_id: str | None = None


@dataclass
class ProvenanceRecord:
    """Provenance Record.

    Tracks a single data access or transformation event in the provenance DAG. Derived
    from provenance_server.py ProvenanceRecord and DataSource fields. Supports SHA-256
    fingerprinting for data integrity verification.
    """

    record_id: str
    source_id: str
    action: str
    actor_id: str
    actor_role: str
    tool_call: str
    timestamp: str
    source_type: str | None = None
    input_hash: str | None = None
    output_hash: str | None = None
    origin_server: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RobotCapabilityProfile:
    """Robot Capability Profile.

    Describes the capabilities, safety prerequisites, and readiness scoring of a Physical
    AI robotic platform participating in oncology clinical trials. Derived from
    trial_robot_agent.py platform fields and trial_schedule.json USL scoring.
    """

    robot_id: str
    platform: str
    robot_type: str
    usl_score: float
    safety_prerequisites: list[dict[str, Any]]
    mcp_tools_required: list[str]
    simulation_frameworks: list[str] | None = None
    site_id: str | None = None
    firmware_version: str | None = None
    last_calibration: str | None = None


@dataclass
class SiteCapabilityProfile:
    """Site Capability Profile.

    Describes a clinical trial site's MCP infrastructure, jurisdiction, deployed servers,
    data residency, and conformance posture within the National MCP-PAI Oncology Trials
    network.
    """

    site_id: str
    site_name: str
    jurisdiction: dict[str, Any]
    servers: list[Any]
    conformance_level: int
    data_residency: dict[str, Any]
    site_type: str | None = None
    robots: list[Any] | None = None
    irb_approval: dict[str, Any] | None = None
    contact: dict[str, Any] | None = None


@dataclass
class TaskOrder:
    """Task Order.

    Defines a scheduled clinical trial task for a Physical AI system, including the
    assigned robot, procedure type, patient reference, safety prerequisites, and
    scheduling metadata. Derived from the trial_schedule.json structure.
    """

    task_id: str
    trial_id: str
    site_id: str
    procedure_type: str
    robot_id: str
    status: str
    scheduled_at: str
    patient_pseudonym: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    safety_prerequisites: list[dict[str, Any]] | None = None
    usl_score_minimum: float | None = None
    mcp_tools_used: list[str] | None = None
    audit_record_ids: list[str] | None = None
    notes: str | None = None
