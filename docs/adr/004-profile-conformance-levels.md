# ADR-004: Conformance Profiles Map to Clinical Deployment Tiers

**Status**: Accepted
**Date**: 2026-02-19
**Decision Makers**: Conformance Working Group
**Tracking**: DL-009 in `docs/governance/decision-log.md`

---

## Context

Implementations of the national standard vary dramatically in scope. A community
oncology clinic performing data monitoring needs only authorization and audit
capabilities. An NCI-designated cancer center performing robot-assisted surgical
procedures needs the full stack including imaging, provenance, and safety modules.

A single conformance level would impose the full implementation burden on every
deployment, regardless of operational scope. This would delay adoption by sites
that need only basic capabilities and would make conformance testing
disproportionately expensive for simple deployments.

The standard must define conformance levels that:

1. **Match clinical deployment tiers**: Each level corresponds to a real-world
   deployment scenario
2. **Are cumulative**: Higher levels include all requirements of lower levels
3. **Map to server composition**: Each level adds specific servers to the deployment
4. **Are independently testable**: Each level has a complete set of MUST/SHOULD/MAY
   requirements that can be verified
5. **Provide a migration path**: Sites can progressively adopt higher levels as their
   capabilities grow

---

## Decision

Define five cumulative conformance profiles, each mapping to a clinical deployment
tier and a specific server composition:

| Profile | Level | Deployment Tier | Servers Required |
|---------|-------|----------------|------------------|
| `base` | 1 — Core | Authorization and audit only | AuthZ, Ledger |
| `clinical-read` | 2 — Clinical Read | Clinical data monitoring | + FHIR |
| `imaging-guided` | 3 — Imaging | Imaging-guided procedures | + DICOM |
| `multi-site-federated` | 4 — Federated | Multi-site trial coordination | + Provenance |
| `robot-assisted-procedure` | 5 — Robot Procedure | Full robot-assisted clinical workflow | All 5 + safety modules |

---

## Rationale

### Tier 1: Core (Base Profile)

**Clinical scenario**: A site that needs to participate in a trial's authorization
and audit infrastructure without accessing clinical or imaging data. Examples include
regulatory auditors performing remote compliance reviews and sponsors monitoring
trial governance.

**Required servers**: `trialmcp-authz` (5 tools) + `trialmcp-ledger` (5 tools) = 10
tools.

**Regulatory justification**: 21 CFR Part 11 requires audit trails for all electronic
records. HIPAA Security Rule requires access controls. These are the minimum
regulatory requirements for any clinical trial system.

### Tier 2: Clinical Read (Clinical-Read Profile)

**Clinical scenario**: A site performing clinical data monitoring — reviewing patient
enrollment, demographics, study status, and clinical observations. Examples include
CRO data monitors performing source data verification and sponsor medical monitors
reviewing safety data.

**Additional server**: `trialmcp-fhir` (4 tools). Total: 14 tools.

**Regulatory justification**: ICH-GCP E6(R2) requires source data verification and
safety data review. HIPAA Privacy Rule requires de-identification for data access.

### Tier 3: Imaging (Imaging-Guided Profile)

**Clinical scenario**: A site performing imaging-guided oncology procedures —
querying DICOM studies, reviewing tumor measurements, and providing imaging data
to robot agents. Examples include radiation oncology sites performing image-guided
radiation therapy (IGRT) and surgical sites performing image-guided tumor resection.

**Additional server**: `trialmcp-dicom` (4 tools). Total: 18 tools.

**Regulatory justification**: DICOM is the normative standard for medical imaging.
RECIST 1.1 measurements are required for oncology trial response assessment.

### Tier 4: Federated (Multi-Site-Federated Profile)

**Clinical scenario**: A multi-site trial where data lineage must be tracked across
institutional boundaries. Examples include federated learning studies where model
parameters are aggregated from multiple sites, and multi-center trials where
provenance must demonstrate that no patient-level data crossed site boundaries.

**Additional server**: `trialmcp-provenance` (5 tools). Total: 23 tools.

**Regulatory justification**: ICH-GCP E6(R2) requires complete data lineage for
audit purposes. FDA guidance on decentralized clinical trials requires provenance
tracking for data collected at multiple sites.

