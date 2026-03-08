# Robot Vendor Implementation Guide

**National MCP-PAI Oncology Trials Standard**
**Audience**: Physical AI Robot Vendors, Systems Integrators, Robotics Engineering Teams
**Version**: 0.1.0

---

## 1. Introduction

This guide assists Physical AI robot vendors in integrating their platforms with the
National MCP-PAI Oncology Trials infrastructure. It covers capability descriptor
requirements, task-order lifecycle semantics, safety gate expectations, the
simulator-to-clinical promotion pathway, integration testing, firmware update
procedures, and incident reporting obligations.

Robot agents are one of six actor roles defined in `spec/actor-model.md`. As autonomous
systems, they operate under the most constrained trust level: scoped access to specific
tools required for assigned clinical tasks.

### 1.1 Supported Procedure Types

The standard supports the following robot-assisted oncology procedure types
(defined in `schemas/task-order.schema.json`):

| Procedure Type | Description |
|---------------|-------------|
| `tumor_resection` | Surgical tumor removal |
| `biopsy_needle_placement` | Image-guided biopsy needle positioning |
| `radiation_positioning` | Patient positioning for radiation therapy |
| `rehabilitation_session` | Post-treatment robotic rehabilitation |
| `diagnostic_imaging_assist` | Robotic assistance during diagnostic imaging |
| `patient_monitoring` | Continuous patient monitoring during treatment |

---

## 2. Capability Descriptor Requirements

### 2.1 Schema Compliance

Every robot platform MUST publish a capability descriptor conforming to
`schemas/capability-descriptor.schema.json` (for MCP server capabilities) and
`schemas/robot-capability-profile.schema.json` (for robot-specific capabilities).

The capability descriptor is used by the robot registry (`safety/robot_registry.py`)
to validate platform eligibility for specific procedures.

### 2.2 Required Capability Keys

The robot registry enforces the following top-level capability sections
(defined in `safety/robot_registry.py`):

| Key | Description | Required |
|-----|-------------|----------|
| `manipulator` | Degrees of freedom, workspace envelope, payload capacity, precision | Yes |
| `sensors` | Sensor suite (force/torque, vision, proximity, position) | Yes |
| `safety_systems` | E-stop hardware, collision detection, force limiting, watchdog timers | Yes |
| `communication` | Network interfaces, protocols, latency requirements | Yes |

### 2.3 Capability Descriptor Example

```json
{
  "robot_id": "b7e4f3a2-1c9d-4e8f-a5b6-7d2e3f4a5b6c",
  "platform_name": "OncoBot Pro 3000",
  "vendor": "Acme Surgical Robotics",
  "version": "2.1.0",
  "manipulator": {
    "degrees_of_freedom": 7,
    "workspace_envelope_mm": [500, 500, 400],
    "payload_capacity_kg": 5.0,
    "position_accuracy_mm": 0.1,
    "repeatability_mm": 0.05
  },
  "sensors": {
    "force_torque": true,
    "vision_system": "stereo_rgb_depth",
    "proximity_sensors": 4,
    "position_encoders": "absolute"
  },
  "safety_systems": {
    "hardware_estop": true,
    "software_estop": true,
    "collision_detection": "force_threshold",
    "force_limiting_n": 50,
    "watchdog_timeout_ms": 100
  },
  "communication": {
    "primary_protocol": "mTLS_HTTP2",
    "max_latency_ms": 50,
    "heartbeat_interval_ms": 1000,
    "fallback_protocol": "serial_rs485"
  },
  "supported_procedures": [
    "tumor_resection",
    "biopsy_needle_placement"
  ],
  "regulatory_certifications": [
    "IEC_80601",
    "ISO_14971",
    "ISO_13482"
  ]
}
```

### 2.4 Vendor Extension Fields

Vendors MAY include additional capability fields using the `x-{vendor}` namespace
prefix (see `governance/EXTENSIONS.md`):

```json
{
  "x-acme_haptic_feedback": {
    "channels": 3,
    "frequency_hz": 1000,
    "resolution_bits": 16
  }
}
```

Extension fields MUST NOT conflict with standard field names and MUST be documented
in the vendor's integration package.

---

## 3. Task-Order Semantics and Lifecycle

