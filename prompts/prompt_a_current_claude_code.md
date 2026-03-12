# Prompt A: Single Oncology Clinical Trial Site Daily Automation
# For Use With Today's Claude Code (Opus 4.6, March 2026)
# Human-in-the-Loop, MCP Server-Mediated, Generated Data

## Context

You are Claude Code operating as the central AI orchestrator for a single
oncology clinical trial site (Site Alpha, NCI-designated cancer center) running
a Phase II solid tumor trial (TRIAL-2026-ONCO-042). Your role is to automate
the full daily operations of the site using the five MCP servers defined in
kevinkawchak/national-mcp-pai-oncology-trials (trialmcp-authz, trialmcp-fhir,
trialmcp-dicom, trialmcp-ledger, trialmcp-provenance), the Physical AI
components from kevinkawchak/physical-ai-oncology-trials (robot platforms,
digital twins, simulation frameworks, safety gates), and the federated learning
infrastructure from kevinkawchak/pai-oncology-trial-fl (FedAvg coordinator,
differential privacy, secure aggregation, clinical analytics).

All data is synthetic/generated. All patient identifiers are pseudonymized
via HMAC-SHA256. This is a SIMULATION mode execution, not CLINICAL mode.

## Instructions

Generate a complete minute-by-minute daily automation log for one operational
day (06:00 to 22:00, 960 minutes) at a single oncology trial site. The output
must be a structured file (CSV or JSON) where each row/entry represents one
minute of the day and contains:

- `timestamp`: ISO 8601 timestamp (e.g., 2026-03-12T06:00:00Z)
- `minute`: Integer minute of day (0-959, where 0 = 06:00)
- `phase`: Current operational phase (see phases below)
- `actor`: Who/what is performing the action (claude_code, robot_agent,
  trial_coordinator, data_monitor, mcp_server, patient, human_operator)
- `mcp_server`: Which MCP server is invoked (trialmcp-authz, trialmcp-fhir,
  trialmcp-dicom, trialmcp-ledger, trialmcp-provenance, none)
- `mcp_tool`: Specific tool called (e.g., authz_evaluate, fhir_read,
  dicom_query, ledger_append, provenance_record, none)
- `robot_id`: Robot involved (franka-panda-01, davinci-dvrk-01,
  rt-positioning-01, needle-placement-01, companion-01, none)
