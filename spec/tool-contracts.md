# Tool Contracts Specification

**National MCP-PAI Oncology Trials Standard — spec/tool-contracts.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the 23 tool contracts across the five MCP servers. Each contract specifies the tool name, input parameters, output shape, error codes, and audit requirements. All conforming implementations MUST satisfy these contracts exactly.

---

## 2. Contract Format

Each tool contract follows this structure:

- **Tool Name**: The MCP tool identifier
- **Server**: The hosting MCP server
- **Input Parameters**: Named parameters with types and constraints
- **Output Shape**: The structure of successful responses
- **Error Codes**: Applicable error codes from the standard registry
- **Audit**: What MUST be recorded in the audit ledger

---

## 3. AuthZ Server Tools (trialmcp-authz)

### 3.1 authz_evaluate

Evaluates an access request against the policy engine.

| Field | Specification |
|-------|--------------|
| **Input** | `role` (string, REQUIRED): Actor role. `server` (string, REQUIRED): Target server identifier. `tool` (string, REQUIRED): Target tool name. |
| **Output** | `{ "allowed": bool, "matching_rules": list, "effect": "ALLOW" \| "DENY" }` |
| **Errors** | `INVALID_INPUT`, `INTERNAL_ERROR` |
| **Audit** | MUST record role, server, tool, and evaluation result |

### 3.2 authz_issue_token

Issues a scoped session token for an authenticated actor.

| Field | Specification |
|-------|--------------|
| **Input** | `role` (string, REQUIRED): Actor role to scope the token. `subject` (string, REQUIRED): Actor identifier. `duration_seconds` (integer, OPTIONAL, default 3600): Token validity duration. |
| **Output** | `{ "token": string, "expires_at": string (ISO 8601), "role": string, "subject": string }` |
| **Errors** | `AUTHZ_DENIED`, `INVALID_INPUT`, `INTERNAL_ERROR` |
| **Audit** | MUST record subject, role, token hash (NOT the token itself), and expiry |

### 3.3 authz_validate_token

Validates a previously issued token.

| Field | Specification |
|-------|--------------|
| **Input** | `token` (string, REQUIRED): The token to validate. |
| **Output** | `{ "valid": bool, "role": string, "subject": string, "expires_at": string }` |
| **Errors** | `TOKEN_EXPIRED`, `TOKEN_REVOKED`, `INVALID_INPUT` |
| **Audit** | MUST record validation attempt and result |

### 3.4 authz_list_policies

Returns all active authorization policies.

| Field | Specification |
|-------|--------------|
| **Input** | `role_filter` (string, OPTIONAL): Filter policies by role. |
| **Output** | `{ "policies": [{ "role": string, "server": string, "tool": string, "effect": "ALLOW" \| "DENY" }] }` |
| **Errors** | `AUTHZ_DENIED`, `INTERNAL_ERROR` |
| **Audit** | MUST record the requesting actor and any filters applied |

### 3.5 authz_revoke_token

Revokes an active token.

| Field | Specification |
|-------|--------------|
| **Input** | `token` (string, REQUIRED): The token to revoke. |
| **Output** | `{ "revoked": bool, "token_hash": string }` |
| **Errors** | `NOT_FOUND`, `AUTHZ_DENIED`, `INTERNAL_ERROR` |
| **Audit** | MUST record token hash and revocation timestamp |

---

## 4. FHIR Server Tools (trialmcp-fhir)

### 4.1 fhir_read

Reads a single FHIR R4 resource by type and ID. Returns de-identified data.

| Field | Specification |
|-------|--------------|
| **Input** | `resource_type` (string, REQUIRED): FHIR resource type (e.g., Patient, Observation). `resource_id` (string, REQUIRED): Logical ID matching `^[A-Za-z0-9\-._]+$`. |
| **Output** | `{ "resource": object (de-identified FHIR R4 resource) }` |
| **Errors** | `NOT_FOUND`, `VALIDATION_FAILED`, `AUTHZ_DENIED` |
| **Audit** | MUST record resource type, resource ID (pseudonymized if patient), and caller |
| **Validation** | MUST reject IDs containing URLs (SSRF prevention) |

