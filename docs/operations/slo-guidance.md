# SLO/SLA Guidance

**National MCP-PAI Oncology Trials Standard**
**Document Classification**: Operational / Service Level Management
**Last Updated**: 2026-03-08

---

## 1. Overview

This document defines service level objectives (SLOs) and service level agreement (SLA) guidance for MCP-PAI oncology trial deployments. SLOs are tiered by conformance level (1-5 as defined in `spec/conformance.md`) and by whether a robotic procedure is actively in progress.

### 1.1 Conformance Level Summary

| Conformance Level | Description | Typical Deployment |
|-------------------|-------------|--------------------|
| Level 1 | Research / Development | Local dev (`docs/deployment/local-dev.md`) |
| Level 2 | Pre-clinical testing | Staging environment |
| Level 3 | Single-site clinical trial | Hospital site (`docs/deployment/hospital-site.md`) |
| Level 4 | Multi-site clinical trial | Federated (`docs/deployment/multi-site-federated.md`) |
| Level 5 | National-scale production | Full HA deployment |

---

## 2. Uptime Targets

### 2.1 Per-Server Uptime SLOs

| Server | Level 1-2 | Level 3 | Level 4 | Level 5 |
|--------|-----------|---------|---------|---------|
| `trialmcp-authz` | 95% | 99.5% | 99.9% | 99.95% |
| `trialmcp-fhir` | 95% | 99.5% | 99.9% | 99.95% |
| `trialmcp-dicom` | 95% | 99.0% | 99.5% | 99.9% |
| `trialmcp-ledger` | 99% | 99.9% | 99.95% | 99.99% |
| `trialmcp-provenance` | 95% | 99.5% | 99.9% | 99.95% |

**Notes**:
- The Ledger server has the highest uptime requirement because every tool invocation across all servers generates an audit record. Ledger unavailability blocks all clinical operations under strict conformance.
- DICOM server uptime targets are slightly lower because imaging queries are typically batch-oriented rather than real-time.

### 2.2 Composite System Uptime

The composite system SLO is the product of individual server SLOs for the critical path. For a typical clinical workflow (AuthZ + FHIR + Ledger):

| Level | Composite SLO | Allowed Downtime/Month |
|-------|---------------|----------------------|
| Level 3 | 98.9% | ~7.9 hours |
| Level 4 | 99.7% | ~2.2 hours |
| Level 5 | 99.89% | ~48 minutes |

### 2.3 During Active Robotic Procedures

When a robotic procedure is active (as tracked by `safety/procedure_state.py`), elevated SLOs apply:

| Server | Active Procedure SLO | Maximum Allowed Interruption |
|--------|---------------------|------------------------------|
| `trialmcp-authz` | 99.99% | < 5 seconds (token cache must bridge) |
| `trialmcp-fhir` | 99.95% | < 30 seconds |
| `trialmcp-dicom` | 99.9% | < 60 seconds (imaging data pre-loaded) |
| `trialmcp-ledger` | 99.99% | < 5 seconds (queue and retry) |
| `trialmcp-provenance` | 99.95% | < 30 seconds |

If any server exceeds its maximum allowed interruption during an active procedure, the `safety/gate_service.py` safety gate MUST evaluate whether to pause the procedure.

---

## 3. Latency Budgets

### 3.1 Per-Tool Latency SLOs

#### AuthZ Server (port 8001)

| Tool | P50 | P95 | P99 | Max |
|------|-----|-----|-----|-----|
| `authz_issue_token` | 5ms | 20ms | 50ms | 200ms |
| `authz_validate_token` | 2ms | 10ms | 25ms | 100ms |
| `authz_revoke_token` | 5ms | 20ms | 50ms | 200ms |
| `authz_evaluate` | 2ms | 10ms | 25ms | 100ms |
| `authz_list_policies` | 5ms | 25ms | 50ms | 200ms |

#### FHIR Server (port 8002)

