# Privacy Specification

**National MCP-PAI Oncology Trials Standard — spec/privacy.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the privacy requirements for all conforming MCP server implementations. Privacy is enforced through HIPAA Safe Harbor de-identification, HMAC-SHA256 pseudonymization, and minimum necessary data access principles. These requirements are derived from the reference FHIR server's `_deidentify_resource()` implementation and the DICOM server's patient hashing mechanism.

---

## 2. HIPAA Safe Harbor De-identification

### 2.1 Requirement

All MCP servers returning patient data MUST apply HIPAA Safe Harbor de-identification as defined in 45 CFR 164.514(b)(2) before returning results to any actor. De-identification MUST remove or generalize all 18 categories of protected health information (PHI).

### 2.2 The 18 PHI Identifiers

Conforming implementations MUST remove or generalize the following identifiers:

| # | Identifier | Action |
|---|-----------|--------|
| 1 | Names | Remove entirely |
| 2 | Geographic data (below state) | Generalize to state level |
| 3 | Dates (except year) | Reduce to year only |
| 4 | Telephone numbers | Remove entirely |
| 5 | Fax numbers | Remove entirely |
| 6 | Email addresses | Remove entirely |
| 7 | Social Security numbers | Remove entirely |
| 8 | Medical record numbers | Pseudonymize with HMAC-SHA256 |
| 9 | Health plan beneficiary numbers | Remove entirely |
| 10 | Account numbers | Remove entirely |
| 11 | Certificate/license numbers | Remove entirely |
| 12 | Vehicle identifiers | Remove entirely |
| 13 | Device identifiers and serial numbers | Remove entirely |
| 14 | Web URLs | Remove entirely |
| 15 | IP addresses | Remove entirely |
| 16 | Biometric identifiers | Remove entirely |
| 17 | Full-face photographs | Remove entirely |
| 18 | Any other unique identifying number | Pseudonymize or remove |

### 2.3 FHIR Resource De-identification

For FHIR Patient resources, the de-identification pipeline MUST:
- Remove `name`, `telecom`, `address` elements entirely
- Reduce `birthDate` to year only (e.g., `1965-03-15` becomes `1965`)
- Pseudonymize `id` and `identifier` values using HMAC-SHA256
- Preserve `gender` as it does not constitute PHI when isolated
- Preserve clinical content (conditions, observations) with pseudonymized subject references

For other FHIR clinical resources (Observation, Condition, MedicationRequest):
- Pseudonymize `subject.reference` to maintain referential integrity
- Preserve clinical content without modification

### 2.4 DICOM De-identification

For DICOM query results at the PATIENT level:
- Patient names MUST be hashed using SHA-256 truncated to 12 characters
- Patient IDs MUST be pseudonymized using HMAC-SHA256
- All other patient-identifying DICOM tags MUST be removed or generalized

---

## 3. Pseudonymization

### 3.1 HMAC-SHA256 Pseudonymization

Pseudonymization MUST use HMAC-SHA256 with a site-specific salt to generate consistent pseudonyms:

- The same real identifier MUST always produce the same pseudonym within a site
- Different sites MUST use different salts, producing different pseudonyms for the same patient
- Pseudonyms MUST NOT be reversible without access to the salt
- The salt MUST be stored securely and separately from patient data

### 3.2 Referential Integrity

Pseudonymization MUST maintain referential integrity across de-identified records:
- A Patient resource pseudonym MUST match the subject reference pseudonym in related Observation resources
- This enables clinical data analysis without exposing real patient identifiers
- Cross-resource joins MUST work correctly on pseudonymized identifiers

### 3.3 Cross-Site Pseudonymization

- Different sites MUST use different HMAC salts
- The same patient at different sites MUST produce different pseudonyms
- Cross-site patient linking MUST NOT be possible through pseudonym comparison
- If cross-site analysis requires patient linking, it MUST be performed through a trusted third-party linkage service with appropriate patient consent and IRB approval

---

## 4. Minimum Necessary Standard

### 4.1 Data Access Scope

Each actor MUST receive only the minimum data necessary for their assigned function:
- Robot agents receive de-identified clinical data relevant to their procedure
- Data monitors receive aggregate or de-identified data for quality review
- Auditors receive audit records without clinical content
- Search results MUST be capped (default 100) to prevent bulk data extraction

### 4.2 Query Restrictions

- FHIR search results MUST be limited to 100 records per query
- DICOM query levels MUST be restricted by role (see [actor-model.md](actor-model.md))
- Patient-level queries MUST NOT be available to all roles

---

## 5. Data Retention and Disposal

### 5.1 Token Data

- Expired tokens SHOULD be purged after a configurable retention period
- Revoked tokens MUST be retained in the revocation list for the original token's full lifetime

### 5.2 Audit Data

- Audit records MUST NOT be deleted (append-only ledger)
- Audit records MUST be retained for the duration required by 21 CFR Part 11 and applicable trial protocols

### 5.3 Provenance Data

- Provenance records MUST be retained for the duration of the clinical trial plus any regulatory retention period
- Data fingerprints MUST be retained to enable future integrity verification

---

## 6. Federated Privacy

### 6.1 Data Locality

Patient data MUST remain at the originating site. Only the following MAY cross site boundaries:
- Aggregated model parameters (for federated learning)
- De-identified aggregate statistics
- Audit chain summaries (without clinical content)

### 6.2 Differential Privacy

Federated learning aggregation SHOULD apply differential privacy mechanisms:
- Gaussian noise addition to model updates
- Privacy budget tracking per patient and per site
- Configurable epsilon values with site-level override

### 6.3 Secure Aggregation

Cross-site model aggregation SHOULD use mask-based secure aggregation to prevent the aggregation server from observing individual site model updates.
