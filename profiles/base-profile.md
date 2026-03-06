# Base Profile — Core Conformance

**National MCP-PAI Oncology Trials Standard — profiles/base-profile.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

The Base Profile defines the absolute minimum requirements that every conforming implementation of the National MCP-PAI Oncology Trials Standard MUST satisfy. This profile ensures that all deployments — regardless of conformance level, clinical site type, or robot platform — share a common foundation of authorization, audit integrity, and error handling.

> Every implementation claiming conformance to any level of this standard MUST implement the Base Profile in its entirety.

---

## 2. Mandatory Capabilities

### 2.1 Authorization (trialmcp-authz)

All conforming implementations MUST deploy the `trialmcp-authz` server and implement the following tools:

| Tool | Requirement | Description |
|------|-------------|-------------|
| `authz_evaluate` | MUST | Evaluate access requests against deny-by-default RBAC policy engine |
| `authz_issue_token` | MUST | Issue scoped session tokens with SHA-256 hashed storage |
| `authz_validate_token` | MUST | Validate token validity, role scope, and expiry |
| `authz_list_policies` | MUST | Return active authorization policies with optional role filtering |
| `authz_revoke_token` | MUST | Revoke active tokens with immediate effect |

#### Authorization Requirements

- MUST enforce deny-by-default: all access requests MUST be denied unless an explicit ALLOW rule exists
- MUST give DENY rules precedence over ALLOW rules
- MUST store token hashes (SHA-256), never plaintext tokens
- MUST enforce UTC-based token expiry
- MUST support token revocation with immediate effect across all servers
- SHOULD support configurable token duration (default: 3600 seconds)
- MAY support custom policy rules via vendor extensions

### 2.2 Audit Ledger (trialmcp-ledger)

All conforming implementations MUST deploy the `trialmcp-ledger` server and implement the following tools:

| Tool | Requirement | Description |
|------|-------------|-------------|
| `ledger_append` | MUST | Append hash-chained audit record |
| `ledger_verify` | MUST | Verify chain integrity over a record range |
| `ledger_query` | MUST | Query audit records by server, tool, caller, or time range |
| `ledger_replay` | MUST | Generate sequential replay trace for compliance review |
| `ledger_chain_status` | MUST | Report chain health, record count, and latest hash |

#### Audit Requirements

- MUST use SHA-256 for hash chain computation
- MUST use genesis hash `"0" * 64` (64 zero characters) for the first record
- MUST use canonical JSON serialization (alphabetical key ordering) before hashing
- MUST record every tool invocation from every server as an audit entry
- MUST include: timestamp (ISO 8601 UTC), server, tool, caller, parameters (de-identified), result summary, hash, previous hash
- MUST support chain verification for tamper detection
- MUST produce replay traces sufficient for ICH-GCP E6(R2) audit review
- SHOULD support incremental chain verification for performance
- SHOULD support time-range and caller-based replay filtering

### 2.3 Error Taxonomy

All conforming implementations MUST use the standardized 9-code error taxonomy across all servers:

| Error Code | Description | HTTP Equivalent |
|------------|-------------|-----------------|
| `AUTHZ_DENIED` | Authorization policy denied the request | 403 |
| `VALIDATION_FAILED` | Input failed schema or format validation | 400 |
| `NOT_FOUND` | Requested resource does not exist | 404 |
| `INTERNAL_ERROR` | Unexpected server-side failure | 500 |
| `TOKEN_EXPIRED` | Session token has passed its expiry time | 401 |
| `TOKEN_REVOKED` | Session token was explicitly revoked | 401 |
| `PERMISSION_DENIED` | Actor lacks the required role for this operation | 403 |
| `INVALID_INPUT` | Input parameters are malformed or missing | 400 |
| `RATE_LIMITED` | Request rate exceeds configured threshold | 429 |

Error responses MUST conform to the `error-response.schema.json` schema.

---

## 3. Input Validation Requirements

All tools across all servers MUST validate inputs before processing:

| Validation | Pattern/Rule | Applies To |
|-----------|-------------|------------|
| FHIR ID format | `^[A-Za-z0-9\-._]+$` | All FHIR resource identifiers |
| DICOM UID format | `^[\d.]+$` | All DICOM Study/Series/Instance UIDs |
| SSRF prevention | Reject inputs containing `http://` or `https://` (case-insensitive) | All string inputs |
| Token format | Non-empty string, stored as SHA-256 hash | All token parameters |

---

## 4. Optional Capabilities

| Capability | Requirement | Description |
|-----------|-------------|-------------|
| Rate limiting | MAY | Configurable per-actor request rate limits |
| Custom policy rules | MAY | Vendor-specific RBAC extensions via `x-{vendor}` namespace |
| Configurable token duration | SHOULD | Override default 3600-second token validity |
| Incremental chain verification | SHOULD | Verify chain subsets without full replay |

---

## 5. Forbidden Operations

The following operations are forbidden at the Base Profile level:

| Operation | Reason |
|-----------|--------|
| Plaintext token storage | Security: tokens MUST be stored as SHA-256 hashes only |
| Unsigned audit records | Integrity: every audit record MUST be hash-chained |
| ALLOW-by-default authorization | Security: all implementations MUST deny by default |
| Skipping audit for tool calls | Compliance: every tool invocation MUST produce an audit record |
| Returning unhashed patient identifiers | Privacy: all patient identifiers MUST be pseudonymized or removed |

---

## 6. Required Schemas

Implementations at the Base Profile level MUST validate against the following schemas:

| Schema | File | Purpose |
|--------|------|---------|
| Authorization Decision | `schemas/authz-decision.schema.json` | RBAC evaluation input/output |
| Audit Record | `schemas/audit-record.schema.json` | Hash-chained ledger entries |
| Error Response | `schemas/error-response.schema.json` | Standardized error format |
| Health Status | `schemas/health-status.schema.json` | Server health reporting |
| Capability Descriptor | `schemas/capability-descriptor.schema.json` | Server capability advertisement |

---

## 7. Regulatory Overlays

The Base Profile inherently satisfies portions of the following regulatory requirements:

| Regulation | Relevant Section | Coverage |
|-----------|-----------------|----------|
| 21 CFR Part 11 | §11.10(e) Audit trails | Hash-chained immutable audit ledger |
| 21 CFR Part 11 | §11.10(g) Authority checks | Deny-by-default RBAC |
| HIPAA Security Rule | §164.312(b) Audit controls | Comprehensive tool-call auditing |
| HIPAA Security Rule | §164.312(d) Authentication | Token-based session management |
| FDA AI/ML Guidance | Risk management | Policy-enforced access control |

See [regulatory/CFR_PART_11.md](../regulatory/CFR_PART_11.md), [regulatory/HIPAA.md](../regulatory/HIPAA.md), and [regulatory/US_FDA.md](../regulatory/US_FDA.md) for full mappings.

---

## 8. Conformance Test Subset

Implementations claiming Base Profile conformance MUST pass the following test categories:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| AuthZ RBAC enforcement | 5 | Deny-by-default, DENY precedence, role scoping |
| Token lifecycle | 4 | Issue, validate, expire, revoke |
| Ledger chain integrity | 4 | Genesis hash, append, verify, replay |
| Error taxonomy | 3 | Correct error codes, schema-valid responses |
| Input validation | 3 | FHIR ID format, DICOM UID format, SSRF rejection |
| **Total** | **19** | |

---

*This profile is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [spec/conformance.md](../spec/conformance.md) for the full conformance level definitions.*