| Tool | P50 | P95 | P99 | Max |
|------|-----|-----|-----|-----|
| `fhir_read` | 10ms | 50ms | 100ms | 500ms |
| `fhir_search` | 50ms | 200ms | 500ms | 2000ms |
| `fhir_patient_lookup` | 10ms | 50ms | 100ms | 500ms |
| `fhir_study_status` | 10ms | 50ms | 100ms | 500ms |

**Note**: FHIR latency includes the de-identification pipeline (`servers/trialmcp_fhir/deid_pipeline.py`). The HMAC-SHA256 pseudonymization adds approximately 0.1ms per identifier. Latency for `fhir_search` depends on result set size (capped by `search_result_cap` in `deploy/config/fhir.yaml`, default 100).

#### DICOM Server (port 8003)

| Tool | P50 | P95 | P99 | Max |
|------|-----|-----|-----|-----|
| `dicom_query` | 20ms | 100ms | 250ms | 1000ms |
| `dicom_retrieve_pointer` | 10ms | 50ms | 100ms | 500ms |
| `dicom_study_metadata` | 20ms | 100ms | 250ms | 1000ms |

**Note**: DICOM latency is heavily dependent on PACS backend response times. The SLOs above assume the PACS is co-located within the hospital network. For cloud-hosted PACS, add network round-trip time.

#### Ledger Server (port 8004)

| Tool | P50 | P95 | P99 | Max |
|------|-----|-----|-----|-----|
| `ledger_append` | 5ms | 20ms | 50ms | 200ms |
| `ledger_query` | 10ms | 50ms | 100ms | 500ms |
| `ledger_verify` | 100ms | 500ms | 2000ms | 10000ms |
| `ledger_replay` | 50ms | 200ms | 500ms | 5000ms |
| `ledger_chain_status` | 2ms | 10ms | 25ms | 100ms |

**Note**: `ledger_verify` performs O(n) chain traversal and is expected to be slow for large chains. Schedule verification during off-peak hours. The `ledger_append` operation acquires a `threading.Lock` (see `servers/trialmcp_ledger/chain.py`) which serializes writes.

#### Provenance Server (port 8005)

| Tool | P50 | P95 | P99 | Max |
|------|-----|-----|-----|-----|
| `provenance_record_access` | 5ms | 20ms | 50ms | 200ms |
| `provenance_query_forward` | 20ms | 100ms | 500ms | 2000ms |
| `provenance_query_backward` | 20ms | 100ms | 500ms | 2000ms |
| `provenance_verify` | 50ms | 200ms | 1000ms | 5000ms |

**Note**: DAG traversal depth is bounded by `max_dag_depth` (default 100 in `deploy/config/provenance.yaml`). Deep lineage queries approach the P99/Max budgets.

### 3.2 End-to-End Workflow Latency Budgets

| Workflow | Budget | Components |
|----------|--------|------------|
| Robot reads patient data | 200ms | AuthZ validate + FHIR read + Ledger append + Provenance record |
| Robot queries imaging | 300ms | AuthZ validate + DICOM query + Ledger append + Provenance record |
| Trial coordinator searches patients | 500ms | AuthZ validate + FHIR search + Ledger append |
| Auditor verifies chain | 30s | Ledger verify (for chains up to 1M records) |
| Cross-site provenance query | 2000ms | AuthZ validate + Provenance query + network overhead |

---

## 4. Fail-Safe Modes and Degraded Operation

### 4.1 Degraded Operation Rules

When a server enters `degraded` health status, the following rules apply:

| Failed Component | System Behavior | Clinical Impact |
|-----------------|-----------------|-----------------|
| AuthZ unavailable | **All operations blocked** -- deny-by-default enforced | No clinical data access |
| FHIR unavailable | Imaging and audit still available | No clinical record queries |
| DICOM unavailable | Clinical records and audit still available | No imaging queries |
| Ledger unavailable | **All operations blocked** (strict mode) or queued (lenient mode) | Audit gap risk |
| Provenance unavailable | Clinical operations continue, lineage not recorded | Provenance gap |
| Storage backend unavailable | All servers fall back to in-memory (if configured) | Data persistence risk |

