"""trialmcp-provenance — Provenance MCP Server.

Implements DAG-based data lineage tracking with SHA-256 fingerprinting,
W3C PROV alignment, and cross-site trace merging.

Tools:
    provenance_record          — Record a provenance event
    provenance_query_forward   — Query downstream lineage
    provenance_query_backward  — Query upstream lineage
    provenance_verify          — Verify provenance chain integrity
"""

from servers.trialmcp_provenance.dag import ProvenanceDAG
from servers.trialmcp_provenance.server import ProvenanceServer

__all__ = [
    "ProvenanceDAG",
    "ProvenanceServer",
]