### Tier 5: Robot Procedure (Robot-Assisted-Procedure Profile)

**Clinical scenario**: A site performing robot-assisted clinical procedures within
an oncology trial. Examples include robotic surgical resection, robotic radiation
therapy positioning, and robotic biopsy procedures.

**Additional requirements**: All 5 servers (23 tools) plus safety modules (e-stop,
approval checkpoint, gate service, procedure state machine, robot registry, site
verifier, task validator).

**Regulatory justification**: FDA CDRH device classification applies. Robot safety
requirements mandate independent safety modules that operate outside the MCP server
boundary.

### Cumulative Design

Each level inherits all MUST/SHOULD/MAY requirements from lower levels. This means:

- A Level 3 implementation MUST satisfy all Level 1, Level 2, and Level 3 requirements
- A Level 3 implementation can interoperate with Level 1 and Level 2 clients using
  only the tools available at those levels
- Conformance testing for Level 3 includes all Level 1 and Level 2 test cases

This cumulative structure prevents "partial" implementations that skip lower-level
requirements. Every implementation that can read imaging data (Level 3) also has
authorization (Level 1) and clinical data access (Level 2).

---

## Consequences

### Positive

- **Graduated adoption**: Sites adopt the level that matches their clinical scope
- **Reduced deployment cost**: Level 1 and Level 2 sites avoid deploying imaging
  and provenance infrastructure
- **Clear conformance claims**: "Level 3 conformant" is unambiguous about capabilities
- **Progressive migration**: Sites can upgrade from Level 2 to Level 3 by adding the
  DICOM server and passing Level 3 conformance tests
- **Interoperability clarity**: A Level 5 server can serve Level 1 clients by exposing
  only Level 1 tools

### Negative

- **Five levels may be too many for initial adoption**: Early adopters must understand
  which level applies to them
- **Cumulative testing burden**: Level 5 conformance testing includes all Level 1-4
  tests, which increases certification time
- **Level selection disputes**: Sites may disagree about which level is required for
  their clinical scenario

### Mitigations

- Deployment guides in `deploy/` provide clear guidance on level selection based on
  clinical scenario
- Conformance test suites are modular; Level 5 tests build on Level 1-4 tests without
  duplication
- The governance body provides authoritative level selection guidance for ambiguous
  clinical scenarios

---

## Alternatives Rejected

### Two Levels (Basic and Full)

Only "basic" (AuthZ + Ledger) and "full" (all five servers). Rejected because the
gap between basic and full is too large. Sites needing clinical data access but not
imaging would be forced to implement the full stack.

### Three Levels (Core, Clinical, Robot)

Core (AuthZ + Ledger), Clinical (+ FHIR + DICOM), Robot (+ Provenance + safety).
Rejected because combining FHIR and DICOM into a single level forces imaging
infrastructure on sites that only need clinical data monitoring. Additionally,
combining Provenance with Robot separates provenance from the federated use case
it primarily serves.

### Non-Cumulative Profiles

Independent profiles that can be combined arbitrarily (e.g., "AuthZ + DICOM" without
FHIR). Rejected because non-cumulative profiles would allow implementations that
skip foundational requirements. An implementation with DICOM access but no FHIR
access would not be able to correlate imaging with clinical data, which is fundamental
to oncology trial workflows.

### Seven Levels (Adding Scheduling and Notification)

Adding dedicated levels for trial scheduling and real-time notification. Rejected
because scheduling and notification are application concerns not addressed by the
current server architecture. Adding levels for non-existent servers would create
aspirational levels with no testable requirements.

---

## References

- `spec/conformance.md` (full MUST/SHOULD/MAY matrix per level)
- `spec/core.md` Section 3 (Conformance Level overview)
- `profiles/base-profile.md` (Level 1 profile definition)
- `profiles/clinical-read.md` (Level 2 profile definition)
- `profiles/imaging-guided-oncology.md` (Level 3 profile definition)
- `profiles/multi-site-federated.md` (Level 4 profile definition)
- `profiles/robot-assisted-procedure.md` (Level 5 profile definition)
