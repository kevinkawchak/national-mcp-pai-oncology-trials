# Clinical Read Profile

**National MCP-PAI Oncology Trials Standard — profiles/clinical-read.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

The Clinical Read Profile defines the requirements for implementations that provide FHIR R4 clinical data access with mandatory HIPAA de-identification. This profile builds on the [Base Profile](base-profile.md) and is required for any deployment that exposes patient health information, trial enrollment data, or clinical study metadata to MCP clients.

> Implementations claiming Clinical Read conformance MUST satisfy all Base Profile requirements AND all requirements defined in this profile.

---

## 2. Mandatory Tools

The Clinical Read Profile requires the `trialmcp-fhir` server in addition to all Base Profile servers.

| Tool | Requirement | Description |
|------|-------------|-------------|
| `fhir_read` | MUST | Read a single FHIR R4 resource by type and ID with de-identification |
| `fhir_search` | MUST | Search FHIR R4 resources with filters, capped at 100 results |
| `fhir_patient_lookup` | MUST | Return pseudonymized patient demographics and enrollment status |
| `fhir_study_status` | MUST | Return ResearchStudy summary with enrollment counts |

---

## 3. HIPAA De-Identification Requirements

### 3.1 Safe Harbor Method

All tools returning patient data MUST apply HIPAA Safe Harbor de-identification, removing or generalizing the following 18 identifiers:

| # | Identifier | Treatment |
|---|-----------|-----------|
| 1 | Names | MUST remove |
| 2 | Geographic data (smaller than state) | MUST remove |
| 3 | Dates (except year) | MUST reduce to year only |
| 4 | Phone numbers | MUST remove |
| 5 | Fax numbers | MUST remove |
| 6 | Email addresses | MUST remove |
| 7 | Social Security numbers | MUST remove |
| 8 | Medical record numbers | MUST pseudonymize via HMAC-SHA256 |
| 9 | Health plan beneficiary numbers | MUST remove |
| 10 | Account numbers | MUST remove |
| 11 | Certificate/license numbers | MUST remove |
| 12 | Vehicle identifiers | MUST remove |
| 13 | Device identifiers and serial numbers | MUST remove |
| 14 | Web URLs | MUST remove |
| 15 | IP addresses | MUST remove |
| 16 | Biometric identifiers | MUST remove |
| 17 | Full-face photographs | MUST remove |
| 18 | Any other unique identifying number | MUST remove or pseudonymize |

### 3.2 Pseudonymization

- MUST use HMAC-SHA256 with a site-specific salt for patient identifier pseudonymization
- MUST maintain referential integrity: the same real identifier MUST always produce the same pseudonym within a site
- MUST NOT allow reverse lookup from pseudonym to real identifier without the HMAC key
- MUST use separate HMAC keys per clinical site in federated deployments
- SHOULD rotate HMAC keys according to site security policy (minimum: annually)

### 3.3 Date Generalization

- MUST reduce all birth dates to year only (e.g., `1985-03-15` becomes `1985`)
- MUST reduce all clinical event dates to year only in de-identified output
- MUST preserve temporal ordering within year-only dates where clinically relevant
- SHOULD preserve month-level granularity only when explicitly consented and IRB-approved

---

## 4. FHIR R4 Requirements

### 4.1 Resource Validation

- MUST validate FHIR resource IDs against the pattern `^[A-Za-z0-9\-._]+$`
- MUST reject resource IDs containing URLs (SSRF prevention)
- MUST validate resource types against the FHIR R4 resource type list

### 4.2 Search Constraints

- MUST cap search results at 100 entries per query
- MUST support at minimum the `resource_type` search parameter
- SHOULD support additional FHIR search parameters (e.g., `patient`, `date`, `status`)
- MAY support pagination for result sets exceeding 100

### 4.3 Supported Resource Types

Conforming implementations MUST support at minimum:

| Resource Type | Requirement | Clinical Use |
|--------------|-------------|--------------|
| `Patient` | MUST | De-identified patient demographics |
| `ResearchStudy` | MUST | Clinical trial metadata and status |
| `Observation` | SHOULD | Clinical observations and measurements |
| `Condition` | SHOULD | Diagnosis and condition tracking |
| `Procedure` | SHOULD | Completed clinical and robotic procedures |
| `MedicationAdministration` | MAY | Treatment administration records |
| `Encounter` | MAY | Clinical encounter tracking |

---

## 5. Optional Tools

| Tool | Requirement | Description |
|------|-------------|-------------|
| `fhir_capability_statement` | MAY | FHIR CapabilityStatement exposure for client discovery |
| `fhir_batch_search` | MAY | Batch search across multiple resource types |

---

## 6. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Returning un-de-identified patient data | HIPAA: all patient data MUST be de-identified before return |
| Logging real patient identifiers in audit | Privacy: audit records MUST use pseudonymized identifiers |
| Returning more than 100 search results | Specification: search results MUST be capped at 100 |
| Accepting URL-embedded resource IDs | Security: SSRF prevention |
| Cross-site patient matching without consent | Privacy: federated patient matching requires explicit consent |

---

## 7. Required Schemas

In addition to Base Profile schemas, Clinical Read implementations MUST validate against:

| Schema | File | Purpose |
|--------|------|---------|
| FHIR Read | `schemas/fhir-read.schema.json` | Single resource read input/output |
| FHIR Search | `schemas/fhir-search.schema.json` | Collection search input/output |
| Consent Status | `schemas/consent-status.schema.json` | Patient consent state tracking |

---

## 8. Regulatory Overlays

| Regulation | Relevant Section | Coverage |
|-----------|-----------------|----------|
| HIPAA Privacy Rule | §164.514(b) Safe Harbor | 18-identifier de-identification method |
| HIPAA Privacy Rule | §164.502(b) Minimum necessary | Data minimization in search results |
| HIPAA Security Rule | §164.312(a)(1) Access control | Role-based FHIR access restrictions |
| 21 CFR Part 11 | §11.10(d) Authority enforcement | Tool-level access control audit |
| FDA AI/ML Guidance | Data integrity | De-identified data for AI/ML model inputs |

See [regulatory/HIPAA.md](../regulatory/HIPAA.md) for the full HIPAA compliance mapping.

---

## 9. Conformance Test Subset

Implementations claiming Clinical Read conformance MUST pass:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| Base Profile tests | 19 | All Base Profile conformance tests |
| FHIR read with de-identification | 3 | Correct de-ID, pseudonymization, year-only dates |
| FHIR search capping | 2 | Result cap at 100, filter validation |
| Patient lookup pseudonymization | 2 | HMAC-SHA256 consistency, no reverse lookup |
| Study status accuracy | 1 | Enrollment count and study metadata |
| FHIR input validation | 2 | ID format validation, SSRF rejection |
| **Total** | **29** | |

---

*This profile is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [spec/privacy.md](../spec/privacy.md) for the full de-identification specification.*
