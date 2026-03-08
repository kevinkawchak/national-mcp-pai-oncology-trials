# Repository Statistics and Quantitative Summary

**National MCP-PAI Oncology Trials Standard**
**Version**: 1.0.1 | **Status**: Published for Review
**Data Source**: Repository-reported metrics derived from repository contents as of v1.0.1.

---

## Executive Summary

The National MCP-PAI Oncology Trials Standard repository contains 381 files across 88 directories, comprising approximately 69,800 lines of code and documentation. The repository implements 5 MCP servers exposing 23 tools, validated by 668 test functions across 10 conformance categories. It defines 13 machine-readable JSON schemas, 8 conformance profiles, 7 architectural decision records, and 34 integration adapters spanning FHIR, DICOM, federated learning, identity, privacy, and clinical systems. The infrastructure supports 6 deployment targets (individual Docker containers, all-in-one Docker, Docker Compose single-site, Docker Compose multi-site, Kubernetes manifests, and Helm charts) with SDKs in both Python and TypeScript.

This is one of the most comprehensive open-source MCP standard repositories for healthcare AI infrastructure currently available, and is the first to specifically target Physical AI oncology clinical trials at a national scale.

---

## 1. Repository Scale and Scope

### File and Directory Counts (Repository-Reported)

| Metric | Count |
|--------|------:|
| Total files | 381 |
| Total directories | 88 |
| Python files (.py) | 204 |
| TypeScript files (.ts) | 30 |
| Markdown files (.md) | 84 |
| JSON files (.json) | 21 |
| YAML/YML files (.yaml, .yml) | 26 |
| Jinja2 templates (.j2) | 3 |
| TOML files (.toml) | 2 |
| Dockerfiles | 6 |
| JavaScript files (.js) | 1 |

### Lines of Code by Language (Repository-Reported)

| Language | Approximate Lines |
|----------|------------------:|
| Python | 35,027 |
| TypeScript | 6,924 |
| Markdown | 24,243 |
| YAML/YML | 1,784 |
| JSON | 1,644 |
| **Total (all tracked files)** | **~69,800** |

Python accounts for approximately 50% of the codebase, reflecting the primary implementation language for servers, safety modules, integration adapters, conformance tests, and tooling. Markdown accounts for approximately 35%, reflecting the standard's emphasis on normative specification, governance, regulatory overlays, and stakeholder documentation.

---

## 2. MCP Servers

### Server Count and Types (Repository-Reported)

The repository implements **5 domain-specific MCP servers** plus shared infrastructure:

| Server | Directory | Domain |
|--------|-----------|--------|
| Authorization Server | `servers/trialmcp_authz/` | RBAC, token lifecycle, policy evaluation |
| FHIR Server | `servers/trialmcp_fhir/` | Clinical data access, patient lookup, study status |
| DICOM Server | `servers/trialmcp_dicom/` | Imaging queries, study metadata, RECIST measurements |
| Ledger Server | `servers/trialmcp_ledger/` | Hash-chained audit trail, chain verification, replay |
| Provenance Server | `servers/trialmcp_provenance/` | DAG lineage, data source tracking, fingerprinting |
| Common Utilities | `servers/common/` | Shared validators, SSRF prevention, error handling |
| Storage Layer | `servers/storage/` | Persistence abstraction |

---

## 3. Tools

### Tool Count and Distribution by Server (Repository-Reported)

The standard defines **23 tools** distributed across the 5 MCP servers:

| Server | Tool Count | Tools |
|--------|:----------:|-------|
| Authorization | 5 | `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_list_policies`, `authz_revoke_token` |
| FHIR | 4 | `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status` |
| DICOM | 4 | `dicom_query`, `dicom_retrieve_pointer`, `dicom_study_metadata`, `dicom_recist_measurements` |
| Ledger | 5 | `ledger_append`, `ledger_verify`, `ledger_query`, `ledger_replay`, `ledger_export` |
| Provenance | 5 | `provenance_record`, `provenance_query_forward`, `provenance_query_backward`, `provenance_fingerprint`, `provenance_lineage` |
| **Total** | **23** | |

Each tool has a normative contract defined in `spec/tool-contracts.md` specifying input parameters, output shape, error codes, and audit requirements.

---

## 4. Schemas

### Schema Count and Categories (Repository-Reported)

The repository defines **13 machine-readable JSON schemas** in `schemas/`:

