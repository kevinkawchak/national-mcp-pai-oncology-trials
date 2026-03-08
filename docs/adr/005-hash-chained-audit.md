# ADR-005: Hash-Chained Audit Ledger for 21 CFR Part 11 Compliance

**Status**: Accepted
**Date**: 2026-02-05
**Decision Makers**: Compliance Working Group
**Tracking**: DL-005 in `docs/governance/decision-log.md`

---

## Context

21 CFR Part 11 establishes the United States Food and Drug Administration's criteria
for electronic records and electronic signatures in FDA-regulated clinical trials.
Section 11.10(e) specifically requires:

> "Use of secure, computer-generated, time-stamped audit trails to independently
> record the date and time of operator entries and actions that create, modify, or
> delete electronic records."

The audit trail must be:
- **Tamper-evident**: Any modification to historical records must be detectable
- **Append-only**: Records must not be deleted or modified after creation
- **Complete**: Every tool invocation must produce an audit record
- **Replayable**: The full sequence of operations must be reconstructable for
  regulatory review
- **Independently verifiable**: A third party (FDA inspector, IRB auditor) must be
  able to verify trail integrity without trusting the system that produced it

Additionally, ICH-GCP E6(R2) Section 5.5 requires sponsors to ensure "the integrity
of data" and Section 8.1 requires "essential documents which individually and
collectively permit evaluation of the conduct of a trial."

The standard must define an audit mechanism that satisfies these requirements across
all five MCP servers and all 23 tool contracts.

---

## Decision

Implement an append-only, hash-chained audit ledger using SHA-256 with the following
properties:

1. **Hash algorithm**: SHA-256 (NIST FIPS 180-4)
2. **Chain structure**: Each record contains the SHA-256 hash of the previous record
3. **Genesis hash**: The first record uses `"0" * 64` (64 zero characters) as its
   previous hash
4. **Record format**: 9 fields (audit_id, timestamp, server, tool, caller, parameters,
   result_summary, hash, previous_hash)
5. **Hash computation**: Canonical JSON serialization with alphabetical key ordering,
   SHA-256 over UTF-8 encoded bytes
6. **Verification**: Incremental and full-chain verification via `ledger_verify`
7. **Replay**: Sequential trace generation via `ledger_replay`

---

## Rationale

### SHA-256 Selection

SHA-256 was selected because:

- **NIST approved**: Listed in FIPS 180-4, accepted by FDA for electronic records
- **Collision resistant**: No known practical collision attacks (2^128 security level)
- **Widely implemented**: Available in every major programming language and
  cryptographic library
- **Performance**: Sufficient throughput for audit record generation at clinical
  trial scale (thousands of records per day, not millions per second)
- **Deterministic**: Same input always produces same output, enabling independent
  verification

SHA-3 (Keccak) was considered but offers no practical advantage over SHA-256 for
this use case and has less widespread implementation support in healthcare systems.

### Hash Chaining Over Blockchain

A hash-chained ledger was chosen over a distributed blockchain because:

1. **No consensus requirement**: Clinical audit trails are produced by a single
   authoritative system at each site. There is no multi-party consensus problem.
2. **Lower complexity**: Hash chaining is implementable in approximately 100 lines
   of code. Blockchain consensus algorithms add thousands of lines and introduce
   failure modes (network partitions, fork resolution) that are inappropriate for
   safety-critical clinical systems.
3. **Regulatory clarity**: FDA inspectors understand hash chains. Blockchain-based
   audit trails would require educating regulatory reviewers on consensus mechanisms,
   finality, and fork resolution — concepts outside their domain expertise.
4. **Performance**: Hash chaining has O(1) append and O(n) verification. Blockchain
   consensus introduces latency for block finalization that could delay audit record
   creation.
5. **Deterministic verification**: A hash chain can be verified by any party with
   access to the record sequence. No node participation or network access is required.

### Canonical JSON Serialization

Hash computation uses canonical JSON (alphabetical key ordering) to ensure
deterministic hashing. Without canonical serialization, semantically identical
records could produce different hashes due to key ordering differences across
JSON implementations.

Requirements:
- Fields serialized in alphabetical order by key name
- No whitespace outside of string values
- Unicode characters escaped per RFC 8259
- Numbers represented without unnecessary leading zeros or trailing decimal zeros

### Genesis Hash Convention

The genesis hash `"0" * 64` (64 zero characters) serves as the chain anchor point.
This convention:
- Is deterministic and universally known
- Cannot collide with any valid SHA-256 output (all-zeros is not a valid SHA-256
  digest of any input)
