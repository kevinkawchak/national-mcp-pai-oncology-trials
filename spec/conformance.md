# Conformance Specification

**National MCP-PAI Oncology Trials Standard — spec/conformance.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines five conformance levels for MCP server deployments within the national Physical AI oncology trials infrastructure. Each level builds on the previous, adding servers, tools, and requirements. Implementations MUST declare their conformance level and satisfy all MUST requirements for that level and all lower levels.

---

## 2. Conformance Level Definitions

### Level 1 — Core

**Purpose**: Establish authentication, authorization, and audit chain as the foundation for all deployments.

**Required Servers**: `trialmcp-authz`, `trialmcp-ledger`

| Requirement | Keyword |
|------------|---------|
| Implement `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_list_policies`, `authz_revoke_token` | MUST |
| Implement `ledger_append`, `ledger_verify`, `ledger_query`, `ledger_replay`, `ledger_chain_status` | MUST |
| Enforce deny-by-default RBAC | MUST |
| Use SHA-256 hash chain with genesis hash `"0" * 64` | MUST |
| Validate all inputs against format patterns | MUST |
| Reject URL-embedded inputs (SSRF prevention) | MUST |
| Use standardized error codes | MUST |
| Store token hashes, not plaintext tokens | MUST |
| Support token revocation | MUST |
| Support incremental chain verification | SHOULD |
| Support configurable token duration | SHOULD |
| Implement rate limiting | MAY |
| Support custom policy rules | MAY |

### Level 2 — Clinical Read

**Purpose**: Add FHIR R4 clinical data access with mandatory de-identification.

**Required Servers**: Level 1 + `trialmcp-fhir`

| Requirement | Keyword |
|------------|---------|
| Implement `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status` | MUST |
| Apply HIPAA Safe Harbor de-identification to all patient data | MUST |
| Use HMAC-SHA256 pseudonymization with site-specific salt | MUST |
| Maintain referential integrity across pseudonymized records | MUST |
| Validate FHIR IDs against `^[A-Za-z0-9\-._]+$` | MUST |
| Cap search results at 100 | MUST |
| Generate audit records for all FHIR tool calls | MUST |
| Reduce birth dates to year only | MUST |
| Support multiple FHIR resource types | SHOULD |
| Support FHIR search parameters | SHOULD |
| Expose FHIR capability statement | MAY |

### Level 3 — Imaging

**Purpose**: Add DICOM imaging query and retrieve with role-based permission enforcement.

**Required Servers**: Level 2 + `trialmcp-dicom`

| Requirement | Keyword |
|------------|---------|
| Implement `dicom_query`, `dicom_retrieve_pointer`, `dicom_study_metadata`, `dicom_recist_measurements` | MUST |
| Enforce role-based query level restrictions | MUST |
| Hash patient names at PATIENT query level (SHA-256, 12 chars) | MUST |
| Generate time-limited retrieval tokens (default 3600s) | MUST |
| Validate DICOM UIDs against `^[\d.]+$` | MUST |
| Restrict modality access by role | MUST |
| Generate audit records for all DICOM tool calls | MUST |
| Support RECIST 1.1 measurements | SHOULD |
| Support radiotherapy modalities (RTSTRUCT, RTPLAN, RTDOSE) | SHOULD |
| Support multi-frame images | MAY |

### Level 4 — Federated Site

**Purpose**: Add data provenance tracking and enable multi-site collaboration.

**Required Servers**: Level 3 + `trialmcp-provenance`

| Requirement | Keyword |
|------------|---------|
| Implement `provenance_register_source`, `provenance_record_access`, `provenance_get_lineage`, `provenance_get_actor_history`, `provenance_verify_integrity` | MUST |
| Implement DAG-based lineage tracking | MUST |
| Compute SHA-256 fingerprints for input and output data | MUST |
| Support forward and backward lineage queries | MUST |
| Generate audit records for all provenance tool calls | MUST |
| Maintain site-scoped provenance graphs | MUST |
| Support federated learning aggregation recording | SHOULD |
| Apply differential privacy to cross-site model updates | SHOULD |
| Support secure aggregation | SHOULD |
| Support cross-site lineage queries via coordination layer | MAY |

### Level 5 — Robot Procedure

**Purpose**: Enable end-to-end autonomous robot clinical workflows across all five servers.

**Required Servers**: All five servers

| Requirement | Keyword |
|------------|---------|
| Implement the complete six-step robot agent workflow | MUST |
| Support authentication, data retrieval, imaging, execution, audit, and provenance | MUST |
| Register robot agents with the authorization server | MUST |
| Record complete provenance chain for robot procedures | MUST |
| Generate audit records for the full procedure lifecycle | MUST |
| Support multiple robot platforms | SHOULD |
| Support procedure-specific policy templates | SHOULD |
| Integrate with USL scoring framework | SHOULD |
| Support real-time telemetry provenance recording | MAY |
| Support digital twin integration | MAY |

---

## 3. Conformance Declaration

### 3.1 Declaration Format

Conforming implementations MUST declare their conformance level using the following format in their health check response:

```json
{
  "server": "example-implementation",
  "version": "1.0.0",
  "conformance_level": 3,
  "conformance_version": "0.1.0",
  "status": "healthy"
}
```

### 3.2 Partial Conformance

Implementations MUST NOT claim a conformance level unless they satisfy all MUST requirements for that level and all lower levels. Partial implementation of a level's requirements does not constitute conformance at that level.

### 3.3 Conformance Testing

Implementations SHOULD validate their conformance through the standard test suite (when published). The test suite will verify:
- All MUST requirements for the declared level
- Input validation and error handling
- Hash chain integrity
- De-identification completeness
- Permission enforcement

---

## 4. National Conformance Registry

### 4.1 Registration

Conforming implementations SHOULD register with the national conformance registry, providing:
- Implementation name and version
- Declared conformance level
- Contact information for the responsible organization
- Date of last conformance validation

### 4.2 Conformance Badges

Registered implementations MAY display conformance badges indicating their validated level.
