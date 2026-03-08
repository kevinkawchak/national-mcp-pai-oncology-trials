"""National MCP-PAI Oncology Trials — Python Client SDK.

This SDK provides a typed, async Python client for the five MCP servers
that comprise the National MCP-PAI Oncology Clinical Trials network:

* **AuthZ** — role-based access control and session tokens
* **FHIR** — de-identified clinical data (patients, studies, observations)
* **DICOM** — pseudonymised medical imaging
* **Ledger** — SHA-256 hash-chained audit log (21 CFR Part 11)
* **Provenance** — data lineage DAG

Quick start::

    from trialmcp_client import TrialMCPClient, ClientConfig, ActorRole

    config = ClientConfig()
    config.auth.actor_id = "robot_agent_001"
    config.auth.role = ActorRole.ROBOT_AGENT

    async with TrialMCPClient(config) as client:
        decision = await client.authz.evaluate(
            role="robot_agent",
            server="trialmcp-fhir",
            tool="fhir_read",
        )
        print(decision.allowed)
"""

from __future__ import annotations

from .authz import AuthzClient
from .client import TrialMCPClient
from .config import (
    ActorRole,
    AuthCredentials,
    CircuitBreakerPolicy,
    ClientConfig,
    RetryPolicy,
    ServerEndpoint,
    ServerName,
    config_from_env,
)
from .dicom import DICOMClient
from .exceptions import (
    AuthzDeniedError,
    AuthzExpiredError,
    ChainBrokenError,
    InvalidInputError,
    NotFoundError,
    PermissionDeniedError,
    PHILeakError,
    RateLimitedError,
    ServerError,
    TrialMCPError,
    UnavailableError,
)
from .fhir import FHIRClient
from .ledger import LedgerClient
from .models import (
    AuditRecord,
    AuthzDecision,
    ChainVerification,
    DICOMQueryResult,
    DICOMRetrieveResult,
    DICOMStudy,
    Effect,
    FHIRResource,
    FHIRSearchResult,
    MatchingRule,
    ProvenanceAction,
    ProvenanceRecord,
    ProvenanceVerification,
    SafetyCheckStatus,
    SafetyPrerequisite,
    SessionToken,
    SourceType,
    StudyStatus,
    StudyStatusResult,
    TaskOrder,
    TaskStatus,
    TokenInfo,
)
from .provenance import ProvenanceClient

__version__ = "0.9.0"

__all__ = [
    # Core client
    "TrialMCPClient",
    # Sub-clients
    "AuthzClient",
    "DICOMClient",
    "FHIRClient",
    "LedgerClient",
    "ProvenanceClient",
    # Configuration
    "ActorRole",
    "AuthCredentials",
    "CircuitBreakerPolicy",
    "ClientConfig",
    "RetryPolicy",
    "ServerEndpoint",
    "ServerName",
    "config_from_env",
    # Models
    "AuditRecord",
    "AuthzDecision",
    "ChainVerification",
    "DICOMQueryResult",
    "DICOMRetrieveResult",
    "DICOMStudy",
    "Effect",
    "FHIRResource",
    "FHIRSearchResult",
    "MatchingRule",
    "ProvenanceAction",
    "ProvenanceRecord",
    "ProvenanceVerification",
    "SafetyCheckStatus",
    "SafetyPrerequisite",
    "SessionToken",
    "SourceType",
    "StudyStatus",
    "StudyStatusResult",
    "TaskOrder",
    "TaskStatus",
    "TokenInfo",
    # Exceptions
    "AuthzDeniedError",
    "AuthzExpiredError",
    "ChainBrokenError",
    "InvalidInputError",
    "NotFoundError",
    "PermissionDeniedError",
    "PHILeakError",
    "RateLimitedError",
    "ServerError",
    "TrialMCPError",
    "UnavailableError",
]
