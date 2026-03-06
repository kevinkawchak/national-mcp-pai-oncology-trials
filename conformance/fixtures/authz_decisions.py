"""Sample authorization decisions for conformance testing.

Extracted from schemas/authz-decision.schema.json and spec/security.md.
Provides ALLOW and DENY decision fixtures for deny-by-default RBAC testing.
"""

from __future__ import annotations

# 6 actors per spec/actor-model.md
VALID_ROLES = [
    "robot_agent",
    "trial_coordinator",
    "data_monitor",
    "auditor",
    "sponsor",
    "cro",
]

# Default RBAC permission matrix (simplified) per spec/actor-model.md
# Maps role -> list of (server, tool) tuples that are ALLOWED
DEFAULT_ALLOW_RULES: dict[str, list[tuple[str, str]]] = {
    "robot_agent": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_validate_token"),
        ("trialmcp-fhir", "fhir_read"),
        ("trialmcp-fhir", "fhir_search"),
        ("trialmcp-fhir", "fhir_patient_lookup"),
        ("trialmcp-dicom", "dicom_query"),
        ("trialmcp-dicom", "dicom_retrieve_pointer"),
        ("trialmcp-dicom", "dicom_study_metadata"),
        ("trialmcp-dicom", "dicom_recist_measurements"),
        ("trialmcp-ledger", "ledger_append"),
        ("trialmcp-provenance", "provenance_record_access"),
        ("trialmcp-provenance", "provenance_get_lineage"),
    ],
    "trial_coordinator": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_issue_token"),
        ("trialmcp-authz", "authz_validate_token"),
        ("trialmcp-authz", "authz_list_policies"),
        ("trialmcp-authz", "authz_revoke_token"),
        ("trialmcp-fhir", "fhir_read"),
        ("trialmcp-fhir", "fhir_search"),
        ("trialmcp-fhir", "fhir_patient_lookup"),
        ("trialmcp-fhir", "fhir_study_status"),
        ("trialmcp-dicom", "dicom_query"),
        ("trialmcp-dicom", "dicom_retrieve_pointer"),
        ("trialmcp-dicom", "dicom_study_metadata"),
        ("trialmcp-dicom", "dicom_recist_measurements"),
        ("trialmcp-ledger", "ledger_append"),
        ("trialmcp-ledger", "ledger_query"),
        ("trialmcp-provenance", "provenance_register_source"),
        ("trialmcp-provenance", "provenance_record_access"),
    ],
    "data_monitor": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_validate_token"),
        ("trialmcp-fhir", "fhir_read"),
        ("trialmcp-fhir", "fhir_search"),
        ("trialmcp-fhir", "fhir_patient_lookup"),
        ("trialmcp-fhir", "fhir_study_status"),
        ("trialmcp-dicom", "dicom_query"),
        ("trialmcp-dicom", "dicom_study_metadata"),
    ],
    "auditor": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_validate_token"),
        ("trialmcp-ledger", "ledger_verify"),
        ("trialmcp-ledger", "ledger_query"),
        ("trialmcp-ledger", "ledger_replay"),
        ("trialmcp-ledger", "ledger_chain_status"),
    ],
    "sponsor": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_list_policies"),
    ],
    "cro": [
        ("trialmcp-authz", "authz_evaluate"),
        ("trialmcp-authz", "authz_list_policies"),
        ("trialmcp-authz", "authz_validate_token"),
    ],
}


def make_allow_decision(
    role: str = "robot_agent",
    server: str = "trialmcp-fhir",
    tool: str = "fhir_read",
) -> dict:
    """Create a well-formed ALLOW authorization decision."""
    return {
        "allowed": True,
        "effect": "ALLOW",
        "role": role,
        "server": server,
        "tool": tool,
        "matching_rules": [
            {
                "role": role,
                "server": server,
                "tool": tool,
                "effect": "ALLOW",
            },
        ],
        "evaluated_at": "2026-03-06T14:29:55Z",
    }


def make_deny_decision(
    role: str = "data_monitor",
    server: str = "trialmcp-provenance",
    tool: str = "provenance_record_access",
    reason: str = "No matching ALLOW rule found; deny-by-default policy applied",
) -> dict:
    """Create a well-formed DENY authorization decision."""
    return {
        "allowed": False,
        "effect": "DENY",
        "role": role,
        "server": server,
        "tool": tool,
        "matching_rules": [],
        "evaluated_at": "2026-03-06T14:30:10Z",
        "deny_reason": reason,
    }


# Pre-built fixtures: known unauthorized access attempts
UNAUTHORIZED_ACCESS_ATTEMPTS = [
    # data_monitor cannot write provenance
    {"role": "data_monitor", "server": "trialmcp-provenance", "tool": "provenance_record_access"},
    # auditor cannot read FHIR resources
    {"role": "auditor", "server": "trialmcp-fhir", "tool": "fhir_read"},
    # sponsor cannot invoke ledger tools
    {"role": "sponsor", "server": "trialmcp-ledger", "tool": "ledger_append"},
    # cro cannot query DICOM
    {"role": "cro", "server": "trialmcp-dicom", "tool": "dicom_query"},
    # robot_agent cannot revoke tokens
    {"role": "robot_agent", "server": "trialmcp-authz", "tool": "authz_revoke_token"},
    # data_monitor cannot retrieve DICOM images
    {"role": "data_monitor", "server": "trialmcp-dicom", "tool": "dicom_retrieve_pointer"},
]
