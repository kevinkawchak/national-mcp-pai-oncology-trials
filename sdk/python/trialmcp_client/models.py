"""Typed data models for the National MCP-PAI Oncology Trials SDK.

All models use :mod:`dataclasses` and are designed to mirror the JSON schemas
published in ``schemas/``.  They provide type-safe, IDE-friendly
representations of authorization decisions, audit records, provenance records,
task orders, and clinical resources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Effect(str, Enum):
    """Authorization policy evaluation outcome."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class SourceType(str, Enum):
    """Category of a provenance data source."""

    FHIR_RESOURCE = "fhir_resource"
    DICOM_STUDY = "dicom_study"
    MODEL_PARAMETERS = "model_parameters"
    ROBOT_TELEMETRY = "robot_telemetry"
    CLINICAL_OBSERVATION = "clinical_observation"


class ProvenanceAction(str, Enum):
    """Operation performed on a provenance data source."""

    READ = "read"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"
    DERIVE = "derive"
    EXPORT = "export"


class TaskStatus(str, Enum):
    """Current status of a clinical task order."""

    SCHEDULED = "scheduled"
    SAFETY_CHECK = "safety_check"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ProcedureType(str, Enum):
    """Type of clinical procedure for a Physical AI task order."""

    TUMOR_RESECTION = "tumor_resection"
    BIOPSY_NEEDLE_PLACEMENT = "biopsy_needle_placement"
    RADIATION_POSITIONING = "radiation_positioning"
    REHABILITATION_SESSION = "rehabilitation_session"
    DIAGNOSTIC_IMAGING_ASSIST = "diagnostic_imaging_assist"
    PATIENT_MONITORING = "patient_monitoring"


class SafetyCheckStatus(str, Enum):
    """Status of an individual safety prerequisite check."""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"


class StudyStatus(str, Enum):
    """Clinical study lifecycle status."""

    RECRUITING = "recruiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    WITHDRAWN = "withdrawn"


# ---------------------------------------------------------------------------
# Authorization models
# ---------------------------------------------------------------------------


@dataclass
class MatchingRule:
    """A single RBAC policy rule that matched an authorization request."""

    role: str
    server: str
    tool: str
    effect: Effect


@dataclass
class TokenInfo:
    """Session token metadata (never contains the raw token)."""

    token_hash: str
    subject: str
    expires_at: str


@dataclass
class AuthzDecision:
    """Result of an authorization evaluation from the AuthZ server.

    Mirrors ``authz-decision.schema.json``.
    """

    allowed: bool
    effect: Effect
    role: str
    server: str
    tool: str
    evaluated_at: str
    matching_rules: list[MatchingRule] = field(default_factory=list)
    deny_reason: str | None = None
    token_info: TokenInfo | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthzDecision:
        """Construct an :class:`AuthzDecision` from a raw response dict."""
        rules = [
            MatchingRule(
                role=r["role"],
                server=r["server"],
                tool=r["tool"],
                effect=Effect(r["effect"]),
            )
            for r in data.get("matching_rules", [])
        ]
        token_raw = data.get("token_info")
        token = (
            TokenInfo(
                token_hash=token_raw["token_hash"],
                subject=token_raw["subject"],
                expires_at=token_raw["expires_at"],
            )
            if token_raw
            else None
        )
        return cls(
            allowed=data["allowed"],
            effect=Effect(data["effect"]),
            role=data["role"],
            server=data["server"],
            tool=data["tool"],
            evaluated_at=data["evaluated_at"],
            matching_rules=rules,
            deny_reason=data.get("deny_reason"),
            token_info=token,
        )


@dataclass
class SessionToken:
    """An issued session token with metadata."""

    token: str
    subject: str
    role: str
    issued_at: str
    expires_at: str
    token_hash: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionToken:
        return cls(
            token=data.get("token", ""),
            subject=data.get("subject", ""),
            role=data.get("role", ""),
            issued_at=data.get("issued_at", ""),
            expires_at=data.get("expires_at", ""),
            token_hash=data.get("token_hash", ""),
        )


# ---------------------------------------------------------------------------
# Audit ledger models
# ---------------------------------------------------------------------------


