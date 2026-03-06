# National Architecture

> **Version 0.5.0** | **Normative** | **National MCP-PAI Oncology Trials Standard**

This document defines the five-server topology, data flow, and audit
chain architecture for the National MCP-PAI Oncology Trials Standard.
All U.S. clinical sites, sponsors, CROs, and technology vendors operating
Physical AI systems within FDA-regulated oncology trials MUST deploy MCP
servers conforming to this architecture.

---

## Five-Server Topology

Every conforming site deploys five MCP servers.  Each server encapsulates
a distinct responsibility; together they provide the complete protocol
surface required for Physical AI integration with clinical trial systems.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SITE MCP SERVER DEPLOYMENT                       │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ trialmcp-    │  │ trialmcp-    │  │ trialmcp-    │              │
│  │ authz        │  │ fhir         │  │ dicom        │              │
│  │              │  │              │  │              │              │
│  │ 5 tools      │  │ 4 tools      │  │ 4 tools      │              │
│  │ Deny-by-     │  │ FHIR R4      │  │ DICOM        │              │
│  │ default RBAC │  │ + HIPAA      │  │ query/       │              │
│  │ Token mgmt   │  │ de-ID        │  │ retrieve     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            │                                         │
│                   ┌────────▼────────┐                                │
│                   │   AUDIT BUS     │                                │
│                   └────────┬────────┘                                │
│                            │                                         │
│         ┌──────────────────┼──────────────┐                         │
│         │                                  │                         │
│  ┌──────▼───────┐              ┌───────────▼──┐                     │
│  │ trialmcp-    │              │ trialmcp-     │                     │
│  │ ledger       │              │ provenance    │                     │
│  │              │              │               │                     │
│  │ 5 tools      │              │ 5 tools       │                     │
│  │ Hash-chained │              │ DAG lineage   │                     │
│  │ 21 CFR 11    │              │ SHA-256       │                     │
│  └──────────────┘              └───────────────┘                     │
│                                                                      │
│  Total: 23 tools across 5 servers                                   │
│  Conformance Level 5 = all 5 servers required                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Server Responsibilities

| Server | Tools | Conformance Level | Primary Function |
|--------|-------|-------------------|------------------|
| **trialmcp-authz** | `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_list_policies`, `authz_revoke_token` | Level 1 (Core) | Deny-by-default RBAC, token lifecycle |
| **trialmcp-fhir** | `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status` | Level 2 (Clinical Read) | FHIR R4 clinical data with HIPAA de-identification |
| **trialmcp-dicom** | `dicom_query`, `dicom_retrieve_pointer`, `dicom_study_metadata`, `dicom_recist_measurements` | Level 3 (Imaging) | DICOM imaging with role-based permissions |
| **trialmcp-ledger** | `ledger_append`, `ledger_verify`, `ledger_query`, `ledger_replay`, `ledger_chain_status` | Level 1 (Core) | Hash-chained 21 CFR Part 11 audit trail |
| **trialmcp-provenance** | `provenance_register_source`, `provenance_record_access`, `provenance_get_lineage`, `provenance_get_actor_history`, `provenance_verify_integrity` | Level 4 (Federated) | DAG-based data lineage and SHA-256 fingerprinting |

---

## Data Flow

The following diagram shows the complete data flow for a Physical AI
robot agent executing a clinical procedure within the national standard.

```
ROBOT AGENT            MCP SERVERS                    CLINICAL SYSTEMS
───────────            ───────────                    ────────────────

  ┌────────┐
  │ START  │
  └───┬────┘
      │
      │  1. Request Token
      ▼
  ┌────────┐    ┌──────────────┐
  │ AuthZ  │───▶│ trialmcp-    │  Issue scoped token
  │ Phase  │◀───│ authz        │  (role + expiry + SHA-256)
  └───┬────┘    └──────────────┘
      │
      │  2. Query Patient Data
      ▼
  ┌────────┐    ┌──────────────┐    ┌──────────────┐
  │ FHIR   │───▶│ trialmcp-    │───▶│ EHR System   │
  │ Phase  │◀───│ fhir         │◀───│ (FHIR R4)    │
  └───┬────┘    └──────────────┘    └──────────────┘
      │           De-identified
      │           response
      │
      │  3. Retrieve Imaging
      ▼
  ┌────────┐    ┌──────────────┐    ┌──────────────┐
  │ DICOM  │───▶│ trialmcp-    │───▶│ PACS System  │
  │ Phase  │◀───│ dicom        │◀───│ (DICOM)      │
  └───┬────┘    └──────────────┘    └──────────────┘
      │           Image pointer
      │           (no pixel data)
      │
      │  4. Execute Procedure
      ▼
  ┌────────┐
  │ ROBOT  │  Physical AI system performs
  │ ACTION │  clinical task under safety
  └───┬────┘  constraints from policy
      │
      │  5. Record Audit
      ▼
  ┌────────┐    ┌──────────────┐
  │ Audit  │───▶│ trialmcp-    │  Hash-chained record
  │ Phase  │◀───│ ledger       │  (21 CFR Part 11)
  └───┬────┘    └──────────────┘
      │
      │  6. Record Provenance
      ▼
  ┌────────┐    ┌──────────────┐
  │ Prov.  │───▶│ trialmcp-    │  DAG lineage entry
  │ Phase  │◀───│ provenance   │  (SHA-256 fingerprint)
  └───┬────┘    └──────────────┘
      │
      ▼
  ┌────────┐
  │  DONE  │
  └────────┘
```

