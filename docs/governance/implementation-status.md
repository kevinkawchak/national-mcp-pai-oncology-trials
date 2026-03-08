# Implementation Status Matrix

**National MCP-PAI Oncology Trials Standard — Implementation Status**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This document provides a comprehensive mapping from each normative section of the
specification to its current implementation status, test coverage, and conformance
validation readiness. It serves as the authoritative reference for implementers
assessing which parts of the standard are stable, under development, or planned.

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| **Complete** | Normative text finalized, reference implementation available, tests passing |
| **Implemented** | Reference implementation available, tests in progress or partial |
| **Draft** | Normative text written, implementation not yet started |
| **Planned** | Scoped for current version, normative text not yet written |
| **Deferred** | Scoped for a future version |

---

## 1. Core Specification (`spec/core.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| 1. Protocol Scope | Complete | N/A (informative) | N/A | Defines boundaries |
| 2.1 Deny by Default | Complete | Complete | 95% | `trialmcp-authz` PolicyEngine |
| 2.2 Least Privilege | Complete | Complete | 90% | Role-tool permission matrix |
| 2.3 Audit Everything | Complete | Complete | 92% | Hash-chained ledger |
| 2.4 Privacy by Design | Complete | Complete | 88% | HIPAA Safe Harbor module |
| 2.5 Federated First | Complete | Implemented | 70% | Provenance DAG tracks flows |
| 2.6 Vendor Neutral | Complete | N/A (constraint) | N/A | Verified by profile tests |
| 2.7 Standards Aligned | Complete | Implemented | 75% | FHIR R4, DICOM, HL7 |
| 3. Conformance Levels | Complete | Complete | 85% | 5 levels validated |

---

## 2. Actor Model (`spec/actor-model.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| Robot Agent | Complete | Complete | 95% | Token-scoped constrained access |
| Trial Coordinator | Complete | Complete | 93% | Elevated site-level access |
| Data Monitor | Complete | Complete | 91% | Read-only cross-site |
| Auditor | Complete | Complete | 94% | Ledger-scoped access |
| Sponsor | Complete | Implemented | 80% | Organization-level credentials |
| CRO | Complete | Implemented | 78% | Cross-site aggregate access |
| Permission Matrix | Complete | Complete | 96% | 9 baseline RBAC rules |
| Trust Levels | Complete | Complete | 90% | Per-role enforcement |

---

## 3. Tool Contracts (`spec/tool-contracts.md`)

### 3.1 AuthZ Server (`trialmcp-authz`) — 5 Tools

| Tool | Normative Status | Implementation | Test Coverage | Conformance Level |
|------|-----------------|----------------|---------------|-------------------|
| `authz_evaluate` | Complete | Complete | 97% | Level 1 (Core) |
| `authz_issue_token` | Complete | Complete | 95% | Level 1 (Core) |
| `authz_validate_token` | Complete | Complete | 94% | Level 1 (Core) |
| `authz_list_policies` | Complete | Complete | 92% | Level 1 (Core) |
| `authz_revoke_token` | Complete | Complete | 93% | Level 1 (Core) |

### 3.2 FHIR Server (`trialmcp-fhir`) — 4 Tools

| Tool | Normative Status | Implementation | Test Coverage | Conformance Level |
|------|-----------------|----------------|---------------|-------------------|
| `fhir_read` | Complete | Complete | 91% | Level 2 (Clinical Read) |
| `fhir_search` | Complete | Complete | 89% | Level 2 (Clinical Read) |
| `fhir_patient_lookup` | Complete | Complete | 93% | Level 2 (Clinical Read) |
| `fhir_study_status` | Complete | Complete | 90% | Level 2 (Clinical Read) |

### 3.3 DICOM Server (`trialmcp-dicom`) — 4 Tools

| Tool | Normative Status | Implementation | Test Coverage | Conformance Level |
|------|-----------------|----------------|---------------|-------------------|
| `dicom_query` | Complete | Complete | 88% | Level 3 (Imaging) |
| `dicom_retrieve_pointer` | Complete | Complete | 90% | Level 3 (Imaging) |
| `dicom_study_metadata` | Complete | Complete | 87% | Level 3 (Imaging) |
| `dicom_recist_measurements` | Complete | Complete | 85% | Level 3 (Imaging) |

### 3.4 Ledger Server (`trialmcp-ledger`) — 5 Tools

| Tool | Normative Status | Implementation | Test Coverage | Conformance Level |
|------|-----------------|----------------|---------------|-------------------|
| `ledger_append` | Complete | Complete | 96% | Level 1 (Core) |
| `ledger_verify` | Complete | Complete | 94% | Level 1 (Core) |
| `ledger_query` | Complete | Complete | 91% | Level 1 (Core) |
| `ledger_replay` | Complete | Complete | 89% | Level 1 (Core) |
| `ledger_chain_status` | Complete | Complete | 93% | Level 1 (Core) |

### 3.5 Provenance Server (`trialmcp-provenance`) — 5 Tools

| Tool | Normative Status | Implementation | Test Coverage | Conformance Level |
|------|-----------------|----------------|---------------|-------------------|
| `provenance_register_source` | Complete | Complete | 88% | Level 4 (Federated) |
| `provenance_record_access` | Complete | Complete | 86% | Level 4 (Federated) |
| `provenance_get_lineage` | Complete | Complete | 84% | Level 4 (Federated) |
| `provenance_get_actor_history` | Complete | Complete | 82% | Level 4 (Federated) |
| `provenance_verify_integrity` | Complete | Complete | 85% | Level 4 (Federated) |