| Schema | Category | Validates |
|--------|----------|-----------|
| `audit-record.schema.json` | Audit | Audit trail entries |
| `authz-decision.schema.json` | Authorization | RBAC evaluation results |
| `capability-descriptor.schema.json` | Infrastructure | MCP server capability declarations |
| `consent-status.schema.json` | Privacy | Patient consent state |
| `dicom-query.schema.json` | Imaging | DICOM query parameters and results |
| `error-response.schema.json` | Infrastructure | Standardized error envelopes |
| `fhir-read.schema.json` | Clinical | FHIR resource read responses |
| `fhir-search.schema.json` | Clinical | FHIR search bundle responses |
| `health-status.schema.json` | Infrastructure | Server health check responses |
| `provenance-record.schema.json` | Provenance | DAG lineage records |
| `robot-capability-profile.schema.json` | Robotics | Robot system capability declarations |
| `site-capability-profile.schema.json` | Infrastructure | Site-level capability declarations |
| `task-order.schema.json` | Robotics | Procedure task orders for robotic systems |

**Category breakdown**: 3 Infrastructure, 2 Clinical, 2 Robotics, 2 Audit/Authorization, 2 Imaging/Provenance, 1 Privacy, 1 Error handling.

---

## 5. Profiles

### Profile Count and Types (Repository-Reported)

The repository defines **8 conformance profiles** in `profiles/`:

| Profile | Level | Scope |
|---------|:-----:|-------|
| `base-profile.md` | 1 | Core authorization + audit (minimum viable) |
| `clinical-read.md` | 2 | FHIR clinical data access + de-identification |
| `imaging-guided-oncology.md` | 3 | DICOM imaging + RECIST measurements |
| `multi-site-federated.md` | 4 | Cross-site coordination + federated learning |
| `robot-assisted-procedure.md` | 5 | Full robotic procedure lifecycle |
| `country-us-fda.md` | Regulatory | US FDA overlay (21 CFR Part 11) |
| `state-us-ca.md` | Regulatory | California state overlay (CCPA/CMIA) |
| `state-us-ny.md` | Regulatory | New York state overlay |

**Breakdown**: 5 conformance levels (hierarchical, each level includes all lower levels) + 3 regulatory overlay profiles.

---

## 6. Tests

### Total Test Count (Repository-Reported)

| Suite | Test Functions |
|-------|---------------:|
| Unit tests (`tests/`) | 337 |
| Conformance tests (`conformance/`) | 331 |
| **Total** | **668** |

### Unit Test Breakdown by File (Repository-Reported)

| Test File | Test Functions | Validates |
|-----------|---------------:|-----------|
| `test_integrations.py` | 205 | All 34 integration adapters |
| `test_safety.py` | 88 | All 8 safety modules |
| `test_core_server.py` | 32 | 5 MCP server implementations |
| `test_conformance_runner.py` | 6 | Conformance harness infrastructure |
| `test_schema_validator.py` | 6 | JSON schema validation utilities |

### Conformance Test Breakdown by Category (Repository-Reported)

| Category | Directory | Test Functions | Validates |
|----------|-----------|---------------:|-----------|
| Positive | `conformance/positive/` | 69 | Correct behavior across conformance levels |
| Adversarial | `conformance/adversarial/` | 57 | Attack resistance and abuse prevention |
| Blackbox | `conformance/blackbox/` | 63 | Per-server external conformance |
| Security | `conformance/security/` | 39 | SSRF, token lifecycle, chain integrity |
| Interoperability | `conformance/interoperability/` | 32 | Cross-server trace and schema validation |
| Fixture Construction | `conformance/fixtures/` | 32 | Test data integrity |
| Negative | `conformance/negative/` | 26 | Invalid input rejection |
| Integration | `conformance/integration/` | 13 | Multi-server integration |

### Conformance Test Breakdown by File (Repository-Reported)

| Test File | Functions | Category |
|-----------|----------:|----------|
| `test_core_conformance.py` | 26 | Positive (Level 1) |
| `test_clinical_read_conformance.py` | 20 | Positive (Level 2) |
| `test_imaging_conformance.py` | 23 | Positive (Level 3) |
| `test_cross_server_trace.py` | 15 | Interoperability |
| `test_schema_validation.py` | 17 | Interoperability |
| `test_chain_integrity.py` | 16 | Security |
| `test_token_lifecycle.py` | 16 | Security |
| `test_ssrf_prevention.py` | 7 | Security |
| `test_invalid_inputs.py` | 14 | Negative |
| `test_unauthorized_access.py` | 12 | Negative |
| `test_authz_bypass.py` | 9 | Adversarial |
| `test_chain_tampering.py` | 12 | Adversarial |
| `test_malformed_inputs.py` | 12 | Adversarial |
| `test_phi_leakage.py` | 10 | Adversarial |
| `test_rate_limiting.py` | 7 | Adversarial |
| `test_replay_attacks.py` | 7 | Adversarial |
| `test_authz_conformance.py` | 11 | Blackbox |
| `test_cross_server_workflow.py` | 8 | Blackbox |
| `test_dicom_conformance.py` | 10 | Blackbox |
| `test_fhir_conformance.py` | 11 | Blackbox |
| `test_ledger_conformance.py` | 11 | Blackbox |
| `test_provenance_conformance.py` | 12 | Blackbox |
| `test_server_integration.py` | 13 | Integration |
| `test_fixture_construction.py` | 32 | Fixtures |

### Test Type Coverage Summary

- **Unit tests**: 337 functions covering server implementations, integration adapters, safety modules, and infrastructure.
- **Positive conformance tests**: 69 functions validating correct behavior at Levels 1-3.
- **Negative conformance tests**: 26 functions validating rejection of invalid inputs and unauthorized access.
- **Security conformance tests**: 39 functions validating SSRF prevention, token lifecycle, and chain integrity.
- **Adversarial tests**: 57 functions validating resistance to authorization bypass, chain tampering, PHI leakage, rate limit abuse, and replay attacks.
- **Blackbox tests**: 63 functions validating per-server external conformance for all 5 MCP servers.
- **Interoperability tests**: 32 functions validating cross-server trace linkage and schema validation.
- **Integration tests**: 13 functions validating multi-server integration scenarios.

---

## 7. Integration Adapters

### Adapter Count and Categories (Repository-Reported)

The repository implements **34 integration adapter modules** across 6 categories in `integrations/`:

| Category | Directory | Modules | Key Adapters |
|----------|-----------|:-------:|--------------|
| FHIR | `integrations/fhir/` | 9 | HAPI FHIR, SMART on FHIR, de-identification, terminology, patient filter, bundle handler, capability |
| DICOM | `integrations/dicom/` | 9 | dcm4chee, Orthanc, DICOMweb, RECIST, modality filter, metadata normalizer, safety |
| Clinical | `integrations/clinical/` | 3 | Scheduling, e-consent, provenance export |
| Federation | `integrations/federation/` | 4 | Coordinator, policy enforcement, secure aggregation, site harmonization |
| Identity | `integrations/identity/` | 5 | OIDC, mTLS, KMS, policy engine, base adapter |
| Privacy | `integrations/privacy/` | 4 | De-identification pipeline, privacy budget, data residency, access control |
| **Total** | | **34** | |

---

## 8. Safety Modules

### Safety Module Count and Categories (Repository-Reported)

The repository implements **8 safety modules** in `safety/`:

| Module | Purpose |
|--------|---------|
| `estop.py` | Emergency stop coordination for robotic systems |
| `procedure_state.py` | Procedure state machine enforcement |
| `robot_registry.py` | Robot registration and capability validation |
| `task_validator.py` | Task order validation against safety constraints |
| `gate_service.py` | Safety gate evaluation service |
| `approval_checkpoint.py` | Multi-party approval checkpoints |
| `site_verifier.py` | Site capability verification |
| `__init__.py` | Module initialization and exports |

All 8 modules are validated by 88 unit test functions in `tests/test_safety.py`.

---

## 9. Benchmark and Certification Tooling

### Benchmark Count (Repository-Reported)

The repository provides **5 benchmark modules** in `benchmarks/`:

| Benchmark | Measures |
|-----------|----------|
| `latency_benchmark.py` | Per-tool response latency |
| `throughput_benchmark.py` | Requests per second under load |
| `concurrent_benchmark.py` | Concurrent session performance |
| `chain_benchmark.py` | Hash chain verification throughput |
| `report.py` | Benchmark report generation |

### Certification Tooling Count (Repository-Reported)

The repository provides **4 certification modules** in `tools/certification/`:

| Tool | Purpose |
|------|---------|
| `evidence_pack.py` | Generate conformance evidence packages |
| `report_generator.py` | Generate certification reports |
| `schema_diff.py` | Schema compatibility checking |
| `site_certification.py` | Site-level certification validation |

---

## 10. Deployment Targets and Infrastructure

### Deployment Modes (Repository-Reported)

The repository supports **6 deployment configurations**:

| Mode | Artifacts | Use Case |
|------|-----------|----------|
| Individual Docker containers | 5 Dockerfiles in `deploy/docker/` | Per-server deployment |
| All-in-one Docker | `deploy/docker/Dockerfile.allinone` | Single-container evaluation |
| Docker Compose (single-site) | `deploy/docker-compose.yml` | Single-site deployment |
| Docker Compose (multi-site) | `deploy/docker-compose.multi-site.yml` | Multi-site federated deployment |
| Kubernetes | 7 manifests in `deploy/kubernetes/` | Production Kubernetes clusters |
| Helm | Chart in `deploy/helm/trialmcp/` | Templated Kubernetes deployment |

