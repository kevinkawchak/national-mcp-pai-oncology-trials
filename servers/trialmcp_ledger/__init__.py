"""trialmcp-ledger — Audit Ledger MCP Server.

Implements a hash-chained immutable audit ledger with SHA-256
canonical JSON serialization, genesis block initialization, and
chain verification.

Tools:
    ledger_append — Append a new audit record to the chain
    ledger_verify — Verify the integrity of the audit chain
    ledger_query  — Query audit records
    ledger_export — Export audit records
"""

from servers.trialmcp_ledger.chain import AuditChain
from servers.trialmcp_ledger.server import LedgerServer

__all__ = [
    "AuditChain",
    "LedgerServer",
]
