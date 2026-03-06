# HIPAA Compliance Overlay

**National MCP-PAI Oncology Trials Standard — HIPAA Mapping**
**Version**: 0.1.0

---

## 1. Overview

This document maps the national MCP-PAI oncology trials standard to HIPAA Privacy Rule and Security Rule requirements. The standard mandates HIPAA Safe Harbor de-identification for all patient data returned through MCP tool contracts.

---

## 2. HIPAA Privacy Rule

### 2.1 De-identification Standard (45 CFR 164.514)

The specification mandates the Safe Harbor method of de-identification (45 CFR 164.514(b)(2)), requiring removal or generalization of all 18 categories of identifiers.

| PHI Category | Specification Requirement | Implementation |
|-------------|--------------------------|----------------|
| Names | MUST remove | FHIR: remove `name` element |
| Geographic data (below state) | MUST generalize | Reduce to state level |
| Dates (except year) | MUST generalize | Year-only format |
| Phone numbers | MUST remove | Remove `telecom` with phone system |
| Fax numbers | MUST remove | Remove `telecom` with fax system |
| Email addresses | MUST remove | Remove `telecom` with email system |
| SSN | MUST remove | Remove from all identifiers |
| Medical record numbers | MUST pseudonymize | HMAC-SHA256 with site salt |
| Health plan numbers | MUST remove | Remove from identifiers |
| Account numbers | MUST remove | Remove from identifiers |
| Certificate/license numbers | MUST remove | Remove from identifiers |
| Vehicle identifiers | MUST remove | Not typically in clinical data |
| Device identifiers | MUST remove | Remove from identifiers |
| Web URLs | MUST remove | Remove; also SSRF prevention |
| IP addresses | MUST remove | Not included in clinical responses |
| Biometric identifiers | MUST remove | Not typically in FHIR/DICOM |
| Full-face photos | MUST remove | Not returned through MCP tools |
| Other unique identifiers | MUST pseudonymize or remove | Case-by-case evaluation |

### 2.2 Minimum Necessary Standard (45 CFR 164.502(b))

The specification enforces minimum necessary through:
- Role-based access control limiting data access by actor type
- Search result caps (100 records maximum)
- Query level restrictions for DICOM (role-dependent)
- De-identification applied before data leaves the server boundary

### 2.3 Authorization and Consent

- The specification does not manage patient consent directly
- Sites MUST obtain appropriate patient authorization or consent per their IRB-approved protocol
- The authorization server enforces technical access controls; it does not replace human authorization workflows

---

## 3. HIPAA Security Rule

### 3.1 Administrative Safeguards (45 CFR 164.308)

| Safeguard | Specification Coverage |
|-----------|----------------------|
| § 164.308(a)(1) Security management | Deny-by-default RBAC, input validation |
| § 164.308(a)(3) Workforce security | Role-based access with six defined actors |
| § 164.308(a)(4) Access management | Token-based sessions with role scoping |
| § 164.308(a)(5) Security awareness | Audit ledger enables security review |
| § 164.308(a)(6) Security incidents | Chain verification detects tampering |
| § 164.308(a)(8) Evaluation | Conformance testing validates security |

### 3.2 Technical Safeguards (45 CFR 164.312)

| Safeguard | Specification Coverage |
|-----------|----------------------|
| § 164.312(a)(1) Access control | Deny-by-default RBAC, token lifecycle |
| § 164.312(b) Audit controls | Hash-chained append-only ledger |
| § 164.312(c)(1) Integrity | SHA-256 hash chains, provenance fingerprinting |
| § 164.312(d) Authentication | Token-based with SHA-256 hashed storage |
| § 164.312(e)(1) Transmission security | TLS 1.2+ required in production |

### 3.3 Physical Safeguards (45 CFR 164.310)

Physical safeguards are implementation-specific and outside the scope of the protocol specification. Sites MUST address physical security in their deployment procedures.

---

## 4. Pseudonymization Details

### 4.1 HMAC-SHA256 Implementation

Pseudonymization MUST use HMAC-SHA256:
- **Key**: Site-specific salt (minimum 32 bytes, cryptographically random)
- **Input**: Real patient identifier (as UTF-8 bytes)
- **Output**: Hexadecimal digest used as pseudonym
- **Consistency**: Same identifier + same salt = same pseudonym (enables referential integrity)

### 4.2 Salt Management

- Each site MUST generate a unique salt
- Salts MUST be stored in a secure key management system
- Salts MUST NOT be transmitted to other sites or stored alongside patient data
- Salt rotation MUST be coordinated with the re-pseudonymization of all affected records

### 4.3 DICOM Patient Name Hashing

For DICOM PATIENT-level queries:
- Patient names MUST be hashed using SHA-256
- The hash MUST be truncated to 12 characters
- The truncated hash replaces the patient name in query results

---

## 5. Breach Notification

### 5.1 Breach Detection

The specification supports breach detection through:
- Audit ledger monitoring for unauthorized access patterns
- Chain verification for data tampering
- Token validation failure tracking

### 5.2 Breach Response

If a breach is detected:
1. The audit ledger MUST be preserved as evidence
2. Provenance records MUST be queried to determine the scope of affected data
3. Notification procedures per 45 CFR 164.404-408 MUST be followed by the covered entity

---

## 6. Business Associate Requirements

### 6.1 BAA Coverage

Organizations operating MCP servers on behalf of covered entities MUST execute Business Associate Agreements covering:
- The MCP server infrastructure
- Any data processed through MCP tool calls
- Audit and provenance records

### 6.2 Subcontractor Obligations

Vendors providing MCP server implementations MUST acknowledge that their software may process PHI (in its identified form within the server boundary, before de-identification) and comply with BAA requirements.

---

## 7. References

- [45 CFR Part 164 — Security and Privacy](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164)
- [HHS HIPAA De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)
- [NIST SP 800-188 — De-Identifying Government Datasets](https://csrc.nist.gov/publications/detail/sp/800-188/final)