---

## Audit Chain Architecture

The audit subsystem uses a hash-chained immutable ledger that satisfies
21 CFR Part 11 requirements for electronic records in clinical trials.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HASH-CHAINED AUDIT LEDGER                         │
│                                                                      │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────┐  │
│  │  Genesis   │───▶│  Record 1  │───▶│  Record 2  │───▶│  ...   │  │
│  │  Block     │    │            │    │            │    │        │  │
│  │            │    │ prev_hash: │    │ prev_hash: │    │        │  │
│  │ hash:      │    │  genesis   │    │  hash(R1)  │    │        │  │
│  │ 000...000  │    │            │    │            │    │        │  │
│  │ (64 zeros) │    │ hash:      │    │ hash:      │    │        │  │
│  │            │    │  SHA-256(  │    │  SHA-256(  │    │        │  │
│  │            │    │   prev +   │    │   prev +   │    │        │  │
│  │            │    │   canon)   │    │   canon)   │    │        │  │
│  └────────────┘    └────────────┘    └────────────┘    └────────┘  │
│                                                                      │
│  Canonical JSON: alphabetical keys, hash excluded, UTF-8 encoded    │
│  Chain verification: re-compute each hash and compare                │
│  Tamper detection: any modification invalidates all subsequent hashes│
│                                                                      │
│  Every tool invocation across ALL 5 servers produces an audit record │
│  Records are immutable once appended — no update, no delete          │
└─────────────────────────────────────────────────────────────────────┘
```

### Cross-Server Audit Coordination

In a multi-server deployment, each server appends to the same audit
chain.  The operational order for a complete robot procedure is:

1. **trialmcp-authz** — Token issuance and RBAC evaluation
2. **trialmcp-fhir** — Patient data query with de-identification
3. **trialmcp-dicom** — Imaging query and metadata retrieval
4. **trialmcp-ledger** — Audit record for the procedure itself
5. **trialmcp-provenance** — Lineage record for data flow tracking

This ordering ensures that every step in the robot's clinical workflow
is traceable, auditable, and verifiable by any authorized party.

---

## National Deployment Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                  NATIONAL GOVERNANCE LAYER                           │
│                                                                      │
│  National Standards Body        Conformance Registry                │
│  Extension Namespace Mgmt      Version Compatibility Policy         │
│  Schema Registry                Validation Services                 │
└───────────────┬──────────────────────────────────┬──────────────────┘
                │                                   │
     ┌──────────┼──────────────┐                   │
     ▼          ▼              ▼                   ▼
  ┌────────┐ ┌────────┐  ┌────────┐         ┌──────────┐
  │REGION 1│ │REGION 2│  │REGION N│         │FEDERATED │
  │(East)  │ │(Central│  │(West)  │         │LAYER     │
  │        │ │       )│  │        │         │          │
  │200+    │ │300+    │  │250+    │────────▶│Aggregation│
  │Sites   │ │Sites   │  │Sites   │         │Diff Priv │
  │5 Svrs  │ │5 Svrs  │  │5 Svrs  │         │Audit     │
  │per Site│ │per Site│  │per Site│         │Merge     │
  └────────┘ └────────┘  └────────┘         └──────────┘
```

Each site operates its own five-server deployment.  The federated layer
aggregates model updates using privacy-preserving techniques (FedAvg,
FedProx, SCAFFOLD) with differential privacy budgets, while audit
chains are verified cross-site without exposing patient data.

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

### Related Repositories

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework with USL scoring
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework
