# Actor Model Specification

**National MCP-PAI Oncology Trials Standard — spec/actor-model.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the six actors that interact with the national MCP infrastructure. The actor model is derived from the four operational roles implemented in the reference authorization server (`robot_agent`, `trial_coordinator`, `data_monitor`, `auditor`) plus two organizational actors (`sponsor`, `CRO`) required for national-scale trial governance.

---

## 2. Actor Definitions

### 2.1 Robot Agent

- **Type**: Autonomous system
- **Description**: A Physical AI system (surgical robot, therapeutic positioning system, diagnostic platform, or rehabilitative exoskeleton) executing clinical procedures within an oncology trial
- **Authentication**: Token-based session with `robot_agent` role scope
- **Trust Level**: Constrained — scoped to specific tools required for assigned clinical tasks

### 2.2 Trial Coordinator

- **Type**: Human operator
- **Description**: Clinical site staff responsible for managing trial operations, patient enrollment, and procedure scheduling
- **Authentication**: Token-based session with `trial_coordinator` role scope
- **Trust Level**: Elevated — full access to clinical data and imaging at their site

### 2.3 Data Monitor

- **Type**: Human operator
- **Description**: CRO or sponsor representative responsible for reviewing trial data quality, adverse events, and protocol adherence
- **Authentication**: Token-based session with `data_monitor` role scope
- **Trust Level**: Read-only — can query clinical and imaging data but cannot modify or retrieve raw images

### 2.4 Auditor

- **Type**: Human operator
- **Description**: Compliance officer responsible for verifying regulatory adherence, audit trail integrity, and chain-of-custody
- **Authentication**: Token-based session with `auditor` role scope
- **Trust Level**: Audit-scoped — limited to ledger operations for compliance verification

### 2.5 Sponsor

- **Type**: Organization
- **Description**: Pharmaceutical company, medical device company, or research institution funding and overseeing the clinical trial
- **Authentication**: Organization-level credentials with `sponsor` role scope
- **Trust Level**: Governance — policy configuration, aggregate reporting, no direct patient data access

### 2.6 CRO (Contract Research Organization)

- **Type**: Organization
- **Description**: Organization contracted to manage multi-site trial operations, monitor data quality, and coordinate regulatory submissions
- **Authentication**: Organization-level credentials with `cro` role scope
- **Trust Level**: Coordination — cross-site aggregate access, no direct patient-level data

---

## 3. Permission Matrix

The following matrix defines the default access policy for each actor across all 23 tools. Implementations MUST enforce these as minimum restrictions. Sites MAY apply additional restrictions but MUST NOT grant broader access than specified.

### 3.1 AuthZ Server Tools

| Tool | robot_agent | trial_coordinator | data_monitor | auditor | sponsor | cro |
|------|:-----------:|:-----------------:|:------------:|:-------:|:-------:|:---:|
| `authz_evaluate` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `authz_issue_token` | DENY | ALLOW | DENY | DENY | ALLOW | ALLOW |
| `authz_validate_token` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `authz_list_policies` | DENY | ALLOW | DENY | ALLOW | ALLOW | ALLOW |
| `authz_revoke_token` | DENY | ALLOW | DENY | DENY | ALLOW | ALLOW |

### 3.2 FHIR Server Tools

| Tool | robot_agent | trial_coordinator | data_monitor | auditor | sponsor | cro |
|------|:-----------:|:-----------------:|:------------:|:-------:|:-------:|:---:|
| `fhir_read` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| `fhir_search` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| `fhir_patient_lookup` | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| `fhir_study_status` | ALLOW | ALLOW | ALLOW | DENY | ALLOW | ALLOW |

### 3.3 DICOM Server Tools

| Tool | robot_agent | trial_coordinator | data_monitor | auditor | sponsor | cro |
|------|:-----------:|:-----------------:|:------------:|:-------:|:-------:|:---:|
| `dicom_query` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| `dicom_retrieve_pointer` | ALLOW | ALLOW | DENY | DENY | DENY | DENY |
| `dicom_study_metadata` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| `dicom_recist_measurements` | ALLOW | ALLOW | ALLOW | DENY | DENY | ALLOW |

### 3.4 Ledger Server Tools

| Tool | robot_agent | trial_coordinator | data_monitor | auditor | sponsor | cro |
|------|:-----------:|:-----------------:|:------------:|:-------:|:-------:|:---:|
| `ledger_append` | ALLOW | ALLOW | DENY | DENY | DENY | DENY |
| `ledger_verify` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `ledger_query` | DENY | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `ledger_replay` | DENY | ALLOW | DENY | ALLOW | ALLOW | ALLOW |
| `ledger_chain_status` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |

### 3.5 Provenance Server Tools

| Tool | robot_agent | trial_coordinator | data_monitor | auditor | sponsor | cro |
|------|:-----------:|:-----------------:|:------------:|:-------:|:-------:|:---:|
| `provenance_register_source` | ALLOW | ALLOW | DENY | DENY | DENY | DENY |
| `provenance_record_access` | ALLOW | ALLOW | DENY | DENY | DENY | DENY |
| `provenance_get_lineage` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `provenance_get_actor_history` | DENY | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `provenance_verify_integrity` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |

---

## 4. Policy Enforcement Rules

### 4.1 Deny-by-Default

Any request that does not match an explicit ALLOW rule MUST be denied. Implementations MUST NOT fall back to permissive defaults.

### 4.2 DENY Precedence

If both ALLOW and DENY rules match a request, the DENY rule MUST take precedence. This prevents privilege escalation through overlapping policies.

### 4.3 Role Scoping

Tokens MUST be scoped to a single role. An actor MUST NOT hold tokens for multiple roles simultaneously within the same session. Role changes require token revocation and re-issuance.

### 4.4 Site Boundaries

Permissions are scoped to the issuing site. A token issued at Site A MUST NOT grant access to resources at Site B. Cross-site access requires coordination through the federated layer.

---

## 5. National-Scale Considerations

### 5.1 Role Delegation

Sponsors and CROs MAY delegate specific permissions to named individuals via the authorization server. Delegated permissions MUST NOT exceed the delegating actor's own permissions.

### 5.2 Multi-Site Auditor Access

Auditors operating across multiple sites MUST obtain separate tokens from each site's authorization server. A single auditor token MUST NOT grant cross-site access.

### 5.3 Robot Agent Registration

Each robot agent MUST be registered with the site's authorization server before receiving tokens. Registration MUST include the robot platform type, serial number, and the specific clinical procedures it is authorized to perform.