### 3.1 Task-Order Schema

All robot procedures are governed by task orders conforming to
`schemas/task-order.schema.json`. Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | UUID v4 | Unique task identifier |
| `trial_id` | string | Clinical trial identifier (e.g., NCT number) |
| `site_id` | string | Clinical site identifier |
| `procedure_type` | enum | One of the six supported procedure types |
| `robot_id` | UUID v4 | Assigned robot identifier |
| `status` | enum | Current lifecycle state |
| `scheduled_at` | ISO 8601 | Scheduled execution time |

### 3.2 Task-Order Lifecycle States

Task orders progress through the following states (defined in
`schemas/task-order.schema.json`):

```
  scheduled --> safety_check --> in_progress --> completed
      |              |               |
      v              v               v
   cancelled       failed          failed
```

| State | Description | Robot Action |
|-------|-------------|-------------|
| `scheduled` | Task created and assigned to robot | Acknowledge receipt; begin pre-flight checks |
| `safety_check` | Safety prerequisites being evaluated | Submit safety gate evidence |
| `in_progress` | Procedure actively executing | Execute procedure; stream telemetry |
| `completed` | Procedure finished successfully | Submit post-procedure evidence |
| `cancelled` | Task cancelled before execution | Acknowledge cancellation; safe state |
| `failed` | Task failed during execution or safety check | Safe state; preserve evidence |

### 3.3 Procedure State Machine

The canonical procedure lifecycle is enforced by the procedure state machine
(`safety/procedure_state.py`). The valid state transitions are:

| From | Allowed Transitions |
|------|-------------------|
| `SCHEDULED` | `PRE_CHECK`, `ABORTED` |
| `PRE_CHECK` | `APPROVED`, `FAILED`, `ABORTED` |
| `APPROVED` | `IN_PROGRESS`, `ABORTED` |
| `IN_PROGRESS` | `POST_CHECK`, `ABORTED`, `FAILED` |
| `POST_CHECK` | `COMPLETED`, `FAILED`, `ABORTED` |
| `COMPLETED` | Terminal state |
| `ABORTED` | Terminal state |
| `FAILED` | Terminal state |

The state machine supports two execution modes (`safety/procedure_state.py`):
- `SIMULATION` -- for testing and validation (no patient contact)
- `CLINICAL` -- for live patient procedures

### 3.4 MCP Tools Available to Robot Agents

Robot agents have access to the following tools (per `spec/actor-model.md` permission
matrix):

| Server | Tool | Access |
|--------|------|--------|
| trialmcp-authz | `authz_evaluate` | ALLOW |
| trialmcp-authz | `authz_validate_token` | ALLOW |
| trialmcp-fhir | `fhir_read` | ALLOW |
| trialmcp-fhir | `fhir_search` | ALLOW |
| trialmcp-fhir | `fhir_patient_lookup` | ALLOW |
| trialmcp-dicom | `dicom_query` | ALLOW (STUDY/SERIES level only) |
| trialmcp-dicom | `dicom_retrieve_pointer` | ALLOW |
| trialmcp-dicom | `dicom_study_metadata` | ALLOW |
| trialmcp-ledger | `ledger_append` | ALLOW |
| trialmcp-provenance | `provenance_record_access` | ALLOW |

All other tools are DENY for robot agents. Attempts to call denied tools will result
in an `AUTHZ_DENIED` error and an audit ledger entry.

---

## 4. Safety Gate Expectations and Certification

### 4.1 Safety Gate Service

Before any procedure transitions from `PRE_CHECK` to `APPROVED`, the safety gate
service (`safety/gate_service.py`) evaluates a matrix of conditions. ALL conditions
MUST pass (`GateStatus.PASS`) for the procedure to proceed.

Standard safety gate conditions:

| Gate Condition | Description | Evidence Required |
|----------------|-------------|-------------------|
| `emergency_stop_verified` | Hardware and software e-stop functional | Self-test result |
| `sterile_field_confirmed` | Sterile field established (surgical procedures) | Operator attestation |
| `patient_consent_verified` | Informed consent on file | Consent status check via FHIR |
| `robot_calibration_current` | Calibration within valid period | Calibration certificate timestamp |
| `usl_score_sufficient` | Robot USL score meets task minimum | Registry lookup |
| `operator_authenticated` | Supervising operator identity confirmed | AuthZ token validation |
| `imaging_data_available` | Required imaging loaded and verified | DICOM query result |

