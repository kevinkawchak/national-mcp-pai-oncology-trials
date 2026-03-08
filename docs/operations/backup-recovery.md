# Backup and Recovery Procedures

**National MCP-PAI Oncology Trials Standard**
**Document Classification**: Operational / Business Continuity
**Last Updated**: 2026-03-08

---

## 1. Overview

This document defines backup, integrity verification, and disaster recovery procedures for MCP-PAI oncology trial deployments. The backup strategy must satisfy regulatory retention requirements defined in `regulatory/CFR_PART_11.md` and `regulatory/HIPAA.md`.

### 1.1 Data Classification

| Data Category | Criticality | Backup Frequency | Retention Period |
|--------------|-------------|-------------------|------------------|
| Audit chain | Critical | Continuous + daily snapshot | Duration of trial + 15 years |
| Provenance DAG | Critical | Continuous + daily snapshot | Duration of trial + 15 years |
| Authorization policies | High | On every change + daily | Duration of trial + 5 years |
| Token store | Medium | Hourly | 90 days (tokens are short-lived) |
| Server configuration | High | On every change | Duration of trial + 2 years |
| Site capability profiles | High | On every change | Duration of trial + 5 years |
| FHIR resource cache | Medium | Daily | Duration of trial (source of truth is upstream EHR) |
| DICOM metadata cache | Medium | Daily | Duration of trial (source of truth is PACS) |

---

## 2. Recovery Objectives

### 2.1 Recovery Time Objective (RTO)

| Scenario | RTO | Notes |
|----------|-----|-------|
| Single server failure | 15 minutes | Kubernetes auto-restart or Docker restart |
| Storage backend failure | 30 minutes | Failover to replica or restore from snapshot |
| Full site failure | 4 hours | Restore from backup to new infrastructure |
| Cross-site coordination failure | 1 hour | Each site operates independently |
| Audit chain corruption | 2 hours | Restore from last verified backup |
| Complete data center loss | 8 hours | Restore to alternate data center |

### 2.2 Recovery Point Objective (RPO)

| Data Category | RPO | Justification |
|--------------|-----|---------------|
| Audit chain | 0 (zero data loss) | Regulatory requirement -- every audit record must be preserved |
| Provenance DAG | 5 minutes | Near-zero loss; provenance records can be reconstructed from audit chain |
| Authorization policies | 0 (zero data loss) | Policies are critical for deny-by-default enforcement |
| Token store | 1 hour | Expired tokens are rebuilt; active tokens re-issued |
| Configuration | 0 (zero data loss) | Configuration is version-controlled |
| FHIR/DICOM cache | 24 hours | Source data resides in upstream EHR/PACS systems |

---

## 3. Audit Chain Backup

### 3.1 Backup Strategy

The audit chain (`servers/trialmcp_ledger/chain.py`) is the most critical data asset. It provides the tamper-evident record required by 21 CFR Part 11.

**Continuous replication** (preferred for production):
```yaml
# PostgreSQL streaming replication for audit chain
# Primary: writes audit records via servers/storage/postgres_adapter.py
# Replica: synchronous streaming replication for zero RPO

# postgresql.conf (primary)
wal_level = replica
synchronous_commit = on
synchronous_standby_names = 'trialmcp_audit_replica'
```

**Daily snapshot backup**:
```bash
#!/usr/bin/env bash
# backup-audit-chain.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/audit-chain"
SITE_ID=$(grep site_id deploy/config/site-profile-example.yaml | awk '{print $2}' | tr -d '"')

# Export the full audit chain via the ledger tool
# The chain.py export() method returns the complete chain as JSON
curl -sf http://localhost:8004/tools/call -d '{
  "tool": "ledger_export",
  "parameters": {"format": "json"}
}' > "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json"

# Compute integrity checksum
sha256sum "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json" \
  > "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.sha256"

# Verify the exported chain
python3 -c "
import json, hashlib

with open('${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json') as f:
    chain = json.load(f)

prev_hash = '0' * 64
for i, record in enumerate(chain):
    filtered = {k: v for k, v in sorted(record.items()) if k != 'hash'}
    canonical = json.dumps(filtered, sort_keys=True, ensure_ascii=True)
    expected = hashlib.sha256((prev_hash + canonical).encode()).hexdigest()
    assert record['hash'] == expected, f'HASH_MISMATCH at index {i}'
    assert record['previous_hash'] == prev_hash, f'PREV_HASH_MISMATCH at index {i}'
    prev_hash = record['hash']

print(f'Backup verified: {len(chain)} records, chain intact')
"

# Encrypt the backup
gpg --encrypt --recipient backup-encryption-key \
  "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json"

# Upload to offsite storage
aws s3 cp "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json.gpg" \
  "s3://trialmcp-backups/${SITE_ID}/audit-chain/"

# Clean up plaintext
rm "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json"

echo "Audit chain backup complete: ${DATE}"
```

