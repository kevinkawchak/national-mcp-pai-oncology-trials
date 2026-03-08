# Decision Log

**National MCP-PAI Oncology Trials Standard — Governance Decision Log**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This document records all significant technical and governance decisions made during the
development of the National MCP-PAI Oncology Trials Standard. Each entry captures the
decision, its rationale, alternatives considered, and outcome. This log provides an
auditable history of how the standard evolved and why specific choices were made.

Decisions are numbered sequentially. Status values are:
- **Accepted** — Decision ratified and incorporated into the specification
- **Declined** — Proposal evaluated and rejected with documented rationale
- **Superseded** — Decision replaced by a later entry (cross-referenced)
- **Deferred** — Decision postponed to a future version with documented reasoning

---

## Decision Log

### DL-001: Adopt MCP as Protocol Boundary

| Field | Value |
|-------|-------|
| **Date** | 2026-01-15 |
| **Status** | Accepted |
| **Proposer** | Architecture Working Group |
| **ADR** | [ADR-001](../adr/001-mcp-protocol-boundary.md) |

**Context**: The standard needed a protocol boundary between Physical AI systems and
clinical infrastructure. Candidates included custom REST APIs, gRPC, HL7 FHIR Messaging,
and Model Context Protocol (MCP).

**Decision**: Adopt MCP as the sole protocol boundary for all robot-to-clinical-system
interactions.

**Rationale**: MCP provides a tool-oriented interface that maps naturally to clinical
operations, supports structured input/output contracts, and has growing ecosystem
adoption among AI agent frameworks. Its tool abstraction enables vendor-neutral
interoperability without mandating specific transport implementations.

**Alternatives Declined**:
- Custom REST API: Would fragment the ecosystem with per-vendor schemas
- gRPC: Strong typing but poor alignment with clinical workflow semantics
- HL7 FHIR Messaging: Limited to clinical data exchange, no robot control semantics

---

### DL-002: Five-Server Architecture

| Field | Value |
|-------|-------|
| **Date** | 2026-01-22 |
| **Status** | Accepted |
| **Proposer** | Architecture Working Group |
| **ADR** | [ADR-002](../adr/002-five-server-architecture.md) |

**Context**: Determined the minimum number of MCP servers required to cover authorization,
clinical data, imaging, audit, and provenance.

**Decision**: Define exactly five MCP servers: `trialmcp-authz`, `trialmcp-fhir`,
`trialmcp-dicom`, `trialmcp-ledger`, `trialmcp-provenance`.

**Rationale**: Each server maps to a distinct regulatory or clinical concern. Fewer
servers would create monolithic surfaces that cross regulatory boundaries. More servers
would increase deployment complexity without proportionate benefit.

**Alternatives Declined**:
- Monolithic single server: Impossible to isolate security domains
- Three servers (auth+audit, clinical, imaging): Audit lifecycle tied to auth lifecycle
- Seven servers (adding scheduling and notification): Outside protocol scope

---

### DL-003: 23-Tool Surface Area

| Field | Value |
|-------|-------|
| **Date** | 2026-01-29 |
| **Status** | Accepted |
| **Proposer** | Tool Contracts Working Group |
| **ADR** | [ADR-003](../adr/003-twenty-three-tools.md) |

**Context**: Needed to define the minimum set of tool contracts that covers all required
clinical trial operations without introducing unnecessary complexity.

**Decision**: Standardize 23 tools across 5 servers (AuthZ: 5, FHIR: 4, DICOM: 4,
Ledger: 5, Provenance: 5).

**Rationale**: Each tool maps to a single clinical operation with clear input/output
contracts. The count was derived by enumerating the minimum operations required for each
server's regulatory mandate and verifying that no tool could be split or merged without
losing operational clarity.

---

### DL-004: Deny-by-Default RBAC

| Field | Value |
|-------|-------|
| **Date** | 2026-02-05 |
| **Status** | Accepted |
| **Proposer** | Security Working Group |
| **ADR** | [ADR-007](../adr/007-deny-by-default-rbac.md) |

**Context**: Access control for autonomous robot agents in clinical environments
requires a fail-safe authorization model.

**Decision**: All access is denied unless explicitly permitted by a matching ALLOW rule.
Explicit DENY rules take precedence over ALLOW rules.

**Rationale**: In safety-critical clinical environments involving autonomous systems,
the cost of unauthorized access far exceeds the cost of denied legitimate access.
Deny-by-default ensures that configuration errors result in denied access, not
unauthorized access.

---

### DL-005: SHA-256 Hash-Chained Audit Ledger

| Field | Value |
|-------|-------|
| **Date** | 2026-02-05 |
| **Status** | Accepted |
| **Proposer** | Compliance Working Group |
| **ADR** | [ADR-005](../adr/005-hash-chained-audit.md) |

**Context**: 21 CFR Part 11 requires tamper-evident audit trails for electronic records
in clinical trials.

**Decision**: Implement an append-only hash-chained ledger using SHA-256 with a genesis
hash of `"0" * 64`.

**Rationale**: Hash chaining provides cryptographic tamper evidence without requiring
a distributed consensus mechanism. SHA-256 is NIST-approved and widely supported.

---

### DL-006: DAG-Based Provenance Over Linear Lineage