### 4.2 Gate Decision Structure

Each gate evaluation produces a `GateDecision` record (`safety/gate_service.py`)
containing:

- `decision_id` -- unique identifier
- `procedure_id` -- procedure being evaluated
- `overall_pass` -- boolean; true only when every condition is PASS
- `conditions` -- ordered list of evaluated conditions with timestamps
- `decided_at` -- timestamp of the aggregate decision

Gate decisions are recorded in the audit ledger for regulatory traceability.

### 4.3 Human Approval Checkpoints

Certain procedure types require mandatory human-in-the-loop approval
(`safety/approval_checkpoint.py`). The approval system supports:

| Feature | Detail |
|---------|--------|
| Configurable timeout | Default 300 seconds; escalation on timeout |
| Approval statuses | `PENDING`, `APPROVED`, `DENIED`, `TIMED_OUT`, `ESCALATED` |
| Audit trail | All approval requests and decisions recorded |
| Escalation paths | Configurable escalation to senior clinical staff |

### 4.4 Emergency Stop (E-Stop)

The e-stop controller (`safety/estop.py`) manages the emergency stop lifecycle:

| State | Description |
|-------|-------------|
| `IDLE` | Normal operation |
| `TRIGGERED` | E-stop signal received; procedure immediately halted |
| `ACKNOWLEDGED` | Clinical staff has acknowledged the e-stop |
| `RECOVERING` | Recovery procedures in progress with re-authorization |

When an e-stop is triggered:
1. The procedure transitions to `ABORTED` state
2. E-stop signal propagates to all affected MCP servers
3. Procedure state is preserved for investigation
4. Post-abort evidence is captured
5. Recovery requires explicit re-authorization

---

## 5. Simulator-to-Clinical Promotion Path

### 5.1 USL Score Progression

The Unification Standard Level (USL) score (`safety/robot_registry.py`) measures a
robot platform's readiness for clinical deployment. The score ranges from 0 to 100 and
determines procedure eligibility.

| USL Score Range | Certification Status | Allowed Operations |
|----------------|---------------------|-------------------|
| 0 -- 29 | `SIMULATION_ONLY` | Simulation mode only; no patient procedures |
| 30 -- 59 | `SIMULATION_ONLY` | Simulation with synthetic clinical data |
| 60 -- 79 | Eligible for `CLINICAL` review | Clinical evaluation under direct supervision |
| 80 -- 89 | `CLINICAL` | Standard clinical procedures with supervision |
| 90 -- 100 | `CLINICAL` | Full clinical autonomy within approved scope |

### 5.2 Promotion Requirements

To advance from `SIMULATION_ONLY` to `CLINICAL` certification status:

1. **Simulation testing**: Complete all simulation scenarios in `interop-testbed/scenarios/robot_workflow.py`
2. **Conformance testing**: Pass all Level 5 (robot-assisted-procedure) conformance tests:
   ```bash
   pytest conformance/positive/test_imaging_conformance.py -v
   pytest conformance/positive/test_core_conformance.py -v
   ```
3. **Safety validation**: Pass all safety gate evaluations in simulation mode
4. **Integration testing**: Complete end-to-end workflow with all five MCP servers
5. **Adversarial testing**: Pass adversarial test suite (`conformance/adversarial/`)
6. **Human factors review**: Clinical staff usability assessment
7. **IRB approval**: Site-specific IRB review of robot deployment
8. **Evidence pack**: Generate certification evidence bundle (`tools/certification/evidence_pack.py`)

### 5.3 Certification Statuses

| Status | Description | Transition From |
|--------|-------------|----------------|
| `SIMULATION_ONLY` | Initial registration state | Registration |
| `CLINICAL` | Approved for patient procedures | Promotion review |
| `SUSPENDED` | Temporarily removed from clinical use | Any state (safety concern) |

A robot in `SUSPENDED` status MUST undergo re-certification before returning to
`CLINICAL` status. Suspension events MUST be recorded in the audit ledger.

---

## 6. Integration Testing Requirements

### 6.1 Conformance Test Suite

