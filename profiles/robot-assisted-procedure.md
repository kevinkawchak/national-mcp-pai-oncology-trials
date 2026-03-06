# Robot-Assisted Procedure Profile

**National MCP-PAI Oncology Trials Standard — profiles/robot-assisted-procedure.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

The Robot-Assisted Procedure Profile defines the requirements for implementations that enable end-to-end autonomous or semi-autonomous robot clinical workflows across all five MCP servers. This profile builds on the [Multi-Site Federated Profile](multi-site-federated.md) and represents the highest conformance level — Level 5 — requiring full integration of authorization, clinical data, imaging, audit, and provenance for Physical AI systems executing oncology procedures.

> Implementations claiming Robot-Assisted Procedure conformance MUST satisfy all lower-profile requirements AND all requirements defined in this profile.

---

## 2. Robot Capability Profile

### 2.1 Registration Requirements

Every robot agent participating in MCP-mediated clinical procedures MUST be registered with a capability profile conforming to `schemas/robot-capability-profile.schema.json`.

| Field | Requirement | Description |
|-------|-------------|-------------|
| `robot_id` | MUST | Globally unique robot identifier |
| `platform` | MUST | Robot platform name (e.g., manufacturer and model) |
| `robot_type` | MUST | One of: `surgical`, `therapeutic_positioning`, `diagnostic_needle_placement`, `rehabilitative_exoskeleton`, `companion_monitoring` |
| `usl_score` | MUST | Unification Standard Level score (1.0–10.0 scale) |
| `safety_prerequisites` | MUST | Array of safety checks with name, status, verified_at, verified_by |
| `mcp_tools_required` | MUST | List of MCP tools the robot requires for its procedure type |
| `simulation_frameworks` | SHOULD | Simulation environments used for validation (e.g., MuJoCo, Isaac Sim) |
| `digital_twin_support` | MAY | Whether the robot supports digital twin integration |

### 2.2 Supported Robot Types

| Robot Type | Oncology Use | Minimum USL Score |
|-----------|-------------|-------------------|
| `surgical` | Tumor resection, tissue excision | 7.0 |
| `therapeutic_positioning` | Radiation beam alignment, patient positioning | 6.0 |
| `diagnostic_needle_placement` | Biopsy needle guidance, port placement | 6.0 |
| `rehabilitative_exoskeleton` | Post-surgical rehabilitation, mobility assistance | 4.0 |
| `companion_monitoring` | Vital signs monitoring, patient comfort | 3.0 |

---

## 3. Task-Order Contract

### 3.1 Task Lifecycle

Every robot-assisted procedure MUST follow the task-order lifecycle defined in `schemas/task-order.schema.json`:

```
scheduled → safety_check → in_progress → completed
                                       → cancelled
                                       → failed
```

| State | Description | Transitions |
|-------|-------------|-------------|
| `scheduled` | Task created and assigned to robot | → `safety_check`, → `cancelled` |
| `safety_check` | Pre-procedure safety verification in progress | → `in_progress`, → `cancelled`, → `failed` |
| `in_progress` | Robot executing the clinical procedure | → `completed`, → `failed` |
| `completed` | Procedure finished successfully | Terminal |
| `cancelled` | Procedure cancelled before or during execution | Terminal |
| `failed` | Procedure failed due to safety concern or error | Terminal |

### 3.2 Procedure Types

| Procedure Type | Robot Types | Description |
|---------------|------------|-------------|
| `tumor_resection` | `surgical` | Robotic tumor excision |
| `biopsy_needle_placement` | `diagnostic_needle_placement` | Image-guided biopsy |
| `radiation_positioning` | `therapeutic_positioning` | Patient alignment for radiotherapy |
| `rehabilitation_session` | `rehabilitative_exoskeleton` | Post-operative rehabilitation |
| `diagnostic_imaging_assist` | `companion_monitoring`, `diagnostic_needle_placement` | Robot-assisted imaging procedures |
| `patient_monitoring` | `companion_monitoring` | Continuous patient vital monitoring |

---

## 4. Safety Matrix

### 4.1 Pre-Procedure Safety Checks

Before any task may transition from `safety_check` to `in_progress`, ALL applicable safety prerequisites MUST pass:

| Check Category | Checks | Requirement |
|---------------|--------|-------------|
| **Authorization** | Valid token, correct role scope, procedure-specific policy | MUST |
| **Patient Identity** | Pseudonymized patient match, enrollment verification, consent status | MUST |
| **Clinical Data** | Required FHIR resources available, study status active | MUST |
| **Imaging Data** | Required DICOM studies accessible, correct modalities available | MUST (if imaging-guided) |
| **Robot Readiness** | USL score meets minimum threshold, hardware self-test passed | MUST |
| **Environmental** | Operating room environment sensors nominal | SHOULD |
| **Simulation Validation** | Procedure rehearsed in simulation environment | SHOULD |
| **Digital Twin Sync** | Digital twin model synchronized with current patient state | MAY |

### 4.2 Runtime Safety Monitoring

During procedure execution (`in_progress` state):

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Continuous authorization validation | MUST | Token validity checked at configurable intervals |
| Real-time audit recording | MUST | Procedure steps recorded to ledger in real time |
| Emergency stop capability | MUST | Immediate halt with audit record on safety violation |
| Force/torque limit monitoring | MUST | For surgical and positioning robots |
| Patient vital sign integration | SHOULD | Via companion monitoring or clinical systems |
| Provenance recording for each step | SHOULD | Fine-grained lineage for procedure sub-steps |