### 4.2 fhir_search

Searches FHIR R4 resources by type with optional filters. Results capped at 100.

| Field | Specification |
|-------|--------------|
| **Input** | `resource_type` (string, REQUIRED): FHIR resource type. `filters` (object, OPTIONAL): Key-value search parameters. `max_results` (integer, OPTIONAL, default 100, max 100). |
| **Output** | `{ "results": [object], "total": integer }` |
| **Errors** | `VALIDATION_FAILED`, `AUTHZ_DENIED`, `INTERNAL_ERROR` |
| **Audit** | MUST record resource type, filter parameters, and result count |

### 4.3 fhir_patient_lookup

Returns pseudonymized patient demographics and enrollment status.

| Field | Specification |
|-------|--------------|
| **Input** | `patient_id` (string, REQUIRED): Patient logical ID. |
| **Output** | `{ "pseudonym": string, "enrollment_status": string, "birth_year": integer, "gender": string }` |
| **Errors** | `NOT_FOUND`, `VALIDATION_FAILED`, `AUTHZ_DENIED` |
| **Audit** | MUST record pseudonymized patient ID (NEVER the real ID) |
| **Privacy** | MUST apply HMAC-SHA256 pseudonymization and year-only birth date |

### 4.4 fhir_study_status

Returns ResearchStudy summary with enrollment counts.

| Field | Specification |
|-------|--------------|
| **Input** | `study_id` (string, REQUIRED): ResearchStudy logical ID. |
| **Output** | `{ "study_id": string, "title": string, "status": string, "enrollment_count": integer, "phase": string }` |
| **Errors** | `NOT_FOUND`, `VALIDATION_FAILED` |
| **Audit** | MUST record study ID and requesting actor |

---

## 5. DICOM Server Tools (trialmcp-dicom)

### 5.1 dicom_query

Queries DICOM studies with role-based access control.

| Field | Specification |
|-------|--------------|
| **Input** | `query_level` (string, REQUIRED): One of `PATIENT`, `STUDY`, `SERIES`, `IMAGE`. `filters` (object, OPTIONAL): DICOM attribute filters. `caller_role` (string, REQUIRED): Actor role for permission evaluation. |
| **Output** | `{ "results": [object], "total": integer, "query_level": string }` |
| **Errors** | `AUTHZ_DENIED`, `VALIDATION_FAILED`, `INTERNAL_ERROR` |
| **Audit** | MUST record query level, filters, caller role, and result count |
| **Privacy** | Patient names at PATIENT level MUST be hashed (SHA-256, truncated to 12 chars) |
| **Permissions** | `trial_coordinator`: PATIENT/STUDY/SERIES. `robot_agent`: STUDY/SERIES only. `data_monitor`: PATIENT/STUDY only. `auditor`: STUDY only. |

### 5.2 dicom_retrieve_pointer

Generates a time-limited retrieval token for a DICOM study.

| Field | Specification |
|-------|--------------|
| **Input** | `study_instance_uid` (string, REQUIRED): DICOM Study Instance UID matching `^[\d.]+$`. `caller_role` (string, REQUIRED): Actor role. |
| **Output** | `{ "retrieval_token": string, "expires_at": string (ISO 8601), "study_instance_uid": string }` |
| **Errors** | `AUTHZ_DENIED`, `VALIDATION_FAILED`, `NOT_FOUND` |
| **Audit** | MUST record study UID, caller role, and token hash |
| **Validation** | MUST reject UIDs containing URLs (SSRF prevention). Token expiry MUST default to 3600 seconds. |

### 5.3 dicom_study_metadata

Returns metadata for a DICOM study.

