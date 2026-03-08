# Incident Response Playbook

**National MCP-PAI Oncology Trials Standard**
**Document Classification**: Operational / Regulatory
**Last Updated**: 2026-03-08

---

## 1. Purpose

This playbook defines the incident response procedures for MCP-PAI oncology trial deployments. It covers severity classification, escalation paths, communication protocols, evidence preservation for 21 CFR Part 11 and HIPAA compliance, and post-incident review processes.

All incidents involving clinical trial systems are subject to additional regulatory reporting obligations. See `regulatory/HIPAA.md`, `regulatory/CFR_PART_11.md`, and `regulatory/US_FDA.md` for applicable requirements.

---

## 2. Severity Classification

### 2.1 Severity Levels

| Severity | Label | Description | Response Time | Resolution Target |
|----------|-------|-------------|---------------|-------------------|
| **P1** | Critical | Patient safety at risk, active procedure failure, audit chain tampering, PHI exposure | 15 minutes | 1 hour |
| **P2** | High | Service outage affecting clinical operations, data integrity failure, authorization bypass | 30 minutes | 4 hours |
| **P3** | Medium | Degraded performance, non-critical dependency failure, single-server outage with failover | 2 hours | 24 hours |
| **P4** | Low | Minor issues, cosmetic errors, documentation gaps, non-urgent configuration changes | Next business day | 1 week |

### 2.2 Classification Decision Tree

```
Is a patient currently undergoing a robotic procedure?
  YES --> Is the procedure affected?
    YES --> P1 (patient safety)
    NO  --> Continue assessment below
  NO  --> Continue assessment below

Is PHI exposed or potentially breached?
  YES --> P1 (HIPAA breach)

Is the audit chain integrity compromised?
  YES --> P1 (regulatory compliance)

Are clinical operations blocked?
  YES --> Is there a failover/workaround?
    NO  --> P2 (service outage)
    YES --> P3 (degraded operation)
  NO  --> P3 or P4 based on impact
```

### 2.3 Automatic P1 Triggers

The following events automatically trigger P1 classification:

- E-stop signal triggered (`safety/estop.py` -- `EStopStatus.TRIGGERED`)
- Audit chain `HASH_MISMATCH` or `PREV_HASH_MISMATCH` from `servers/trialmcp_ledger/chain.py`
- AuthZ server reports token validation bypass
- FHIR de-identification pipeline failure during active data access
- Any server reports `unhealthy` status during an active procedure
- PHI detected in log output or external-facing responses

---

## 3. Incident Response Phases

### 3.1 Phase 1: Detection and Triage (0-15 minutes)

**Objective**: Confirm the incident, classify severity, assemble the response team.

1. **Confirm the alert**: Verify the alert is not a false positive
   - Check health endpoints for all 5 servers
   - Review structured JSON logs for corroborating errors
   - Confirm via a second monitoring source if available

2. **Classify severity**: Use the decision tree in Section 2.2

3. **Declare the incident**: Create an incident record with:
   - Unique incident ID (format: `INC-YYYY-MM-DD-NNNN`)
   - Severity level
   - Affected servers and components
   - Initial description
   - Declaring responder

4. **Assemble response team**: Based on severity:

| Severity | Required Responders |
|----------|-------------------|
| P1 | Site Operations Engineer, Clinical Trial Coordinator, Security Officer, Site PI |
| P2 | Site Operations Engineer, Clinical Trial Coordinator |
| P3 | Site Operations Engineer |
| P4 | On-call engineer (async) |

### 3.2 Phase 2: Containment (15-60 minutes for P1/P2)

**Objective**: Limit the blast radius and preserve evidence.

**For patient safety incidents (P1)**:
1. If a robotic procedure is active, coordinate with the clinical team for safe abort
2. The e-stop controller (`safety/estop.py`) must be triggered by authorized personnel
3. Preserve procedure state -- the `EStopSignal.preserved_state` captures the snapshot automatically
4. Do NOT restart servers until evidence is preserved

