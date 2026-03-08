# Production Operations Runbook

**National MCP-PAI Oncology Trials Standard**
**Document Classification**: Operational / Internal
**Last Updated**: 2026-03-08

---

## 1. Overview

This runbook covers day-to-day production operations for the five MCP servers that compose a conforming National MCP-PAI Oncology Trials deployment:

| Server | Default Port | Config File | Purpose |
|--------|-------------|-------------|---------|
| `trialmcp-authz` | 8001 | `deploy/config/authz.yaml` | Deny-by-default RBAC, token lifecycle |
| `trialmcp-fhir` | 8002 | `deploy/config/fhir.yaml` | FHIR R4 clinical data with Safe Harbor de-identification |
| `trialmcp-dicom` | 8003 | `deploy/config/dicom.yaml` | DICOM imaging metadata and pointer retrieval |
| `trialmcp-ledger` | 8004 | `deploy/config/ledger.yaml` | Hash-chained immutable audit ledger |
| `trialmcp-provenance` | 8005 | `deploy/config/provenance.yaml` | DAG-based data lineage tracking |

All servers emit structured JSON logs to stderr via `servers/common/logging.py` and expose a health-check endpoint conforming to `schemas/health-status.schema.json`.

---

## 2. Server Startup Procedures

### 2.1 Startup Order

Servers MUST be started in the following order to satisfy authorization dependencies:

1. **trialmcp-authz** -- all other servers depend on AuthZ for token validation
2. **trialmcp-ledger** -- audit recording must be available before clinical servers start
3. **trialmcp-fhir** -- depends on AuthZ and Ledger
4. **trialmcp-dicom** -- depends on AuthZ and Ledger
5. **trialmcp-provenance** -- depends on AuthZ and Ledger

### 2.2 Docker Compose (Single Site)

```bash
# From the repository root
cd deploy/
cp .env.example .env
# Edit .env with site-specific values (storage backend, HMAC key, etc.)

# Start all servers in dependency order
docker-compose up -d

# Verify all containers are running
docker-compose ps
```

### 2.3 Kubernetes / Helm

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/namespace.yaml

# Apply ConfigMap
kubectl apply -f deploy/kubernetes/configmap.yaml

# Deploy via Helm (recommended)
helm install trialmcp deploy/helm/trialmcp/ \
  --namespace trialmcp \
  --values deploy/helm/trialmcp/values.yaml \
  -f site-values.yaml

# Or deploy individual manifests
kubectl apply -f deploy/kubernetes/deployment-authz.yaml
# Wait for AuthZ readiness before proceeding
kubectl rollout status deployment/trialmcp-authz -n trialmcp --timeout=120s
kubectl apply -f deploy/kubernetes/deployment-ledger.yaml
kubectl rollout status deployment/trialmcp-ledger -n trialmcp --timeout=120s
kubectl apply -f deploy/kubernetes/deployment-fhir.yaml
kubectl apply -f deploy/kubernetes/deployment-dicom.yaml
kubectl apply -f deploy/kubernetes/deployment-provenance.yaml
```

### 2.4 Environment Variables

All servers accept the following environment variables (see `deploy/.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `TRIALMCP_STORAGE_BACKEND` | `memory` | Storage backend: `memory`, `sqlite`, `postgresql` |
| `TRIALMCP_STORAGE_DSN` | `""` | Connection string for sqlite or postgresql |
| `TRIALMCP_LOG_LEVEL` | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `TRIALMCP_HOST` | `0.0.0.0` | Bind address |
| `TRIALMCP_HMAC_KEY` | (none) | HMAC key for FHIR de-identification pseudonymization |
| `TRIALMCP_CONFIG_FILE` | (none) | Path to YAML config file override |

### 2.5 Pre-flight Checks

Before starting servers in production, verify the following:

```bash
# 1. Validate site profile
python -m tools.certification.site_certification validate \
  --profile deploy/config/site-profile-example.yaml

# 2. Verify schema files are present
ls schemas/*.schema.json | wc -l  # Should return 13

# 3. Run conformance smoke tests
python -m pytest conformance/positive/test_core_conformance.py -v --timeout=30

# 4. Confirm storage backend connectivity (if using postgresql)
psql "$TRIALMCP_STORAGE_DSN" -c "SELECT 1;"
```

---

## 3. Server Shutdown Procedures

### 3.1 Graceful Shutdown Order

Servers MUST be stopped in reverse startup order:

1. **trialmcp-provenance** -- stop lineage recording
2. **trialmcp-dicom** -- stop imaging queries
3. **trialmcp-fhir** -- stop clinical data access
4. **trialmcp-ledger** -- flush and finalize audit chain
5. **trialmcp-authz** -- revoke active sessions, stop last

### 3.2 Graceful Shutdown Commands

```bash
# Docker Compose
docker-compose stop provenance dicom fhir ledger authz
# or for full teardown:
docker-compose down

# Kubernetes
kubectl scale deployment trialmcp-provenance --replicas=0 -n trialmcp
kubectl scale deployment trialmcp-dicom --replicas=0 -n trialmcp
kubectl scale deployment trialmcp-fhir --replicas=0 -n trialmcp
kubectl scale deployment trialmcp-ledger --replicas=0 -n trialmcp
kubectl scale deployment trialmcp-authz --replicas=0 -n trialmcp
```

### 3.3 Active Procedure Safety Check

**CRITICAL**: Before shutting down servers during an active robotic procedure, verify the procedure state:

```bash
# Check for active procedures via the safety gate service
curl -s http://localhost:8001/tools/call -d '{
  "tool": "authz_list_active_sessions"
}' | jq '.active_procedures'

# If procedures are active, coordinate with clinical staff before proceeding.
# The safety/estop.py e-stop controller must be in IDLE status.
```

If an active procedure is in progress, shutdowns MUST be deferred until the procedure completes or an authorized e-stop is initiated per `safety/estop.py`.

---

## 4. Health Check Monitoring

### 4.1 Health Endpoint

Each server exposes a health check via the MCP `tools/call` interface. The response conforms to `schemas/health-status.schema.json` and is produced by `servers/common/health.py`:

```json
{
  "server_name": "trialmcp-ledger",
  "status": "healthy",
  "version": "0.7.0",
  "uptime_seconds": 3642.17,
  "checked_at": "2026-03-08T14:22:01.123456+00:00",
  "dependencies": [
    {"name": "authz", "status": "healthy", "latency_ms": 2.4},
    {"name": "storage", "status": "healthy", "latency_ms": 0.8}
  ]
}
```

### 4.2 Health Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `healthy` | All dependencies reachable, chain intact | None |
| `degraded` | Non-critical dependency unavailable | Investigate, alert on-call |
| `unhealthy` | Critical dependency unavailable or chain integrity failure | Page on-call, prepare failover |

### 4.3 Monitoring Script

```bash
#!/usr/bin/env bash
# health-check-all.sh -- Poll all 5 servers
SERVERS=("authz:8001" "fhir:8002" "dicom:8003" "ledger:8004" "provenance:8005")

for entry in "${SERVERS[@]}"; do
  name="${entry%%:*}"
  port="${entry##*:}"
  status=$(curl -sf "http://localhost:${port}/health" | jq -r '.status')
  if [ "$status" != "healthy" ]; then
    echo "ALERT: trialmcp-${name} status=${status}"
  fi
done
```

### 4.4 Recommended Monitoring Stack

- **Prometheus**: Scrape health endpoints every 15 seconds
- **Grafana**: Dashboard per server with uptime, dependency latency, chain length
- **PagerDuty / Opsgenie**: Alert on `unhealthy` status or dependency timeout > 5s
- **ELK / Loki**: Aggregate structured JSON logs from all servers

---

## 5. Log Analysis and Troubleshooting

### 5.1 Log Format

All servers emit structured JSON logs to stderr (configured in `servers/common/logging.py`):

```json
{
  "timestamp": "2026-03-08T14:22:01.123456+00:00",
  "level": "ERROR",
  "logger": "trialmcp-ledger",
  "message": "Chain integrity verification failed at index 4217"
}
```

### 5.2 Log Level Recommendations

| Environment | Level | Notes |
|-------------|-------|-------|
| Development | `DEBUG` | Full request/response logging |
| Staging | `INFO` | Standard operational logging |
| Production | `INFO` | Default; switch to `DEBUG` for incident investigation |
| Production (steady-state) | `WARNING` | After initial stabilization if log volume is a concern |

### 5.3 Common Log Queries

