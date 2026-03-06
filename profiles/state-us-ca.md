# California CCPA Overlay

**National MCP-PAI Oncology Trials Standard — profiles/state-us-ca.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

This profile defines the California Consumer Privacy Act (CCPA) / California Privacy Rights Act (CPRA) overlay for implementations of the National MCP-PAI Oncology Trials Standard deployed at clinical sites within the State of California. This overlay supplements — but does not replace — the federal regulatory requirements defined in the [Base Profile](base-profile.md) and higher conformance levels.

> Implementations deployed at California clinical sites MUST satisfy all applicable conformance profile requirements AND all requirements defined in this overlay.

---

## 2. Applicability

This overlay applies to any conforming implementation where:

- The clinical site is physically located in California, OR
- The implementation processes personal information of California residents, OR
- The sponsoring entity meets CCPA business thresholds (annual revenue > $25M, processes data of 100,000+ consumers, or derives 50%+ revenue from selling personal information)

### 2.1 CCPA-HIPAA Interaction

The CCPA provides a partial exemption for protected health information (PHI) governed by HIPAA. However, the following categories of data processed by MCP servers may NOT fall under the HIPAA exemption and MUST be treated as CCPA-covered personal information:

| Data Category | HIPAA Exempt? | CCPA Treatment |
|--------------|---------------|----------------|
| Patient PHI in FHIR resources | Yes (when covered entity) | HIPAA governs; CCPA defers |
| Robot telemetry linked to patient | Partial | MUST apply CCPA if not in designated record set |
| Site staff user accounts and access logs | No | MUST apply CCPA consumer rights |
| Trial participant contact information (outside EHR) | Depends on context | MUST evaluate per record |
| De-identified data | N/A | Not personal information under CCPA |
| Pseudonymized data (reversible) | Depends | MUST treat as personal information under CCPA |

---

## 3. Mandatory Requirements

### 3.1 Right to Know (CCPA §1798.100)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Categories disclosure | MUST | Disclose categories of personal information collected via MCP tools |
| Purpose disclosure | MUST | Disclose purposes for which personal information is used |
| Source disclosure | MUST | Disclose categories of sources from which PI is collected |
| Provenance support | MUST | Use trialmcp-provenance to track data lineage for disclosure |

### 3.2 Right to Delete (CCPA §1798.105)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Deletion request handling | MUST | Process verified deletion requests for non-exempt data |
| Audit trail preservation | MUST | Retain audit records in ledger even after data deletion (21 CFR Part 11) |
| Provenance annotation | MUST | Record deletion events in provenance DAG |
| Exemption documentation | MUST | Document exemptions applied (e.g., HIPAA, legal obligation) |

### 3.3 Right to Opt-Out of Sale (CCPA §1798.120)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| No sale of PI | MUST | MCP server implementations MUST NOT sell personal information |
| Cross-site sharing controls | MUST | Federated data sharing MUST be limited to trial purposes |
| Consent tracking | MUST | Use consent-status schema to track opt-out preferences |

### 3.4 Non-Discrimination (CCPA §1798.125)

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Equal service | MUST | MUST NOT discriminate against consumers exercising CCPA rights |
| Trial participation | MUST | Privacy rights exercise MUST NOT affect clinical trial eligibility |

---

## 4. CPRA Enhancements (Effective January 1, 2023)

### 4.1 Sensitive Personal Information

The CPRA designates certain categories as sensitive personal information requiring additional protections:

| Category | Present in MCP? | Additional Requirement |
|----------|----------------|----------------------|
| Health information | Yes (FHIR data) | Limit use to clinical trial purposes |
| Precise geolocation | Possible (site logs) | MUST NOT collect precise geolocation |
| Biometric data | Possible (robot sensors) | MUST de-identify before MCP processing |
| Genetic data | Possible (genomic records) | MUST apply enhanced access controls |

### 4.2 Data Minimization (CPRA §1798.100(c))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Collection limitation | MUST | Collect only PI reasonably necessary for clinical trial purposes |
| Retention limitation | MUST | Retain PI only as long as necessary; define retention schedules |
| Purpose limitation | MUST | Use PI only for disclosed purposes |

### 4.3 Risk Assessments (CPRA §1798.185(a)(15))

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Processing risk assessment | SHOULD | Conduct risk assessments for PI processing via robot agents |
| Document safeguards | SHOULD | Document security measures in site capability profile |

---

## 5. Implementation Guidance

### 5.1 Consent Status Integration

The `schemas/consent-status.schema.json` MUST be extended (via vendor extension `x-{vendor}`) or interpreted to include California-specific consent categories:

| Consent Category | Description |
|-----------------|-------------|
| `ccpa_data_collection` | Consent to collection of personal information |
| `ccpa_data_sharing` | Consent to cross-site data sharing for trial purposes |
| `ccpa_sensitive_pi` | Consent to processing of sensitive personal information |
| `ccpa_automated_decision` | Consent to automated decision-making by robot agents |

### 5.2 Privacy Notice Requirements

California-deployed sites MUST make available a privacy notice that includes:

- Categories of PI collected via MCP server interactions
- Purposes for collection and use
- Categories of third parties with whom PI is shared
- Consumer rights under CCPA/CPRA
- Contact information for privacy inquiries

---

## 6. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Sale of personal information | CCPA §1798.120: MCP servers MUST NOT facilitate PI sale |
| Collecting precise geolocation | CPRA: precise geolocation is sensitive PI requiring opt-in |
| Retaining PI beyond documented retention period | CPRA: data minimization requires defined retention schedules |
| Discrimination based on privacy rights exercise | CCPA §1798.125: non-discrimination requirement |

---

## 7. Regulatory Cross-References

| CCPA/CPRA Section | Standard Component | Mapping |
|-------------------|-------------------|---------|
| §1798.100 Right to Know | trialmcp-provenance | Lineage queries support disclosure |
| §1798.105 Right to Delete | trialmcp-ledger | Deletion recorded in audit; data removed |
| §1798.110 Categories | Site capability profile | PI categories documented per site |
| §1798.120 Opt-Out | Consent status schema | Opt-out preferences tracked |
| §1798.125 Non-Discrimination | trialmcp-authz | Access policies MUST NOT penalize rights exercise |
| §1798.185 Risk Assessment | Robot capability profile | Processing risks documented |

---

*This overlay is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [regulatory/HIPAA.md](../regulatory/HIPAA.md) for federal privacy requirements that apply alongside this state overlay.*