### 3.2 Integrity Verification

Run chain integrity verification daily (or more frequently for high-activity sites):

```bash
# Verify via the ledger server's built-in verification
# This calls chain.py verify() which checks the full hash chain
curl -sf http://localhost:8004/tools/call -d '{
  "tool": "ledger_verify"
}' | jq '.'

# Expected output for a valid chain:
# {"valid": true, "length": 42317}

# If verification fails:
# {"valid": false, "reason": "HASH_MISMATCH at index 4217", "index": 4217}
```

### 3.3 Audit Chain Restoration

```bash
# 1. Stop the ledger server
docker stop trialmcp-ledger

# 2. Decrypt the backup
gpg --decrypt "${BACKUP_DIR}/${SITE_ID}_audit_chain_${DATE}.json.gpg" \
  > /tmp/audit_chain_restore.json

# 3. Verify the backup chain integrity before restoring
python3 -c "
import json, hashlib
with open('/tmp/audit_chain_restore.json') as f:
    chain = json.load(f)
# ... verification logic as above ...
print(f'Backup verified: {len(chain)} records')
"

# 4. Restore to storage backend
# For PostgreSQL:
psql "$TRIALMCP_STORAGE_DSN" -c "TRUNCATE audit_chain;"
# Import records...

# For SQLite:
# Replace the database file

# 5. Restart the ledger server
docker start trialmcp-ledger

# 6. Verify post-restoration
curl -sf http://localhost:8004/tools/call -d '{"tool": "ledger_verify"}' | jq '.'
```

---

## 4. Provenance Graph Backup

### 4.1 Backup Strategy

The provenance DAG (`servers/trialmcp_provenance/dag.py`) stores data lineage as a directed acyclic graph with forward and backward edge indexes.

```bash
#!/usr/bin/env bash
# backup-provenance.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/provenance"
SITE_ID=$(grep site_id deploy/config/site-profile-example.yaml | awk '{print $2}' | tr -d '"')

# Export provenance records
# For PostgreSQL backend:
pg_dump -t provenance "$TRIALMCP_STORAGE_DSN" \
  > "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sql"

# Compute checksum
sha256sum "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sql" \
  > "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sha256"

# Encrypt and upload
gpg --encrypt --recipient backup-encryption-key \
  "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sql"
aws s3 cp "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sql.gpg" \
  "s3://trialmcp-backups/${SITE_ID}/provenance/"
rm "${BACKUP_DIR}/${SITE_ID}_provenance_${DATE}.sql"
```

### 4.2 Provenance Integrity Verification

```bash
# Verify DAG integrity (no cycles)
curl -sf http://localhost:8005/tools/call -d '{
  "tool": "provenance_verify"
}' | jq '.'

# Expected output:
# {"valid": true, "total_records": 12847, "total_edges": 18293}
```

### 4.3 Provenance Restoration

1. Stop the provenance server
2. Restore the database from backup
3. Restart the provenance server -- the DAG is rebuilt from storage via `_load_graph()`
4. Verify integrity with `provenance_verify`

---

## 5. Configuration Backup

### 5.1 Version-Controlled Configuration

All configuration files MUST be version-controlled. The following files must be backed up:

```
deploy/config/authz.yaml        # AuthZ server configuration
deploy/config/fhir.yaml         # FHIR server configuration
deploy/config/dicom.yaml        # DICOM server configuration
deploy/config/ledger.yaml       # Ledger server configuration (includes genesis_hash)
deploy/config/provenance.yaml   # Provenance server configuration
deploy/.env                     # Environment variables (NEVER commit secrets)
deploy/helm/trialmcp/values.yaml # Helm chart values
```