| Field | Specification |
|-------|--------------|
| **Input** | `study_instance_uid` (string, REQUIRED): DICOM Study Instance UID. `caller_role` (string, REQUIRED): Actor role. |
| **Output** | `{ "study_instance_uid": string, "modalities": [string], "series_count": integer, "study_date": string, "description": string }` |
| **Errors** | `AUTHZ_DENIED`, `VALIDATION_FAILED`, `NOT_FOUND` |
| **Audit** | MUST record study UID and caller role |

### 5.4 dicom_recist_measurements

Returns RECIST 1.1 tumor measurements for a study.

| Field | Specification |
|-------|--------------|
| **Input** | `study_instance_uid` (string, REQUIRED): DICOM Study Instance UID. |
| **Output** | `{ "study_instance_uid": string, "measurements": [{ "lesion_id": string, "diameter_mm": number, "response": string }], "overall_response": string }` |
| **Errors** | `NOT_FOUND`, `VALIDATION_FAILED` |
| **Audit** | MUST record study UID and measurement count |

---

## 6. Ledger Server Tools (trialmcp-ledger)

### 6.1 ledger_append

Appends a new audit record to the hash-chained ledger.

| Field | Specification |
|-------|--------------|
| **Input** | `server` (string, REQUIRED): Originating server identifier. `tool` (string, REQUIRED): Tool that was invoked. `caller` (string, REQUIRED): Actor identifier. `parameters` (object, REQUIRED): Tool call parameters (de-identified). `result_summary` (string, REQUIRED): Outcome description. |
| **Output** | `{ "audit_id": string, "hash": string (SHA-256), "previous_hash": string, "timestamp": string (ISO 8601) }` |
| **Errors** | `AUTHZ_DENIED`, `INVALID_INPUT`, `INTERNAL_ERROR` |
| **Chain** | The `previous_hash` MUST be the SHA-256 hash of the immediately preceding record. The genesis record MUST use `"0" * 64` as its previous hash. |

### 6.2 ledger_verify

Verifies the integrity of the audit chain.

| Field | Specification |
|-------|--------------|
| **Input** | `start_index` (integer, OPTIONAL): Start verification from this record index. `end_index` (integer, OPTIONAL): End verification at this record index. |
| **Output** | `{ "valid": bool, "records_checked": integer, "first_invalid_index": integer \| null, "genesis_valid": bool }` |
| **Errors** | `INTERNAL_ERROR` |
| **Verification** | MUST verify genesis hash, recompute each record hash, and validate chain continuity. |

### 6.3 ledger_query

Queries audit records by filter criteria.

| Field | Specification |
|-------|--------------|
| **Input** | `server` (string, OPTIONAL): Filter by server. `tool` (string, OPTIONAL): Filter by tool. `caller` (string, OPTIONAL): Filter by caller. `start_time` (string, OPTIONAL): ISO 8601 start. `end_time` (string, OPTIONAL): ISO 8601 end. |
| **Output** | `{ "records": [object], "total": integer }` |
| **Errors** | `AUTHZ_DENIED`, `INVALID_INPUT` |
| **Audit** | MUST record the query parameters and requesting actor |

### 6.4 ledger_replay

Generates a sequential replay trace for compliance review.

| Field | Specification |
|-------|--------------|
| **Input** | `start_time` (string, OPTIONAL): ISO 8601 start. `end_time` (string, OPTIONAL): ISO 8601 end. `caller` (string, OPTIONAL): Filter by caller. |
| **Output** | `{ "trace": [object], "total": integer, "duration": string }` |
| **Errors** | `AUTHZ_DENIED`, `INTERNAL_ERROR` |
| **Compliance** | MUST produce traces sufficient for ICH-GCP E6(R2) audit review |

### 6.5 ledger_chain_status

Reports the health and statistics of the audit chain.

| Field | Specification |
|-------|--------------|
| **Input** | None |
| **Output** | `{ "total_records": integer, "chain_valid": bool, "genesis_hash": string, "latest_hash": string, "latest_timestamp": string }` |
| **Errors** | `INTERNAL_ERROR` |

---

## 7. Provenance Server Tools (trialmcp-provenance)

