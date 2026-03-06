# Security Specification

**National MCP-PAI Oncology Trials Standard — spec/security.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the security requirements for all conforming MCP server implementations. Security is implemented through four complementary mechanisms: deny-by-default RBAC, token lifecycle management, input validation with SSRF prevention, and mandatory audit of all operations.

---

## 2. Authorization Model

### 2.1 Deny-by-Default RBAC

The authorization server MUST implement a deny-by-default role-based access control (RBAC) model derived from the reference `PolicyEngine` implementation.

**Requirements:**

- All access requests MUST be evaluated against the active policy set
- Any request that does not match an explicit ALLOW rule MUST be denied
- Explicit DENY rules MUST take precedence over ALLOW rules when both match
- Policy rules MUST specify: `role`, `server`, `tool`, and `effect` (ALLOW or DENY)
- Wildcard matching (`*`) MAY be used for server and tool fields in policy rules
- The default policy set MUST include the nine baseline rules defined in [actor-model.md](actor-model.md)

### 2.2 Policy Evaluation Algorithm

The policy engine MUST evaluate requests using the following algorithm:

1. Collect all rules matching the request's role, server, and tool
2. If any matching rule has effect DENY, return DENIED
3. If any matching rule has effect ALLOW, return ALLOWED
4. If no rules match, return DENIED (deny-by-default)

### 2.3 Policy Extensibility

Sites MAY add additional policy rules beyond the default set. Additional rules MUST NOT weaken the default restrictions — they MAY only add further restrictions or grant access to vendor extension tools (see [versioning.md](versioning.md)).

---

## 3. Token Lifecycle

### 3.1 Token Issuance

- Tokens MUST be generated using cryptographically secure random values (e.g., UUID v4)
- Tokens MUST be scoped to a single role
- Tokens MUST include an expiration timestamp (UTC, ISO 8601)
- Default token duration SHOULD be 3600 seconds (1 hour)
- Maximum token duration MUST NOT exceed 86400 seconds (24 hours)
- The authorization server MUST store token hashes (SHA-256), not plaintext tokens

### 3.2 Token Validation

- Token validation MUST check: existence, expiry, and revocation status
- Expired tokens MUST return `TOKEN_EXPIRED` error code
- Revoked tokens MUST return `TOKEN_REVOKED` error code
- Token validation MUST be performed by the authorization server; other servers MUST NOT implement independent token validation

### 3.3 Token Revocation

- Tokens MUST be revocable at any time
- Revocation MUST be immediate — subsequent validation attempts MUST fail
- Revocation MUST be recorded in the audit ledger
- Token revocation MUST be idempotent

### 3.4 Token Rotation

- Implementations SHOULD support automatic token rotation for long-running robot procedures
- Rotation MUST issue a new token and revoke the old token atomically
- The audit ledger MUST record both the revocation and issuance

---

## 4. Input Validation

### 4.1 FHIR ID Validation

All FHIR resource IDs MUST be validated against the pattern `^[A-Za-z0-9\-._]+$` before processing. IDs failing validation MUST be rejected with `VALIDATION_FAILED`.

### 4.2 DICOM UID Validation

All DICOM UIDs MUST be validated against the pattern `^[\d.]+$` before processing. UIDs failing validation MUST be rejected with `VALIDATION_FAILED`.

### 4.3 SSRF Prevention

All string input parameters MUST be checked for embedded URLs. Any value containing `http://` or `https://` (case-insensitive matching) MUST be rejected with `VALIDATION_FAILED`. This prevents Server-Side Request Forgery attacks through crafted input parameters.

### 4.4 Input Length Limits

Implementations MUST enforce reasonable input length limits:
- String parameters: maximum 1000 characters unless otherwise specified
- Object parameters: maximum 50 keys
- Array parameters: maximum 100 elements

---

## 5. Transport Security

### 5.1 TLS Requirements

- All MCP server endpoints MUST be served over TLS 1.2 or higher in production deployments
- Self-signed certificates MAY be used in development environments only
- Certificate validation MUST be enforced in production

### 5.2 Network Isolation

- MCP servers SHOULD be deployed on isolated network segments
- Backend clinical systems (EHR, PACS) MUST NOT be directly accessible to robot agents
- All clinical system access MUST be mediated through MCP servers

---

## 6. Cryptographic Requirements

### 6.1 Hashing

- Audit chain hashing MUST use SHA-256
- Token hashing MUST use SHA-256
- Data fingerprinting MUST use SHA-256
- Pseudonymization MUST use HMAC-SHA256 with a site-specific salt

### 6.2 Salt Management

- HMAC salts MUST be unique per site
- Salts MUST be stored securely and separately from hashed data
- Salt rotation procedures MUST be documented

---

## 7. Incident Response

### 7.1 Security Events

Conforming implementations MUST detect and log the following security events:
- Authentication failures (invalid tokens)
- Authorization denials (policy violations)
- Input validation failures (SSRF attempts, malformed IDs)
- Hash chain integrity failures (ledger tampering)

### 7.2 Chain Compromise

If the audit chain fails verification:
1. The ledger server MUST immediately halt accepting new records
2. An alert MUST be generated for all registered auditors
3. The chain MUST NOT be repaired without auditor review
4. A new chain branch MUST be started with a reference to the compromised chain
