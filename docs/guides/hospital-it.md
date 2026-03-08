# Hospital IT / Cancer Center Implementation Guide

**National MCP-PAI Oncology Trials Standard**
**Audience**: Hospital IT Directors, Biomedical Engineering, Clinical Informatics
**Version**: 0.1.0

---

## 1. Introduction

This guide provides Hospital IT departments and Cancer Center informatics teams with a
comprehensive checklist and operational reference for deploying the National MCP-PAI
Oncology Trials infrastructure at a clinical site. It covers infrastructure
prerequisites, network architecture, identity provider integration, EHR/PACS
connectivity, PHI boundary enforcement, monitoring, backup, and staff training.

All five MCP servers are in scope:

| Server | Port | Function |
|--------|------|----------|
| `trialmcp-authz` | 8001 | Authorization and RBAC policy enforcement |
| `trialmcp-fhir` | 8002 | FHIR R4 clinical data access with de-identification |
| `trialmcp-dicom` | 8003 | DICOMweb imaging query and retrieval |
| `trialmcp-ledger` | 8004 | Hash-chained audit ledger |
| `trialmcp-provenance` | 8005 | Data lineage and provenance tracking |

---

## 2. Site Deployment Checklist

### 2.1 Prerequisites

- [ ] IRB protocol approval obtained and documented (reference `deploy/config/site-profile-example.yaml` field `irb_approval`)
- [ ] Conformance level determined (1 through 5; see `spec/conformance.md`)
- [ ] Regulatory overlay(s) identified based on jurisdiction:
  - Federal: 21 CFR Part 11 (`profiles/country-us-fda.md`)
  - California sites: CCPA/CPRA (`profiles/state-us-ca.md`)
  - New York sites: PHL/SHIELD Act (`profiles/state-us-ny.md`)
- [ ] Site capability profile YAML drafted from template (`deploy/config/site-profile-example.yaml`)
- [ ] Data residency region selected (`data_residency.storage_region` in site profile)
- [ ] Robot inventory registered in site profile (`robots[]` array)
- [ ] Sponsor/CRO contact information exchanged
- [ ] Staff training plan approved (see Section 10)

### 2.2 Infrastructure Requirements

| Component | Minimum Specification |
|-----------|----------------------|
| Compute | 8 vCPU, 32 GB RAM per MCP server (production) |
| Storage | 500 GB SSD for ledger and provenance; sized to imaging volume for DICOM cache |
| Container Runtime | Docker 24+ or Kubernetes 1.28+ |
| Database | PostgreSQL 15+ (production) or SQLite (development only) |
| TLS Certificates | X.509 certificates from institution CA or public CA; RSA-2048 or ECDSA P-256 minimum |
| HSM / KMS | Required for HMAC-SHA256 pseudonymization salt and token signing keys |

### 2.3 Software Dependencies

- [ ] Container images built from `deploy/docker/Dockerfile.*` or pulled from registry
- [ ] Helm chart available at `deploy/helm/trialmcp/` for Kubernetes deployments
- [ ] Python 3.11+ installed for conformance test runner (`conformance/harness/runner.py`)
- [ ] JSON Schema validation libraries available for schema enforcement (`schemas/*.schema.json`)

---

## 3. Network Segmentation Requirements

### 3.1 Zone Architecture

The MCP deployment MUST be segmented into the following network zones:

```
                          +-----------------------+
                          |   EXTERNAL / WAN      |
                          | (Sponsor, CRO, Sites) |
                          +----------+------------+
                                     |
                              [Firewall / WAF]
                                     |
                          +----------v------------+
                          |     DMZ ZONE          |
                          | - API Gateway / LB    |
                          | - mTLS termination    |
                          +----------+------------+
                                     |
                              [Internal FW]
                                     |
              +----------------------v-----------------------+
              |              MCP SERVER ZONE                 |
              | trialmcp-authz    trialmcp-fhir              |
              | trialmcp-dicom    trialmcp-ledger             |
              | trialmcp-provenance                          |
              +----------------------+-----------------------+
                                     |
                              [Data FW]
                                     |
              +----------------------v-----------------------+
              |           CLINICAL DATA ZONE                 |
              | - EHR / FHIR R4 Server (HAPI, Epic, Cerner)  |
              | - PACS / DICOMweb (Orthanc, dcm4chee)        |
              | - Database (PostgreSQL)                      |
              +----------------------------------------------+
```