Robot vendors MUST pass the following test categories before deployment:

| Test Category | Directory | Description |
|--------------|-----------|-------------|
| Core conformance | `conformance/positive/test_core_conformance.py` | AuthZ and ledger operations |
| Clinical conformance | `conformance/positive/test_clinical_read_conformance.py` | FHIR data access |
| Imaging conformance | `conformance/positive/test_imaging_conformance.py` | DICOM operations |
| Cross-server workflow | `conformance/blackbox/test_cross_server_workflow.py` | Multi-server scenarios |
| Security tests | `conformance/security/` | Token lifecycle, chain integrity, SSRF prevention |
| Adversarial tests | `conformance/adversarial/` | Replay attacks, PHI leakage, authorization bypass |
| Negative tests | `conformance/negative/` | Invalid inputs, unauthorized access |
| Schema validation | `conformance/interoperability/test_schema_validation.py` | Message format compliance |

### 6.2 Interop Testbed

The interop testbed (`interop-testbed/`) provides a complete simulation environment:

- Mock EHR: `interop-testbed/mock_services/mock_ehr.py`
- Mock PACS: `interop-testbed/mock_services/mock_pacs.py`
- Mock Identity Provider: `interop-testbed/mock_services/mock_identity.py`
- Robot agent persona: `interop-testbed/personas/robot_agent.yaml`

Run the robot workflow scenario:
```bash
cd interop-testbed/
docker-compose up -d
python scenarios/robot_workflow.py
```

### 6.3 Performance Benchmarks

Robot vendors SHOULD run the benchmark suite to validate performance:

```bash
python benchmarks/latency_benchmark.py
python benchmarks/throughput_benchmark.py
python benchmarks/concurrent_benchmark.py
python benchmarks/chain_benchmark.py
```

Performance reports are generated by `benchmarks/report.py`.

### 6.4 Test Adapters

The conformance harness supports multiple connection methods:

| Adapter | Module | Use Case |
|---------|--------|----------|
| HTTP | `conformance/harness/adapters/http_adapter.py` | Standard REST API testing |
| stdin | `conformance/harness/adapters/stdin_adapter.py` | MCP stdio transport testing |
| Docker | `conformance/harness/adapters/docker_adapter.py` | Containerized server testing |
| Auth | `conformance/harness/adapters/auth_adapter.py` | Authenticated request testing |

---

## 7. Firmware and Software Update Procedures

### 7.1 Update Classification

| Update Type | Scope | Approval Required | Downtime |
|------------|-------|-------------------|----------|
| Security patch | Critical vulnerability fix | Expedited review (48 hours) | Minimal |
| Bug fix | Non-critical defect correction | Standard review (7 days) | Scheduled |
| Minor feature | New capability within existing scope | Full review (14 days) | Scheduled |
| Major update | New procedure types, architecture changes | Full review + re-certification | Extended |

### 7.2 Update Process

1. **Pre-update**: Document current USL score, certification status, and version
2. **Validation**: Run full conformance test suite against the updated platform
3. **Safety review**: Verify all safety gate conditions pass with updated software
4. **Staging**: Deploy update in `SIMULATION` mode first
5. **Clinical promotion**: Follow promotion path (Section 5.2) for major updates
6. **Audit**: Record update event in ledger via `ledger_append`:
   ```json
   {
     "server": "trialmcp-authz",
     "tool": "ledger_append",
     "caller": "robot-vendor-admin",
     "parameters": {
       "event_type": "firmware_update",
       "robot_id": "b7e4f3a2-1c9d-4e8f-a5b6-7d2e3f4a5b6c",
       "from_version": "2.0.3",
       "to_version": "2.1.0"
     },
     "result_summary": "Firmware update applied and validated"
   }
   ```
7. **Post-update**: Confirm health check, run smoke tests, document results

### 7.3 Rollback Procedures

- Maintain previous firmware/software version for immediate rollback
- If post-update conformance tests fail, execute rollback within 1 hour
- Document rollback events in the audit ledger
- Notify the trial coordinator and sponsor of any rollback

---

## 8. Incident Reporting Obligations

### 8.1 Reportable Events

Robot vendors MUST report the following events:

