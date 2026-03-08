# 06 — Audit and Provenance Chain

**National MCP-PAI Oncology Trials Standard v0.9.0**

Hash-chained audit ledger construction and DAG-based provenance tracking
across all five MCP servers and cross-site boundaries.

## Hash-Chained Audit Ledger Construction

```
+-----------------------------------------------------------------------------+
|                  HASH-CHAINED AUDIT LEDGER CONSTRUCTION                     |
+-----------------------------------------------------------------------------+
|                                                                              |
|  GENESIS BLOCK          RECORD 1              RECORD 2              REC N   |
|  +------------------+   +------------------+  +------------------+  +-----+ |
|  |                  |   |                  |  |                  |  |     | |
|  | audit_id:        |   | audit_id:        |  | audit_id:        |  |     | |
|  |   genesis-001    |   |   rec-001        |  |   rec-002        |  | ... | |
|  |                  |   |                  |  |                  |  |     | |
|  | previous_hash:   |   | previous_hash:   |  | previous_hash:   |  |     | |
|  |   000000...0000  +-->+   a4f2c8...1b3e  +->+   7d9e1a...4c2f  +->+     | |
|  |   (64 zeros)     |   |                  |  |                  |  |     | |
|  |                  |   | server:          |  | server:          |  |     | |
|  | server:          |   |   trialmcp-authz |  |   trialmcp-fhir  |  |     | |
|  |   trialmcp-      |   |                  |  |                  |  |     | |
|  |   ledger         |   | tool:            |  | tool:            |  |     | |
|  |                  |   |   authz_evaluate |  |   fhir_read      |  |     | |
|  | tool:            |   |                  |  |                  |  |     | |
|  |   ledger_append  |   | caller:          |  | caller:          |  |     | |
|  |                  |   |   robot_agent_01 |  |   robot_agent_01 |  |     | |
|  | hash:            |   |                  |  |                  |  |     | |
|  |   a4f2c8...1b3e  |   | hash:            |  | hash:            |  |     | |
|  |                  |   |   7d9e1a...4c2f  |  |   b2c3d4...5e6f  |  |     | |
|  +------------------+   +------------------+  +------------------+  +-----+ |
|                                                                              |
|  HASH COMPUTATION:                                                           |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  1. Serialize record to canonical JSON (alphabetical keys)        |      |
|  |  2. Exclude the "hash" field itself from serialization            |      |
|  |  3. Encode as UTF-8 bytes                                        |      |
|  |  4. Compute SHA-256 digest                                       |      |
|  |  5. Store as lowercase hexadecimal (64 characters)               |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
|  VERIFICATION ALGORITHM:                                                     |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  for each record in chain:                                        |      |
|  |    1. Recompute hash from record fields (excluding hash)          |      |
|  |    2. Verify computed hash == stored hash                         |      |
|  |    3. Verify record.previous_hash == prior_record.hash            |      |
|  |    4. Verify genesis record has previous_hash = 64 zeros          |      |
|  |    5. Any mismatch -> TAMPER DETECTED at specific record          |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```

## DAG-Based Provenance Graph

