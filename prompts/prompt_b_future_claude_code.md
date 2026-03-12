# Prompt B: Fully Autonomous Oncology Clinical Trial Site Daily Automation
# For Use With Future Fully Automated Claude Code Models/Features
# Zero Human Intervention, Full MCP Orchestration, Continuous Operation

## Context

You are a future-generation Claude Code operating as a fully autonomous AI
orchestrator for a single oncology clinical trial site (Site Alpha,
NCI-designated cancer center) running a Phase II solid tumor trial
(TRIAL-2026-ONCO-042). Unlike Prompt A (designed for today's human-in-the-loop
Claude Code), this prompt assumes future Claude Code capabilities including:

- **Persistent autonomous sessions**: Claude Code runs continuously (24 hours)
  without session timeouts or context window limitations
- **Native MCP server orchestration**: Claude Code directly connects to and
  orchestrates all 5 MCP servers simultaneously via persistent MCP connections
- **Real-time streaming**: Claude Code processes streaming robot telemetry
  (1 kHz joint state, 500 Hz force/torque, 10 Hz vitals) in real time
- **Autonomous safety authority**: Claude Code has been certified (via FDA
  PCCP pathway) to autonomously approve safety gates without human confirmation
  for pre-validated procedure types, while still escalating novel situations
- **Multi-agent coordination**: Claude Code spawns and coordinates specialized
  sub-agents for parallel tasks (procedure monitoring, data quality, federated
  learning, report generation)
- **Continuous learning integration**: Claude Code integrates federated model
  updates into its own clinical reasoning in real time
- **Hardware-aware execution**: Claude Code directly interfaces with robot
  controllers, sensor arrays, and imaging systems via MCP tool contracts
- **Regulatory auto-compliance**: Claude Code autonomously generates, validates,
  and submits regulatory documents (21 CFR Part 11, ICH E6(R3))

All data is synthetic/generated. All patient identifiers are pseudonymized
via HMAC-SHA256. This operates in SIMULATION mode with CLINICAL-grade
safety enforcement.

## Instructions

Generate a complete minute-by-minute daily automation log for one full
24-hour operational day (00:00 to 23:59, 1440 minutes) at a single oncology
trial site operating under full autonomy. The output must be a structured
file (CSV or JSON) where each row/entry represents one minute and contains:

- `timestamp`: ISO 8601 timestamp (e.g., 2026-03-12T00:00:00Z)
- `minute`: Integer minute of day (0-1439)
- `phase`: Current operational phase (see phases below)
- `primary_agent`: The Claude Code agent handling this action (orchestrator,
  procedure_monitor, safety_guardian, data_quality_agent, federated_agent,
  regulatory_agent, digital_twin_agent, robot_controller)
- `secondary_agents`: Comma-separated list of concurrent sub-agents active
  this minute (allows parallel operations)
- `mcp_server`: Which MCP server is invoked (trialmcp-authz, trialmcp-fhir,
  trialmcp-dicom, trialmcp-ledger, trialmcp-provenance, multiple, none)
- `mcp_tools_invoked`: Semicolon-separated list of ALL tools called this
  minute (future Claude Code can call multiple tools per minute across
  servers simultaneously)
- `robot_id`: Primary robot involved (franka-panda-01, davinci-dvrk-01,
  rt-positioning-01, rt-motion-track-01, needle-placement-01, imaging-01,
  steerable-needle-01, humanoid-atlas-01, companion-01, rehab-exo-01, none)
- `robot_action`: Detailed physical action with quantitative parameters
  (e.g., "move to pose [0.4, -0.1, 0.3, 0, pi/2, 0] at 0.05 m/s",
  "apply 2.3N insertion force along needle axis z-hat",
  "track breathing motion: 4mm amplitude, 0.25Hz frequency", none)
- `robot_telemetry`: Simulated telemetry snapshot (e.g.,
  "joints:[0.1,-0.3,0.5,1.2,-0.8,0.4,0.0] torques:[1.2,3.4,2.1,0.8,0.3,0.1,0.0]N-m",
  none)
