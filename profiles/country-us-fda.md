# FDA 21 CFR Part 11 Overlay

**National MCP-PAI Oncology Trials Standard — profiles/country-us-fda.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

This profile defines the FDA 21 CFR Part 11 (Electronic Records; Electronic Signatures) overlay for implementations of the National MCP-PAI Oncology Trials Standard. 21 CFR Part 11 applies to all electronic records created, modified, maintained, archived, retrieved, or transmitted under any records requirements set forth in FDA regulations. This overlay ensures that MCP server deployments satisfy Part 11 requirements for audit trails, electronic signatures, system validation, and record integrity.

> All implementations deployed in FDA-regulated oncology clinical trials MUST satisfy the requirements defined in this overlay in addition to their declared conformance level.

---

## 2. Applicability

This overlay applies to any conforming implementation where:

- The clinical trial operates under an FDA Investigational New Drug (IND) or Investigational Device Exemption (IDE) application
- Electronic records are used to satisfy FDA predicate rules (e.g., 21 CFR Part 312, Part 812)
- Robot-assisted procedures generate electronic records submitted to or inspectable by FDA
- The sponsor, CRO, or clinical site is subject to FDA inspection

### 2.1 Scope of Electronic Records

The following MCP-generated records are within 21 CFR Part 11 scope:

| Record Type | MCP Source | Part 11 Classification |
|------------|-----------|----------------------|
| Audit trail entries | trialmcp-ledger | Electronic records — audit trails |
| Authorization decisions | trialmcp-authz | Electronic records — access controls |
| Clinical data queries | trialmcp-fhir | Electronic records — source data access |
| Imaging access logs | trialmcp-dicom | Electronic records — imaging data access |
| Data lineage records | trialmcp-provenance | Electronic records — data integrity |
| Robot procedure records | Task-order lifecycle | Electronic records — device operation logs |
| Consent status changes | Consent-status schema | Electronic records — informed consent tracking |

---

## 3. Subpart B — Electronic Records (§11.10)

### 3.1 System Validation (§11.10(a))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| System validation | MUST | Conforming implementations MUST be validated to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records |
| Validation documentation | MUST | Maintain documentation of validation activities including test protocols, results, and deviations |
| Schema validation | MUST | Use JSON Schema (draft 2020-12) validation for all MCP inputs/outputs as part of system validation |
| Conformance testing | MUST | Pass all conformance tests for declared profile level |

### 3.2 Record Generation (§11.10(b))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Human-readable copies | MUST | Audit ledger records MUST be exportable in human-readable format |
| Electronic copies | MUST | All electronic records MUST be exportable for FDA inspection |
| Ledger replay | MUST | `ledger_replay` tool MUST generate complete sequential traces |

### 3.3 Record Protection (§11.10(c))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Record retention | MUST | Electronic records MUST be retained for the duration required by applicable predicate rules |
| Record availability | MUST | Records MUST be available for FDA inspection throughout the retention period |
| Backup and recovery | MUST | Site-level responsibility; MCP audit records support reconstruction |

### 3.4 System Access Controls (§11.10(d))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Authority-based access | MUST | trialmcp-authz RBAC policies MUST limit system access to authorized individuals |
| Role-based permissions | MUST | 6-actor model enforces least-privilege access per [spec/actor-model.md](../spec/actor-model.md) |
| Token-based sessions | MUST | Time-limited, role-scoped tokens with revocation capability |

### 3.5 Audit Trail (§11.10(e))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Computer-generated audit trail | MUST | trialmcp-ledger produces hash-chained audit records automatically |
| Record creation/modification | MUST | Audit trail MUST independently record date/time of operator entries and actions |
| No record obscuring | MUST | Hash chain immutability ensures previously recorded information is not obscured |
| Audit trail retention | MUST | Audit records MUST be retained at least as long as the subject electronic records |
| Regulatory inspection | MUST | Audit trail MUST be available for FDA review and copying |

### 3.6 Operational System Checks (§11.10(f))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Sequence enforcement | MUST | Task-order lifecycle enforces step sequencing for robot procedures |
| Validity checks | MUST | JSON Schema validation enforces data entry constraints |
| Input validation | MUST | Format patterns, SSRF prevention, and range checks per [spec/security.md](../spec/security.md) |

### 3.7 Authority Checks (§11.10(g))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Permission verification | MUST | `authz_evaluate` MUST be called before every tool execution |
| Source/destination verification | MUST | Provenance tracking MUST verify data source and destination |
| Signature authority | MUST | Electronic signatures scoped to authorized signers only |

### 3.8 Device Checks (§11.10(h))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Input device verification | MUST | Robot capability profiles MUST verify device identity before procedure |
| Terminal identification | SHOULD | MCP client identification in audit records |

### 3.9 Personnel Training (§11.10(i))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Training documentation | MUST | Site-level responsibility; audit records support training verification |
| Access linked to training | SHOULD | Authorization policies SHOULD consider training status |

### 3.10 Written Policies (§11.10(j))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Accountability policies | MUST | Site-level responsibility; supported by RBAC and audit trails |
| Electronic signature policies | MUST | Document that electronic signatures are legally binding |