### 4.3 Post-Procedure Requirements

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Complete audit trail | MUST | Full procedure lifecycle in ledger |
| Provenance chain | MUST | Data lineage from patient data through procedure to outcomes |
| Outcome recording | MUST | Procedure outcome in FHIR (Procedure resource) |
| Safety incident reporting | MUST | Any safety event recorded with severity classification |
| USL score update | SHOULD | Updated USL score based on procedure performance |

---

## 5. USL Scoring Integration

The Unification Standard Level (USL) scoring framework from the [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179) project provides a standardized readiness assessment for robot platforms.

### 5.1 USL Score Requirements

| Requirement | Keyword | Description |
|------------|---------|-------------|
| USL score in capability profile | MUST | Score between 1.0 and 10.0 in robot registration |
| Minimum USL threshold per procedure type | MUST | Robot MUST meet minimum score for assigned procedure |
| USL score in task-order validation | MUST | Safety check MUST verify USL meets procedure threshold |
| USL score in audit records | MUST | Record robot USL score in procedure audit entries |
| Periodic USL reassessment | SHOULD | Score should be updated based on operational history |

### 5.2 Six-Step Robot Agent Workflow

Every robot-assisted procedure MUST implement the following workflow:

| Step | Server | Tools | Description |
|------|--------|-------|-------------|
| 1. Authenticate | trialmcp-authz | `authz_issue_token`, `authz_evaluate` | Obtain scoped session token |
| 2. Retrieve Clinical Data | trialmcp-fhir | `fhir_patient_lookup`, `fhir_read`, `fhir_study_status` | Fetch de-identified patient and study data |
| 3. Access Imaging | trialmcp-dicom | `dicom_query`, `dicom_retrieve_pointer`, `dicom_study_metadata` | Query and retrieve relevant imaging |
| 4. Execute Procedure | Robot platform | (Platform-specific) | Perform the clinical task |
| 5. Record Audit | trialmcp-ledger | `ledger_append` | Record complete procedure audit trail |
| 6. Record Provenance | trialmcp-provenance | `provenance_record_access`, `provenance_register_source` | Document data lineage through procedure |

---

## 6. Optional Tools

| Tool | Requirement | Description |
|------|-------------|-------------|
| `robot_telemetry_stream` | MAY | Real-time telemetry recording via vendor extension |
| `robot_digital_twin_sync` | MAY | Digital twin state synchronization |
| `robot_simulation_validate` | MAY | Pre-procedure simulation validation |

---

## 7. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| Procedure execution without safety check | Safety: ALL safety prerequisites MUST pass before `in_progress` |
| Procedure without valid authorization token | Security: continuous token validation required |
| Skipping audit for any procedure step | Compliance: complete audit trail is mandatory |
| Robot operation below minimum USL score | Safety: USL threshold enforcement is mandatory |
| Direct clinical system modification by robot | Architecture: robots interact only through MCP servers |
| Procedure continuation after emergency stop | Safety: halted procedures require new safety check cycle |

---

## 8. Required Schemas

In addition to all lower-profile schemas, Robot-Assisted Procedure implementations MUST validate against:

| Schema | File | Purpose |
|--------|------|---------|
| Robot Capability Profile | `schemas/robot-capability-profile.schema.json` | Platform, type, USL score, safety prerequisites |
| Task Order | `schemas/task-order.schema.json` | Procedure scheduling, status lifecycle, safety checks |
| Site Capability Profile | `schemas/site-capability-profile.schema.json` | Site deployment validation |

---

## 9. Regulatory Overlays

| Regulation | Relevant Section | Coverage |
|-----------|-----------------|----------|
| FDA AI/ML Guidance | SaMD classification | Robot as Software as Medical Device component |
| FDA AI/ML Guidance | Predetermined change control | USL score thresholds and safety matrix |
| 21 CFR Part 11 | §11.10(e) Audit trails | Complete procedure lifecycle auditing |
| HIPAA Privacy Rule | §164.514(b) Safe Harbor | De-identified patient data for robot consumption |
| IEC 80601-2-77 | Robot-assisted surgery safety | Safety matrix alignment |
| ISO 14971 | Risk management | USL scoring as risk assessment framework |
| ISO 13482 | Personal care robot safety | Safety prerequisites for companion robots |
| ICH-GCP E6(R2) | §8.1 Essential documents | Replayable procedure audit traces |

---

## 10. Conformance Test Subset

Implementations claiming Robot-Assisted Procedure conformance MUST pass:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| Multi-Site Federated Profile tests | 48 | All lower-profile conformance tests |
| Robot registration and capability | 2 | Schema validation, USL score verification |
| Task-order lifecycle | 3 | State transitions, safety check gate, completion |
| Six-step workflow execution | 2 | Full workflow, audit completeness |
| Safety matrix enforcement | 2 | Pre-procedure checks, emergency stop |
| USL threshold validation | 1 | Minimum score enforcement per procedure type |
| **Total** | **58** | |

---

*This profile is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [spec/tool-contracts.md](../spec/tool-contracts.md) for the complete tool contract specifications and [spec/actor-model.md](../spec/actor-model.md) for robot agent permissions.*