### 3.2 Firewall Rules

| Source Zone | Destination Zone | Ports | Protocol | Purpose |
|-------------|-----------------|-------|----------|---------|
| DMZ | MCP Server | 8001-8005 | HTTPS/mTLS | API traffic |
| MCP Server | Clinical Data | 443, 4242, 8080 | HTTPS, DICOM | Backend connectivity |
| MCP Server | MCP Server | 8001-8005 | HTTPS | Inter-server calls (authz validation) |
| External | DMZ | 443 | HTTPS | Cross-site federation |
| MCP Server | Identity Provider | 443 | HTTPS | OIDC token exchange |
| Any | Any | * | * | DENY (default) |

### 3.3 Robot Network Segment

Robot agents MUST communicate from a dedicated network segment. Traffic from the robot
VLAN to the MCP Server zone MUST be restricted to ports 8001-8005 over mTLS. The robot
segment MUST NOT have direct access to the Clinical Data zone.

---

## 4. PACS / EHR Integration Path

### 4.1 FHIR R4 Connectivity (EHR)

The `trialmcp-fhir` server connects to the institutional EHR via a FHIR R4 adapter.
Supported adapters are defined in `integrations/fhir/`:

| Adapter | Module | Use Case |
|---------|--------|----------|
| HAPI FHIR | `integrations/fhir/hapi_adapter.py` | Open-source HAPI FHIR server |
| SMART on FHIR | `integrations/fhir/smart_adapter.py` | Epic, Cerner, or SMART-enabled EHR |
| Mock | `integrations/fhir/mock_adapter.py` | Development and testing only |

**Configuration steps:**

1. Register the MCP platform as a SMART on FHIR client in the EHR vendor admin portal
2. Configure the FHIR base URL in `deploy/config/fhir.yaml`
3. Establish OAuth 2.0 client credentials for backend service authorization
4. Validate connectivity using the conformance test suite:
   ```bash
   pytest conformance/blackbox/test_fhir_conformance.py -v
   ```
5. Confirm de-identification pipeline operates correctly (`servers/trialmcp_fhir/deid_pipeline.py`):
   - HMAC-SHA256 pseudonymization with site-specific salt
   - Birth date reduced to year only
   - Direct identifiers removed per HIPAA Safe Harbor

### 4.2 DICOMweb Connectivity (PACS)

The `trialmcp-dicom` server connects to the institutional PACS via DICOMweb (WADO-RS,
STOW-RS, QIDO-RS). Supported adapters are in `integrations/dicom/`:

| Adapter | Module | Use Case |
|---------|--------|----------|
| Orthanc | `integrations/dicom/orthanc_adapter.py` | Orthanc DICOM server |
| dcm4chee | `integrations/dicom/dcm4chee_adapter.py` | dcm4chee Arc |
| DICOMweb generic | `integrations/dicom/dicomweb.py` | Any DICOMweb-compliant PACS |
| Mock | `integrations/dicom/mock_adapter.py` | Development and testing only |

**Configuration steps:**

1. Configure PACS DICOMweb endpoint in `deploy/config/dicom.yaml`
2. Register the MCP server as a DICOMweb consumer with the PACS administrator
3. Configure AE title and calling AE title if required
4. Validate connectivity:
   ```bash
   pytest conformance/blackbox/test_dicom_conformance.py -v
   ```
5. Confirm modality filtering and role-based restrictions operate correctly (`integrations/dicom/modality_filter.py`)

### 4.3 Integration Validation

