# ADR-003: Twenty-Three Tools as the Minimal Stable Surface Area

**Status**: Accepted
**Date**: 2026-01-29
**Decision Makers**: Tool Contracts Working Group
**Tracking**: DL-003 in `docs/governance/decision-log.md`

---

## Context

The national standard must define the exact set of MCP tool contracts that all
conforming implementations expose. This tool set must be:

1. **Complete**: Every required clinical trial operation must be achievable through
   the defined tools
2. **Minimal**: No tool should be redundant or decomposable into simpler tools without
   losing operational clarity
3. **Stable**: The tool set must be durable across specification versions; tools should
   not be added or removed frequently
4. **Testable**: Each tool must be independently testable for conformance
5. **Role-aware**: Tools must support the six-actor RBAC model

The tool set was derived by enumerating the operations required for each server's
regulatory mandate, then verifying minimality (no tool can be removed without losing
a required capability) and stability (no tool is likely to split or merge in future
versions).

---

## Decision

Standardize exactly 23 tools across 5 servers:

### AuthZ Server — 5 Tools

| Tool | Purpose |
|------|---------|
| `authz_evaluate` | Evaluate an access request against the policy engine |
| `authz_issue_token` | Issue a scoped session token for an authenticated actor |
| `authz_validate_token` | Validate a previously issued token |
| `authz_list_policies` | Return all active authorization policies |
| `authz_revoke_token` | Revoke an active token |

### FHIR Server — 4 Tools

| Tool | Purpose |
|------|---------|
| `fhir_read` | Read a single FHIR R4 resource by type and ID |
| `fhir_search` | Search FHIR R4 resources with filters |
| `fhir_patient_lookup` | Return pseudonymized patient demographics |
| `fhir_study_status` | Return ResearchStudy summary with enrollment counts |

### DICOM Server — 4 Tools

| Tool | Purpose |
|------|---------|
| `dicom_query` | Query DICOM studies with role-based access control |
| `dicom_retrieve_pointer` | Generate a time-limited retrieval token for a study |
| `dicom_study_metadata` | Return metadata for a DICOM study |
| `dicom_recist_measurements` | Return RECIST 1.1 tumor measurements |

### Ledger Server — 5 Tools

| Tool | Purpose |
|------|---------|
| `ledger_append` | Append a new audit record to the hash chain |
| `ledger_verify` | Verify the integrity of the audit chain |
| `ledger_query` | Query audit records by filter criteria |
| `ledger_replay` | Generate a sequential replay trace |
| `ledger_chain_status` | Report chain health and statistics |

### Provenance Server — 5 Tools

| Tool | Purpose |
|------|---------|
| `provenance_register_source` | Register a new data source in the DAG |
| `provenance_record_access` | Record a data access event |
| `provenance_get_lineage` | Retrieve lineage (forward or backward) |
| `provenance_get_actor_history` | Return all operations by an actor |
| `provenance_verify_integrity` | Verify data integrity via fingerprints |

---

## Rationale

### Derivation Methodology

The 23 tools were derived through the following process:

1. **Regulatory enumeration**: For each regulatory requirement (21 CFR Part 11, HIPAA,
   ICH-GCP E6(R2)), identify the minimum operations needed to satisfy compliance
2. **Clinical workflow mapping**: For each clinical workflow (patient enrollment,
   imaging review, robot procedure execution, adverse event monitoring), identify
   the data access operations required
3. **Actor coverage**: For each of the six actor roles, verify that all permitted
   operations can be expressed through the tool set
4. **Minimality check**: For each tool, attempt to remove it and verify that at least
   one required operation becomes impossible
5. **Merge check**: For each pair of tools on the same server, verify that merging
   them would create a tool with ambiguous semantics or mixed responsibilities

### AuthZ: 5 Tools (Not 3, Not 7)

Three tools (evaluate, issue, validate) would be insufficient because token revocation
is a regulatory requirement and policy listing is needed for audit transparency.
Seven tools (adding role management, policy CRUD) would move policy administration
into the protocol boundary, which is an application concern.

### FHIR: 4 Tools (Not 2, Not 8)