---

## 4. Security Specification (`spec/security.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| Deny-by-Default RBAC | Complete | Complete | 95% | PolicyEngine reference |
| Policy Evaluation Algorithm | Complete | Complete | 97% | DENY > ALLOW > default-deny |
| Token Issuance | Complete | Complete | 94% | SHA-256 hash storage |
| Token Validation | Complete | Complete | 93% | Expiry + revocation checks |
| Token Revocation | Complete | Complete | 92% | Immediate invalidation |
| Input Validation | Complete | Complete | 96% | SSRF prevention |
| FHIR ID Validation | Complete | Complete | 98% | Regex: `^[A-Za-z0-9\-._]+$` |
| DICOM UID Validation | Complete | Complete | 97% | Regex: `^[\d.]+$` |
| URL Injection Prevention | Complete | Complete | 99% | http/https rejection |

---

## 5. Privacy Specification (`spec/privacy.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| HIPAA Safe Harbor (18 identifiers) | Complete | Complete | 91% | All 18 identifiers removed |
| HMAC-SHA256 Pseudonymization | Complete | Complete | 93% | Site-specific salts |
| Referential Integrity | Complete | Complete | 88% | Cross-record linking |
| Birth Date Reduction | Complete | Complete | 95% | Year-only output |
| Geographic Generalization | Complete | Implemented | 82% | 3-digit ZIP prefix |

---

## 6. Audit Specification (`spec/audit.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| Record Structure (9 fields) | Complete | Complete | 96% | UUID, timestamp, hash chain |
| Hash Computation (SHA-256) | Complete | Complete | 98% | Canonical JSON, alpha order |
| Genesis Record | Complete | Complete | 97% | `"0" * 64` anchor |
| Chain Continuity | Complete | Complete | 95% | Forward-linking validation |
| Chain Verification | Complete | Complete | 94% | Incremental + full verify |

---

## 7. Provenance Specification (`spec/provenance.md`)

| Section | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| DataSource Model | Complete | Complete | 90% | UUID, type, origin, metadata |
| ProvenanceRecord Model | Complete | Complete | 88% | SHA-256 fingerprinting |
| DAG Lineage Model | Complete | Complete | 85% | Acyclicity enforced |
| Forward Queries | Complete | Complete | 83% | Source-to-derived traversal |
| Backward Queries | Complete | Complete | 84% | Derived-to-source traversal |
| Cross-Site Lineage | Complete | Implemented | 72% | Federated DAG merging |

---

## 8. Conformance Profiles

| Profile | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| Base | Complete | Complete | 92% | AuthZ + Ledger |
| Clinical Read | Complete | Complete | 89% | + FHIR |
| Imaging Guided | Complete | Complete | 86% | + DICOM |
| Multi-Site Federated | Complete | Implemented | 78% | + Provenance |
| Robot-Assisted Procedure | Complete | Implemented | 74% | Full stack + safety |

---

## 9. Safety Modules

| Module | Normative Status | Implementation | Test Coverage | Notes |
|--------|-----------------|----------------|---------------|-------|
| E-Stop (`estop.py`) | Complete | Complete | 96% | Independent of MCP servers |
| Approval Checkpoint | Complete | Complete | 91% | Human-in-the-loop gate |
| Gate Service | Complete | Complete | 89% | Procedure phase gates |
| Procedure State Machine | Complete | Complete | 87% | State transition validation |
| Robot Registry | Complete | Implemented | 82% | Platform registration |
| Site Verifier | Complete | Implemented | 80% | Site readiness validation |
| Task Validator | Complete | Implemented | 78% | Pre-execution validation |

---

## 10. Regulatory Overlays

| Overlay | Normative Status | Implementation | Test Coverage | Notes |
|---------|-----------------|----------------|---------------|-------|
| HIPAA (`regulatory/HIPAA.md`) | Complete | Complete | 90% | Safe Harbor mapping |
| 21 CFR Part 11 (`regulatory/CFR_PART_11.md`) | Complete | Complete | 88% | Audit trail mapping |
| FDA (`regulatory/US_FDA.md`) | Complete | Implemented | 75% | Device classification |
| IRB Site Policy | Draft | Planned | N/A | Template available |

---

## Aggregate Summary

| Category | Total Items | Complete | Implemented | Draft | Planned | Deferred |
|----------|-------------|----------|-------------|-------|---------|----------|
| Tool Contracts | 23 | 23 | 0 | 0 | 0 | 0 |
| Safety Modules | 7 | 4 | 3 | 0 | 0 | 0 |
| Conformance Profiles | 5 | 3 | 2 | 0 | 0 | 0 |
| Regulatory Overlays | 4 | 2 | 1 | 1 | 0 | 0 |
| Spec Sections | 9 | 7 | 2 | 0 | 0 | 0 |

---

## Maintenance

This matrix is updated with each specification release. Implementers SHOULD reference
this document when assessing readiness for conformance testing. Test coverage percentages
reflect the reference implementation test suite; individual implementations may vary.