- Enables verification of chain completeness from the first record
- Is simple to implement and document

### 9-Field Record Structure

Each audit record contains exactly 9 fields:

| Field | Purpose | 21 CFR Part 11 Mapping |
|-------|---------|----------------------|
| `audit_id` | Unique record identifier (UUID v4) | Record identification |
| `timestamp` | ISO 8601 UTC timestamp | Section 11.10(e): time-stamped |
| `server` | Originating MCP server | System identification |
| `tool` | Invoked tool name | Section 11.10(e): action identification |
| `caller` | Actor identifier (pseudonymized) | Section 11.10(e): operator identification |
| `parameters` | Tool call parameters (de-identified) | Section 11.10(e): entries that create records |
| `result_summary` | Outcome description | Action result |
| `hash` | SHA-256 hash of this record | Tamper evidence |
| `previous_hash` | SHA-256 hash of preceding record | Chain continuity |

This structure satisfies 21 CFR Part 11 Section 11.10(e) requirements for:
- Time-stamped entries (timestamp field)
- Operator identification (caller field)
- Action recording (server, tool, parameters fields)
- Independent verification (hash, previous_hash fields)

---

## Consequences

### Positive

- **Regulatory acceptance**: SHA-256 hash chains are well-understood by FDA inspectors
  and compliance auditors
- **Implementation simplicity**: Hash chaining requires minimal code and no external
  dependencies beyond a SHA-256 implementation
- **Independent verification**: Any party with the audit records can verify chain
  integrity without access to the production system
- **Tamper evidence**: Any modification to a historical record breaks the hash chain
  at the modified record and all subsequent records
- **Replay capability**: The sequential chain supports full operational replay for
  ICH-GCP E6(R2) compliance

### Negative

- **No per-record digital signatures**: Hash chaining provides tamper evidence for
  the chain as a whole but does not cryptographically attribute individual records
  to specific actors. Digital signatures for individual records are planned for v0.2.0
  (see `docs/governance/known-gaps.md`, Gap 1.3)
- **Linear scalability limitation**: Full chain verification is O(n) in chain length.
  For very long chains, incremental verification (verifying only recent records) is
  supported but full verification becomes slow
- **No chain recovery**: If chain integrity is violated, there is no normative
  recovery procedure in v0.1.0 (see `docs/governance/known-gaps.md`, Gap 1.6)
- **Single point of truth**: The ledger server is a single-site authority. Cross-site
  audit chain merging is not supported in v0.1.0

### Mitigations

- Per-record digital signatures will be added as an optional extension in v0.2.0
- Incremental verification (`ledger_verify` with `start_index` and `end_index`)
  enables efficient recent-record verification
- Chain backup procedures are recommended in deployment guides
- Cross-site audit coordination is handled through the provenance server's DAG model

---

## Alternatives Rejected

### Distributed Blockchain (Hyperledger Fabric, Ethereum Private)

Rejected because distributed consensus introduces unnecessary complexity, latency,
and failure modes. Clinical audit trails are single-authority records, not
multi-party transactions. Blockchain would also require FDA auditor education
on consensus mechanisms.

### Merkle Tree Audit Log

Rejected for the primary audit structure because Merkle trees optimize for
membership proof (proving a specific record exists in the tree) rather than
sequential integrity (proving no records were modified or removed). Hash chaining
provides stronger sequential tamper evidence. Merkle trees may be added in a future
version as a complementary structure for efficient membership proofs.

### Database-Level Audit Triggers

Rejected because database triggers are implementation-specific (PostgreSQL, MySQL,
Oracle) and do not provide protocol-level tamper evidence. A conformance test
cannot verify that a database trigger is correctly configured across all
vendor implementations. The hash chain is protocol-level and verifiable through
the standard MCP tool interface.

### Signed Timestamps (RFC 3161)

RFC 3161 trusted timestamps were considered as an addition to hash chaining but
rejected for v0.1.0 because they require an external Time Stamping Authority (TSA),
which adds a network dependency to audit record creation. TSA integration is being
evaluated for v0.2.0 as an optional enhancement.

---

## References

- 21 CFR Part 11 (Electronic Records; Electronic Signatures)
- NIST FIPS 180-4 (Secure Hash Standard)
- ICH-GCP E6(R2) Section 5.5 (Data Integrity)
- `spec/audit.md` (Full audit specification)
- `regulatory/CFR_PART_11.md` (Regulatory overlay)
- `spec/tool-contracts.md` Section 6 (Ledger tools)
