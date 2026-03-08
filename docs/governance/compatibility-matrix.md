# Compatibility Matrix

**National MCP-PAI Oncology Trials Standard — Compatibility Matrix**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This document defines the compatibility relationships between specification versions,
conformance profiles, server implementations, and external standards. Implementers
MUST consult this matrix to determine which versions of the specification are
interoperable and which profiles are compatible with their deployment tier.

---

## 1. Specification Version Compatibility

### 1.1 Version Numbering

The standard follows Semantic Versioning 2.0.0 (SemVer):
- **Major** (X.0.0): Breaking changes to normative tool contracts or security model
- **Minor** (0.X.0): Additive changes (new tools, new profiles, new optional features)
- **Patch** (0.0.X): Clarifications, errata, and non-behavioral changes

### 1.2 Version Compatibility Table

| Version A | Version B | Compatibility | Notes |
|-----------|-----------|---------------|-------|
| 0.1.x | 0.1.y | Full | Patch versions are fully compatible |
| 0.1.x | 0.2.x | Backward | 0.2 clients can consume 0.1 servers |
| 0.2.x | 0.1.x | Partial | 0.1 clients lack 0.2 features; graceful degradation required |
| 0.x.x | 1.0.x | Migration | Migration guide will be provided; breaking changes possible |
| 1.0.x | 1.y.x | Backward | Minor versions are backward compatible within major |

### 1.3 Compatibility Guarantees

| Guarantee | Scope | Enforcement |
|-----------|-------|-------------|
| Tool contract stability | All 23 normative tools | Input/output schemas frozen within major version |
| Error code stability | All standard error codes | Codes never removed within major version |
| Audit record format | 9-field record structure | Fields never removed within major version |
| Actor model stability | 6-actor role set | Roles never removed within major version |
| Hash algorithm | SHA-256 | Algorithm never changed within major version |

---

## 2. Profile Compatibility Matrix

### 2.1 Profile-to-Conformance Level Mapping

| Profile | Conformance Level | Required Servers | Required Tools |
|---------|-------------------|------------------|----------------|
| `base` | Level 1 (Core) | `trialmcp-authz`, `trialmcp-ledger` | 10 |
| `clinical-read` | Level 2 (Clinical Read) | Level 1 + `trialmcp-fhir` | 14 |
| `imaging-guided` | Level 3 (Imaging) | Level 2 + `trialmcp-dicom` | 18 |
| `multi-site-federated` | Level 4 (Federated) | Level 3 + `trialmcp-provenance` | 23 |
| `robot-assisted-procedure` | Level 5 (Robot Procedure) | All 5 servers + safety modules | 23 + safety |

### 2.2 Profile Cumulative Requirements

Profiles are cumulative. Each higher-level profile includes all requirements of lower
profiles. An implementation declaring Level 3 (Imaging) conformance MUST also satisfy
all Level 1 (Core) and Level 2 (Clinical Read) requirements.

```
Level 5: Robot-Assisted Procedure
  └── Level 4: Multi-Site Federated
       └── Level 3: Imaging Guided
            └── Level 2: Clinical Read
                 └── Level 1: Core (Base)
```

### 2.3 Profile Interoperability

| Client Profile | Server Profile | Interoperable | Behavior |
|---------------|----------------|---------------|----------|
| base | base | Yes | Full functionality |
| base | clinical-read | Yes | Client uses only base tools |
| base | robot-assisted | Yes | Client uses only base tools |
| clinical-read | base | Partial | FHIR tools unavailable |
| imaging-guided | clinical-read | Partial | DICOM tools unavailable |
| robot-assisted | multi-site-fed | Partial | Safety modules managed locally |
| multi-site-fed | multi-site-fed | Yes | Full cross-site functionality |

---

## 3. Server Version Compatibility

### 3.1 MCP Server Versions

| Server | Current Version | Min Compatible | Protocol Version |
|--------|----------------|----------------|-----------------|
| `trialmcp-authz` | 0.1.0 | 0.1.0 | MCP 2024-11-05 |
| `trialmcp-fhir` | 0.1.0 | 0.1.0 | MCP 2024-11-05 |
| `trialmcp-dicom` | 0.1.0 | 0.1.0 | MCP 2024-11-05 |
| `trialmcp-ledger` | 0.1.0 | 0.1.0 | MCP 2024-11-05 |
| `trialmcp-provenance` | 0.1.0 | 0.1.0 | MCP 2024-11-05 |