```
+-----------------------------------------------------------------------------+
|                    DAG-BASED PROVENANCE GRAPH                                |
+-----------------------------------------------------------------------------+
|                                                                              |
|  A complete robot-assisted procedure generates the following lineage:       |
|                                                                              |
|  +-------------+                                                             |
|  | Token       |                                                             |
|  | Issuance    |                                                             |
|  | (authz)     |                                                             |
|  +------+------+                                                             |
|         |                                                                    |
|         v                                                                    |
|  +------+------+     +-------------+                                         |
|  | AuthZ       |     | Patient     |                                         |
|  | Evaluation  |     | Consent     |                                         |
|  | (authz)     |     | Check       |                                         |
|  +------+------+     | (fhir)      |                                         |
|         |             +------+------+                                         |
|         |                    |                                                |
|         +--------+-----------+                                                |
|                  |                                                            |
|                  v                                                            |
|  +-------------+ +------+------+                                              |
|  | DICOM Query | | Safety Gate |                                              |
|  | (dicom)     | | Evaluation  |                                              |
|  +------+------+ +------+------+                                              |
|         |                |                                                    |
|         +--------+-------+                                                    |
|                  |                                                            |
|                  v                                                            |
|           +------+------+                                                     |
|           | Human       |                                                     |
|           | Approval    |                                                     |
|           +------+------+                                                     |
|                  |                                                            |
|                  v                                                            |
|           +------+------+                                                     |
|           | Procedure   |                                                     |
|           | Execution   |                                                     |
|           | (robot)     |                                                     |
|           +------+------+                                                     |
|                  |                                                            |
|         +--------+-------+                                                    |
|         |                |                                                    |
|         v                v                                                    |
|  +------+------+  +-----+-------+                                             |
|  | Post-Proc   |  | Observation |                                             |
|  | Imaging     |  | Capture     |                                             |
|  | (dicom)     |  | (fhir)      |                                             |
|  +------+------+  +------+------+                                             |
|         |                |                                                    |
|         +--------+-------+                                                    |
|                  |                                                            |
|                  v                                                            |
|           +------+------+                                                     |
|           | Completion  |                                                     |
|           | Audit       |                                                     |
|           | (ledger)    |                                                     |
|           +-------------+                                                     |
|                                                                              |
|  PROVENANCE RECORD STRUCTURE:                                                |
|  +-------------------------------------------------------------------+      |
|  | record_id    : Unique provenance node ID                          |      |
|  | source_type  : clinical_data | imaging | audit | authorization    |      |
|  | action       : create | transform | derive | aggregate | transfer |      |
|  | input_refs[] : Parent node IDs (DAG edges)                        |      |
|  | output_ref   : This node's output reference                       |      |
|  | agent        : Actor who performed the action                     |      |
|  | server       : MCP server that recorded it                        |      |
|  | fingerprint  : SHA-256 of canonical record                        |      |
|  | recorded_at  : ISO-8601 UTC timestamp                             |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Cross-Site Provenance Merge

```
+-----------------------------------------------------------------------------+
|                   CROSS-SITE PROVENANCE MERGE                               |
+-----------------------------------------------------------------------------+
|                                                                              |
|  SITE A PROVENANCE DAG                   SITE B PROVENANCE DAG              |
|  +---------------------+                +---------------------+             |
|  |                     |                |                     |             |
|  |  A1: Patient Enroll |                |  B1: Patient Enroll |             |
|  |       |             |                |       |             |             |
|  |       v             |                |       v             |             |
|  |  A2: Baseline Scan  |                |  B2: Treatment Scan |             |
|  |       |             |                |       |             |             |
|  |       v             |                |       v             |             |
|  |  A3: Treatment      |                |  B3: Follow-Up      |             |
|  |       |             |                |       |             |             |
|  +-------+-------------+                +-------+-------------+             |
|          |                                      |                           |
|          +------------------+-------------------+                           |
|                             |                                               |
|                             v                                               |
|                   +---------+---------+                                     |
|                   | MERGED DAG        |                                     |
|                   | (Federation Layer)|                                     |
|                   |                   |                                     |
|                   | M1: Merge Node    |                                     |
|                   |   inputs: [A3,B3] |                                     |
|                   |   action: merge   |                                     |
|                   |   fingerprint:    |                                     |
|                   |     SHA-256 of    |                                     |
|                   |     combined DAG  |                                     |
|                   +-------------------+                                     |
|                                                                              |
|  MERGE VERIFICATION:                                                         |
|  +-------------------------------------------------------------------+      |
|  | 1. Verify Site A DAG integrity (all fingerprints valid)            |      |
|  | 2. Verify Site B DAG integrity (all fingerprints valid)            |      |
|  | 3. Verify no cycles in merged graph                               |      |
|  | 4. Verify merge node references valid parent nodes                |      |
|  | 5. Verify cross-site patient pseudonyms are consistent            |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```
