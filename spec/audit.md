# Audit Specification

**National MCP-PAI Oncology Trials Standard — spec/audit.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the audit ledger requirements for all conforming MCP server deployments. The audit system implements an append-only, hash-chained ledger derived from the reference `AuditLedger` implementation, satisfying 21 CFR Part 11 requirements for electronic records in clinical trials.

---

## 2. Audit Record Structure

### 2.1 Record Fields

Each audit record MUST contain the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | string | Unique identifier (UUID v4) |
| `timestamp` | string | ISO 8601 UTC timestamp of the event |
| `server` | string | MCP server that generated the event |
| `tool` | string | Tool that was invoked |
| `caller` | string | Actor identifier (pseudonymized for patient-related calls) |
| `parameters` | object | Tool call parameters (de-identified) |
| `result_summary` | string | Outcome description |
| `hash` | string | SHA-256 hash of this record |
| `previous_hash` | string | SHA-256 hash of the preceding record |

### 2.2 Hash Computation

The record hash MUST be computed by:
1. Creating a canonical JSON serialization of the record (excluding the `hash` field itself)
2. Fields MUST be serialized in alphabetical key order for deterministic hashing
3. Computing SHA-256 over the canonical UTF-8 encoded bytes
4. Storing the hexadecimal digest (64 characters)

---

## 3. Hash Chain

### 3.1 Genesis Record

The first record in every audit chain MUST use a genesis hash of `"0" * 64` (64 zero characters) as its `previous_hash` value. This establishes the chain anchor point.

### 3.2 Chain Continuity

Each subsequent record MUST set its `previous_hash` to the `hash` value of the immediately preceding record. This creates an immutable, tamper-evident chain.

### 3.3 Chain Diagram

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Record 0 │    │ Record 1 │    │ Record 2 │    │ Record N │
│          │    │          │    │          │    │          │
│ prev: 0* │───▶│ prev: H0 │───▶│ prev: H1 │───▶│prev: HN-1│
│ hash: H0 │    │ hash: H1 │    │ hash: H2 │    │ hash: HN │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
  Genesis
```

---

## 4. Chain Verification

### 4.1 Verification Algorithm

The `ledger_verify` tool MUST implement the following verification:

1. **Genesis check**: Verify the first record's `previous_hash` equals `"0" * 64`
2. **Hash recomputation**: For each record, recompute the hash from the canonical serialization and verify it matches the stored `hash` value
3. **Chain continuity**: For each record after the genesis, verify its `previous_hash` equals the preceding record's `hash`
4. **Report**: Return the total records checked, whether the chain is valid, and the index of the first invalid record (if any)

### 4.2 Failure Modes

| Failure | Meaning | Severity |
|---------|---------|----------|
| Genesis hash mismatch | First record was tampered with | Critical |
| Hash recomputation mismatch | A record's content was modified | Critical |
| Chain continuity break | A record was inserted, deleted, or reordered | Critical |
| Missing records (gaps in timestamps) | Records may have been deleted | Warning |

---

## 5. Replay Trace

### 5.1 Purpose

The replay trace function generates a sequential, human-readable reconstruction of all operations within a time window. This supports ICH-GCP E6(R2) audit review requirements and FDA inspection readiness.

### 5.2 Trace Format

Replay traces MUST include:
- Chronologically ordered list of all audit records in the specified window
- Total record count
- Time span of the trace
- Optional filtering by caller, server, or tool

### 5.3 Compliance Use

Auditors and regulators MUST be able to reconstruct the complete history of any data access, robot procedure, or clinical decision through the replay trace. The trace MUST be sufficient to answer:
- Who accessed what data, when, and why?
- What clinical procedures were performed by robot agents?
- Was all access authorized?
- Was the hash chain intact throughout the period?

---

## 6. 21 CFR Part 11 Mapping

### 6.1 Electronic Records (Subpart B)

| 21 CFR Part 11 Requirement | Specification Coverage |
|----------------------------|----------------------|
| § 11.10(a) Validation | Conformance levels with MUST/SHOULD/MAY requirements |
| § 11.10(b) Readable copies | Replay trace produces human-readable audit trails |
| § 11.10(c) Record protection | Hash-chained immutable ledger prevents modification |
| § 11.10(d) Access limitation | Deny-by-default RBAC with role-scoped tokens |
| § 11.10(e) Audit trails | Every tool call produces a hash-chained audit record |
| § 11.10(g) Authority checks | Policy engine verifies authorization before execution |
| § 11.10(h) Device checks | Token validation ensures authenticated sessions |
| § 11.10(k) Change control | SemVer versioning with compatibility policy |

### 6.2 Electronic Signatures (Subpart C)

| Requirement | Coverage |
|------------|----------|
| § 11.50 Signature manifestation | Audit records include signer ID, timestamp, and purpose |
| § 11.70 Signature linking | SHA-256 hash chain links signatures to their records |
| § 11.100 General requirements | Unique actor IDs, non-reusable tokens |
| § 11.200 Components | Token-based authentication with role scoping |

See [regulatory/CFR_PART_11.md](../regulatory/CFR_PART_11.md) for the complete regulatory overlay.

---

## 7. National-Scale Audit

### 7.1 Per-Site Ledgers

Each site MUST maintain its own independent audit ledger. Audit records MUST NOT be centralized.

### 7.2 Cross-Site Verification

For multi-site trials, the federated coordination layer SHOULD support:
- Collecting chain status from all participating sites
- Identifying sites with chain integrity issues
- Generating aggregate audit reports without transferring individual records

### 7.3 Audit Retention

Audit records MUST be retained for the longer of:
- The duration specified by the trial protocol
- The retention period required by 21 CFR Part 11 (minimum duration of the clinical trial plus regulatory retention requirements)
- Any applicable state or institutional requirements

### 7.4 Ledger Capacity

Implementations MUST be designed to handle the audit volume of a national deployment:
- Thousands of tool calls per site per day
- Chain verification SHOULD complete within acceptable time bounds for the chain length
- Implementations SHOULD support incremental verification (verifying a range rather than the entire chain)
