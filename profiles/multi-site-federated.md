# Multi-Site Federated Profile

**National MCP-PAI Oncology Trials Standard — profiles/multi-site-federated.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

The Multi-Site Federated Profile defines the requirements for implementations that support cross-site data provenance, federated audit chains, and data residency policy enforcement. This profile builds on the [Imaging-Guided Oncology Profile](imaging-guided-oncology.md) and is required for any deployment participating in multi-site oncology clinical trials where data must be tracked, aggregated, and audited across institutional boundaries.

> Implementations claiming Multi-Site Federated conformance MUST satisfy all lower-profile requirements AND all requirements defined in this profile.

---

## 2. Mandatory Tools

The Multi-Site Federated Profile requires the `trialmcp-provenance` server in addition to all lower-profile servers.

| Tool | Requirement | Description |
|------|-------------|-------------|
| `provenance_register_source` | MUST | Register data sources in the provenance DAG with origin metadata |
| `provenance_record_access` | MUST | Record data access events with SHA-256 fingerprinting |
| `provenance_get_lineage` | MUST | Retrieve forward or backward lineage for any data source |
| `provenance_get_actor_history` | MUST | Return all operations performed by a specific actor |
| `provenance_verify_integrity` | MUST | Verify data integrity against recorded SHA-256 fingerprints |

---

## 3. Cross-Site Provenance Requirements

### 3.1 DAG-Based Lineage

- MUST implement a Directed Acyclic Graph (DAG) for data lineage tracking
- MUST support both forward lineage (what happened to this data?) and backward lineage (where did this data come from?)
- MUST compute SHA-256 fingerprints for all input and output data at each provenance node
- MUST maintain provenance records as immutable — no deletion or modification after creation
- MUST include site identifier in all provenance records for cross-site attribution

### 3.2 Source Types

Conforming implementations MUST support the following source types:

| Source Type | Description | Requirement |
|------------|-------------|-------------|
| `direct_clinical_system` | Data originating from EHR or clinical database | MUST |
| `fhir_server` | Data retrieved via trialmcp-fhir tools | MUST |
| `dicom_server` | Data retrieved via trialmcp-dicom tools | MUST |
| `ledger_server` | Audit records from trialmcp-ledger | MUST |
| `provenance_server` | Provenance records (self-referential lineage) | MUST |
| `federated_aggregation` | Cross-site model aggregation outputs | SHOULD |
| `external_data_source` | Third-party data (e.g., genomic databases) | MAY |

### 3.3 Action Types

Conforming implementations MUST support the following action types in provenance records:

| Action Type | Description | Requirement |
|------------|-------------|-------------|
| `read` | Data was read without modification | MUST |
| `write` | New data was created | MUST |
| `computed` | Data was derived from computation on existing data | MUST |
| `aggregated` | Data was aggregated from multiple sources (federated) | MUST |
| `pseudonymized` | Data underwent de-identification or pseudonymization | MUST |

---

## 4. Federated Audit Chain Requirements

### 4.1 Cross-Site Audit Coordination

- MUST maintain independent hash-chained audit ledgers per site (data residency)
- MUST include a globally unique site identifier in every audit record
- MUST support audit chain verification within a single site
- SHOULD support cross-site audit chain integrity verification via coordination layer
- SHOULD support audit record exchange for regulatory reporting without exposing patient data

### 4.2 Federated Learning Provenance

For sites participating in federated learning:

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Record local model training | MUST | Provenance entry for each local training round |
| Record aggregation participation | MUST | Track which sites contributed to each aggregation round |
| Record aggregated model receipt | MUST | Provenance entry for receiving global model updates |
| Apply differential privacy | SHOULD | Record privacy budget (epsilon, delta) in provenance |
| Record gradient clipping | SHOULD | Document gradient norm bounds in provenance metadata |
| Support secure aggregation | SHOULD | Track encryption/decryption steps in provenance |

### 4.3 Supported Aggregation Strategies

| Strategy | Description | Requirement |
|---------|-------------|-------------|
| FedAvg | Federated Averaging | SHOULD |
| FedProx | Proximal term for heterogeneous data | SHOULD |
| SCAFFOLD | Stochastic Controlled Averaging | MAY |