### 4.2 Strict vs. Lenient Audit Mode

**Strict mode** (required for Level 4-5):
- If the Ledger server is unavailable, ALL tool invocations on ALL servers MUST be rejected
- This prevents any un-audited clinical data access
- Ensures zero audit gaps

**Lenient mode** (allowed for Level 1-3):
- If the Ledger server is unavailable, clinical operations MAY continue
- Audit records MUST be queued locally and flushed when the Ledger recovers
- The queue depth and maximum queue time must be monitored
- Any audit gap must be documented and reported

### 4.3 AuthZ Fail-Closed Behavior

The AuthZ server implements deny-by-default (`servers/trialmcp_authz/policy_engine.py`). When AuthZ is unavailable:

- All servers MUST deny all requests (fail-closed)
- Cached tokens MAY be honored for up to 60 seconds (grace period) if the token was validated within the last successful health check
- After the grace period, all cached authorizations expire
- No fallback to permissive mode is ever allowed

### 4.4 E-Stop Override

During an active e-stop (`safety/estop.py` -- `EStopStatus.TRIGGERED`):

- All robotic procedure operations are halted
- Clinical data read operations remain available for clinical staff
- The Ledger server continues recording all e-stop related events
- No new procedures may start until recovery is complete and re-authorized

---

## 5. Data Recovery Procedures and Timelines

### 5.1 Recovery Priority Order

1. **AuthZ server** -- required for all other operations
2. **Ledger server** -- required for audit compliance
3. **FHIR server** -- clinical data access
4. **DICOM server** -- imaging access
5. **Provenance server** -- lineage tracking (can be deferred briefly)

### 5.2 Recovery Timelines

| Scenario | Detection Time | Response Time | Recovery Time | Total |
|----------|---------------|---------------|---------------|-------|
| Pod restart | < 30 seconds | Automatic | < 2 minutes | < 3 minutes |
| Server redeployment | < 1 minute | < 5 minutes | < 10 minutes | < 16 minutes |
| Storage failover | < 1 minute | < 5 minutes | < 25 minutes | < 31 minutes |
| Full site restore | < 5 minutes | < 30 minutes | < 4 hours | < 4.5 hours |

### 5.3 Data Reconciliation After Recovery

After any recovery that involves data restoration:

1. Run `ledger_verify` to confirm audit chain integrity
2. Run `provenance_verify` to confirm DAG integrity
3. Compare the recovered chain length against the last known good length
4. If records are missing, identify the gap window and report per `docs/operations/incident-response.md`
5. Run `conformance/positive/test_core_conformance.py` to verify end-to-end functionality

---

## 6. Availability Requirements During Active Procedures

### 6.1 Pre-Procedure Readiness Check

Before any robotic procedure starts, the `safety/gate_service.py` safety gate MUST verify:

```
[ ] All 5 MCP servers report "healthy" status
[ ] AuthZ token for the robot agent is valid and not near expiry
[ ] Audit chain integrity verified (recent verification within 1 hour)
[ ] Provenance DAG integrity verified
[ ] Site capability profile conformance level >= 3
[ ] Robot capability profile verified via safety/robot_registry.py
[ ] Site verification passed via safety/site_verifier.py
```

### 6.2 During-Procedure Monitoring

| Check | Frequency | Failure Action |
|-------|-----------|----------------|
| Health status (all servers) | Every 10 seconds | Alert clinical team if any server unhealthy |
| Token validity | Every 60 seconds | Rotate token if < 5 minutes remaining |
| Ledger append latency | Every append | Alert if > 200ms; pause if > 1000ms |
| Network connectivity to PACS | Every 30 seconds | Alert if latency > 500ms |
| E-stop controller status | Continuous | Halt procedure if TRIGGERED |

### 6.3 Post-Procedure Verification

After procedure completion:

1. Verify all audit records for the procedure are present and chained
2. Verify provenance DAG for the procedure data is complete
3. Run `safety/approval_checkpoint.py` to close the procedure
4. Generate procedure evidence pack