Run the full cross-server integration tests after configuring both EHR and PACS:

```bash
pytest conformance/blackbox/test_cross_server_workflow.py -v
pytest conformance/integration/test_server_integration.py -v
```

---

## 5. PHI Boundary and Retention Controls

### 5.1 PHI Boundary Enforcement

PHI MUST NOT leave the Clinical Data zone in identifiable form. The following controls
enforce this boundary:

| Control | Implementation | Reference |
|---------|---------------|-----------|
| Pseudonymization | HMAC-SHA256 with site-specific salt | `servers/trialmcp_fhir/deid_pipeline.py` |
| Birth date reduction | Year-only representation | `integrations/fhir/deidentification.py` |
| Patient name hashing | SHA-256 truncated to 12 chars (DICOM) | `integrations/dicom/safety.py` |
| SSRF prevention | URL pattern rejection on all inputs | `servers/common/validation.py` |
| Search result caps | Maximum 100 results per query | `spec/tool-contracts.md` Section 4.2 |
| Consent enforcement | Consent status checked before data access | `schemas/consent-status.schema.json` |

### 5.2 Data Retention Policy

| Data Category | Minimum Retention | Maximum Retention | Authority |
|---------------|-------------------|-------------------|-----------|
| Audit ledger records | Duration of trial + 2 years | Per FDA predicate rule (often 15 years for biologics) | 21 CFR 11.10(c) |
| Provenance records | Duration of trial + 2 years | Co-terminus with audit records | ICH-GCP E6(R2) |
| FHIR query logs | Duration of trial | Per institutional policy | HIPAA |
| DICOM retrieval tokens | 1 hour (auto-expire) | Non-retained | System design |
| Authorization tokens | Session duration (default 3600s) | Non-retained after revocation | System design |

### 5.3 Data Residency

The `data_residency` block in the site profile (`deploy/config/site-profile-example.yaml`)
controls where data is stored. For multi-site federated trials, the privacy budget
tracker (`integrations/privacy/privacy_budget.py`) and data residency enforcer
(`integrations/privacy/data_residency.py`) prevent cross-boundary data leakage.

---

## 6. Identity Provider Integration

### 6.1 Supported Protocols

The MCP standard supports identity integration via the modules in `integrations/identity/`:

| Protocol | Module | Notes |
|----------|--------|-------|
| OpenID Connect (OIDC) | `integrations/identity/oidc_adapter.py` | Recommended for production |
| Mutual TLS (mTLS) | `integrations/identity/mtls.py` | Required for robot agent authentication |
| Policy engine | `integrations/identity/policy_engine.py` | Maps IdP claims to MCP roles |
| KMS integration | `integrations/identity/kms.py` | Key management for pseudonymization salts |

### 6.2 OIDC Configuration

1. Register the MCP platform as a relying party in your institutional IdP (Okta, Azure AD, Ping, Keycloak)
2. Configure the following OIDC claims mapping to MCP roles:

   | IdP Group / Claim | MCP Role | Description |
   |-------------------|----------|-------------|
   | `onc-trial-coordinator` | `trial_coordinator` | Clinical site staff |
   | `onc-data-monitor` | `data_monitor` | CRO/sponsor data reviewers |
   | `onc-auditor` | `auditor` | Compliance officers |
   | `onc-sponsor-admin` | `sponsor` | Sponsor organization |
   | `onc-cro-admin` | `cro` | CRO organization |

3. Robot agents authenticate via mTLS client certificates, not OIDC. Each robot MUST
   present a client certificate with a Subject CN matching its `robot_id` in the site profile.

### 6.3 Active Directory / LDAP

For sites using on-premises AD/LDAP:

1. Deploy an OIDC bridge (e.g., Keycloak with LDAP federation)
2. Map AD security groups to the OIDC claims listed above
3. Ensure token refresh intervals align with AD password expiry policies
4. Configure the `integrations/identity/oidc_adapter.py` with the bridge endpoint