**For data integrity incidents**:
1. Isolate the affected server -- remove from load balancer, do not terminate
2. Capture a full export of the audit chain: `ledger_export`
3. Snapshot the provenance DAG state
4. Capture container/pod logs with timestamps
5. If PHI exposure is suspected, disable external access to affected endpoints

**For service outages**:
1. Attempt failover to replica if available
2. If single-server failure, assess whether degraded operation is acceptable
3. Document the failover timeline

### 3.3 Phase 3: Investigation (1-4 hours for P1/P2)

**Objective**: Identify root cause and develop a fix.

1. **Collect evidence** (see Section 5 for details):
   - Server logs from all 5 servers for the incident window
   - Audit chain records covering the incident period
   - Provenance graph for affected data flows
   - Authorization decisions for the incident period
   - Health check history

2. **Root cause analysis**:
   - Review the sequence of events using audit timestamps
   - Trace the provenance DAG for affected data
   - Check for configuration drift from the approved site profile
   - Review recent deployments or configuration changes

3. **Develop fix or workaround**:
   - Document the proposed fix
   - Assess risk of the fix
   - Get approval from the appropriate authority (see escalation matrix)

### 3.4 Phase 4: Resolution

**Objective**: Restore normal operations and verify integrity.

1. Apply the fix or workaround
2. Verify all 5 servers return `healthy` status
3. Run audit chain verification: `ledger_verify`
4. Run provenance DAG verification: `provenance_verify`
5. Run conformance smoke tests: `pytest conformance/positive/test_core_conformance.py`
6. Confirm clinical operations can resume
7. Update the incident record with resolution details

### 3.5 Phase 5: Post-Incident Review (within 72 hours)

See Section 6 for the full post-incident review process.

---

## 4. Escalation Paths

### 4.1 Clinical Trial Escalation Matrix

```
Level 1: Site Operations Engineer
  |
  +--> Level 2: Site Clinical Trial Coordinator
         |
         +--> Level 3: Site Principal Investigator (PI)
                |
                +--> Level 4: Sponsor Medical Monitor
                       |
                       +--> Level 5: IRB / Data Safety Monitoring Board (DSMB)
                              |
                              +--> Level 6: FDA (for reportable events)
```

### 4.2 Technical Escalation Matrix

```
Level 1: On-call Site Engineer
  |
  +--> Level 2: Site Infrastructure Lead
         |
         +--> Level 3: National MCP Standards Technical Committee
                |
                +--> Level 4: MCP Platform Vendor Support
```

### 4.3 Escalation Triggers

| Condition | Escalation Target |
|-----------|-------------------|
| E-stop triggered | Site PI and Sponsor Medical Monitor immediately |
| Audit chain tampering | Security Officer, IRB, and Sponsor within 1 hour |
| PHI breach confirmed | Privacy Officer, HHS OCR within 60 days (or sooner per state law) |
| Unresolved P1 after 1 hour | Site Infrastructure Lead and Sponsor |
| Unresolved P2 after 4 hours | Site Infrastructure Lead |
| Protocol deviation suspected | Site PI and IRB per `regulatory/IRB_SITE_POLICY_TEMPLATE.md` |
| Cross-site data integrity issue | National MCP Standards Technical Committee |

---

## 5. Evidence Preservation Procedures

### 5.1 Regulatory Requirements

Evidence preservation must satisfy:
- **21 CFR Part 11**: Electronic records must be preserved in their original form with complete audit trails (see `regulatory/CFR_PART_11.md`)
- **HIPAA Security Rule**: Security incident logs must be retained for 6 years
- **ICH E6(R2) GCP**: Source data must be attributable, legible, contemporaneous, original, and accurate (ALCOA)

### 5.2 Evidence Collection Checklist

For every P1 and P2 incident, collect and preserve the following:

```
[ ] Audit chain export (full chain as JSON)
    Command: invoke ledger_export tool, format=json
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/audit-chain.json

[ ] Provenance DAG export for affected data
    Command: invoke provenance_query_forward / provenance_query_backward
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/provenance-graph.json

[ ] Server logs (all 5 servers, 1 hour before to 1 hour after incident)
    Command: docker logs --since <start> --until <end> <container>
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/logs/

[ ] Authorization decision log for the incident window
    Command: invoke ledger_query, server=trialmcp-authz
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/authz-decisions.json

[ ] Health check snapshots at time of incident
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/health-snapshots.json

[ ] Configuration files at time of incident
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/config/

[ ] Site capability profile
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/site-profile.yaml

[ ] E-stop signal details (if applicable)
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/estop-signal.json

[ ] Container/pod state snapshots
    Command: kubectl describe pod <pod-name> -n trialmcp
    Store: incident-evidence/INC-YYYY-MM-DD-NNNN/infrastructure/
```

### 5.3 Evidence Integrity

All preserved evidence must be integrity-protected:

```bash
# Generate SHA-256 checksums for all evidence files
find incident-evidence/INC-YYYY-MM-DD-NNNN/ -type f \
  -exec sha256sum {} \; > incident-evidence/INC-YYYY-MM-DD-NNNN/checksums.sha256

# Sign the checksum file with the site evidence signing key
gpg --armor --detach-sign \
  --local-user site-evidence-signing-key \
  incident-evidence/INC-YYYY-MM-DD-NNNN/checksums.sha256
```

### 5.4 Evidence Retention

| Evidence Type | Minimum Retention Period | Storage Requirement |
|--------------|-------------------------|---------------------|
| Audit chain exports | Duration of trial + 15 years | Immutable, encrypted at rest |
| Server logs | 6 years | Encrypted at rest |
| Configuration snapshots | Duration of trial + 2 years | Version controlled |
| E-stop records | Duration of trial + 15 years | Immutable, encrypted at rest |
| Incident reports | Duration of trial + 15 years | Version controlled |

---

## 6. Post-Incident Review Process

### 6.1 Timeline

- **P1 incidents**: Post-incident review within 48 hours
- **P2 incidents**: Post-incident review within 72 hours
- **P3 incidents**: Post-incident review within 1 week
- **P4 incidents**: Reviewed in monthly operations meeting

### 6.2 Review Meeting Agenda

1. **Timeline reconstruction**: Minute-by-minute account using audit records
2. **Root cause analysis**: Use the "5 Whys" technique
3. **Impact assessment**: Patients affected, data integrity impact, regulatory impact
4. **Response effectiveness**: What went well, what could improve
5. **Action items**: Preventive measures with owners and deadlines
6. **Regulatory reporting**: Determine if the incident is reportable

### 6.3 Post-Incident Report Template

```markdown
# Post-Incident Report: INC-YYYY-MM-DD-NNNN

## Summary
- **Severity**: P1/P2/P3/P4
- **Duration**: Start time to resolution time
- **Impact**: Number of affected patients, procedures, data records
- **Root Cause**: Brief description

## Timeline
| Time (UTC) | Event |
|------------|-------|
| HH:MM | First alert triggered |
| HH:MM | Incident declared |
| HH:MM | Containment actions taken |
| HH:MM | Root cause identified |
| HH:MM | Fix applied |
| HH:MM | Normal operations restored |

## Root Cause Analysis
[Detailed analysis]

## Impact Assessment
- **Patient Safety**: [Assessment]
- **Data Integrity**: [Assessment, including audit chain and provenance verification results]
- **Regulatory**: [Reportable? To whom?]
- **Operational**: [Downtime, degraded operation duration]

## Corrective Actions
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | Open/Closed |

## Lessons Learned
[What went well, what could improve]

## Regulatory Notifications
- [ ] IRB notification required: Yes/No
- [ ] Sponsor notification required: Yes/No
- [ ] FDA notification required: Yes/No
- [ ] HHS OCR notification required (PHI breach): Yes/No
```