### 5.2 Site Profile Backup

The site capability profile (`deploy/config/site-profile-example.yaml`) contains critical site identity information including:
- Site ID and classification
- Jurisdiction and regulatory requirements
- Conformance level
- IRB approval details
- Robot registrations

```bash
# Backup site profile with version tracking
cp deploy/config/site-profile.yaml \
  "/backup/config/site-profile_$(date +%Y%m%d).yaml"
```

### 5.3 Policy Backup

Authorization policies are stored in the AuthZ server's storage backend. Back up the full policy matrix:

```bash
# Export current policies
curl -sf http://localhost:8001/tools/call -d '{
  "tool": "authz_list_policies"
}' > "/backup/config/policies_$(date +%Y%m%d).json"
```

---

## 6. Disaster Recovery Procedures

### 6.1 DR Tiers

| Tier | Scenario | Procedure | Target RTO |
|------|----------|-----------|------------|
| **Tier 1** | Single server pod crash | Kubernetes auto-restart; no manual action | < 2 minutes |
| **Tier 2** | Single server persistent failure | Redeploy from Helm chart, restore state from backup | 15 minutes |
| **Tier 3** | Storage backend failure | Failover to replica; if no replica, restore from backup | 30 minutes |
| **Tier 4** | Full site infrastructure failure | Provision new infrastructure, restore all data | 4 hours |
| **Tier 5** | Data center loss | Restore to alternate region from offsite backups | 8 hours |

### 6.2 Tier 2: Single Server Recovery

```bash
# Example: Recovering the Ledger server

# 1. Check the current state
kubectl get pods -l app=trialmcp-ledger -n trialmcp

# 2. If the pod is in CrashLoopBackOff, check logs
kubectl logs -l app=trialmcp-ledger -n trialmcp --previous

# 3. Delete the failing pod (Kubernetes will recreate it)
kubectl delete pod -l app=trialmcp-ledger -n trialmcp

# 4. If persistent volume is corrupted, restore from backup
kubectl apply -f deploy/kubernetes/deployment-ledger.yaml

# 5. Restore audit chain from backup if needed (see Section 3.3)

# 6. Verify
curl -sf http://localhost:8004/tools/call -d '{"tool": "ledger_verify"}' | jq '.'
```

### 6.3 Tier 3: Storage Backend Recovery

**PostgreSQL failover**:
```bash
# 1. Detect primary failure
pg_isready -h primary-db -p 5432  # Returns non-zero if down

# 2. Promote replica
psql -h replica-db -p 5432 -c "SELECT pg_promote();"

# 3. Update connection strings for all servers
kubectl set env deployment/trialmcp-authz \
  TRIALMCP_STORAGE_DSN="postgresql://user:pass@replica-db:5432/trialmcp" \
  -n trialmcp
# Repeat for all 5 server deployments

# 4. Verify all servers reconnect
for port in 8001 8002 8003 8004 8005; do
  curl -sf "http://localhost:${port}/health" | jq '.dependencies[] | select(.name == "storage")'
done

# 5. Rebuild a new replica from the promoted primary
```

**SQLite recovery**:
```bash
# 1. Stop all servers
docker-compose stop

# 2. Restore the SQLite database from backup
cp /backup/trialmcp_latest.db /data/trialmcp.db

# 3. Verify database integrity
sqlite3 /data/trialmcp.db "PRAGMA integrity_check;"

# 4. Restart all servers
docker-compose up -d
```

### 6.4 Tier 4: Full Site Recovery

```bash
# 1. Provision new infrastructure (Kubernetes cluster)
# Follow docs/deployment/hospital-site.md for infrastructure setup

# 2. Deploy the MCP platform
helm install trialmcp deploy/helm/trialmcp/ \
  --namespace trialmcp \
  --values deploy/helm/trialmcp/values.yaml \
  -f site-values.yaml

# 3. Restore storage backend
# For PostgreSQL: restore from most recent backup
pg_restore -h new-db -d trialmcp /backup/trialmcp_latest.dump

# 4. Restore audit chain and verify integrity
# (see Section 3.3)

# 5. Restore provenance graph
# (see Section 4.3)

# 6. Restore authorization policies
# Import saved policies into the AuthZ server

# 7. Restore certificates and keys from KMS/HSM
# (see docs/operations/key-management.md)

# 8. Verify all servers
for port in 8001 8002 8003 8004 8005; do
  status=$(curl -sf "http://localhost:${port}/health" | jq -r '.status')
  echo "Port ${port}: ${status}"
done

# 9. Run conformance tests
python -m pytest conformance/positive/test_core_conformance.py -v

# 10. Run full audit chain verification
curl -sf http://localhost:8004/tools/call -d '{"tool": "ledger_verify"}' | jq '.'

# 11. Run provenance DAG verification
curl -sf http://localhost:8005/tools/call -d '{"tool": "provenance_verify"}' | jq '.'
```