### 3.2 Cross-Server Compatibility

All five servers MUST be deployed at the same specification version within a single
site deployment. Mixed-version deployments within a site are not supported.

Cross-site deployments MAY have different patch versions (0.1.x vs 0.1.y) but MUST
share the same minor version for federated operations.

---

## 4. External Standards Compatibility

### 4.1 Healthcare Standards

| Standard | Version | Compatibility | Usage |
|----------|---------|---------------|-------|
| HL7 FHIR | R4 (4.0.1) | Required | Clinical data model |
| DICOM | PS3.18 (2024b) | Required | Imaging data model |
| HL7 v2 | 2.5.1+ | Optional | Legacy system integration |
| ICD-10-CM | 2026 | Required | Diagnosis coding |
| LOINC | 2.77+ | Required | Laboratory coding |
| RxNorm | Current | Required | Medication coding |
| MedDRA | 27.0+ | Required | Adverse event coding |
| SNOMED CT | US Edition | Optional | Clinical terminology |

### 4.2 Regulatory Standards

| Standard | Version | Compatibility | Usage |
|----------|---------|---------------|-------|
| 21 CFR Part 11 | Current | Required | Electronic records/signatures |
| HIPAA Privacy Rule | Current | Required | De-identification |
| HIPAA Security Rule | Current | Required | Technical safeguards |
| ICH-GCP E6(R2) | Current | Required | Good Clinical Practice |
| ICH E8(R1) | Current | Informative | Trial design principles |
| ISO 14155:2020 | Current | Informative | Medical device clinical trials |
| IEC 62304:2006+A1:2015 | Current | Informative | Medical device software lifecycle |

### 4.3 Security Standards

| Standard | Version | Compatibility | Usage |
|----------|---------|---------------|-------|
| NIST SP 800-53 | Rev 5 | Informative | Security controls baseline |
| NIST SP 800-171 | Rev 3 | Informative | CUI protection |
| OWASP Top 10 | 2021 | Required | Web application security |
| CWE/SANS Top 25 | 2024 | Informative | Software weakness prevention |

---

## 5. Runtime Environment Compatibility

### 5.1 Python Runtime

| Component | Minimum Version | Recommended | Notes |
|-----------|----------------|-------------|-------|
| Python | 3.10 | 3.12+ | Type hints, asyncio |
| MCP SDK | 1.0.0 | Latest stable | Server framework |
| FHIR Client | fhir.resources 7.0+ | Latest | FHIR R4 models |
| Cryptography | cryptography 41.0+ | Latest | SHA-256, HMAC |

### 5.2 TypeScript Runtime

| Component | Minimum Version | Recommended | Notes |
|-----------|----------------|-------------|-------|
| Node.js | 18 LTS | 20 LTS | ESM support |
| TypeScript | 5.0 | 5.4+ | Strict mode required |
| MCP SDK | @modelcontextprotocol/sdk 1.0+ | Latest | Server framework |

---

## 6. Deployment Environment Compatibility

| Environment | Supported | Notes |
|-------------|-----------|-------|
| On-premises (air-gapped) | Yes | Recommended for Level 5 |
| Private cloud (single-tenant) | Yes | HIPAA BAA required |
| Public cloud (multi-tenant) | Conditional | HIPAA BAA + encryption at rest |
| Hybrid (on-prem + cloud) | Yes | Data residency constraints apply |
| Edge (operating room) | Yes | Required for real-time robot control |

---

## 7. State and Jurisdictional Overlays

| Jurisdiction | Overlay Profile | Additional Requirements |
|-------------|----------------|------------------------|
| United States (Federal) | `country-us-fda` | FDA CDRH device classification |
| California | `state-us-ca` | CCPA/CPRA data rights |
| New York | `state-us-ny` | NY SHIELD Act security requirements |
| Texas | Planned | THIPA compliance |
| Florida | Planned | FL HB 1551 compliance |

---

## Matrix Maintenance

This compatibility matrix is updated with each specification release. New entries
are added when new versions, profiles, or external standard dependencies are
introduced. Entries are never removed from the matrix; deprecated entries are marked
with their deprecation version and replacement.