---

## 5. Data Residency Policy

### 5.1 Core Residency Requirements

- MUST enforce that patient-level data never leaves the originating site without explicit consent
- MUST enforce that de-identified aggregate data may be shared cross-site only after provenance recording
- MUST maintain a data residency declaration per site specifying jurisdiction and applicable laws
- MUST validate data residency compliance before any cross-site data exchange

### 5.2 Data Classification for Residency

| Data Class | Residency Rule | Cross-Site Sharing |
|-----------|---------------|-------------------|
| Patient identifiers (real) | MUST remain on-site | NEVER |
| Patient identifiers (pseudonymized) | MUST remain on-site | NEVER (site-specific HMAC keys) |
| De-identified clinical data | Site-local by default | ALLOWED with provenance recording |
| Aggregate model parameters | No residency constraint | ALLOWED with privacy budget tracking |
| Audit records | MUST remain on-site | ALLOWED for regulatory reporting (redacted) |
| Provenance records | MUST remain on-site | Lineage queries permitted via coordination layer |

### 5.3 Jurisdictional Compliance

Multi-site deployments MUST declare applicable jurisdictions per site. See:
- [state-us-ca.md](state-us-ca.md) — California CCPA overlay
- [state-us-ny.md](state-us-ny.md) — New York health information overlay
- [country-us-fda.md](country-us-fda.md) — FDA 21 CFR Part 11 overlay

---

## 6. Optional Tools

| Tool | Requirement | Description |
|------|-------------|-------------|
| `provenance_cross_site_query` | MAY | Query lineage across site boundaries via coordination layer |
| `provenance_export_report` | MAY | Export provenance report for regulatory submission |
| `provenance_privacy_budget` | MAY | Track and report differential privacy budget consumption |

---

## 7. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Cross-site patient ID sharing | Privacy: real and pseudonymized patient IDs MUST NOT leave originating site |
| Modifying provenance records | Integrity: provenance records are immutable after creation |
| Aggregation without provenance | Compliance: all federated aggregation steps MUST be recorded |
| Data export without residency check | Residency: cross-site data exchange MUST pass residency validation |
| Audit chain tampering | Integrity: cross-site audit records MUST maintain hash chain integrity |

---

## 8. Required Schemas

In addition to lower-profile schemas, Multi-Site Federated implementations MUST validate against:

| Schema | File | Purpose |
|--------|------|---------|
| Provenance Record | `schemas/provenance-record.schema.json` | DAG lineage entries with SHA-256 fingerprints |
| Site Capability Profile | `schemas/site-capability-profile.schema.json` | Site jurisdiction, data residency, deployed servers |

---

## 9. Regulatory Overlays

| Regulation | Relevant Section | Coverage |
|-----------|-----------------|----------|
| HIPAA Privacy Rule | §164.508 Authorization | Cross-site data sharing requires consent |
| HIPAA Privacy Rule | §164.514(b) Safe Harbor | De-identification before cross-site exchange |
| 21 CFR Part 11 | §11.10(e) Audit trails | Site-local hash-chained audit ledgers |
| 21 CFR Part 11 | §11.10(k)(2) Record retention | Provenance records for data lineage retention |
| FDA AI/ML Guidance | Predetermined change control | Federated model update tracking |
| ICH-GCP E6(R2) | §8.1 Essential documents | Cross-site audit trail for sponsor oversight |

---

## 10. Conformance Test Subset

Implementations claiming Multi-Site Federated conformance MUST pass:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| Imaging-Guided Oncology Profile tests | 39 | All lower-profile conformance tests |
| Provenance DAG operations | 3 | Register, record access, verify integrity |
| Lineage queries | 2 | Forward and backward traversal |
| SHA-256 fingerprint verification | 1 | Input/output hash consistency |
| Actor history tracking | 1 | Complete actor operation history |
| Data residency enforcement | 2 | Site-local enforcement, cross-site rejection |
| **Total** | **48** | |

---

*This profile is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [spec/provenance.md](../spec/provenance.md) for the full DAG lineage specification.*