@dataclass
class AuditRecord:
    """A single hash-chained audit ledger record per 21 CFR Part 11.

    Mirrors ``audit-record.schema.json``.
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditRecord:
        return cls(
            audit_id=data["audit_id"],
            timestamp=data["timestamp"],
            server=data["server"],
            tool=data["tool"],
            caller=data["caller"],
            parameters=data.get("parameters", {}),
            result_summary=data.get("result_summary", ""),
            hash=data["hash"],
            previous_hash=data["previous_hash"],
        )


@dataclass
class ChainVerification:
    """Result of an audit chain integrity verification."""

    valid: bool
    records_checked: int
    first_record_id: str | None = None
    last_record_id: str | None = None
    broken_at_id: str | None = None
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Provenance models
# ---------------------------------------------------------------------------


@dataclass
class ProvenanceRecord:
    """A single provenance DAG node tracking data lineage.

    Mirrors ``provenance-record.schema.json``.
    """

    record_id: str
    source_id: str
    action: ProvenanceAction
    actor_id: str
    actor_role: str
    tool_call: str
    timestamp: str
    source_type: SourceType | None = None
    input_hash: str | None = None
    output_hash: str | None = None
    origin_server: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceRecord:
        source_type = None
        if data.get("source_type"):
            source_type = SourceType(data["source_type"])
        return cls(
            record_id=data["record_id"],
            source_id=data["source_id"],
            action=ProvenanceAction(data["action"]),
            actor_id=data["actor_id"],
            actor_role=data["actor_role"],
            tool_call=data["tool_call"],
            timestamp=data["timestamp"],
            source_type=source_type,
            input_hash=data.get("input_hash"),
            output_hash=data.get("output_hash"),
            origin_server=data.get("origin_server"),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProvenanceVerification:
    """Result of a provenance chain integrity verification."""

    valid: bool
    records_checked: int
    broken_links: list[str] = field(default_factory=list)
    error_message: str | None = None


# ---------------------------------------------------------------------------
# FHIR models
# ---------------------------------------------------------------------------


@dataclass
class FHIRResource:
    """A de-identified FHIR resource returned by the FHIR server."""

    resource_type: str
    resource_id: str
    data: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FHIRResource:
        return cls(
            resource_type=data.get("resource_type", data.get("resourceType", "")),
            resource_id=data.get("resource_id", data.get("id", "")),
            data=data,
            meta=data.get("meta", {}),
        )


@dataclass
class FHIRSearchResult:
    """Result set from a FHIR search operation."""

    total: int
    resources: list[FHIRResource] = field(default_factory=list)
    next_page_token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FHIRSearchResult:
        entries = data.get("entries", data.get("resources", []))
        resources = [FHIRResource.from_dict(e) for e in entries]
        return cls(
            total=data.get("total", len(resources)),
            resources=resources,
            next_page_token=data.get("next_page_token"),
        )


@dataclass
class StudyStatusResult:
    """Status information for a clinical study."""

    study_id: str
    status: str
    title: str = ""
    enrollment_count: int = 0
    site_count: int = 0
    last_updated: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StudyStatusResult:
        return cls(
            study_id=data.get("study_id", ""),
            status=data.get("status", ""),
            title=data.get("title", ""),
            enrollment_count=data.get("enrollment_count", 0),
            site_count=data.get("site_count", 0),
            last_updated=data.get("last_updated", ""),
            details=data,
        )


# ---------------------------------------------------------------------------
# DICOM models
# ---------------------------------------------------------------------------


@dataclass
class DICOMStudy:
    """A DICOM imaging study summary."""

    study_instance_uid: str
    patient_pseudonym: str = ""
    study_date: str = ""
    modality: str = ""
    description: str = ""
    series_count: int = 0
    instance_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DICOMStudy:
        return cls(
            study_instance_uid=data.get("study_instance_uid", ""),
            patient_pseudonym=data.get("patient_pseudonym", ""),
            study_date=data.get("study_date", ""),
            modality=data.get("modality", ""),
            description=data.get("description", ""),
            series_count=data.get("series_count", 0),
            instance_count=data.get("instance_count", 0),
            metadata=data,
        )


@dataclass
class DICOMQueryResult:
    """Result set from a DICOM query operation."""

    studies: list[DICOMStudy] = field(default_factory=list)
    total: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DICOMQueryResult:
        studies_raw = data.get("studies", [])
        studies = [DICOMStudy.from_dict(s) for s in studies_raw]
        return cls(studies=studies, total=data.get("total", len(studies)))


@dataclass
class DICOMRetrieveResult:
    """Result of a DICOM retrieve operation."""

    study_instance_uid: str
    series_retrieved: int = 0
    instances_retrieved: int = 0
    storage_path: str = ""
    transfer_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DICOMRetrieveResult:
        return cls(
            study_instance_uid=data.get("study_instance_uid", ""),
            series_retrieved=data.get("series_retrieved", 0),
            instances_retrieved=data.get("instances_retrieved", 0),
            storage_path=data.get("storage_path", ""),
            transfer_hash=data.get("transfer_hash", ""),
            metadata=data,
        )


# ---------------------------------------------------------------------------
# Task order models
# ---------------------------------------------------------------------------


@dataclass
class SafetyPrerequisite:
    """A single safety check required before task execution."""

    check_name: str
    status: SafetyCheckStatus

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SafetyPrerequisite:
        return cls(
            check_name=data["check_name"],
            status=SafetyCheckStatus(data["status"]),
        )


@dataclass
class TaskOrder:
    """A scheduled clinical task for a Physical AI system.

    Mirrors ``task-order.schema.json``.
    """

    task_id: str
    trial_id: str
    site_id: str
    procedure_type: ProcedureType
    robot_id: str
    status: TaskStatus
    scheduled_at: str
    patient_pseudonym: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    safety_prerequisites: list[SafetyPrerequisite] = field(default_factory=list)
    usl_score_minimum: float = 1.0
    mcp_tools_used: list[str] = field(default_factory=list)
    audit_record_ids: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskOrder:
        prereqs = [SafetyPrerequisite.from_dict(p) for p in data.get("safety_prerequisites", [])]
        return cls(
            task_id=data["task_id"],
            trial_id=data["trial_id"],
            site_id=data["site_id"],
            procedure_type=ProcedureType(data["procedure_type"]),
            robot_id=data["robot_id"],
            status=TaskStatus(data["status"]),
            scheduled_at=data["scheduled_at"],
            patient_pseudonym=data.get("patient_pseudonym", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            safety_prerequisites=prereqs,
            usl_score_minimum=data.get("usl_score_minimum", 1.0),
            mcp_tools_used=data.get("mcp_tools_used", []),
            audit_record_ids=data.get("audit_record_ids", []),
            notes=data.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