```bash
# Find all errors in the last hour (using jq on Docker logs)
docker logs trialmcp-ledger --since 1h 2>&1 | jq 'select(.level == "ERROR")'

# Find authorization denials
docker logs trialmcp-authz --since 1h 2>&1 | jq 'select(.message | contains("DENY"))'

# Find chain integrity warnings
docker logs trialmcp-ledger --since 24h 2>&1 | jq 'select(.message | contains("HASH_MISMATCH"))'

# Kubernetes log queries
kubectl logs -l app=trialmcp-fhir -n trialmcp --since=1h | jq 'select(.level == "ERROR")'
```

---

## 6. Common Failure Scenarios and Resolutions

### 6.1 AuthZ Server Unreachable

**Symptoms**: All clinical servers return authorization errors; tokens cannot be validated.

**Resolution**:
1. Check AuthZ container/pod status: `docker ps | grep authz` or `kubectl get pods -l app=trialmcp-authz`
2. Verify port 8001 is not blocked by firewall or network policy
3. Check AuthZ logs for startup errors
4. Restart AuthZ server; other servers will reconnect automatically
5. If persistent, check storage backend connectivity

### 6.2 Audit Chain Integrity Failure

**Symptoms**: `ledger_verify` tool returns `HASH_MISMATCH` or `PREV_HASH_MISMATCH`.

**Resolution**:
1. **Do not restart the ledger server** -- preserve state for forensic analysis
2. Record the mismatch index from the verification response
3. Export the full chain for offline analysis: call `ledger_export` tool
4. Compare against the most recent verified backup
5. Escalate to the security team -- chain tampering is a P1 regulatory incident
6. See `docs/operations/incident-response.md` for escalation procedures

### 6.3 FHIR Backend Connection Failure

**Symptoms**: `fhir_read` and `fhir_search` return connection errors.

**Resolution**:
1. Check the upstream EHR/FHIR server connectivity
2. Verify `fhir_backend` configuration in `deploy/config/fhir.yaml`
3. Test connectivity: `curl -sf https://<fhir-backend>/metadata`
4. Check mTLS certificate validity if mutual TLS is configured
5. Review `search_result_cap` (default 100) for query timeouts on large result sets

### 6.4 DICOM/PACS Connectivity Loss

**Symptoms**: `dicom_query` returns timeout or connection refused errors.

**Resolution**:
1. Verify PACS network reachability from the DICOM server container
2. Check configured modalities in `deploy/config/dicom.yaml` (`must_modalities`: CT, MR, PT)
3. Verify DICOM AE titles and port configuration
4. Test with a DICOM C-ECHO to the PACS
5. Check for firewall rules blocking DICOM ports (typically 104 or 11112)

### 6.5 Provenance DAG Cycle Detection

**Symptoms**: `provenance_verify` returns `CYCLE_DETECTED`.

**Resolution**:
1. This indicates a logic error in provenance recording -- DAGs must be acyclic
2. Query the provenance graph to identify the cycle: use `provenance_query_forward` and `provenance_query_backward`
3. Review recent provenance records for incorrect `parent_ids` linkage
4. This is a data integrity issue -- escalate as P2

### 6.6 Storage Backend Failure (PostgreSQL)

**Symptoms**: All servers report `unhealthy` with storage dependency failure.

**Resolution**:
1. Check PostgreSQL connectivity: `pg_isready -h <host> -p 5432`
2. Verify connection pool exhaustion: check `max_connections` in PostgreSQL
3. Check disk space on the database server
4. If using connection pooling (PgBouncer), verify pooler health
5. Failover to replica if available; servers reconnect on next request

---

## 7. Performance Tuning

### 7.1 Server Resource Defaults

From `deploy/helm/trialmcp/values.yaml`:

| Server | CPU Request | CPU Limit | Memory Request | Memory Limit |
|--------|------------|-----------|----------------|--------------|
| All servers | 100m | 500m | 128Mi | 512Mi |

### 7.2 Tuning Recommendations

**AuthZ Server**:
- Token validation is CPU-bound (SHA-256 hashing). Increase CPU limits for high-throughput sites.
- Token store grows linearly; use PostgreSQL backend for sites with > 10,000 tokens/day.

**FHIR Server**:
- De-identification pipeline (`servers/trialmcp_fhir/deid_pipeline.py`) is CPU-intensive for large bundles.
- Tune `search_result_cap` in `deploy/config/fhir.yaml` (default: 100) based on expected query sizes.
- HMAC-SHA256 pseudonymization adds ~0.1ms per patient ID.