---

## 7. Communication Templates

### 7.1 Initial Incident Notification (Internal)

```
Subject: [P{N}] Incident INC-YYYY-MM-DD-NNNN - {Brief Description}

An incident has been declared affecting the MCP-PAI oncology trial system.

Severity: P{N}
Affected Components: {list of affected servers}
Impact: {brief impact description}
Current Status: {Investigating / Contained / Resolving}

Response Team:
- Incident Commander: {name}
- Operations Lead: {name}
- Clinical Contact: {name}

Next update in {30 minutes / 1 hour}.
```

### 7.2 Stakeholder Update

```
Subject: [UPDATE] Incident INC-YYYY-MM-DD-NNNN - {Brief Description}

Status Update #{N} as of {timestamp UTC}

Current Status: {Investigating / Contained / Resolving / Resolved}
Impact: {updated impact assessment}
Actions Taken: {summary of actions since last update}
Next Steps: {planned actions}
ETA to Resolution: {estimate}

Next update in {timeframe}.
```

### 7.3 Resolution Notification

```
Subject: [RESOLVED] Incident INC-YYYY-MM-DD-NNNN - {Brief Description}

The incident has been resolved.

Resolution Time: {timestamp UTC}
Total Duration: {duration}
Root Cause: {brief root cause}
Fix Applied: {brief description of fix}

Verification:
- All 5 MCP servers report healthy status
- Audit chain integrity verified
- Provenance DAG integrity verified
- Conformance tests passing

Post-incident review scheduled for {date/time}.
```

### 7.4 Regulatory Notification (IRB)

```
Subject: Protocol Deviation Report - {Trial Protocol ID}

Per IRB policy and 21 CFR Part 11 requirements, we are reporting
the following event affecting the MCP-PAI oncology trial system:

Protocol ID: {from site-profile irb_approval.protocol_id}
Site: {site_name}
Incident ID: INC-YYYY-MM-DD-NNNN
Date/Time: {timestamp}

Description: {detailed description}

Patient Impact: {assessment}
Data Integrity Impact: {assessment}
Corrective Actions: {summary}

Evidence Package: {location of preserved evidence}

Reported by: {name, role}
Date: {date}
```

---

## 8. Incident Categories Specific to MCP-PAI

### 8.1 Robotic Procedure Incidents

Any incident during an active robotic procedure follows additional protocols:

1. The e-stop controller (`safety/estop.py`) must be engaged if patient safety is at risk
2. The `safety/gate_service.py` safety gate must prevent new procedures from starting
3. The `safety/procedure_state.py` procedure state must be preserved
4. The `safety/approval_checkpoint.py` re-approval is required before resuming procedures
5. The `safety/site_verifier.py` must re-verify site readiness

### 8.2 Cross-Site Data Incidents

For incidents affecting federated deployments (`deploy/docker-compose.multi-site.yml`):

1. Notify all affected sites immediately
2. The shared ledger (`shared-ledger` service) must be preserved
3. Coordinate response through the National MCP Standards Technical Committee
4. Each site must independently verify their local audit chain and provenance DAG
5. Cross-site provenance merge (`cross_site_merge` in `deploy/config/provenance.yaml`) should be suspended until integrity is confirmed

### 8.3 De-identification Failures

If the FHIR de-identification pipeline (`servers/trialmcp_fhir/deid_pipeline.py`) fails:

1. Immediately classify as P1 (potential PHI exposure)
2. Identify all data returned without proper de-identification
3. Determine if PHI reached any unauthorized recipients
4. If PHI was exposed, initiate HIPAA breach notification procedures
5. Verify the HMAC key configuration in `deploy/config/fhir.yaml`
6. Test de-identification with known fixtures from `conformance/fixtures/clinical_resources.py`

---

*For operational procedures, see `docs/operations/runbook.md`.*
*For evidence preservation signing keys, see `docs/operations/key-management.md`.*