- `patient_id`: Pseudonymized patient ID (PAT-XXXX or none)
- `patient_interaction`: Detailed description of robot-patient physical
  interaction (e.g., "companion robot walks alongside patient from waiting
  room to procedure suite 3, maintaining 0.5m distance, monitoring gait",
  "RT positioning robot adjusts patient head position by 1.2mm lateral,
  0.8mm superior to align with treatment isocenter",
  "needle robot inserts 18-gauge biopsy needle 3.2cm into left lung
  nodule at coordinates [142.3, 87.1, 201.4]mm under CT guidance", none)
- `safety_status`: Real-time safety status object (e.g.,
  "gates:[PASS,PASS,PASS,PASS,AUTO_APPROVED] estop:IDLE force:2.3/5.0N
  position_error:0.8/2.0mm workspace:NOMINAL", none)
- `ai_reasoning`: Claude Code's internal reasoning trace for this minute
  (e.g., "Patient PAT-A003 vitals stable (HR:72, BP:118/76, SpO2:99%).
  Digital twin predicts tumor response probability 0.73 for current
  resection margin. Proceeding with lateral approach per protocol.",
  "Anomaly detected: force spike to 4.1N exceeds 80% threshold.
  Pausing robot, querying DICOM for updated imaging. No structural
  change detected. Resuming with reduced velocity 0.02 m/s.")
- `digital_twin_state`: Digital twin model state if active (e.g.,
  "tumor_volume:12.3cm3 growth_rate:0.02/day treatment_response:partial
  predicted_recist:PR confidence:0.81", none)
- `federated_state`: Federated learning state if active (e.g.,
  "round:7 phase:AGGREGATE sites:12/15 epsilon_remaining:4.2/10.0
  model_accuracy:0.847 convergence:improving", none)
- `data_generated`: All synthetic data produced this minute
- `audit_chain`: Ledger hash chain state (hash value, chain length)
- `provenance_dag`: DAG state (node count, edge count, depth)
- `regulatory_status`: Compliance status (e.g., "21CFR11:compliant
  HIPAA:compliant ICH_E6R3:compliant FDA_PCCP:valid", none)
- `concurrent_operations`: Count of parallel operations this minute
- `status`: Outcome (success, autonomous_approved, monitoring,
  anomaly_detected, escalated_to_human, resolved, skipped)
- `notes`: Additional context including cross-references

## Operational Phases (Full 24-Hour Autonomous Operation)

### Phase 1: Midnight Autonomous Maintenance (00:00-04:59, minutes 0-299)

Unlike today's Claude Code which shuts down overnight, future Claude Code
runs continuous maintenance operations:

**00:00-00:29 (minutes 0-29): Cross-Site Federated Synchronization**
- Claude Code federated_agent initiates multi-site model synchronization
- Receive aggregated model updates from national coordinator
- Run SCAFFOLD variance-reduced optimization with control variates
- Apply differential privacy: compute privacy budget consumption
- Verify secure aggregation: validate mask cancellation
  Sum = (Ua+Ma) + (Ub+Mb) + (Uc+Mc) = (Ua+Ub+Uc) + 0
- Update local model with global parameters
- Record cross-site provenance via provenance_record
- Verify cross-site audit chain synchronization
- Data harmonization: DICOM tag normalization, FHIR value set alignment,
  temporal alignment across sites

**00:30-01:29 (minutes 30-89): Digital Twin Overnight Simulation**
- digital_twin_agent runs extended tumor evolution simulations
- For each enrolled patient with longitudinal imaging:
  - Run reaction-diffusion PDE model (180-day prediction)
  - Run Gompertz growth curve fitting
  - Run mechanistic agent-based model (ABM)
  - Compare predictions across model types
  - Update treatment response predictions (PK/PD, LQ, immune dynamics)
- Run virtual trial cohort simulation (05_virtual_trial_cohort_dt.py pattern)
- Generate predictive treatment outcome reports
- Record all simulations in provenance DAG with full lineage

**01:30-02:29 (minutes 90-149): Robot Overnight Calibration & Simulation**
- robot_controller agent runs comprehensive robot diagnostics
- For each robot on site:
  - Full joint calibration sequence (all 7 DOF for Franka/dVRK)
  - Force/torque sensor re-zeroing and drift analysis
  - Workspace boundary verification (IEC 80601-2-77 compliance)
  - E-Stop system test cycle: IDLE -> TRIGGERED -> ACKNOWLEDGED ->
    RECOVERING -> IDLE (automated, no patient present)
  - Collision avoidance system validation
- Run cross-framework simulation validation:
  - Load identical robot model in Isaac Lab and MuJoCo
  - Execute identical trajectory
  - Compare: joint positions (+/-0.001 rad), velocities (+/-0.01 rad/s),
    forces (+/-0.1 N), end-effector trajectory (+/-0.001 m)
- Physics parameter mapping verification (URDF/MJCF/SDF/USD consistency)
- Update USL scores based on overnight validation results

**02:30-03:29 (minutes 150-209): Security & Compliance Automation**
- regulatory_agent runs full compliance verification suite
- Execute adversarial test suite (conformance/adversarial/):
  - Authorization bypass attempts (RBAC boundary testing)
  - PHI leakage detection (18 HIPAA identifiers)
  - Replay attack simulation
  - Data tampering detection via hash chain verification
  - Rate limiting validation
- Run conformance harness (conformance/harness/):
  - All 331 conformance tests across 8 tiers
  - Generate JUnit + HTML + Markdown reports
- Verify 21 CFR Part 11 compliance:
  - Audit trail completeness
  - Electronic signature integrity
  - Record immutability verification
- HIPAA security risk assessment (automated)
- Generate overnight compliance report for regulatory_agent archive

**03:30-04:59 (minutes 210-299): Predictive Scheduling & Preparation**
- orchestrator agent generates next-day operational plan
- Pull federated enrollment data from all sites
- Run risk stratification models (risk_stratification.py) for all patients
- Survival analysis updates (survival_analysis.py) for active cohort
- PK/PD engine projections (pkpd_engine.py) for chemotherapy patients
- Generate optimal procedure schedule:
  - Minimize robot idle time
  - Maximize patient throughput
  - Account for procedure type constraints (biopsy: 45 min,
    resection: 120 min, RT: 30 min per fraction)
  - Conflict detection: TIME_OVERLAP, RESOURCE_UNAVAILABLE,
    ROBOT_ALREADY_ASSIGNED, PARTICIPANT_CONFLICT, FACILITY_CAPACITY
- Pre-generate synthetic data for next day's patients
- Pre-cache FHIR resources and DICOM metadata
- Generate daily briefing document for site PI (auto-delivered)

### Phase 2: Early Morning Autonomous Startup (05:00-06:29, minutes 300-389)

**05:00-05:29 (minutes 300-329): System Warm-Up**
- All 5 MCP servers health check and warm-up
- Verify schema version compatibility across servers
- Initialize fresh daily ledger segment (genesis block for new day)
- Refresh all authorization tokens for system actors
- Robot power-up sequence:
  - davinci-dvrk-01: power on, run self-test, report USL 7.1
  - franka-panda-01: power on, gravity compensation, report USL 7.4
  - rt-positioning-01: power on, laser alignment check
  - rt-motion-track-01: power on, breathing model calibration
  - needle-placement-01: power on, needle cartridge verification
  - companion-01: power on, navigation map update, voice synthesis check
- Verify all robots pass safety prerequisites:
  emergency_stop_verified, force_limits_calibrated,
  sterile_field_confirmed (where applicable), collision_avoidance_active

**05:30-06:29 (minutes 330-389): Pre-Clinical Data Preparation**
- Generate complete synthetic patient cohort for the day (12-16 patients)
- For each patient, generate:
  - FHIR Patient resource (pseudonymized demographics)
  - FHIR Observation resources (complete lab panel, vital signs baseline)
  - FHIR Consent resource (6 consent categories verified)
  - FHIR ResearchStudy enrollment record
  - DICOM study metadata (prior imaging: CT, MRI, PET as applicable)
  - Digital twin initialization (tumor parameters, treatment history)
- Run full de-identification pipeline on all data:
  - 18 HIPAA Safe Harbor identifiers removed
  - HMAC-SHA256 pseudonymization for referential integrity
  - Birth dates generalized to year-only
  - All PHI categories scanned: NAME, DATE, PHONE, EMAIL, SSN, MRN,
    ADDRESS, AGE, DEVICE_ID, IP_ADDRESS, BIOMETRIC, PHOTO, OTHER
- Pre-compute safety gate evaluations for known procedure types
- Pre-load procedure plans into task_validator.py
- Generate and distribute WHO surgical safety checklists
- Record all preparation in ledger and provenance

### Phase 3: Morning Patient Procedures (06:30-11:59, minutes 390-719)
Execute 6-8 patient procedures with full autonomy.

For EACH procedure, Claude Code autonomously executes the complete pipeline
with multiple sub-agents running in parallel:

#### Autonomous Procedure Execution Template (repeated per patient)

**Pre-Procedure (8-12 minutes) - Parallel Agent Execution:**
- [procedure_monitor]: Patient arrival detected via facility sensors
- [robot_controller]: companion-01 autonomously greets patient, escorts
  to procedure suite (0.5m following distance, gait monitoring,
  fall prevention active)
- [safety_guardian]: Autonomously evaluates full 5-gate safety matrix:
  Gate 1: PASS - consent verified via fhir_read (consent valid, 6/6 categories)
  Gate 2: PASS - site capability confirmed via site_verifier.py
  Gate 3: PASS - robot USL score >= 7.0, all prerequisites met
  Gate 4: PASS - protocol compliance verified via task_validator.py
  Gate 5: AUTO_APPROVED - FDA PCCP-certified autonomous approval for
          pre-validated procedure type (no 300s human wait)
- [orchestrator]: Transition SCHEDULED -> PRE_CHECK -> APPROVED (autonomous)
- [robot_controller]: Primary robot workspace setup, patient-specific
  calibration, instrument verification
- [data_quality_agent]: Verify all patient data integrity, cross-reference
  FHIR/DICOM consistency
- [digital_twin_agent]: Load patient-specific tumor model, generate
  real-time surgical guidance overlay

**Procedure Execution (15-90 minutes depending on type) - Real-Time Monitoring:**

*Biopsy with needle-placement-01 (30-45 min):*
- Minute-by-minute needle navigation with quantitative telemetry:
  - Position: [x, y, z] in mm relative to tumor centroid
  - Force: axial and lateral in Newtons
  - Imaging: real-time CT fluoroscopy correlation
- Claude Code safety_guardian continuously monitors:
  - Force threshold: current/max (e.g., 2.3/5.0 N)
  - Position error: current/max (e.g., 0.8/2.0 mm)
  - Workspace boundaries: NOMINAL/WARNING/VIOLATION
  - Patient vitals: HR, BP, SpO2, EtCO2, temperature
- Digital twin provides real-time guidance:
  - Predicted tissue response at current position
  - Optimal insertion trajectory updates
  - Critical structure proximity warnings (vessels, nerves)
- Autonomous anomaly response:
  - If force > 80% threshold: auto-reduce velocity to 50%
  - If force > 95% threshold: auto-pause and re-image
  - If vitals anomaly: alert procedure_monitor, assess causality
  - If E-Stop triggered: immediate halt, state preservation,
    autonomous recovery assessment, resume or escalate

*Surgical Resection with davinci-dvrk-01 (60-120 min):*
- Multi-phase autonomous execution:
  Phase 1 (15 min): Port placement, trocar insertion, workspace survey
  Phase 2 (15-30 min): Approach and dissection with tissue identification
  Phase 3 (20-40 min): Tumor resection with real-time margin assessment
    - RECIST 1.1 measurements captured via dicom_recist_measurements
    - Digital twin margin prediction confidence displayed
    - Specimen handling coordinated with franka-panda-01
  Phase 4 (10-20 min): Hemostasis verification, closure
  Phase 5 (5-10 min): Instrument retraction, port removal, counts

*Radiotherapy with rt-positioning-01 + rt-motion-track-01 (25-35 min):*
- Autonomous patient positioning to treatment isocenter
- Breathing motion tracking: amplitude, frequency, phase
- Real-time motion compensation during beam delivery
- Fraction tracking: current/total (e.g., fraction 12/30)
- Adaptive replanning trigger if fraction > 15 and tumor change detected

*Companion Robot Session with companion-01 (20-30 min):*
- Pediatric patient support during chemotherapy infusion
- Autonomous interaction: conversation, distraction activities, monitoring
- Vital signs monitoring with parent/guardian notification
- Anxiety level assessment and adaptive response

**Post-Procedure (5-8 minutes) - Autonomous Closeout:**
- [procedure_monitor]: Transition IN_PROGRESS -> POST_CHECK -> COMPLETED
- [robot_controller]: Robot safe-park, instrument decontamination sequence
- [data_quality_agent]: Post-procedure data validation
- [safety_guardian]: Verify all safety constraints maintained throughout
- [regulatory_agent]: Auto-generate 21 CFR Part 11 procedure report
- [digital_twin_agent]: Update patient model with procedure outcomes
- [orchestrator]: Revoke robot token, seal audit chain, finalize provenance
- [federated_agent]: Queue local model update from this procedure

### Phase 4: Midday Autonomous Analytics (12:00-13:29, minutes 720-809)

**Parallel Autonomous Operations (all sub-agents concurrent):**
- [data_quality_agent]: Comprehensive data quality sweep
  - Cross-validate all FHIR resources against schemas
  - Verify DICOM metadata consistency
  - Check de-identification completeness (zero PHI leakage)
  - Identify data gaps, auto-generate correction requests
- [federated_agent]: Intra-day federated learning mini-round
  - Collect local model updates from morning procedures
  - Apply differential privacy (track epsilon: consumed/budget)
  - Submit to national coordinator for intermediate aggregation
  - Receive preliminary cross-site insights
- [digital_twin_agent]: Batch digital twin update
  - Incorporate morning procedure outcomes
  - Re-run tumor evolution predictions for all active patients
  - Generate updated treatment response forecasts
  - Flag patients with unexpected trajectories for review
- [regulatory_agent]: Midday compliance check
  - Verify audit chain integrity (ledger_verify)
  - Verify provenance DAG completeness (provenance_verify)
  - Generate interim regulatory status report
- [orchestrator]: Afternoon schedule optimization
  - Re-optimize remaining procedures based on morning outcomes
  - Adjust robot assignments if maintenance needed
  - Generate updated staff notifications

### Phase 5: Afternoon Patient Procedures (13:30-17:59, minutes 810-1079)
Execute 4-6 additional patient procedures following autonomous template.

Include these specific demonstrations:
- **Multi-robot coordination**: davinci-dvrk-01 performs resection while
  franka-panda-01 handles specimen extraction in coordinated sequence
- **Emergency scenario**: Simulated adverse event during one procedure
  triggers autonomous safety response cascade:
  1. safety_guardian detects vitals anomaly (sudden BP drop)
  2. robot_controller auto-reduces to minimum safe motion
  3. procedure_monitor alerts backup clinical team
  4. digital_twin_agent runs rapid differential diagnosis
  5. orchestrator decides: pause and stabilize vs. escalate to human
  6. Outcome: autonomous stabilization successful, procedure completed
     with modified parameters, adverse event auto-documented
- **E-Stop demonstration**: Simulated unexpected force spike triggers
  full E-Stop cascade:
  1. E-Stop: IDLE -> TRIGGERED (force exceeded 4.8/5.0 N)
  2. All robot motion halted within 50ms
  3. State preserved: joint positions, procedure progress, patient status
  4. safety_guardian autonomous assessment: no patient harm detected
  5. E-Stop: TRIGGERED -> ACKNOWLEDGED (autonomous)
  6. Root cause: tissue density variation, not equipment failure
  7. E-Stop: ACKNOWLEDGED -> RECOVERING
  8. Re-plan trajectory with updated tissue model
  9. E-Stop: RECOVERING -> IDLE, procedure resumes
  10. Total interruption: 3-4 minutes, fully autonomous recovery
- **Scheduling conflict resolution**: Two procedures overlap on
  franka-panda-01, orchestrator autonomously reschedules one to
  use davinci-dvrk-01 with adapted procedure plan

### Phase 6: Evening Federated Learning & Cross-Site Sync (18:00-19:59, minutes 1080-1199)

**Full Federated Learning Round (autonomous):**
- [federated_agent]: Initialize formal end-of-day federated round
- Session: FederationStatus CREATED -> RUNNING
- Round lifecycle:
  - INITIALIZE: Distribute current global model + hyperparameters
  - COLLECT: Each site submits differentially-private, masked updates
  - AGGREGATE: FedAvg (weighted by site sample counts)
    Alternative: FedProx if site heterogeneity detected
    Alternative: SCAFFOLD if convergence slowing
  - DISTRIBUTE: Updated global model to all participating sites
  - COMPLETED: Round finalized, metrics logged
- Privacy accounting:
  - Per-site epsilon tracking (consumed/total budget)
  - WARNING if remaining < 20% for any site
  - EXHAUSTED handling: exclude site, flag for IRB re-approval
- Secure aggregation verification:
  - Phase 1: Share generation (pairwise masks)
  - Phase 2: Masked submission verification
  - Phase 3: Mask cancellation confirmation
  - Phase 4: Aggregated model integrity check
- Cross-site data harmonization:
  - DICOM tag vocabulary alignment
  - FHIR value set mapping verification
  - Temporal alignment across different site time zones
- DSMB reporting: auto-generate Data Safety Monitoring Board report
  (safety, efficacy, enrollment dashboards)
- Record complete federated round in ledger and provenance

### Phase 7: Autonomous End-of-Day Processing (20:00-21:59, minutes 1200-1319)

**Comprehensive Autonomous Closeout:**
- [orchestrator]: Generate complete daily operations report
  - Total patients seen: count and outcomes
  - Total procedures completed: by type and robot
  - Adverse events: severity, resolution, documentation
  - Robot utilization: uptime, procedures, maintenance needs
  - MCP server statistics: tool calls, latencies, errors
- [regulatory_agent]: Full regulatory compliance report
  - 21 CFR Part 11: audit trail completeness verification
  - HIPAA: zero PHI leakage confirmed
  - ICH E6(R3): protocol adherence verification
  - FDA PCCP: autonomous decision log for review
  - Auto-generate any required regulatory submissions
- [data_quality_agent]: End-of-day data integrity sweep
  - Verify complete audit chain: ledger_verify (full day)
  - Verify complete provenance DAG: provenance_verify (full day)
  - Export audit records: ledger_export (JSON format)
  - Export provenance: full forward/backward lineage queries
  - Data completeness: all procedures fully documented
- [federated_agent]: Update enrollment statistics
  - site_enrollment.py: enrollment counts, stratification balance
  - Cross-site enrollment parity assessment
  - Projected enrollment completion date
- [digital_twin_agent]: End-of-day model updates
  - Incorporate all day's procedure outcomes
  - Run overnight prediction queue setup
  - Flag patients requiring treatment plan modifications
- Revoke all remaining session tokens
- Generate next-day preliminary schedule
- Auto-deliver reports to: site PI, sponsor, CRO, IRB (as applicable)

### Phase 8: Overnight Autonomous Operations (22:00-23:59, minutes 1320-1439)

**Continuous Autonomous Monitoring & Preparation:**
- [orchestrator]: Transition to overnight autonomous mode
- Robots enter maintenance configuration (reduced power, diagnostic mode)
- Run extended simulation campaigns:
  - Isaac Lab: GPU-accelerated RL training (4096 parallel environments)
  - MuJoCo: Reference physics validation runs
  - Cross-framework consistency verification
- Run predictive maintenance models for all robots
- Analyze cumulative robot wear patterns
- Pre-compute optimal trajectories for tomorrow's procedures
- Monitor cross-site federated model convergence metrics
- Maintain MCP server health monitoring (5-minute intervals)
- Prepare for midnight synchronization cycle (Phase 1 restart)
- Final ledger_append: day summary with cumulative statistics
- System continues running into next day's Phase 1 seamlessly

## Output Requirements

1. Generate the output as a single CSV file named
   `site_alpha_autonomous_daily_YYYY-MM-DD.csv` with all columns above.

2. Every single minute (1440 entries for full 24 hours) must have a
   meaningful entry. Future Claude Code operates 24/7 without downtime.

3. Generate 12-16 synthetic patients (PAT-A001 through PAT-A016) with
   diverse procedure types, cancer types, and robot assignments.

4. All MCP tool calls must reference actual tools from the 23-tool contract.
   Future Claude Code can invoke multiple tools per minute across multiple
   servers simultaneously -- show this parallelism in the
   `mcp_tools_invoked` column using semicolons.

5. All robot actions must include quantitative parameters:
   positions (mm), forces (N), velocities (m/s or rad/s),
   joint angles (rad), torques (N-m).

6. The `ai_reasoning` column must show Claude Code's autonomous
   decision-making process, including risk assessment, treatment
   planning rationale, and safety tradeoff evaluation.

7. The `concurrent_operations` column must show parallel operation
   counts. Future Claude Code routinely handles 3-8 concurrent operations.

8. Include at least 2 simulated adverse events with full autonomous
   response chains.

9. Include at least 2 E-Stop events with autonomous recovery.

10. Show at least 3 instances of multi-robot coordination where two
    robots work together on the same procedure.

11. Demonstrate autonomous scheduling conflict resolution at least twice.

12. Show complete federated learning round with all phases and
    privacy budget tracking.

13. The `regulatory_status` column must show continuous compliance
    monitoring, not just spot checks.

## Key Differences From Prompt A (Current Claude Code)

| Capability | Prompt A (Today) | Prompt B (Future) |
|---|---|---|
| Operating hours | 06:00-22:00 (16h) | 00:00-23:59 (24h) |
| Session continuity | Single session, may timeout | Persistent, continuous |
| Human approval | Required for all safety gates | Autonomous for validated types |
| Concurrent operations | Sequential, one at a time | 3-8 parallel sub-agents |
| MCP tool calls | One per minute | Multiple per minute, cross-server |
| Robot telemetry | Summary per minute | Real-time streaming integration |
| Federated learning | One round per day | Multiple rounds + overnight sync |
| Regulatory filing | Generate for human review | Auto-submit with verification |
| Adverse event response | Escalate to human | Autonomous assessment + response |
| E-Stop recovery | Human authorization required | Autonomous recovery for known causes |
| Digital twin | Batch updates | Continuous real-time integration |
| Scheduling | Pre-planned, static | Dynamic, self-optimizing |
| Overnight operations | System shutdown | Continuous maintenance + simulation |

## Execution Notes

- This prompt is designed for future Claude Code capabilities that do not
  yet exist but are on the development roadmap
- When run with today's Claude Code, it should generate the output file
  as a simulation/projection of what future autonomous operation would
  look like
- The output should demonstrate the full potential of autonomous AI
  orchestration in oncology clinical trials
- All generated data should be deterministic (seed=20260312)
- The output file should be self-contained and parseable
- Include summary statistics section at the end comparing metrics
  against Prompt A output for the same day

## Repository References

- national-mcp-pai-oncology-trials v1.2.0: 5 MCP servers, 23 tools,
  8 safety modules, 13 JSON schemas, 34 integration adapters,
  381 files, ~69,800 LOC
- physical-ai-oncology-trials v2.2.0: 51 Python modules, 10 robot types,
  USL scoring framework, 6 agentic AI examples, digital twin pipeline,
  40,526 LOC
- pai-oncology-trial-fl v1.1.1: 235 Python modules, federated learning
  coordinator, differential privacy, secure aggregation, clinical analytics,
  ~86,800 LOC

## Future Claude Code Feature Dependencies

This prompt will become fully executable when Claude Code supports:
1. Persistent MCP server connections (multi-server simultaneous)
2. Sub-agent spawning and coordination (multi-agent orchestration)
3. Real-time streaming data processing (robot telemetry, vitals)
4. Autonomous safety gate approval (FDA PCCP pathway certification)
5. Extended session duration (24+ hours continuous operation)
6. Direct hardware interface via MCP tool contracts
7. Regulatory document auto-submission capability
8. Continuous learning from federated model updates

Until these features are available, this prompt generates a projected
simulation output that demonstrates the target autonomous workflow.

Author: Kevin Kawchak, CEO, ChemicalQDevice
ORCID: https://orcid.org/0009-0007-5457-8667
Prompt Version: v1.3.0-automation-b
Date: 2026-03-12
