# New York Health Information Overlay

**National MCP-PAI Oncology Trials Standard — profiles/state-us-ny.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

This profile defines the New York state health information privacy overlay for implementations of the National MCP-PAI Oncology Trials Standard deployed at clinical sites within the State of New York. New York imposes additional requirements beyond federal HIPAA through the New York Public Health Law (PHL), the New York SHIELD Act, and Department of Health (DOH) regulations. This overlay supplements — but does not replace — the federal regulatory requirements.

> Implementations deployed at New York clinical sites MUST satisfy all applicable conformance profile requirements AND all requirements defined in this overlay.

---

## 2. Applicability

This overlay applies to any conforming implementation where:

- The clinical site is physically located in New York State, OR
- The implementation processes private information of New York residents, OR
- The sponsoring entity conducts business in New York and maintains computerized data including New York residents' private information

---

## 3. New York Public Health Law (PHL) Requirements

### 3.1 PHL Article 27-F — HIV/AIDS Confidentiality

New York has among the most stringent HIV-related confidentiality laws in the nation. While oncology trials may not directly involve HIV data, co-morbidity records may include HIV status.

| Requirement | Keyword | Description |
|------------|---------|-------------|
| HIV-related information segregation | MUST | FHIR resources containing HIV-related data MUST be flagged and access-restricted |
| Written authorization for HIV disclosure | MUST | MUST NOT return HIV-related data without specific PHL 2782 authorization |
| Audit of HIV data access | MUST | Every access to HIV-related clinical data MUST be separately audited |
| De-identification of HIV indicators | MUST | HIPAA Safe Harbor de-identification MUST remove HIV-related diagnostic codes when HIV is not the trial focus |

### 3.2 PHL Article 44 — Research Participant Protections

| Requirement | Keyword | Description |
|------------|---------|-------------|
| IRB oversight documentation | MUST | Site capability profile MUST reference NY-approved IRB |
| Informed consent verification | MUST | Consent status MUST include New York-specific research consent |
| Vulnerable population protections | MUST | Enhanced consent tracking for minors, incarcerated, and cognitively impaired |

---

## 4. SHIELD Act Requirements (S5575B)

The Stop Hacks and Improve Electronic Data Security (SHIELD) Act (effective March 2020) imposes data security requirements on entities holding private information of New York residents.

### 4.1 Reasonable Security Safeguards

| Category | Requirement | Keyword | MCP Standard Mapping |
|----------|------------|---------|---------------------|
| Administrative | Risk assessment | MUST | Robot and site capability profiles document risks |
| Administrative | Employee training | MUST | Outside MCP scope; site-level responsibility |
| Administrative | Incident response plan | MUST | Audit ledger supports incident reconstruction |
| Technical | Access controls | MUST | trialmcp-authz deny-by-default RBAC |
| Technical | Data encryption | MUST | SHA-256 hashing; TLS for transport (site responsibility) |
| Technical | Intrusion detection | SHOULD | Health status monitoring supports anomaly detection |
| Physical | Physical security | MUST | Outside MCP scope; site-level responsibility |
| Physical | Secure disposal | MUST | Provenance records track data lifecycle including disposal |

### 4.2 Breach Notification

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Breach detection capability | MUST | Audit chain verification supports tamper detection |
| Breach timeline documentation | MUST | Ledger replay provides exact timeline of accessed records |
| Notification support | SHOULD | Audit queries support identifying affected individuals |
| NY Attorney General notification | MUST | Site-level responsibility; MCP audit data supports investigation |

---

## 5. New York Department of Health Regulations

### 5.1 10 NYCRR Part 405 — Hospital Requirements

For implementations deployed at New York hospitals:

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Medical record confidentiality | MUST | All FHIR data access MUST comply with hospital record confidentiality rules |
| Authorized access only | MUST | trialmcp-authz policies MUST reflect NY hospital access policies |
| Record retention | MUST | Audit and provenance records MUST be retained per DOH requirements (minimum 6 years for adults) |
| Quality assurance integration | SHOULD | Robot procedure outcomes available for hospital QA programs |

### 5.2 10 NYCRR Part 86 — Research Requirements

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Research data segregation | MUST | Clinical trial data MUST be segregated from routine care data in MCP server access |
| Research consent tracking | MUST | Consent status MUST distinguish clinical care consent from research consent |
| Data use agreements | MUST | Cross-site data sharing MUST comply with NY research data use agreement requirements |

---

## 6. Mental Health Law (MHL) Article 33

New York Mental Health Law provides additional protections for mental health records that may be present in oncology patient co-morbidity data.

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Mental health record access restriction | MUST | FHIR resources containing mental health data MUST have enhanced access controls |
| Separate consent for MH disclosure | MUST | Mental health data disclosure requires consent separate from general research consent |
| Audit of MH data access | MUST | Every access to mental health clinical data MUST be separately audited |

---

## 7. Implementation Guidance

### 7.1 Consent Status Extensions

For New York deployments, the consent-status schema MUST be extended (via vendor extension) or interpreted to include:

| Consent Category | Description |
|-----------------|-------------|
| `ny_research_consent` | New York research participant consent per PHL Article 44 |
| `ny_hiv_authorization` | PHL 2782 written authorization for HIV data access |
| `ny_mental_health_consent` | MHL Article 33 consent for mental health record access |
| `ny_shield_data_processing` | SHIELD Act compliant data processing acknowledgment |

### 7.2 Enhanced Audit Requirements

New York sites MUST configure their audit systems to:

- Separately flag and track access to HIV-related, mental health, and substance abuse records
- Retain audit records for a minimum of 6 years (adult patients) or 6 years past age 18 (minor patients)
- Support breach investigation queries with actor, time range, and data category filtering

### 7.3 Site Capability Profile

New York site capability profiles MUST declare:

- `jurisdiction`: `"US-NY"`
- `irb_approval`: Reference to New York-approved IRB
- `data_retention_years`: Minimum 6
- `special_categories`: Array including applicable categories (`hiv`, `mental_health`, `substance_abuse`)

---

## 8. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Returning HIV data without PHL 2782 authorization | NY PHL Article 27-F: strict HIV confidentiality |
| Returning mental health data without MHL consent | NY MHL Article 33: separate mental health consent |
| Audit record retention less than 6 years | NY DOH 10 NYCRR Part 405: minimum retention period |
| Cross-site sharing without NY data use agreement | NY research regulations: DUA required for data sharing |

---

## 9. Regulatory Cross-References

| NY Regulation | Standard Component | Mapping |
|--------------|-------------------|---------|
| PHL Article 27-F | trialmcp-fhir, trialmcp-authz | HIV data segregation and access control |
| PHL Article 44 | Consent status schema | Research participant consent tracking |
| SHIELD Act S5575B | trialmcp-authz, trialmcp-ledger | Access controls and breach detection |
| 10 NYCRR Part 405 | Site capability profile | Hospital-level compliance documentation |
| 10 NYCRR Part 86 | trialmcp-provenance | Research data segregation and tracking |
| MHL Article 33 | trialmcp-fhir, trialmcp-authz | Mental health record protection |

---

*This overlay is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [regulatory/HIPAA.md](../regulatory/HIPAA.md) for federal privacy requirements that apply alongside this state overlay.*