### 6.4 Token Lifecycle

- Default token duration: 3600 seconds (configurable via `authz_issue_token`)
- Tokens MUST be revocable via `authz_revoke_token`
- Token hashes (not plaintext) are stored in the AuthZ server (`servers/trialmcp_authz/token_store.py`)
- All token operations are recorded in the audit ledger

---

## 7. Monitoring and Alerting

### 7.1 Health Endpoints

Each MCP server exposes a health check endpoint (see `servers/common/health.py`). Monitor
these endpoints at 30-second intervals:

| Server | Endpoint | Expected Response |
|--------|----------|-------------------|
| trialmcp-authz | `GET /health` | `{"status": "ok", "version": "..."}` |
| trialmcp-fhir | `GET /health` | `{"status": "ok", "version": "..."}` |
| trialmcp-dicom | `GET /health` | `{"status": "ok", "version": "..."}` |
| trialmcp-ledger | `GET /health` | `{"status": "ok", "version": "..."}` |
| trialmcp-provenance | `GET /health` | `{"status": "ok", "version": "..."}` |

### 7.2 Critical Alerts

Configure alerts for the following conditions:

| Condition | Severity | Response SLA |
|-----------|----------|-------------|
| Any MCP server health check failure | Critical | 15 minutes |
| Audit chain integrity failure (`ledger_verify` returns `valid: false`) | Critical | Immediate |
| E-stop signal triggered (`safety/estop.py`) | Critical | Immediate |
| Token issuance rate exceeds 100/minute | Warning | 1 hour |
| FHIR/DICOM backend connectivity loss | Critical | 30 minutes |
| Database storage exceeds 80% capacity | Warning | 24 hours |
| TLS certificate expiry within 30 days | Warning | 7 days |
| Failed safety gate evaluation (`safety/gate_service.py`) | High | 30 minutes |

### 7.3 Logging

All MCP servers use structured logging (`servers/common/logging.py`). Configure log
aggregation (ELK, Splunk, CloudWatch) to capture:

- All tool invocations and their outcomes
- Authorization decisions (allow/deny)
- Error conditions and stack traces
- Performance metrics (latency, throughput)

Logs MUST NOT contain PHI. The de-identification pipeline ensures that log entries
reference pseudonymized identifiers only.

---

## 8. Data Backup and Recovery

### 8.1 Backup Scope

| Component | Backup Method | Frequency | Retention |
|-----------|--------------|-----------|-----------|
| PostgreSQL database (ledger, provenance) | pg_dump with WAL archiving | Continuous (WAL) + daily full | Per retention policy (Section 5.2) |
| Site profile YAML | Version-controlled in institutional repo | On change | Indefinite |
| TLS certificates and keys | HSM backup procedures | On issuance | Until expiry + 1 year |
| HMAC pseudonymization salt | KMS key backup | On creation | Duration of trial |
| Container images | Registry retention policy | On build | 3 prior versions minimum |
| Conformance test results | Evidence pack export | On each test run | Duration of trial + 2 years |

### 8.2 Recovery Procedures

**Scenario 1: Single MCP server failure**
1. Restart the container from the existing image
2. Verify health check returns `ok`
3. Run `ledger_chain_status` to confirm audit chain integrity
4. Resume operations

**Scenario 2: Database corruption**
1. Stop all MCP servers
2. Restore PostgreSQL from the most recent WAL-consistent backup
3. Restart all servers
4. Run `ledger_verify` across the full chain
5. Run the conformance test suite to validate system integrity
6. Document the incident and recovery in the audit ledger

**Scenario 3: Complete site recovery**
1. Provision new infrastructure per Section 2.2
2. Deploy container images from registry
3. Restore database from backup
4. Restore site profile YAML from version control
5. Re-import TLS certificates and pseudonymization salt from KMS/HSM
6. Run full conformance suite (`conformance/`)
7. Notify sponsor/CRO of the recovery event