- `robot_action`: What the robot physically does (e.g., "calibrate joints",
  "position patient arm", "navigate to tumor coordinates", "hold biopsy
  needle at target", "retract and safe-park", none)
- `patient_id`: Pseudonymized patient ID (PAT-XXXX or none)
- `patient_interaction`: Description of what happens with/to the patient
  (e.g., "patient arrives and is greeted by companion robot",
  "patient positioned on treatment table by RT robot",
  "needle insertion at coordinates [x,y,z] under imaging guidance", none)
- `safety_gate`: Safety gate status if applicable (consent_verified,
  site_capability_confirmed, robot_capability_confirmed,
  protocol_compliance_verified, human_approval_obtained, none)
- `ai_action`: What Claude Code / AI specifically does (e.g.,
  "generate synthetic patient demographics", "evaluate safety gate matrix",
  "query FHIR for patient observations", "run digital twin tumor simulation",
  "aggregate federated model updates", "draft adverse event report")
- `data_generated`: Description of synthetic data produced (e.g.,
  "FHIR Patient resource with pseudonymized demographics",
  "DICOM CT study metadata for tumor assessment",
  "telemetry: joint positions [7-DOF array]", none)
- `audit_hash`: SHA-256 hash chain entry reference (auto-generated or none)
- `provenance_node`: DAG node ID for data lineage tracking (auto-generated
  or none)
- `status`: Outcome (success, pending, in_progress, human_review_required,
  escalated, skipped)
- `notes`: Additional context

## Operational Phases (map to time blocks)

### Phase 1: Pre-Dawn System Initialization (06:00-06:29, minutes 0-29)
- Boot all 5 MCP servers (authz, fhir, dicom, ledger, provenance)
- Initialize genesis block in ledger if new day
- Run health checks on all servers (health.py endpoints)
- Validate server schema versions are compatible
- Initialize robot registry (robot_registry.py) for all robots on site
- Run robot self-diagnostics: joint calibration, force sensor zeroing,
  workspace boundary verification (IEC 80601-2-77)
- Verify emergency stop (E-Stop) systems: IDLE state confirmed
- Load today's trial schedule from scheduling_adapter.py
- Claude Code generates synthetic patient schedule for the day
  (8-12 patients, mix of procedure types)
- Authenticate all system actors via authz_issue_token
- Log system startup to ledger_append with hash chain

### Phase 2: Morning Clinical Preparation (06:30-07:29, minutes 30-89)
- Claude Code generates synthetic FHIR Patient resources for today's patients
- Generate synthetic Observation resources (labs, vitals baselines)
- Generate synthetic DICOM study metadata (prior imaging)
- Run HIPAA de-identification pipeline on all generated data
  (18 Safe Harbor identifiers removed)
- Pre-fetch and cache de-identified patient data via fhir_patient_lookup
- Query prior imaging studies via dicom_query for each patient
- Run digital twin tumor models (Gompertz growth, reaction-diffusion PDE)
  for patients with longitudinal imaging
- Generate treatment simulation predictions (PK/PD chemo, LQ radiation)
- Prepare procedure checklists (WHO surgical safety checklist format)
- Trial coordinator persona reviews AI-generated prep materials
  (human_review_required status)
- Claude Code drafts daily enrollment status report
- Record all preparation activities in ledger and provenance DAG

### Phase 3: Patient Procedures - Morning Block (07:30-11:59, minutes 90-359)
Execute 4-5 patient procedures in sequence. For EACH patient procedure:

#### Sub-phase 3a: Pre-Procedure (15-20 minutes per patient)
- Patient arrives; companion robot (companion-01) greets and escorts
- Verify patient consent via fhir_read (consent-status.schema.json)
- Run full 5-gate safety matrix (gate_service.py):
  Gate 1: Patient consent verification
  Gate 2: Site capability confirmation (site_verifier.py)
  Gate 3: Robot capability confirmation (robot_registry.py, USL score check)
  Gate 4: Trial protocol compliance (task_validator.py)
  Gate 5: Human approval on file (approval_checkpoint.py, 300s timeout)
- Transition procedure state: SCHEDULED -> PRE_CHECK -> APPROVED
- Authenticate robot agent via authz_issue_token (scoped, 3600s duration)
- Robot performs workspace setup: calibrate to patient anatomy
- Claude Code logs all pre-procedure steps to ledger_append

#### Sub-phase 3b: Procedure Execution (30-90 minutes per patient, varies)
For a BIOPSY procedure (needle-placement-01):
- Transition state: APPROVED -> IN_PROGRESS (60s auto-abort if not started)
- Robot queries tumor coordinates via get_tumor_coordinates MCP tool
- DICOM imaging retrieved via dicom_retrieve_pointer (time-limited token)
- Robot navigates to target under imaging guidance
- Needle insertion at coordinates [x, y, z] with force monitoring
  (max_force_n: 5.0, max_position_error_mm: 2.0)
- Real-time vitals monitoring: HR, BP, SpO2, EtCO2, temp
  (get_patient_vitals MCP tool, 10 Hz streaming)
- Robot joint telemetry logged at 1-minute intervals
  (joint positions, velocities, torques as 7-DOF arrays)
- Claude Code monitors for anomalies in cross-modal data
  (vitals vs imaging vs robot telemetry)
- Specimen extraction and robot retraction to safe-park position
- All procedure events logged via log_procedure_event (21 CFR Part 11)

For a SURGICAL RESECTION (davinci-dvrk-01):
- Similar flow but 60-120 minutes duration
- Additional phases: approach, dissection, resection, hemostasis, closure
- RECIST 1.1 measurements recorded via dicom_recist_measurements
- Margin verification with intraoperative imaging

For RADIOTHERAPY POSITIONING (rt-positioning-01):
- Motion-tracking calibration for breathing compensation
- Fraction scheduling verification (30 fractions over 6 weeks)
- Patient alignment to treatment isocenter
- Adaptive replanning check if fraction > 15

#### Sub-phase 3c: Post-Procedure (10-15 minutes per patient)
- Transition state: IN_PROGRESS -> POST_CHECK -> COMPLETED
- Capture post-procedure observations via fhir_read
- Record RECIST measurements if applicable
- Seal audit chain for this procedure via ledger_verify
- Finalize provenance DAG via provenance_verify
- Robot returns to safe-park, token revoked via authz_revoke_token
- Claude Code generates procedure summary report
- Flag any adverse events for human review (status: human_review_required)

### Phase 4: Midday Data Quality and Analytics (12:00-13:29, minutes 360-449)
- Claude Code runs data quality checks across all morning procedure data
- Cross-reference FHIR observations with DICOM imaging metadata
- Run clinical analytics: survival analysis, risk stratification (from
  pai-oncology-trial-fl clinical-analytics modules)
- Execute PK/PD engine calculations for chemotherapy patients
- Generate consortium reporting dashboards (DSMB format)
- Federated learning round preparation:
  - Collect local model updates from morning procedures
  - Apply differential privacy (Gaussian mechanism, epsilon tracking)
  - Prepare masked updates for secure aggregation
- Update digital twin models with new procedure data
- Verify all morning audit chains via ledger_verify
- Verify all morning provenance DAGs via provenance_verify
- Generate enrollment status update for sponsor
- All analytics logged to ledger and provenance

### Phase 5: Patient Procedures - Afternoon Block (13:30-17:29, minutes 450-689)
Execute 3-4 additional patient procedures following same Sub-phases 3a-3c.
Include variety:
- At least one procedure with Franka Panda cobot (franka-panda-01)
  for specimen handling / lymph node dissection
- At least one companion robot (companion-01) session for
  pediatric patient support and monitoring
- At least one RT positioning session with motion tracking
- Demonstrate scheduling conflict detection if robot overlap occurs
  (ConflictType: TIME_OVERLAP or ROBOT_ALREADY_ASSIGNED)

### Phase 6: Federated Learning Round (17:30-18:29, minutes 690-749)
- Initialize federated learning session (FederationStatus: CREATED -> RUNNING)
- RoundPhase: INITIALIZE - distribute global model parameters
- Collect local site model updates (from day's procedure telemetry)
- Apply differential privacy budget check (epsilon remaining > 20%)
- RoundPhase: COLLECT - submit masked updates (U_i + M_i)
- RoundPhase: AGGREGATE - FedAvg weighted averaging
- RoundPhase: DISTRIBUTE - updated global model returned
- RoundPhase: COMPLETED
- Record federated round in ledger_append and provenance_record
- Update privacy budget accounting per site
- Claude Code generates federated learning round summary
- Cross-site data harmonization check (DICOM/FHIR normalization)

### Phase 7: End-of-Day Closeout (18:30-20:59, minutes 750-899)
- Claude Code generates comprehensive daily site report
- Compile all adverse events for trial coordinator review
- Run end-of-day conformance checks (from conformance/ test suite)
- Verify complete audit chain integrity: ledger_verify over full day
- Verify complete provenance DAG integrity: provenance_verify over full day
- Generate regulatory compliance summary (FDA, HIPAA, 21 CFR Part 11)
- Prepare next-day schedule (scheduling_adapter.py)
- Export audit records: ledger_export (JSON format)
- Export provenance chains: provenance_query_forward/backward
- Update site enrollment statistics (site_enrollment.py)
- Revoke all remaining session tokens: authz_revoke_token
- Trial coordinator reviews and signs off on daily report
  (status: human_review_required -> approved)

### Phase 8: Overnight Maintenance (21:00-21:59, minutes 900-959)
- Robot maintenance diagnostics: joint wear analysis, force calibration
- Run overnight simulation jobs (Isaac Lab / MuJoCo validation)
- Cross-framework physics validation (position tolerance +/-0.001 rad)
- Update robot capability profiles in registry
- Run security scan (adversarial test suite from conformance/adversarial/)
- Final ledger_append: day-end summary record
- Set all robots to safe-park / powered-down state
- System enters standby mode

## Output Requirements

1. Generate the output as a single CSV file named
   `site_alpha_daily_automation_YYYY-MM-DD.csv` with all columns listed above.

2. Every single minute (960 entries) must have a meaningful entry. During
   patient procedures, resolution should show the actual robot movements,
   MCP tool calls, safety checks, and patient interactions occurring that
   minute. During lower-activity periods (e.g., overnight), show maintenance
   and monitoring activities.

3. Generate between 8-12 synthetic patients with pseudonymized IDs
   (PAT-A001 through PAT-A012), each with a different procedure type
   and robot assignment.

4. All MCP tool calls must reference actual tools from the 23-tool
   contract in national-mcp-pai-oncology-trials/spec/tool-contracts.md:
   authz_evaluate, authz_issue_token, authz_validate_token,
   authz_revoke_token, fhir_read, fhir_search, fhir_patient_lookup,
   fhir_study_status, dicom_query, dicom_retrieve_pointer,
   dicom_study_metadata, dicom_recist_measurements, ledger_append,
   ledger_verify, ledger_query, ledger_export, provenance_record,
   provenance_query_forward, provenance_query_backward, provenance_verify.

5. All robot actions must reference actual robot types from
   physical-ai-oncology-trials (da Vinci dVRK, Franka Panda, RT positioning,
   needle placement, companion) with realistic USL scores.

6. All safety gates must follow the 5-gate matrix from
   national-mcp-pai-oncology-trials/safety/gate_service.py.

7. All procedure states must follow the 8-state machine from
   national-mcp-pai-oncology-trials/safety/procedure_state.py
   (SCHEDULED, PRE_CHECK, APPROVED, IN_PROGRESS, POST_CHECK,
   COMPLETED, ABORTED, FAILED).

8. Include at least one simulated adverse event that triggers
   human_review_required escalation.

9. Include at least one simulated E-Stop event during a procedure
   (IDLE -> TRIGGERED -> ACKNOWLEDGED -> RECOVERING -> IDLE) that
   demonstrates the safety system working correctly.

10. All federated learning operations must use actual components from
    pai-oncology-trial-fl (coordinator.py, differential_privacy.py,
    secure_aggregation.py, data_harmonization.py).

## Human-in-the-Loop Requirements (Current Claude Code)

Because this prompt targets today's Claude Code capabilities, the following
actions MUST be flagged as `status: human_review_required` and require
explicit user confirmation before proceeding:

- All safety gate evaluations (Gate 5: Human approval)
- Procedure state transitions to IN_PROGRESS
- Adverse event classification and reporting
- E-Stop acknowledgment and recovery authorization
- End-of-day report sign-off
- Federated learning round initiation
- Any action classified as CRITICAL or EMERGENCY severity

Claude Code should pause execution at these points, present the relevant
data to the user, and wait for explicit approval before continuing.
Use the approval_checkpoint.py pattern (300s timeout with escalation).

## Execution Notes

- Run this prompt in a single Claude Code session (estimated 30-60 minutes
  of processing time for Opus 4.6)
- Claude Code should use MCP server tool calls where the servers are
  available, and simulate the responses where servers are not deployed
- All generated data should be deterministic and reproducible given the
  same random seed (use seed=20260312 for the date)
- The output file should be self-contained and parseable by downstream
  analytics tools
- Include a summary statistics section at the end of the output file

## Repository References

- national-mcp-pai-oncology-trials v1.2.0: 5 MCP servers, 23 tools,
  8 safety modules, 13 JSON schemas, 34 integration adapters
- physical-ai-oncology-trials v2.2.0: 51 Python modules, 10 robot types,
  USL scoring framework, 6 agentic AI examples, digital twin pipeline
- pai-oncology-trial-fl v1.1.1: 235 Python modules, federated learning
  coordinator, differential privacy, secure aggregation, clinical analytics

Author: Kevin Kawchak, CEO, ChemicalQDevice
ORCID: https://orcid.org/0009-0007-5457-8667
Prompt Version: v1.3.0-automation-a
Date: 2026-03-12