### Per-Server Dockerfiles

| Dockerfile | Server |
|------------|--------|
| `Dockerfile.authz` | Authorization server |
| `Dockerfile.fhir` | FHIR server |
| `Dockerfile.dicom` | DICOM server |
| `Dockerfile.ledger` | Ledger server |
| `Dockerfile.provenance` | Provenance server |
| `Dockerfile.allinone` | All servers combined |

### Configuration Files

6 server configuration files in `deploy/config/` (one per server plus a site profile example).

---

## 11. Interoperability Testbed

### Scenario Count (Repository-Reported)

The interoperability testbed in `interop-testbed/` contains **8 scenarios** and **6 actor personas**:

| Scenario | Validates |
|----------|-----------|
| `audit_replay.py` | Audit trail replay across sites |
| `cross_site_provenance.py` | Cross-site provenance chain integrity |
| `partial_outage.py` | Graceful degradation during partial failures |
| `robot_workflow.py` | End-to-end robotic procedure workflow |
| `schema_drift.py` | Schema version compatibility |
| `site_onboarding.py` | New site onboarding workflow |
| `state_overlay.py` | State-level regulatory overlay application |
| `token_exchange.py` | Cross-site token exchange |

| Persona | Actor |
|---------|-------|
| `robot_agent.yaml` | Autonomous robotic system |
| `trial_coordinator.yaml` | Clinical site coordinator |
| `data_monitor.yaml` | CRO/sponsor data reviewer |
| `auditor.yaml` | Compliance officer |
| `sponsor.yaml` | Trial sponsor organization |
| `cro.yaml` | Contract research organization |

---

## 12. Specification and Governance

### Specification Documents (Repository-Reported)

9 normative specification files in `spec/`:

| Document | Scope |
|----------|-------|
| `core.md` | Protocol scope, design principles, 5 conformance levels |
| `actor-model.md` | 6 actors, permission matrices, trust levels |
| `tool-contracts.md` | 23 tool signatures, input/output contracts, error codes |
| `security.md` | Deny-by-default RBAC, mTLS, OIDC, SSRF prevention |
| `privacy.md` | HIPAA Safe Harbor, de-identification, consent, data residency |
| `provenance.md` | DAG lineage, SHA-256 fingerprinting, forward/backward queries |
| `audit.md` | Hash-chained ledger, genesis hash, 21 CFR Part 11 mapping |
| `conformance.md` | 5 conformance levels, MUST/SHOULD/MAY per level |
| `versioning.md` | SemVer, compatibility, extension namespace, deprecation |

### Architectural Decision Records (Repository-Reported)

7 ADRs in `docs/adr/`:

1. MCP protocol boundary decisions
2. Five-server architecture rationale
3. Twenty-three tool selection
4. Profile conformance level design
5. Hash-chained audit approach
6. DAG provenance model
7. Deny-by-default RBAC policy

### Governance Documents (Repository-Reported)

- 5 files in `governance/`: charter, decision process, extensions, version compatibility, CODEOWNERS
- 6 files in `docs/governance/`: compatibility matrix, contribution policy, decision log, implementation status, known gaps, roadmap

### Regulatory Overlays (Repository-Reported)

4 regulatory documents in `regulatory/`: US FDA, HIPAA, 21 CFR Part 11, IRB site policy template.

3 regulatory profile overlays in `profiles/`: US FDA, California, New York.

### Stakeholder Guides (Repository-Reported)

5 stakeholder-specific guides in `docs/guides/`: hospital IT, regulator/IRB, robot vendor, sponsor/CRO, standards community.

### Operational Documentation (Repository-Reported)

5 operational documents in `docs/operations/`: backup/recovery, incident response, key management, runbook, SLO guidance.

### Walkthroughs (Repository-Reported)

5 profile-level walkthroughs in `docs/walkthroughs/`: base profile, clinical read, imaging-guided, multi-site federated, robot procedure.

---

## 13. SDK and Tooling

### SDK Coverage (Repository-Reported)

| SDK | Language | Modules | Middleware |
|-----|----------|:-------:|:----------:|
| `sdk/python/` | Python | 8 client modules | 4 (audit, auth, circuit breaker, retry) |
| `sdk/typescript/` | TypeScript | 8 client modules | 4 (audit, auth, circuit breaker, retry) |

Each SDK provides typed clients for all 5 MCP servers, role-scoped examples for all 6 actor types, and middleware for audit logging, authentication, circuit breaking, and retry.

