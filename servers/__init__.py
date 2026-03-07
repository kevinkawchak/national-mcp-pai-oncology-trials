"""National MCP-PAI Oncology Trials — Production-shaped MCP server packages.

This package contains five domain-specific MCP servers implementing the
National MCP-PAI Oncology Trials Standard:

- trialmcp_authz    — Authorization server (deny-by-default RBAC)
- trialmcp_fhir     — FHIR clinical data server (HIPAA Safe Harbor)
- trialmcp_dicom    — DICOM imaging server (role-based modality)
- trialmcp_ledger   — Audit ledger server (hash-chained immutable ledger)
- trialmcp_provenance — Provenance server (DAG-based lineage)

Shared infrastructure lives in servers.common and servers.storage.
"""

__version__ = "0.7.0"