### 8.3 Recovery Point Objective (RPO) and Recovery Time Objective (RTO)

| Scenario | RPO | RTO |
|----------|-----|-----|
| Single server failure | 0 (stateless restart) | 5 minutes |
| Database failure | Last WAL segment (< 5 minutes) | 30 minutes |
| Complete site recovery | Last daily backup | 4 hours |

---

## 9. Deployment Methods

### 9.1 Docker Compose (Single Site)

For initial deployment or smaller sites, use the provided Docker Compose configuration:

```bash
cd deploy/
cp .env.example .env
# Edit .env with site-specific values
docker-compose up -d
```

Reference: `deploy/docker-compose.yml`

### 9.2 Kubernetes / Helm (Production)

For production deployments, use the Helm chart:

```bash
helm install trialmcp deploy/helm/trialmcp/ \
  --namespace trialmcp \
  --values deploy/helm/trialmcp/values.yaml \
  -f site-values.yaml
```

Kubernetes manifests for individual servers are available in `deploy/kubernetes/`:
- `deployment-authz.yaml`
- `deployment-fhir.yaml`
- `deployment-dicom.yaml`
- `deployment-ledger.yaml`
- `deployment-provenance.yaml`

### 9.3 Multi-Site Federation

For sites participating in federated trials, use the multi-site Docker Compose
configuration as a starting reference: `deploy/docker-compose.multi-site.yml`

The federation coordination layer (`integrations/federation/coordinator.py`) handles
cross-site communication, and the policy enforcement module
(`integrations/federation/policy_enforcement.py`) ensures data residency compliance.

---

## 10. Staff Training Requirements

### 10.1 Required Training by Role

| Role | Training Topics | Frequency |
|------|----------------|-----------|
| IT Operations | MCP server deployment, monitoring, backup/recovery, incident response | Initial + annual |
| Clinical Informatics | FHIR R4 integration, de-identification pipeline, consent workflow | Initial + annual |
| Biomedical Engineering | Robot network segment, mTLS certificate management, e-stop procedures | Initial + annual |
| Information Security | RBAC policy configuration, token lifecycle, audit review, penetration testing | Initial + annual |
| Help Desk | Basic MCP troubleshooting, escalation procedures, health check interpretation | Initial + semi-annual |

### 10.2 Training Documentation

- System architecture overview: `docs/architecture.md`
- MCP process workflows: `docs/mcp-process/` (7 process documents)
- Glossary of terms: `docs/glossary.md`
- Adoption roadmap: `docs/adoption-roadmap.md`
- Quickstart demo: `examples/quickstart/`

### 10.3 Competency Verification

All IT staff with access to MCP infrastructure MUST demonstrate competency through:

1. Successful completion of training modules
2. Supervised deployment of the interop testbed (`interop-testbed/`)
3. Execution of a site onboarding scenario (`interop-testbed/scenarios/site_onboarding.py`)
4. Documented acknowledgment of PHI handling responsibilities

---

## 11. Pre-Go-Live Validation Checklist

- [ ] All five MCP servers pass health checks
- [ ] `ledger_chain_status` reports `chain_valid: true` with correct genesis hash
- [ ] Conformance tests pass for declared level (`conformance/positive/`)
- [ ] Security tests pass (`conformance/security/`)
- [ ] Adversarial tests pass (`conformance/adversarial/`)
- [ ] FHIR backend connectivity verified with live EHR
- [ ] DICOM backend connectivity verified with live PACS
- [ ] Identity provider integration tested with all six actor roles
- [ ] Robot agent mTLS authentication tested
- [ ] Monitoring and alerting confirmed operational
- [ ] Backup and recovery procedures tested
- [ ] Site profile YAML reviewed and approved by sponsor/CRO
- [ ] Evidence pack generated (`tools/certification/evidence_pack.py`)
- [ ] Staff training completed and documented
- [ ] IRB approval documentation on file
- [ ] Regulatory overlay requirements reviewed and attested