**DICOM Server**:
- Image pointer retrieval is I/O-bound. Increase memory limits for concurrent PACS queries.
- Network latency to PACS is the primary bottleneck; colocate where possible.

**Ledger Server**:
- Chain append is serialized via `threading.Lock` (see `servers/trialmcp_ledger/chain.py`).
- For high-throughput deployments, use PostgreSQL backend to offload write serialization.
- Chain verification is O(n) -- schedule during off-peak hours for chains > 100K records.

**Provenance Server**:
- DAG traversal depth is bounded by `max_dag_depth` (default: 100 in `deploy/config/provenance.yaml`).
- Forward/backward queries are recursive; increase memory for deep lineage graphs.
- Cross-site merge (`cross_site_merge: true`) adds network overhead per federated query.

### 7.3 Connection Pooling

For PostgreSQL backends:
```yaml
# Recommended pg pool settings for a single hospital site
storage_backend: postgresql
storage_dsn: "postgresql://trialmcp:****@db:5432/trialmcp?pool_size=20&max_overflow=10"
```

---

## 8. Capacity Planning

### 8.1 Sizing Guidelines

| Metric | Small Site (< 50 patients) | Medium Site (50-500 patients) | Large Site (500+ patients) |
|--------|---------------------------|-------------------------------|---------------------------|
| AuthZ replicas | 1 | 2 | 3 |
| FHIR replicas | 1 | 2 | 3 |
| DICOM replicas | 1 | 2 | 4 |
| Ledger replicas | 1 | 1 (serialized writes) | 2 (with write leader) |
| Provenance replicas | 1 | 2 | 3 |
| PostgreSQL | Single node | Single node + replica | Primary + 2 replicas |
| Estimated audit records/day | 1,000 | 10,000 | 100,000 |
| Estimated storage growth/month | 50 MB | 500 MB | 5 GB |

### 8.2 Storage Growth Projections

- **Audit records**: ~500 bytes/record (canonical JSON + hash). 100K records/day = ~50 MB/day.
- **Provenance records**: ~800 bytes/record (includes parent linkage). Growth rate is proportional to clinical activity.
- **Chain verification time**: ~1 second per 100K records on modern hardware.

### 8.3 Scaling Triggers

| Metric | Threshold | Action |
|--------|-----------|--------|
| Health check latency | > 500ms P95 | Add replicas |
| Audit chain verification | > 30 seconds | Archive and start new chain segment |
| Storage utilization | > 70% | Expand storage, archive old data |
| Token validation latency | > 100ms P99 | Add AuthZ replicas or upgrade CPU |
| FHIR search response time | > 2s P95 | Tune `search_result_cap`, add replicas |

---

## 9. Routine Maintenance Tasks

### 9.1 Daily

- Verify health status of all 5 servers
- Review error-level log entries
- Confirm audit chain integrity: invoke `ledger_verify`

### 9.2 Weekly

- Review authorization denial patterns for anomalies
- Export and archive audit chain to offsite storage
- Run conformance test suite: `python -m pytest conformance/ -v`
- Review provenance DAG integrity: invoke `provenance_verify`

### 9.3 Monthly

- Rotate HMAC keys for de-identification (see `docs/operations/key-management.md`)
- Review and update RBAC policies
- Capacity review against sizing guidelines
- Generate site certification evidence pack: `python -m tools.certification.evidence_pack`

### 9.4 Quarterly

- Full disaster recovery drill (see `docs/operations/backup-recovery.md`)
- Security audit of token lifecycle and key management
- Review SLO compliance (see `docs/operations/slo-guidance.md`)
- Update site capability profile if jurisdiction requirements change

---

## 10. Emergency Contacts

| Role | Responsibility | Escalation Time |
|------|---------------|-----------------|
| Site Operations Engineer | First responder for infrastructure issues | Immediate |
| Clinical Trial Coordinator | Authorize procedure-affecting changes | < 15 minutes |
| Security Officer | Chain integrity, authorization, and PHI incidents | < 30 minutes |
| National MCP Standards Body | Specification interpretation, cross-site issues | < 4 hours |
| IRB Contact | Protocol deviation reporting | Per IRB policy |

---

*For incident-specific procedures, see `docs/operations/incident-response.md`.*
*For key and certificate management, see `docs/operations/key-management.md`.*
*For backup and disaster recovery, see `docs/operations/backup-recovery.md`.*
