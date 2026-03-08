# ADR-002: Five-Server Architecture

**Status**: Accepted
**Date**: 2026-01-22
**Decision Makers**: Architecture Working Group
**Tracking**: DL-002 in `docs/governance/decision-log.md`

---

## Context

The national standard must define the MCP server topology — how many servers exist,
what responsibilities each server has, and how they relate to each other. This
decision directly affects deployment complexity, security isolation, conformance
testing scope, and regulatory alignment.

The server architecture must satisfy:

1. **Security domain isolation**: Authorization, clinical data, imaging, audit, and
   provenance each have distinct security and regulatory requirements
2. **Independent lifecycle**: Servers must be deployable and upgradable independently
3. **Regulatory mapping**: Each server's scope must map cleanly to specific regulatory
   requirements (HIPAA, 21 CFR Part 11, FDA device classification)
4. **Minimal deployment footprint**: Sites deploying only basic audit capabilities
   should not need imaging or provenance servers
5. **Composability**: The conformance level system requires additive server composition

### Server Candidates

The architecture team evaluated configurations ranging from 1 (monolithic) to 8 servers.

---

## Decision

Define exactly five MCP servers, each with a distinct regulatory and operational domain:

| Server | Domain | Tools | Regulatory Alignment |
|--------|--------|-------|---------------------|
| `trialmcp-authz` | Authorization and access control | 5 | HIPAA Security Rule, RBAC |
| `trialmcp-fhir` | Clinical data access (FHIR R4) | 4 | HIPAA Privacy Rule, FHIR R4 |
| `trialmcp-dicom` | Medical imaging access | 4 | DICOM standard, FDA imaging |
| `trialmcp-ledger` | Audit trail (hash-chained) | 5 | 21 CFR Part 11 |
| `trialmcp-provenance` | Data lineage (DAG) | 5 | ICH-GCP E6(R2), data integrity |

---

## Rationale

### One Server Per Regulatory Domain

Each server maps to a distinct regulatory concern:

- **AuthZ** enforces HIPAA Security Rule access controls and RBAC policies
- **FHIR** enforces HIPAA Privacy Rule de-identification for clinical data
- **DICOM** enforces imaging-specific access controls and de-identification
- **Ledger** satisfies 21 CFR Part 11 requirements for tamper-evident audit trails
- **Provenance** satisfies ICH-GCP E6(R2) requirements for data lineage and integrity

This separation ensures that a security audit of one domain does not require
reviewing the entire system. Regulatory auditors (FDA inspectors, HIPAA auditors)
can examine the relevant server in isolation.

### Independent Failure Domains

Each server operates independently. A failure in the DICOM server does not affect
FHIR data access. A failure in the provenance server does not break the audit chain.
This isolation is critical for clinical safety — a robot agent must be able to
verify its authorization (AuthZ) and record its actions (Ledger) even if the imaging
server is unavailable.

### Cumulative Conformance Levels

The five-server architecture enables the five cumulative conformance levels:

```
Level 1 (Core):            AuthZ + Ledger
Level 2 (Clinical Read):   AuthZ + Ledger + FHIR
Level 3 (Imaging):         AuthZ + Ledger + FHIR + DICOM
Level 4 (Federated):       AuthZ + Ledger + FHIR + DICOM + Provenance
Level 5 (Robot Procedure): All five + safety modules
```

Sites deploy only the servers required for their conformance level. A data monitoring
site at Level 2 does not deploy DICOM or Provenance servers.

### Separation of Audit and Provenance

Audit (Ledger) and provenance serve related but distinct purposes:

- **Ledger**: Sequential, append-only record of what happened (who did what, when).
  Optimized for tamper detection and compliance replay. Linear hash chain.
- **Provenance**: Graph-based record of data lineage (where did this data come from,
  what was derived from it). Optimized for forward/backward lineage queries. DAG
  structure.

Combining these into a single server would conflate their data models (linear chain
vs. DAG) and their query patterns (sequential replay vs. graph traversal).

### Authorization as a Separate Server

Authorization is isolated in its own server rather than embedded in each domain
server. This provides:

- **Single policy evaluation point**: All access decisions flow through one engine
- **Consistent deny-by-default enforcement**: No risk of domain servers implementing
  inconsistent access control
- **Token lifecycle management**: Token issuance, validation, and revocation are
  centralized
- **Audit of authorization decisions**: All policy evaluations are recorded

---

## Consequences

### Positive

- **Clean regulatory mapping**: Each server can be independently audited against its
  regulatory requirements
- **Flexible deployment**: Sites deploy only the servers they need
- **Independent scaling**: Servers can be scaled independently based on load
- **Clear ownership**: Each server has a well-defined scope for development and testing
- **Conformance composability**: Conformance levels map directly to server combinations

### Negative

- **Deployment complexity**: Five servers require more operational infrastructure than
  a monolithic deployment
- **Cross-server coordination**: Operations spanning multiple servers (e.g., a FHIR
  read that requires AuthZ validation and Ledger recording) involve multiple server
  interactions
- **Configuration management**: Five servers means five configuration surfaces to
  manage and synchronize
- **Testing complexity**: Integration tests must cover cross-server interactions

### Mitigations

- Deployment complexity is addressed by providing reference deployment configurations
  in `deploy/` for each conformance level
- Cross-server coordination is handled by the MCP client (robot agent or trial
  coordinator application), which orchestrates multi-server workflows
- Configuration management is simplified by sharing configuration schemas across
  servers where appropriate

---

## Alternatives Rejected

### Monolithic Single Server

A single MCP server exposing all 23 tools. Rejected because:
- Impossible to isolate security domains (AuthZ, clinical data, audit)
- Cannot deploy partial capability sets
- A single vulnerability exposes all functionality
- Regulatory auditors must review the entire system for any compliance check

### Three Servers (Auth+Audit, Clinical, Imaging)

Combining AuthZ with Ledger, and FHIR with Provenance. Rejected because:
- Audit lifecycle coupled to authorization lifecycle (cannot upgrade audit without
  affecting authorization)
- Provenance DAG model conflated with FHIR resource model
- Conformance levels cannot be cleanly mapped

### Seven Servers (Adding Scheduling and Notification)

Adding dedicated scheduling and notification servers. Rejected because:
- Scheduling is an application concern, not a protocol concern
- Notification delivery mechanisms vary by site and are infrastructure-dependent
- Additional servers increase deployment complexity without addressing core
  interoperability requirements

### Six Servers (Splitting DICOM Query and DICOM Retrieve)

Separating DICOM query/metadata from DICOM retrieval. Rejected because:
- DICOM query and retrieval are operationally coupled
- The retrieval pointer pattern (`dicom_retrieve_pointer`) already decouples
  metadata access from pixel data transfer
- Additional server for four tools is disproportionate

---

## References

- `spec/core.md` Section 3 (Conformance Levels)
- `spec/tool-contracts.md` Sections 3-7 (per-server tool definitions)
- `spec/conformance.md` (Level requirements)
- `spec/security.md` Section 2 (Authorization Model)
- `spec/audit.md` (Ledger specification)
- `spec/provenance.md` (Provenance DAG specification)
