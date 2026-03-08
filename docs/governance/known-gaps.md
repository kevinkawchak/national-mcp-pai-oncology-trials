# Known Gaps, Non-Goals, and Future Work

**National MCP-PAI Oncology Trials Standard — Known Gaps**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This document catalogs the known limitations of the current specification version,
features that are explicitly excluded from scope, and planned future work. It ensures
that implementers, regulators, and adopters have clear expectations about what the
standard does and does not cover.

---

## 1. Known Gaps

### 1.1 Federated Learning Aggregation Protocol

| Field | Detail |
|-------|--------|
| **Gap** | No normative specification for federated learning aggregation algorithms |
| **Impact** | Sites implementing multi-site model training must agree on aggregation algorithms out-of-band |
| **Current State** | The provenance server tracks federated learning workflows (data source registration, lineage, integrity verification) but does not specify aggregation algorithms (FedAvg, FedProx, SCAFFOLD) |
| **Mitigation** | Implementers SHOULD use provenance tools to record aggregation parameters and algorithm selection |
| **Target Resolution** | v0.2.0 — Normative federated learning aggregation specification |
| **Tracking** | DL-012 in decision-log.md |

### 1.2 Real-Time Robot Telemetry Streaming

| Field | Detail |
|-------|--------|
| **Gap** | No normative specification for continuous telemetry streaming from robot agents |
| **Impact** | Real-time monitoring of robot procedure execution relies on vendor-specific telemetry interfaces |
| **Current State** | The audit ledger records discrete tool invocations but does not handle high-frequency telemetry data (e.g., 1kHz force/torque sensor readings) |
| **Mitigation** | Vendors MAY implement telemetry streaming as vendor extension tools using the `x-vendor-` namespace |
| **Target Resolution** | v0.3.0 — Telemetry streaming specification |

### 1.3 Digital Signature for Audit Records

| Field | Detail |
|-------|--------|
| **Gap** | Audit records are hash-chained but not individually digitally signed |
| **Impact** | Tamper detection relies on chain verification rather than per-record cryptographic signatures |
| **Current State** | SHA-256 hash chaining provides tamper evidence. Per-record digital signatures (e.g., ECDSA, Ed25519) are not required |
| **Mitigation** | The hash chain provides strong tamper evidence for sequential integrity. Implementations MAY add per-record signatures as a non-normative enhancement |
| **Target Resolution** | v0.2.0 — Optional digital signature extension for audit records |

### 1.4 Cross-Site Identity Federation

| Field | Detail |
|-------|--------|
| **Gap** | No normative specification for cross-site actor identity federation |
| **Impact** | Actors operating across multiple sites must obtain separate tokens at each site |
| **Current State** | Each site's `trialmcp-authz` server issues and validates its own tokens independently |
| **Mitigation** | CROs and sponsors can manage multi-site credentials through their own identity management infrastructure |
| **Target Resolution** | v0.2.0 — Cross-site identity federation specification |

### 1.5 Adverse Event Auto-Detection

| Field | Detail |
|-------|--------|
| **Gap** | No normative specification for automated adverse event detection from clinical data |
| **Impact** | Adverse event identification during robot-assisted procedures relies on manual reporting |
| **Current State** | FHIR R4 AdverseEvent resources can be queried via `fhir_search` but the standard does not specify automated detection logic |
| **Mitigation** | Sites MAY implement adverse event detection as application logic consuming MCP tool outputs |
| **Target Resolution** | v0.3.0 — Adverse event detection framework |

### 1.6 Partial Chain Recovery

| Field | Detail |
|-------|--------|
| **Gap** | No specification for recovering from audit chain corruption |
| **Impact** | If chain integrity is violated, no normative recovery procedure exists |
| **Current State** | `ledger_verify` detects chain breaks but does not provide remediation |
| **Mitigation** | Implementations SHOULD maintain offline backups of the audit chain. Chain breaks MUST be reported to the compliance officer |
| **Target Resolution** | v0.2.0 — Chain recovery and remediation specification |

### 1.7 Internationalization

| Field | Detail |
|-------|--------|
| **Gap** | Specification assumes United States jurisdiction only |
| **Impact** | International deployments (EU MDR, UK MHRA, Japan PMDA) require additional regulatory mappings |
| **Current State** | Regulatory overlays exist for US FDA, HIPAA, and 21 CFR Part 11 only |
| **Mitigation** | International sites can implement the technical specification and develop local regulatory overlays |
| **Target Resolution** | v1.0.0 — International regulatory overlay framework |

### 1.8 Large-Scale Performance Benchmarks