### 3.11 System Documentation (§11.10(k))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Controls documentation | MUST | This specification and its profiles serve as system controls documentation |
| Change control | MUST | [governance/DECISION_PROCESS.md](../governance/DECISION_PROCESS.md) defines change control procedures |
| Revision history | MUST | [changelog.md](../changelog.md) maintains revision history |

---

## 4. Subpart B — Electronic Signatures (§11.50, §11.70, §11.100)

### 4.1 Signature Manifestation (§11.50)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Signer identification | MUST | Electronic signatures MUST contain the printed name of the signer |
| Date and time | MUST | Signatures MUST include date and time of signing |
| Meaning | MUST | Signatures MUST include the meaning (review, approval, responsibility, authorship) |

### 4.2 Signature Linking (§11.70)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Record-signature binding | MUST | Electronic signatures MUST be linked to their respective electronic records |
| Non-repudiation | MUST | Hash-chained audit records provide non-repudiation of signed actions |
| Tamper detection | MUST | Chain verification detects any attempt to excise, copy, or transfer signatures |

### 4.3 General Requirements (§11.100)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Unique identifiers | MUST | Each signer MUST have a unique identifier (actor_id in MCP) |
| Identity verification | MUST | trialmcp-authz MUST verify signer identity before token issuance |
| Signature non-reuse | MUST | Signed tokens MUST NOT be reused across sessions |

---

## 5. FDA AI/ML Medical Device Guidance

### 5.1 Software as Medical Device (SaMD)

Robot agents operating under this standard may be classified as SaMD or components of a medical device:

| Consideration | Mapping | Description |
|--------------|---------|-------------|
| SaMD classification | Robot capability profile | Robot type and USL score inform risk classification |
| Predetermined change control plan | USL scoring framework | Score thresholds define acceptable operational boundaries |
| Real-world performance monitoring | Audit and provenance | Continuous monitoring via hash-chained audit trail |
| Transparency | Provenance DAG | Complete data lineage from input to clinical decision |

### 5.2 Good Machine Learning Practice (GMLP)

| Principle | MCP Standard Support |
|----------|---------------------|
| Multi-disciplinary expertise | 6-actor model with distinct roles |
| Good software engineering practices | JSON Schema validation, conformance testing |
| Representative data | Provenance tracking of training data sources |
| Independent training and test datasets | Provenance lineage separates data uses |
| Reference datasets | Federated audit enables cross-site validation |
| Designed for real-world conditions | USL scoring assesses operational readiness |
| Clinically meaningful performance | RECIST measurements, procedure outcome tracking |

---

## 6. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Obscuring previously recorded audit information | §11.10(e): audit trails MUST NOT allow previous records to be obscured |
| Reusing electronic signatures across sessions | §11.100(b): signatures MUST be unique per signing event |
| Deleting or modifying audit chain records | §11.10(e): immutable hash-chained ledger requirement |
| Operating without validated system documentation | §11.10(a): system validation is mandatory |
| Allowing unauthorized access to electronic records | §11.10(d): authority-based access controls required |

---

## 7. Conformance Test Subset

Implementations claiming FDA 21 CFR Part 11 compliance MUST pass:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| Hash chain immutability | 3 | Genesis hash, append integrity, tamper detection |
| Audit trail completeness | 3 | All tool calls audited, timestamps correct, no gaps |
| Authority enforcement | 2 | RBAC evaluation, token lifecycle |
| Record export | 2 | Human-readable export, electronic copy export |
| Signature linking | 1 | Signature-record binding verification |
| Schema validation | 2 | Input validation, output validation |
| **Total** | **13** | |

---

## 8. Regulatory Cross-References

| 21 CFR Part 11 Section | MCP Standard Component | Implementation |
|------------------------|----------------------|----------------|
| §11.10(a) Validation | Conformance testing | Schema validation + profile test suites |
| §11.10(b) Copies | trialmcp-ledger | `ledger_replay`, `ledger_query` |
| §11.10(c) Protection | Site capability | Retention and availability per site policy |
| §11.10(d) Access | trialmcp-authz | Deny-by-default RBAC, 6-actor model |
| §11.10(e) Audit trails | trialmcp-ledger | Hash-chained immutable audit ledger |
| §11.10(f) Checks | JSON Schema, task-order | Schema validation + workflow sequencing |
| §11.10(g) Authority | trialmcp-authz, trialmcp-provenance | Permission evaluation + source verification |
| §11.10(k) Documentation | Governance | Specification, changelog, decision process |
| §11.50 Manifestation | Audit records | Signer name, timestamp, action meaning |
| §11.70 Linking | Hash chain | SHA-256 chain links signatures to records |
| §11.100 General | trialmcp-authz | Unique IDs, identity verification |

---

*This overlay is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [regulatory/CFR_PART_11.md](../regulatory/CFR_PART_11.md) for the full 21 CFR Part 11 compliance mapping and [regulatory/US_FDA.md](../regulatory/US_FDA.md) for FDA AI/ML guidance alignment.*