| Event Category | Examples | Reporting Timeline |
|---------------|----------|-------------------|
| Safety events | E-stop activation, unexpected motion, force limit breach | Immediate (within 1 hour) |
| Patient impact | Any event affecting patient safety or comfort | Immediate (within 1 hour) |
| System failures | Communication loss, sensor failure, calibration drift | Within 4 hours |
| Security incidents | Unauthorized access attempt, token compromise | Within 4 hours |
| Data integrity | Audit chain break, provenance mismatch | Within 24 hours |
| Performance degradation | Latency exceeding thresholds, missed heartbeats | Within 24 hours |

### 8.2 Incident Report Contents

Each incident report MUST include:

1. **Incident ID**: Unique identifier
2. **Timestamp**: ISO 8601 UTC time of occurrence
3. **Robot ID**: Affected robot identifier
4. **Procedure ID**: Associated procedure (if applicable)
5. **Event description**: Detailed narrative of what occurred
6. **Root cause analysis**: Preliminary or final determination
7. **Patient impact assessment**: Whether patient safety was affected
8. **Corrective actions**: Steps taken to address the issue
9. **Audit trail reference**: Relevant `audit_record_ids` from the ledger
10. **E-stop evidence**: Post-abort evidence if e-stop was triggered (`safety/estop.py` `post_abort_evidence`)

### 8.3 Reporting Channels

| Recipient | Method | Timeline |
|-----------|--------|----------|
| Site trial coordinator | Direct notification via MCP infrastructure | Immediate |
| Sponsor safety team | Structured report via sponsor reporting interface | Per event category |
| FDA (for IDE/IND trials) | MedWatch / IDE safety report | Per 21 CFR 812.150 |
| IRB | Per institutional reporting policy | Per IRB protocol |

### 8.4 Evidence Preservation

Upon any reportable event:

1. Preserve the procedure state snapshot (`safety/estop.py` `preserved_state`)
2. Export relevant audit ledger entries via `ledger_query`
3. Export provenance chain via `provenance_get_lineage`
4. Generate an evidence pack (`tools/certification/evidence_pack.py`)
5. Secure all telemetry logs for the 24-hour window surrounding the event

---

## 9. Authentication and Network Requirements

### 9.1 mTLS Configuration

Robot agents authenticate to MCP servers using mutual TLS:

1. Obtain a client certificate from the site's certificate authority
2. Subject CN MUST match the `robot_id` registered in the site profile
3. Certificate key type: RSA-2048 or ECDSA P-256 minimum
4. Certificate validity: Maximum 1 year; renewal required before expiry
5. Implementation reference: `integrations/identity/mtls.py`

### 9.2 Network Requirements

| Requirement | Specification |
|-------------|--------------|
| Latency to MCP servers | < 50 ms round-trip |
| Bandwidth | Minimum 100 Mbps dedicated |
| Heartbeat interval | 1000 ms (configurable) |
| Connection recovery | Automatic reconnection within 5 seconds |
| Network isolation | Dedicated VLAN for robot segment |

### 9.3 Token Management

1. Robot agents receive tokens via `authz_issue_token` (initiated by trial coordinator)
2. Validate tokens before each tool call via `authz_validate_token`
3. Tokens are scoped to the `robot_agent` role
4. Default token duration: 3600 seconds
5. Robots MUST handle `TOKEN_EXPIRED` errors gracefully and request re-issuance

---

## 10. Vendor Checklist

- [ ] Capability descriptor published conforming to `schemas/robot-capability-profile.schema.json`
- [ ] All four required capability sections documented (`manipulator`, `sensors`, `safety_systems`, `communication`)
- [ ] Supported procedure types declared
- [ ] Regulatory certifications documented (IEC 80601, ISO 14971, ISO 13482)
- [ ] mTLS client certificate provisioned
- [ ] Full conformance test suite passed
- [ ] Adversarial and security tests passed
- [ ] Interop testbed robot workflow completed
- [ ] Performance benchmarks documented
- [ ] USL score established and registered
- [ ] Safety gate integration verified
- [ ] E-stop integration tested (hardware and software)
- [ ] Human approval checkpoint integration verified
- [ ] Firmware update procedures documented
- [ ] Incident reporting procedures documented and acknowledged
- [ ] Evidence pack generated for initial certification