| Field | Detail |
|-------|--------|
| **Gap** | No normative performance requirements or benchmark specifications |
| **Impact** | Implementations may have inconsistent performance characteristics at scale |
| **Current State** | Benchmark framework exists in `benchmarks/` but performance targets are informative, not normative |
| **Mitigation** | Implementers SHOULD benchmark against the reference implementation |
| **Target Resolution** | v0.2.0 — Informative performance guidelines |

---

## 2. Non-Goals

The following items are explicitly outside the scope of this standard and will not
be addressed in any planned version.

### 2.1 Robot Control Algorithms

The standard defines the MCP protocol boundary for robot-to-clinical-system
communication. It does not specify robot control algorithms, motion planning,
kinematics, path planning, or actuator control. These are implementation concerns
of the robot platform vendor.

**Rationale**: Robot control is domain-specific to each platform. Standardizing
control algorithms would restrict innovation and create safety risks by imposing
one-size-fits-all control strategies on diverse robotic platforms.

### 2.2 Clinical Decision Support Logic

The standard does not specify clinical decision support (CDS) algorithms, treatment
recommendation engines, or clinical reasoning logic. MCP tools provide data access;
clinical decisions are made by qualified clinicians.

**Rationale**: Clinical decision support is regulated separately (FDA CDS guidance)
and must remain under the authority of licensed medical professionals.

### 2.3 Electronic Health Record Internals

The standard interfaces with EHR systems through FHIR R4 but does not specify
EHR internal data models, workflows, or user interfaces.

**Rationale**: EHR systems are independently regulated and certified (ONC Health IT
Certification). The FHIR R4 interface provides a stable, standards-based boundary.

### 2.4 Network Transport Security

The standard does not specify TLS configuration, network architecture, firewall
rules, or VPN configuration. These are infrastructure concerns addressed by each
site's IT security program.

**Rationale**: Network security requirements vary by institution and are governed
by HIPAA Security Rule technical safeguards, which are already normative for
covered entities.

### 2.5 User Interface Design

The standard does not specify user interfaces for trial coordinators, data monitors,
auditors, or any other human actors. UI design is an implementation concern.

**Rationale**: User interface requirements vary by institution, workflow, and user
preference. The MCP tool contracts define the data interface; presentation is
decoupled from protocol.

### 2.6 Cloud Provider Selection

The standard does not mandate or recommend specific cloud providers, container
orchestration platforms, or infrastructure-as-code tools.

**Rationale**: Vendor neutrality is a core design principle (Section 2.6 of
`spec/core.md`). Infrastructure decisions are site-specific.

### 2.7 Training Data Curation

The standard does not specify how training data for AI/ML models should be
curated, labeled, or validated. Provenance tracking covers data lineage but
not data quality assessment.

**Rationale**: Training data curation is specific to the AI/ML model being
developed and is governed by separate regulatory frameworks (FDA AI/ML SaMD
guidance).

---

## 3. Future Work

### 3.1 Planned for v0.2.0

| Item | Description | Priority |
|------|-------------|----------|
| Federated learning aggregation | Normative specification for FedAvg, FedProx, SCAFFOLD | High |
| Digital signature extension | Optional per-record ECDSA/Ed25519 signatures for audit records | High |
| Cross-site identity federation | Token federation protocol for multi-site actors | High |
| Chain recovery specification | Normative procedure for audit chain corruption remediation | Medium |
| Performance guidelines | Informative performance targets and benchmark methodology | Medium |
| Vendor extension registry | Centralized registry for vendor extension tool definitions | Medium |

### 3.2 Planned for v0.3.0

| Item | Description | Priority |
|------|-------------|----------|
| Real-time telemetry streaming | Normative specification for high-frequency robot telemetry | High |
| Adverse event auto-detection | Framework for automated adverse event identification | Medium |
| Differential privacy | Formal differential privacy guarantees for cross-site analytics | Medium |
| Consent management | Electronic consent capture and verification tools | Medium |
| Multi-language support | Specification translations and locale-aware de-identification | Low |

### 3.3 Planned for v1.0.0

| Item | Description | Priority |
|------|-------------|----------|
| Normative standard ratification | Formal governance body ratification | High |
| International regulatory overlays | EU MDR, UK MHRA, Japan PMDA mappings | High |
| Certification program | Formal conformance certification authority | High |
| Long-term governance structure | Permanent governance body with industry funding | High |
| Reference implementation LTS | Long-term support for reference implementation | Medium |

---

## 4. Gap Reporting

Implementers and adopters who identify additional gaps SHOULD report them through
the standard issue process (see `.github/ISSUE_TEMPLATE/spec_change.md`). Gap
reports MUST include:

1. Description of the gap
2. Impact on implementation or deployment
3. Proposed resolution (if any)
4. Urgency assessment (blocking, important, or enhancement)

Gap reports are triaged by the governance body and assigned to a target version
or classified as a non-goal with documented rationale.