| Field | Value |
|-------|-------|
| **Date** | 2026-02-12 |
| **Status** | Accepted |
| **Proposer** | Data Lineage Working Group |
| **ADR** | [ADR-006](../adr/006-dag-provenance.md) |

**Context**: Clinical trial data flows are inherently non-linear. A single imaging
study may derive multiple downstream analyses, and federated aggregation merges
data from multiple sites.

**Decision**: Implement provenance as a directed acyclic graph (DAG) rather than
linear lineage chains.

**Rationale**: DAG structure accurately represents fan-out (one source, many
derivatives) and fan-in (many sources, one aggregate) patterns that are fundamental
to multi-site oncology trials and federated learning workflows.

---

### DL-007: HIPAA Safe Harbor De-identification

| Field | Value |
|-------|-------|
| **Date** | 2026-02-12 |
| **Status** | Accepted |
| **Proposer** | Privacy Working Group |

**Context**: Patient data accessed by robot agents and cross-site workflows must
comply with HIPAA de-identification requirements.

**Decision**: Mandate HIPAA Safe Harbor method (removal of all 18 identifiers) with
HMAC-SHA256 pseudonymization to maintain referential integrity.

**Rationale**: Safe Harbor provides a deterministic compliance path without requiring
expert determination. HMAC-SHA256 pseudonymization with site-specific salts maintains
the ability to link records within a site without exposing real identifiers.

---

### DL-008: Six Actor Model

| Field | Value |
|-------|-------|
| **Date** | 2026-02-19 |
| **Status** | Accepted |
| **Proposer** | Governance Working Group |

**Context**: Need to define the complete set of actors that interact with the MCP
infrastructure, spanning both operational roles and organizational roles.

**Decision**: Define six actors: `robot_agent`, `trial_coordinator`, `data_monitor`,
`auditor`, `sponsor`, `cro`.

**Rationale**: Four operational roles cover the clinical site workflow. Two
organizational roles cover trial governance and multi-site coordination. This set
was validated against ICH-GCP E6(R2) role definitions and FDA trial oversight
requirements.

---

### DL-009: Conformance Profile Tiers

| Field | Value |
|-------|-------|
| **Date** | 2026-02-19 |
| **Status** | Accepted |
| **Proposer** | Conformance Working Group |
| **ADR** | [ADR-004](../adr/004-profile-conformance-levels.md) |

**Context**: Implementations vary in scope from basic audit-only deployments to
full robot-assisted surgical procedures. A single conformance level would impose
unnecessary requirements on simpler deployments.

**Decision**: Define five cumulative conformance levels (Core, Clinical Read,
Imaging, Federated Site, Robot Procedure) with corresponding profiles.

**Rationale**: Cumulative levels ensure that each tier builds on the security and
audit guarantees of lower tiers. Sites can declare and test against their
operational tier without implementing capabilities they do not use.

---

### DL-010: Vendor Extension Namespace

| Field | Value |
|-------|-------|
| **Date** | 2026-02-26 |
| **Status** | Accepted |
| **Proposer** | Architecture Working Group |

**Context**: Vendors and sites need to extend the standard with custom tools
without breaking conformance.

**Decision**: Allow vendor extension tools using a `x-vendor-` namespace prefix.
Extension tools MUST NOT override normative tool contracts. Extension tools MUST
generate audit records using the standard ledger.

**Rationale**: Namespaced extensions enable innovation without fragmenting the
normative surface area. Mandatory audit ensures that extension operations remain
within the compliance boundary.

---

### DL-011: Separate Safety Module from MCP Servers

| Field | Value |
|-------|-------|
| **Date** | 2026-03-01 |
| **Status** | Accepted |
| **Proposer** | Safety Working Group |

**Context**: Robot execution boundary enforcement (e-stop, approval checkpoints,
procedure state machines) must operate independently of MCP server availability.

**Decision**: Safety modules (e-stop, approval checkpoint, gate service, procedure
state, robot registry, site verifier, task validator) are implemented as standalone
components outside the MCP server boundary.

**Rationale**: Safety enforcement must not depend on network connectivity to MCP
servers. An e-stop must function even if the authorization server is unreachable.
Decoupling safety from MCP ensures that safety-critical functions have independent
failure modes.

---

### DL-012: Federated Learning Aggregation Support

| Field | Value |
|-------|-------|
| **Date** | 2026-03-01 |
| **Status** | Deferred |
| **Proposer** | Data Science Working Group |
| **Deferred To** | v0.2.0 |

**Context**: Multi-site federated learning for oncology model training requires
standardized aggregation protocols (FedAvg, FedProx, SCAFFOLD).

**Decision**: Deferred to v0.2.0. The current specification defines provenance
tracking for federated workflows but does not normatively specify aggregation
algorithms.

**Rationale**: Aggregation algorithm standardization requires broader consensus
from the machine learning research community. The provenance infrastructure in
v0.1.0 supports tracking federated workflows without prescribing algorithms.

---

## Log Maintenance

- New entries MUST be appended at the end of the log
- Entries MUST NOT be modified after acceptance; corrections require a new entry
- Superseded entries MUST cross-reference the replacing entry
- Each entry MUST include date, status, proposer, and rationale
- Entries referencing ADRs MUST link to the corresponding ADR document