### 7.1 provenance_register_source

Registers a new data source in the provenance graph.

| Field | Specification |
|-------|--------------|
| **Input** | `source_type` (string, REQUIRED): Type of data source. `origin_server` (string, REQUIRED): Server that owns the data. `description` (string, REQUIRED): Human-readable description. `metadata` (object, OPTIONAL): Additional properties. |
| **Output** | `{ "source_id": string, "registered_at": string (ISO 8601) }` |
| **Errors** | `AUTHZ_DENIED`, `INVALID_INPUT`, `INTERNAL_ERROR` |
| **Audit** | MUST record source type, origin server, and registering actor |

### 7.2 provenance_record_access

Records a data access event in the provenance graph.

| Field | Specification |
|-------|--------------|
| **Input** | `source_id` (string, REQUIRED): Data source identifier. `action` (string, REQUIRED): Action performed (e.g., `read`, `transform`, `aggregate`). `actor_id` (string, REQUIRED): Actor performing the action. `actor_role` (string, REQUIRED): Actor's role. `tool_call` (string, REQUIRED): Tool invocation that triggered this access. `input_data` (string, OPTIONAL): Input data for fingerprinting. `output_data` (string, OPTIONAL): Output data for fingerprinting. |
| **Output** | `{ "record_id": string, "input_hash": string (SHA-256), "output_hash": string (SHA-256), "timestamp": string }` |
| **Errors** | `AUTHZ_DENIED`, `NOT_FOUND`, `INVALID_INPUT` |
| **Fingerprinting** | Input and output data MUST be hashed with SHA-256 for integrity verification |

### 7.3 provenance_get_lineage

Retrieves the full access history for a data source (forward or backward query).

| Field | Specification |
|-------|--------------|
| **Input** | `source_id` (string, REQUIRED): Data source identifier. `direction` (string, OPTIONAL, default `backward`): `forward` or `backward` traversal. |
| **Output** | `{ "source_id": string, "lineage": [object], "total": integer }` |
| **Errors** | `NOT_FOUND`, `INTERNAL_ERROR` |

### 7.4 provenance_get_actor_history

Returns all operations performed by a specific actor.

| Field | Specification |
|-------|--------------|
| **Input** | `actor_id` (string, REQUIRED): Actor identifier. `start_time` (string, OPTIONAL): ISO 8601 start. `end_time` (string, OPTIONAL): ISO 8601 end. |
| **Output** | `{ "actor_id": string, "records": [object], "total": integer }` |
| **Errors** | `AUTHZ_DENIED`, `NOT_FOUND` |

### 7.5 provenance_verify_integrity

Verifies data integrity by comparing fingerprints.

| Field | Specification |
|-------|--------------|
| **Input** | `source_id` (string, REQUIRED): Data source identifier. `data` (string, REQUIRED): Data to verify against recorded fingerprint. |
| **Output** | `{ "source_id": string, "verified": bool, "expected_hash": string, "actual_hash": string }` |
| **Errors** | `NOT_FOUND`, `INTERNAL_ERROR` |

---

## 8. Cross-Cutting Requirements

### 8.1 Input Validation

All tools MUST validate input parameters before processing:
- FHIR IDs MUST match `^[A-Za-z0-9\-._]+$`
- DICOM UIDs MUST match `^[\d.]+$`
- All string inputs MUST be checked for embedded URLs (SSRF prevention)
- Inputs containing `http://` or `https://` (case-insensitive) MUST be rejected with `VALIDATION_FAILED`

### 8.2 Audit Generation

Every tool invocation MUST produce an audit record containing:
- Timestamp (ISO 8601 UTC)
- Server identifier
- Tool name
- Caller identifier
- Input parameters (de-identified where applicable)
- Result summary
- Hash linking to previous audit record

### 8.3 De-identification

All tools returning patient data MUST apply HIPAA Safe Harbor de-identification before returning results. See [privacy.md](privacy.md) for the full de-identification specification.