---

## 7. Monitoring and Alerting Thresholds

### 7.1 Health Check Alerts

| Metric | Warning | Critical | Channel |
|--------|---------|----------|---------|
| Server status != "healthy" | After 1 check | After 3 consecutive checks | PagerDuty |
| Health check timeout | > 5 seconds | > 15 seconds | PagerDuty |
| Dependency status "unhealthy" | Immediate | After 2 minutes | PagerDuty |
| Uptime < SLO target (rolling 30 days) | < 0.5% buffer | Exceeded | Email + Slack |

### 7.2 Latency Alerts

| Metric | Warning | Critical | Channel |
|--------|---------|----------|---------|
| P95 latency > SLO | 1.5x SLO | 2x SLO | Slack |
| P99 latency > SLO | 1.5x SLO | 2x SLO | PagerDuty |
| Max latency > budget | Immediate | N/A | Log + Slack |
| `ledger_append` > 100ms | Warning | > 500ms Critical | PagerDuty |

### 7.3 Capacity Alerts

| Metric | Warning | Critical | Channel |
|--------|---------|----------|---------|
| CPU utilization | > 70% sustained | > 90% sustained | Slack |
| Memory utilization | > 75% sustained | > 90% sustained | PagerDuty |
| Audit chain length | > 500K records | > 1M records | Email (plan archival) |
| Storage utilization | > 70% | > 85% | Slack |
| Connection pool utilization | > 75% | > 90% | PagerDuty |

### 7.4 Security Alerts

| Metric | Threshold | Severity | Channel |
|--------|-----------|----------|---------|
| Authorization DENY rate | > 10% of requests | Warning | Slack |
| Token validation failures | > 5/minute | Warning | PagerDuty |
| Chain integrity failure | Any occurrence | P1 Critical | PagerDuty + Phone |
| E-stop triggered | Any occurrence | P1 Critical | PagerDuty + Phone + SMS |

### 7.5 Prometheus Alerting Rules Example

```yaml
groups:
  - name: trialmcp-slo
    rules:
      - alert: TrialMCPServerUnhealthy
        expr: trialmcp_health_status != 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MCP server {{ $labels.server_name }} is unhealthy"

      - alert: TrialMCPLatencyHigh
        expr: histogram_quantile(0.99, trialmcp_tool_latency_seconds) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency for {{ $labels.tool }} exceeds 500ms"

      - alert: TrialMCPAuditChainIntegrityFailure
        expr: trialmcp_ledger_chain_valid == 0
        for: 0s
        labels:
          severity: critical
        annotations:
          summary: "Audit chain integrity verification FAILED"

      - alert: TrialMCPEStopTriggered
        expr: trialmcp_estop_status == 1
        for: 0s
        labels:
          severity: critical
        annotations:
          summary: "Emergency stop triggered"
```

---

## 8. SLO Reporting

### 8.1 Reporting Cadence

| Report | Frequency | Audience |
|--------|-----------|----------|
| Operational dashboard | Real-time | Site operations team |
| Weekly SLO summary | Weekly | Site PI, trial coordinator |
| Monthly SLO report | Monthly | Sponsor, CRO |
| Quarterly compliance report | Quarterly | IRB, regulatory |

### 8.2 SLO Budget Tracking

Track error budget consumption per rolling 30-day window:

```
Error Budget = (1 - SLO) * total_minutes_in_window

Example for Level 4 AuthZ (99.9% SLO):
  Error Budget = 0.001 * 43200 = 43.2 minutes/month
  Consumed = actual_downtime_minutes
  Remaining = 43.2 - consumed
```

When error budget is exhausted:
1. Halt all non-critical changes and deployments
2. Focus engineering effort on reliability improvements
3. Increase monitoring frequency
4. Report to trial leadership

---

*For operational procedures and troubleshooting, see `docs/operations/runbook.md`.*
*For incident response when SLOs are breached, see `docs/operations/incident-response.md`.*
