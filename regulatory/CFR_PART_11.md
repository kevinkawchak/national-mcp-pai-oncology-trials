# 21 CFR Part 11 Compliance Overlay

**National MCP-PAI Oncology Trials Standard — 21 CFR Part 11 Mapping**
**Version**: 0.1.0

---

## 1. Overview

This document provides a detailed mapping between the national MCP-PAI oncology trials standard and 21 CFR Part 11 (Electronic Records; Electronic Signatures). The hash-chained audit ledger, token-based authentication, and provenance tracking system provide the foundation for Part 11 compliance.

---

## 2. Subpart B — Electronic Records

### § 11.10 Controls for Closed Systems

| Requirement | Paragraph | Specification Coverage |
|------------|-----------|----------------------|
| System validation | (a) | Five conformance levels with MUST/SHOULD/MAY requirements; conformance testing validates system behavior |
| Readable copies of records | (b) | `ledger_replay` generates human-readable audit traces; `ledger_query` provides filtered record access |
| Record protection | (c) | Append-only hash-chained ledger; SHA-256 integrity verification; genesis hash anchoring |
| Access limitation | (d) | Deny-by-default RBAC; six defined actor roles; token-based sessions with expiry |
| Computer-generated audit trails | (e) | Every tool call produces a hash-chained audit record with timestamp, server, tool, caller, parameters, and result |
| Operational system checks | (f) | Input validation (FHIR ID format, DICOM UID format, SSRF prevention); error code taxonomy |
| Authority checks | (g) | PolicyEngine evaluates every request; DENY precedence over ALLOW |
| Device checks | (h) | Token validation verifies existence, expiry, and revocation status |
| Personnel training | (i) | Outside specification scope — site responsibility |
| Written policies | (j) | Governance charter, decision process, and extension policies |
| System documentation | (k) | Specification documents, tool contracts, and conformance checklists |

### § 11.10(e) Audit Trail Detail

The audit ledger satisfies Part 11 audit trail requirements by recording:

| Audit Trail Element | Ledger Field |
|--------------------|-------------|
| Who performed the action | `caller` (actor identifier) |
| What action was performed | `tool` (tool name) + `parameters` |
| When the action occurred | `timestamp` (ISO 8601 UTC) |
| What system was used | `server` (MCP server identifier) |
| What was the outcome | `result_summary` |
| Record integrity | `hash` (SHA-256) + `previous_hash` (chain link) |

### § 11.30 Controls for Open Systems

Open system requirements apply when MCP servers communicate over public networks. Additional requirements:
- TLS 1.2+ for all production deployments (transport encryption)
- Token-based authentication (document authenticity)
- Hash chain verification (record integrity)

---

## 3. Subpart C — Electronic Signatures

### § 11.50 Signature Manifestation

Electronic signatures in the MCP context are manifested through audit records that include:
- The printed name of the signer (actor identifier)
- The date and time of signing (timestamp)
- The meaning of the signature (tool invocation = approval of action)

### § 11.70 Signature/Record Linking

Signatures (audit records) are linked to their associated records through:
- SHA-256 hash of the record content
- Hash chain linking to preceding records
- Provenance records linking data access to audit entries

Falsifying this linking would require:
1. Recomputing all subsequent hash chain entries
2. Modifying all downstream provenance fingerprints
3. Both operations are detectable through chain verification

### § 11.100 General Requirements

| Requirement | Implementation |
|------------|---------------|
| Unique to one individual | Actor identifiers are unique per individual or robot |
| Not reused | Token UUIDs are generated uniquely; actor IDs are permanent |
| Verified identity | Token issuance requires role verification |
| Certification | Outside specification scope — organizational responsibility |

### § 11.200 Electronic Signature Components

| Component | Implementation |
|-----------|---------------|
| Identification | Actor identifier (subject field in token) |
| Authentication | Token validation (SHA-256 hashed, time-limited) |
| Continuous sessions | Token remains valid for configured duration |
| Re-authentication | New token required after expiry or revocation |

---

## 4. Hash Chain as Part 11 Control

### 4.1 Tamper Evidence

The hash-chained ledger provides tamper evidence because:
- Modifying any record changes its hash
- A changed hash breaks the chain link to the next record
- Chain verification (`ledger_verify`) detects any modification
- The genesis hash provides the chain anchor

### 4.2 Chain Verification Process

```
For each record i in [0, N]:
  1. If i == 0: verify previous_hash == "0" * 64 (genesis)
  2. Recompute hash from canonical serialization
  3. Verify recomputed hash matches stored hash
  4. If i > 0: verify previous_hash == record[i-1].hash
  5. If any check fails: report first_invalid_index = i
```

### 4.3 Regulatory Inspection Support

The `ledger_replay` tool enables FDA inspectors to:
- Reconstruct the complete sequence of operations for any time period
- Verify chain integrity for the inspection scope
- Filter by specific actors, servers, or tools
- Generate reports suitable for inspection documentation

---

## 5. Gap Analysis

### 5.1 Areas Requiring Site-Level Implementation

The following Part 11 requirements are outside the protocol specification scope and MUST be addressed by each site:

| Requirement | Section | Site Responsibility |
|------------|---------|-------------------|
| Personnel training | § 11.10(i) | Training programs for all actors |
| Written policies holding individuals accountable | § 11.10(j) | Site-specific SOPs |
| Biometric signature components | § 11.200(b) | If biometric auth is used |
| Certification of electronic signatures | § 11.100(c) | Organizational certification |

### 5.2 Recommendations

Sites SHOULD:
1. Develop SOPs covering MCP server operation and maintenance
2. Train all actors on their roles and responsibilities
3. Conduct periodic chain verification (at least daily)
4. Maintain documentation linking their deployment to this Part 11 mapping

---

## 6. References

- [21 CFR Part 11 — Electronic Records; Electronic Signatures](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11)
- FDA. (2003). *Guidance for Industry: Part 11, Electronic Records; Electronic Signatures — Scope and Application.* U.S. Food and Drug Administration.
- [ICH E6(R2) Good Clinical Practice](https://database.ich.org/sites/default/files/E6_R2_Addendum.pdf)