### Tooling (Repository-Reported)

| Tool Category | Directory | Modules |
|---------------|-----------|:-------:|
| CLI | `tools/cli/` | 1 (trialmcp_cli.py) |
| Code generation | `tools/codegen/` | 3 generators + 3 templates |
| Certification | `tools/certification/` | 4 modules |
| **Total** | | **11** |

Code generation targets: OpenAPI specification, Python models, TypeScript interfaces.

---

## 14. Key Quantitative Summary

| Category | Count |
|----------|------:|
| MCP servers | 5 |
| Tools across all servers | 23 |
| JSON schemas | 13 |
| Conformance profiles | 8 |
| Test functions (total) | 668 |
| Unit test functions | 337 |
| Conformance test functions | 331 |
| Adversarial test functions | 57 |
| Security test functions | 39 |
| Integration adapters | 34 |
| Safety modules | 8 |
| Benchmark modules | 5 |
| Certification tools | 4 |
| Deployment modes | 6 |
| Interoperability scenarios | 8 |
| Actor personas | 6 |
| Specification documents | 9 |
| ADRs | 7 |
| Regulatory overlays | 7 |
| Stakeholder guides | 5 |
| Operational documents | 5 |
| Walkthroughs | 5 |
| Governance documents | 11 |
| Total files | 381 |
| Total directories | 88 |
| Total lines of code (approx.) | ~69,800 |

---

## 15. Key Takeaways

### Technical Maturity Signals

1. **668 test functions** across unit, conformance, adversarial, blackbox, security, interoperability, and integration categories indicate systematic quality assurance. The test-to-source ratio is high for a specification repository.

2. **8 conformance test categories** (positive, negative, security, adversarial, blackbox, interoperability, integration, fixture) provide layered validation that goes beyond basic functional testing into security posture, attack resistance, and multi-system interoperability.

3. **13 machine-readable JSON schemas** enable automated validation and code generation. All server outputs are validated against these schemas in the interoperability test suite.

4. **34 integration adapters** across 6 categories (FHIR, DICOM, clinical, federation, identity, privacy) demonstrate the standard's commitment to real-world interoperability rather than abstract specification.

5. **6 deployment modes** from single-container evaluation to Helm-templated Kubernetes deployment reflect production-readiness considerations.

6. **Dual-language SDKs** (Python and TypeScript) with matching middleware stacks (audit, auth, circuit breaker, retry) lower the barrier to adoption for both backend and frontend teams.

### National Interoperability Significance

The quantitative profile demonstrates several properties relevant to national-scale adoption:

- **Multi-actor RBAC** covering 6 actor types with 23-tool permission matrices enables fine-grained access control across organizational boundaries.
- **5 hierarchical conformance levels** allow sites to adopt incrementally based on their capabilities, from basic authorization and audit (Level 1) through full robotic procedure orchestration (Level 5).
- **3 regulatory overlay profiles** (US FDA, California, New York) demonstrate the standard's approach to jurisdictional compliance variation.
- **8 interoperability scenarios** including cross-site provenance, partial outage, and schema drift validate the standard's resilience under realistic multi-site conditions.
- **Federated learning integration** (coordinator, policy enforcement, secure aggregation, site harmonization) addresses the multi-institutional data collaboration requirements of national oncology trials.

### MCP Ecosystem Significance

For practitioners working in the MCP ecosystem:

- This repository demonstrates how to structure an MCP-based standard with normative specifications, conformance levels, and machine-readable schemas.
- The 5-server architecture with 23 tools provides a reference for domain-specific MCP server decomposition in regulated industries.
- The conformance test harness (with HTTP, stdin, Docker, and auth adapters) provides a reusable pattern for MCP conformance validation.
- The hash-chained audit trail and DAG provenance model demonstrate how MCP infrastructure can satisfy regulatory requirements (21 CFR Part 11, HIPAA).

### Physical AI Clinical Trial Significance

For the Physical AI oncology trials domain:

- **8 safety modules** covering emergency stop, procedure state machines, approval checkpoints, and task validation address the unique safety requirements of robotic systems in clinical settings.
- **Robot capability profile schema** and **task order schema** provide machine-readable contracts between MCP infrastructure and robotic systems.
- **57 adversarial test functions** specifically targeting authorization bypass, chain tampering, PHI leakage, rate limiting, and replay attacks demonstrate security-first design for safety-critical applications.
- The standard's positioning as a national reference for Physical AI oncology trials is unique in the current MCP ecosystem.

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

### Related Repositories

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation (single-site proof of concept)
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework with USL scoring and patient instructions
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework with privacy and regulatory modules