### 6.5 Tier 5: Data Center Loss

1. Activate the disaster recovery site (if pre-provisioned) or provision new infrastructure in the alternate region
2. Retrieve offsite backups from S3/GCS/Azure Blob storage
3. Decrypt backups using the DR encryption key (stored separately from the primary site)
4. Follow Tier 4 procedures to restore all services
5. Update DNS/load balancer to point to the new site
6. Notify the National MCP Standards Technical Committee of the site relocation
7. Re-verify cross-site federation connectivity if applicable

---

## 7. Backup Verification

### 7.1 Automated Verification Schedule

| Verification | Frequency | Method |
|-------------|-----------|--------|
| Audit chain backup integrity | Daily | SHA-256 checksum + chain hash verification |
| Provenance backup integrity | Daily | SHA-256 checksum + DAG cycle check |
| Configuration backup completeness | Weekly | Diff against running config |
| Full restore test | Quarterly | Restore to isolated environment |
| Cross-site backup coordination | Quarterly | Verify shared ledger backups across sites |

### 7.2 Quarterly DR Drill Procedure

1. Provision an isolated test environment
2. Restore all data from the most recent backups
3. Verify audit chain integrity (zero hash mismatches)
4. Verify provenance DAG integrity (zero cycles)
5. Run full conformance test suite
6. Measure actual RTO against targets
7. Document results and any deviations
8. Update DR procedures based on findings

### 7.3 Backup Monitoring Alerts

| Alert Condition | Severity | Action |
|----------------|----------|--------|
| Daily backup not completed by 06:00 UTC | P3 | Investigate backup job failure |
| Backup integrity check failed | P2 | Re-run backup, investigate storage corruption |
| Backup storage utilization > 80% | P4 | Expand storage, review retention policy |
| DR drill RTO exceeded target | P3 | Review and optimize recovery procedures |
| Offsite replication lag > 1 hour | P3 | Check network connectivity and replication config |

---

## 8. Retention and Archival

### 8.1 Retention Policy

| Data Category | Active Retention | Archive Retention | Total |
|--------------|------------------|-------------------|-------|
| Audit chain | Duration of trial | 15 years post-trial | Trial + 15 years |
| Provenance DAG | Duration of trial | 15 years post-trial | Trial + 15 years |
| Authorization policies | Duration of trial | 5 years post-trial | Trial + 5 years |
| Server logs | 90 days | 6 years (HIPAA) | 6 years |
| Configuration | Duration of trial | 2 years post-trial | Trial + 2 years |
| Backup checksums | Same as source data | Same as source data | Same as source |

### 8.2 Archival Procedure

When a trial phase completes:

1. Export the complete audit chain with verification
2. Export the complete provenance DAG
3. Create a site certification evidence pack: `python -m tools.certification.evidence_pack`
4. Sign all archive files with the evidence signing key
5. Upload to long-term archival storage (AWS Glacier, Azure Archive, etc.)
6. Record the archive location and checksums in the trial master file
7. Verify the archive can be retrieved and decrypted

### 8.3 Data Destruction

At the end of the retention period:
1. Verify regulatory hold status -- do NOT destroy data under legal or regulatory hold
2. Obtain written authorization from the Site PI and Sponsor
3. Perform cryptographic erasure (destroy all copies of the encryption key)
4. Record the destruction event with timestamp and authorizer
5. Retain the destruction record indefinitely

---

*For key management including backup encryption keys, see `docs/operations/key-management.md`.*
*For incident response during recovery, see `docs/operations/incident-response.md`.*
*For operational procedures, see `docs/operations/runbook.md`.*