Two tools (read, search) would be insufficient because patient lookup requires
mandatory pseudonymization logic that differs from generic FHIR read, and study
status is a trial-specific aggregate that does not map to a single FHIR resource.
Eight tools (adding write, create, update, delete) would introduce data modification
operations that are outside the standard's read-oriented clinical data scope.

### DICOM: 4 Tools (Not 2, Not 6)

Two tools (query, retrieve) would conflate metadata access with pixel data retrieval
and would not support RECIST measurements. Six tools (adding series-level query, image-
level metadata, annotation query) would exceed the minimum required for oncology trial
imaging workflows.

### Ledger: 5 Tools (Not 2, Not 7)

Two tools (append, verify) would not support the query, replay, and status operations
required for compliance auditing. Seven tools (adding archive, export, merge, compact)
would introduce lifecycle management that is an operational concern, not a protocol
concern.

### Provenance: 5 Tools (Not 3, Not 7)

Three tools (register, record, lineage) would not support actor-specific history
queries or integrity verification. Seven tools (adding merge, delete, annotate, tag)
would introduce graph manipulation operations that are outside the append-only
provenance model.

### Stability Analysis

Each tool was evaluated for stability across anticipated specification evolution:

- **High stability**: All 10 AuthZ and Ledger tools — foundational security and
  compliance operations unlikely to change
- **High stability**: All 5 Provenance tools — DAG operations are well-established
  in data lineage literature
- **Medium stability**: FHIR tools — additional resource types may be supported but
  the four core operations are stable
- **Medium stability**: DICOM tools — additional query levels or measurement types
  may be added but the four core operations are stable

No tool is anticipated to be removed or fundamentally restructured within the v0.x
or v1.x lifecycle.

---

## Consequences

### Positive

- **Precise conformance testing**: Each of the 23 tools has a defined input schema,
  output schema, and error code set that can be tested independently
- **Small learning curve**: Implementers need to understand 23 operations, not
  hundreds
- **Stable API surface**: The tool set is designed to be durable across versions
- **Clear vendor extension boundary**: Vendors add tools using the `x-vendor-`
  namespace without affecting the normative 23

### Negative

- **Feature requests require governance**: Adding a 24th tool requires an ADR and
  governance review, which introduces process overhead
- **Limited write operations**: The standard is read-heavy by design; sites needing
  write operations must implement them outside the normative tool set
- **FHIR coverage**: Only four FHIR operations are standardized; sites needing
  broader FHIR interaction use vendor extensions or direct FHIR endpoints

### Extension Mechanism

Vendors and sites MAY define additional tools using the `x-vendor-` namespace prefix.
Extension tools:
- MUST NOT override normative tool contracts
- MUST generate audit records via `ledger_append`
- MUST respect the deny-by-default RBAC model
- SHOULD follow the tool contract format defined in `spec/tool-contracts.md`

---

## Alternatives Rejected

### 15 Tools (Reduced Set)

Removing `ledger_replay`, `ledger_chain_status`, `provenance_get_actor_history`,
`provenance_verify_integrity`, `authz_list_policies`, `authz_revoke_token`,
`dicom_recist_measurements`, `fhir_study_status`. Rejected because each removed
tool maps to a specific regulatory or clinical requirement that cannot be satisfied
by the remaining tools.

### 35 Tools (Expanded Set)

Adding FHIR write operations, DICOM annotation tools, ledger management operations,
provenance graph editing, and additional authorization administration tools. Rejected
because the additional tools cross the boundary from protocol operations into
application logic, and would increase the conformance testing burden without
proportionate benefit.

### Dynamic Tool Registration

Allowing servers to register arbitrary tools at runtime. Rejected because conformance
testing requires a known, fixed tool set. Dynamic registration is supported through
the vendor extension mechanism but does not affect the normative tool set.

---

## References

- `spec/tool-contracts.md` (complete tool contract definitions)
- `spec/conformance.md` (tool-to-level mapping)
- `spec/actor-model.md` (role-tool permission matrix)
- `governance/EXTENSIONS.md` (vendor extension policy)
