# Changelog

All notable changes to the National MCP-PAI Oncology Trials Standard are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) as described in [spec/versioning.md](spec/versioning.md).

---

## [1.2.0] - 2026-03-11

### Added
- `site/` - GitHub Pages demonstration: "Demonstration: National MCP Servers for Physical AI Oncology Clinical Trial Systems"
- `site/index.html` - Main landing page (single-page application) with 11 sections
- `site/css/style.css` - Core styles (medical/clinical design system, light-mode only)
- `site/css/diagrams.css` - Diagram-specific styles and animations
- `site/js/app.js` - Main application logic, navigation, scroll behavior
- `site/js/diagrams.js` - Interactive diagram rendering engine (7 process diagrams)
- `site/js/simulator.js` - National deployment topology simulator (deterministic)
- `site/js/conformance.js` - Conformance level explorer with interactive 5-level hierarchy
- `site/data/topology.json` - National 3-tier deployment topology data (750+ sites)
- `site/data/servers.json` - 5 MCP server metadata, 23 tools, schemas
- `site/data/safety.json` - 8 safety module definitions and state machines
- `site/.nojekyll` - Bypass Jekyll processing
- `site/Demonstration National MCP Servers for Physical AI Oncology Clinical Trial Systems.pdf` - PDF version of the GitHub page

### Changed
- `README.md` - Added GitHub Pages Demonstration section, updated badges to v1.2.0, added site/ to repository structure
- `pyproject.toml` - Version 1.2.0, updated description
- `changelog.md` - This entry
- `releases.md` - Added v1.2.0 release notes
- `prompts.md` - Archived v1.2.0 GitHub Pages generation prompt

---

## [1.1.0] - 2026-03-09

### Added
- `paper/` — 20-page LaTeX paper "National MCP Servers for Physical AI Oncology Clinical Trial Systems"
- `paper/National_MCP_Servers_for_Physical_AI_Oncology_Clinical_Trial_Systems.tex` — Main LaTeX document
- `paper/arxiv.sty` — Modified arxiv-style template (removed "A Preprint" header)
- `paper/references.bib` — BibTeX bibliography with all references
- `paper/README` — LaTeX compilation instructions
- `paper/National_MCP_Servers_for_Physical_AI_Oncology_Clinical_Trial_Systems.pdf` — Compiled 20-page PDF
- `paper/Latex Source Code.zip` — Zip archive containing .tex, .sty, .bib, and README
- `paper/orcid_icon.pdf` — ORCID icon for author identification

### Changed
- `pyproject.toml` — Version 1.1.0, updated description
- `prompts.md` — Archived v1.1.0 paper generation prompt
- `releases.md` — Added v1.1.0 release notes
- `changelog.md` — This entry
- `README.md` — Added paper section with Zenodo DOI link, updated version badge and repository structure

---

- @kevinkawchak main README organizational changes and ASCII diagram fixes. main/paper directory additions and updates. main/peer-review re-organization. 2026-03-09

---

## [1.0.1] — 2026-03-08

### Fixed
- `stats.md` — Corrected version from 0.1.0 to 1.0.1 throughout the document
- `next-steps.md` — Corrected version from 0.1.0 to 1.0.1 throughout the document
- `README.md` — Corrected header version from 0.9.0 to 1.0.1
- `README.md` — Corrected Version badge from 0.9.0 to 1.0.1
- `README.md` — Corrected Unit Tests badge from 44 to 337
- `README.md` — Corrected Conformance Tests badge from 457 to 331
- `README.md` — Corrected Integration Adapters badge from 42 to 34
- `README.md` — Corrected Safety Modules badge from 7 to 8
- `README.md` — Corrected Updated date badge from 2026-03-07 to 2026-03-08
- `README.md` — Corrected all inline test count references (44 → 337 unit, 457 → 331 conformance, 501 → 668 total)
- `README.md` — Updated CI pipeline documentation from 9 jobs to 14 jobs with all job names
- `README.md` — Updated unit test summary table to include test_integrations.py (205 tests) and test_safety.py (88 tests)
- `README.md` — Updated repository structure to include sdk/, tools/cli/, tools/codegen/, and docs/ subdirectories
- `README.md` — Updated conformance test suite description with accurate test count

### Changed
- `pyproject.toml` — Version 1.0.1, updated description
- `prompts.md` — Archived v1.0.1 prompt (Original Prompt + Follow-up Prompt)
- `releases.md` — Added v1.0.1 release notes
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly across all Python files
- All existing 668 tests continue to pass
- All badge counts match repository-reported metrics in stats.md
- All documentation versions are internally consistent at v1.0.1

---

@kevinkawchak v1.0.0 (2nd Prompt) and v1.0.1 prompts.md additions 2026-03-08

---

## [1.0.0] — 2026-03-08

### Added

#### Python SDK
- `sdk/python/trialmcp_client/__init__.py` — Package initialization with key exports
- `sdk/python/trialmcp_client/client.py` — Unified MCP client with connection management, retry logic, circuit breaker
- `sdk/python/trialmcp_client/authz.py` — AuthZ client (evaluate, issue_token, validate_token, revoke_token)
- `sdk/python/trialmcp_client/fhir.py` — FHIR client (read, search, patient_lookup, study_status)
- `sdk/python/trialmcp_client/dicom.py` — DICOM client (query, retrieve)
- `sdk/python/trialmcp_client/ledger.py` — Ledger client (append, verify, query, export)
- `sdk/python/trialmcp_client/provenance.py` — Provenance client (record, query_forward, query_backward, verify)
- `sdk/python/trialmcp_client/models.py` — Re-exported typed models
- `sdk/python/trialmcp_client/exceptions.py` — 9-code error taxonomy exception hierarchy
- `sdk/python/trialmcp_client/config.py` — Client configuration
- `sdk/python/trialmcp_client/middleware/auth_middleware.py` — Automatic token management and refresh
- `sdk/python/trialmcp_client/middleware/audit_middleware.py` — Client-side audit logging
- `sdk/python/trialmcp_client/middleware/retry_middleware.py` — Configurable retry with exponential backoff
- `sdk/python/trialmcp_client/middleware/circuit_breaker.py` — Circuit breaker for clinical dependency resilience
- `sdk/python/examples/` — 6 actor-role example scripts

#### TypeScript SDK
- `sdk/typescript/src/client.ts` — Unified MCP client with connection management
- `sdk/typescript/src/authz.ts`, `fhir.ts`, `dicom.ts`, `ledger.ts`, `provenance.ts` — Domain clients
- `sdk/typescript/src/models/index.ts` — TypeScript interfaces for all domain models
- `sdk/typescript/src/errors.ts` — 9-code error taxonomy
- `sdk/typescript/src/config.ts` — Client configuration
- `sdk/typescript/src/middleware/` — Auth, audit, retry, circuit breaker middleware
- `sdk/typescript/examples/` — 6 actor-role example scripts
- `sdk/typescript/tests/` — SDK test suite

#### CLI and Code Generation Tools
- `tools/cli/trialmcp_cli.py` — CLI with init, scaffold, validate, certify, schema diff, config generate subcommands
- `tools/codegen/generate_python.py` — Python model generation from JSON schemas
- `tools/codegen/generate_typescript.py` — TypeScript interface generation from JSON schemas
- `tools/codegen/generate_openapi.py` — OpenAPI spec generation from tool contracts
- `tools/codegen/templates/` — Code generation templates

#### Stakeholder Implementation Guides
- `docs/guides/hospital-it.md` — Hospital IT / Cancer Center deployment guide
- `docs/guides/robot-vendor.md` — Robot vendor integration guide
- `docs/guides/sponsor-cro.md` — Sponsor/CRO oversight guide
- `docs/guides/regulator-irb.md` — Regulator/IRB evidence review guide
- `docs/guides/standards-community.md` — Standards community contribution guide

#### Operational Documentation
- `docs/operations/runbook.md` — Production operations runbook
- `docs/operations/incident-response.md` — Incident response playbook (P1-P4)
- `docs/operations/key-management.md` — Key management and rotation procedures
- `docs/operations/backup-recovery.md` — Backup, recovery, RTO/RPO guidance
- `docs/operations/slo-guidance.md` — SLO/SLA targets and monitoring thresholds
- `docs/operations/production-concerns.md` — Retries, circuit breakers, idempotency, observability

#### Deployment Guides
- `docs/deployment/local-dev.md` — Local development setup guide
- `docs/deployment/hospital-site.md` — Hospital site deployment guide
- `docs/deployment/multi-site-federated.md` — Multi-site federated deployment guide

#### Architecture Decision Records
- `docs/adr/001-mcp-protocol-boundary.md` — Why MCP is the right protocol boundary
- `docs/adr/002-five-server-architecture.md` — Why these 5 servers were chosen
- `docs/adr/003-twenty-three-tools.md` — Why 23 tools are the minimal stable surface
- `docs/adr/004-profile-conformance-levels.md` — Why profiles map to clinical deployment tiers
- `docs/adr/005-hash-chained-audit.md` — Why hash-chained audit for 21 CFR Part 11
- `docs/adr/006-dag-provenance.md` — Why DAG-based provenance over linear lineage
- `docs/adr/007-deny-by-default-rbac.md` — Why deny-by-default RBAC for clinical safety

#### Governance Artifacts
- `docs/governance/decision-log.md` — Decision log of accepted/declined changes
- `docs/governance/implementation-status.md` — Implementation status matrix
- `docs/governance/roadmap.md` — Adoption milestones and timelines
- `docs/governance/compatibility-matrix.md` — Version/profile/level compatibility matrix
- `docs/governance/known-gaps.md` — Known gaps, non-goals, and future work
- `docs/governance/contribution-policy.md` — Multi-stakeholder contribution policy

#### Security Documentation
- `docs/security/threat-model.md` — STRIDE threat model
- `docs/security/sbom.md` — SBOM generation guidance
- `docs/security/tamper-evident-storage.md` — Tamper-evident storage design
- `docs/security/signed-releases.md` — Signed release policy

#### Repository Strategy
- `docs/repository-strategy.md` — Cross-repo governance and migration strategy

#### Profile Walkthroughs
- `docs/walkthroughs/base-profile.md` — Core AuthZ + Audit walkthrough
- `docs/walkthroughs/clinical-read.md` — FHIR read/search with de-identification
- `docs/walkthroughs/imaging-guided.md` — DICOM query with modality restrictions
- `docs/walkthroughs/multi-site-federated.md` — Cross-site provenance and audit
- `docs/walkthroughs/robot-procedure.md` — Complete robot-assisted procedure

### Changed
- `docs/mcp-process-diagrams/` → `docs/mcp-process/` — Directory renamed for brevity
- `docs/mcp-process/README.md` — Updated version to 1.0.0, added links to new documentation
- `pyproject.toml` — Version 1.0.0, added `trialmcp` CLI entry point, added `sdk/python/` to ruff exclude, added `trialmcp_client` to known-first-party
- `.github/workflows/ci.yml` — Added 5 new CI jobs: `sdk-python`, `sdk-typescript`, `cli-smoke`, `codegen-consistency`, `security-scan`
- `README.md` — v1.0.0 badges, new SDK section, stakeholder guides section, operational docs section, updated repository structure
- `prompts.md` — v1.0.0 prompt archived
- `releases.md` — v1.0.0 release notes added
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly across all Python files
- All existing tests continue to pass
- Python SDK installs and imports verified
- CI pipeline expanded from 9 to 14 jobs

---

## [0.9.0] — 2026-03-07

### Added

#### FHIR Integration Adapters
- `integrations/fhir/__init__.py` — Package initialization
- `integrations/fhir/base_adapter.py` — Abstract FHIR adapter interface (read, search, patient_lookup, study_status, capability_statement)
- `integrations/fhir/mock_adapter.py` — Mock FHIR adapter with synthetic oncology patient data
- `integrations/fhir/hapi_adapter.py` — HAPI FHIR server adapter with REST client
- `integrations/fhir/smart_adapter.py` — SMART-on-FHIR / OAuth2 adapter with token management
- `integrations/fhir/deidentification.py` — Complete HIPAA Safe Harbor de-identification pipeline (18-identifier removal, HMAC-SHA256 pseudonymization, year-only dates, verification suite)
- `integrations/fhir/capability.py` — FHIR CapabilityStatement R4 generation and ingestion
- `integrations/fhir/terminology.py` — Terminology mapping hooks (ICD-10, SNOMED CT, LOINC, RxNorm)
- `integrations/fhir/bundle_handler.py` — FHIR Bundle handling (transaction, batch, search result bundles)
- `integrations/fhir/patient_filter.py` — Patient/resource access filters based on consent status

#### DICOM Integration Adapters
- `integrations/dicom/__init__.py` — Package initialization
- `integrations/dicom/base_adapter.py` — Abstract DICOM adapter interface (query, retrieve_metadata, modality_validation)
- `integrations/dicom/mock_adapter.py` — Mock DICOM adapter with 4 synthetic oncology imaging studies
- `integrations/dicom/orthanc_adapter.py` — Orthanc DICOM server adapter
- `integrations/dicom/dcm4chee_adapter.py` — dcm4chee DICOM archive adapter
- `integrations/dicom/dicomweb.py` — DICOMweb support (QIDO-RS, WADO-RS, STOW-RS)
- `integrations/dicom/metadata_normalizer.py` — DICOM metadata normalization
- `integrations/dicom/modality_filter.py` — Role-based modality restriction enforcement
- `integrations/dicom/recist.py` — RECIST 1.1 measurement validators (target/non-target lesions, overall response)
- `integrations/dicom/safety.py` — Image reference safety constraints (no pixel data transfer)

#### Identity and Security Adapters
- `integrations/identity/__init__.py` — Package initialization
- `integrations/identity/base_adapter.py` — Abstract identity adapter interface
- `integrations/identity/oidc_adapter.py` — OIDC/JWT token validation adapter
- `integrations/identity/mtls.py` — mTLS support utilities and certificate validation
- `integrations/identity/policy_engine.py` — External policy engine integration (OPA-compatible)
- `integrations/identity/kms.py` — KMS/HSM-backed signing key hooks

#### Clinical Operations Adapters
- `integrations/clinical/__init__.py` — Package initialization
- `integrations/clinical/econsent_adapter.py` — eConsent/IRB metadata adapter
- `integrations/clinical/scheduling_adapter.py` — Scheduling/task-order adapter
- `integrations/clinical/provenance_export.py` — Provenance export adapter (W3C PROV-N)

#### Robot Safety and Execution Boundaries
- `safety/__init__.py` — Package initialization
- `safety/gate_service.py` — Safety gate service with 5-gate pre-procedure safety matrix
- `safety/robot_registry.py` — Robot capability registry with USL scoring
- `safety/task_validator.py` — Task-order validator with precondition/postcondition contracts
- `safety/approval_checkpoint.py` — Human-in-the-loop approval gates with timeout and escalation
- `safety/estop.py` — Emergency stop controller with signal propagation and recovery
- `safety/procedure_state.py` — Procedure state machine (8 states with validated transitions)
- `safety/site_verifier.py` — Site capability verification

#### Privacy and Regulatory Modules
- `integrations/privacy/__init__.py` — Package initialization
- `integrations/privacy/access_control.py` — RBAC + ABAC access control with data classification
- `integrations/privacy/deidentification_pipeline.py` — Unified de-identification pipeline (FHIR + DICOM + free-text)
- `integrations/privacy/privacy_budget.py` — Differential privacy budget accounting
- `integrations/privacy/data_residency.py` — Data residency enforcement with jurisdiction-specific rules

#### Federated Coordination
- `integrations/federation/__init__.py` — Package initialization
- `integrations/federation/coordinator.py` — Federated coordinator (site enrollment, round management)
- `integrations/federation/secure_aggregation.py` — Secure aggregation hooks
- `integrations/federation/site_harmonization.py` — Site data harmonization interfaces
- `integrations/federation/policy_enforcement.py` — Site-level federation policy enforcement

#### MCP Process Diagrams
- `docs/mcp-process/README.md` — Diagram index and descriptions
- `docs/mcp-process/01-robot-procedure-lifecycle.md` — Procedure state machine with MCP interactions
- `docs/mcp-process/02-cross-site-mcp-communication.md` — Multi-site topology and synchronization
- `docs/mcp-process/03-clinical-system-integration.md` — FHIR/DICOM/identity integration flows
- `docs/mcp-process/04-safety-gate-evaluation.md` — Safety gate matrix and e-stop propagation
- `docs/mcp-process/05-federated-learning-coordination.md` — Federated round lifecycle and aggregation
- `docs/mcp-process/06-audit-provenance-chain.md` — Hash-chained ledger and DAG provenance
- `docs/mcp-process/07-privacy-deidentification.md` — HIPAA Safe Harbor pipeline and data residency

#### Unit Tests
- `tests/test_integrations.py` — Unit tests for all integration adapter modules
- `tests/test_safety.py` — Unit tests for safety gate, robot registry, procedure state machine

### Changed
- `pyproject.toml` — Version 0.9.0, added `integrations` and `safety` to known-first-party imports, updated description
- `README.md` — v0.9.0 badges, new Integration Adapters section, Safety Boundaries section, MCP Process Diagrams section, updated repository structure and Mermaid diagrams
- `prompts.md` — v0.9.0 prompt archived
- `releases.md` — v0.9.0 release notes added
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly across all Python files
- All existing tests continue to pass
- New integration and safety tests pass
- All 7 MCP process diagrams render correctly with consistent formatting

---

## [0.8.0] — 2026-03-07

### Added

#### Black-Box Conformance Harness
- `conformance/harness/__init__.py` — Package initialization
- `conformance/harness/client.py` — `MCPConformanceClient` with `call_tool()`, `list_tools()`, `initialize()`, `health_check()` methods; `MCPResponse` dataclass; `create_client_from_config()` factory
- `conformance/harness/config.py` — `HarnessConfig`, `ServerTarget`, `SeedConfig` dataclasses; `from_file()` supports JSON/YAML; `default_config()` for local stdin servers
- `conformance/harness/adapters/__init__.py` — Adapters package initialization
- `conformance/harness/adapters/stdin_adapter.py` — `StdinAdapter` managing subprocess stdin/stdout JSON-RPC
- `conformance/harness/adapters/http_adapter.py` — `HttpAdapter` using urllib for HTTP POST
- `conformance/harness/adapters/docker_adapter.py` — `DockerAdapter` using `docker exec` for container communication
- `conformance/harness/adapters/auth_adapter.py` — `AuthSession` and `AuthManager` for multi-role session management
- `conformance/harness/data_seeder.py` — `DataSeeder` with synthetic FHIR Patient, ResearchStudy, DICOM metadata generation; `SeedResult` dataclass
- `conformance/harness/runner.py` — CLI with `--target`, `--profile`, `--level`, `--output-format` flags; `ConformanceReport` with `to_json()`, `to_junit_xml()`, `to_html()`, `to_markdown()` serializers

#### Conformance Suite Refactoring (Unit/Integration/BlackBox Tiers)
- `conformance/unit/__init__.py` — Unit tier package
- `conformance/unit/test_fixture_construction.py` — 30 tests validating fixture construction for audit records, authz decisions, clinical resources, provenance records
- `conformance/integration/__init__.py` — Integration tier package
- `conformance/integration/test_server_integration.py` — Tests for all 5 server packages via in-process calls
- `conformance/blackbox/__init__.py` — BlackBox tier package
- `conformance/blackbox/test_authz_conformance.py` — Token lifecycle, RBAC evaluation, deny-by-default tests
- `conformance/blackbox/test_fhir_conformance.py` — FHIR read, search, de-identification, consent tests
- `conformance/blackbox/test_dicom_conformance.py` — DICOM query, modality restrictions, UID validation tests
- `conformance/blackbox/test_ledger_conformance.py` — Ledger append, verify, chain integrity, genesis tests
- `conformance/blackbox/test_provenance_conformance.py` — Provenance record, query, DAG integrity tests
- `conformance/blackbox/test_cross_server_workflow.py` — End-to-end 5-server workflow, token exchange tests

#### Adversarial Test Packs
- `conformance/adversarial/__init__.py` — Adversarial tier package
- `conformance/adversarial/test_authz_bypass.py` — Role escalation, token reuse, forged tokens
- `conformance/adversarial/test_phi_leakage.py` — De-identification completeness, search result filtering, error message exposure
- `conformance/adversarial/test_replay_attacks.py` — Duplicate audit records, replayed authorization, duplicate provenance
- `conformance/adversarial/test_chain_tampering.py` — Modified records, inserted foreign records, deleted records, reordered records, hash collision attempts
- `conformance/adversarial/test_malformed_inputs.py` — Invalid FHIR/DICOM IDs, oversized payloads, SSRF/XSS/SQL/command injection
- `conformance/adversarial/test_rate_limiting.py` — Rapid token issuance, bulk query flooding, concurrent write contention

#### National Interoperability Testbed
- `interop-testbed/docker-compose.yml` — Multi-site cluster: Site A, Site B, Sponsor, CRO, Mock Identity Provider
- `interop-testbed/personas/robot_agent.yaml` — Robot agent persona
- `interop-testbed/personas/trial_coordinator.yaml` — Trial coordinator persona
- `interop-testbed/personas/data_monitor.yaml` — Data monitor persona
- `interop-testbed/personas/auditor.yaml` — Auditor persona
- `interop-testbed/personas/sponsor.yaml` — Sponsor persona
- `interop-testbed/personas/cro.yaml` — CRO persona
- `interop-testbed/scenarios/cross_site_provenance.py` — Cross-site DAG construction and verification
- `interop-testbed/scenarios/audit_replay.py` — Hash chain replay with per-record verification
- `interop-testbed/scenarios/token_exchange.py` — Cross-site token issuance, validation, revocation
- `interop-testbed/scenarios/partial_outage.py` — Graceful degradation under service failure
- `interop-testbed/scenarios/schema_drift.py` — Major/minor/patch schema drift detection
- `interop-testbed/scenarios/state_overlay.py` — CA CCPA, NY PHL/SHIELD, FDA 21 CFR Part 11 overlays
- `interop-testbed/scenarios/robot_workflow.py` — 8-step robot-assisted procedure workflow
- `interop-testbed/scenarios/site_onboarding.py` — 10-check site certification checklist
- `interop-testbed/mock_services/mock_ehr.py` — Mock FHIR R4 EHR with synthetic patients
- `interop-testbed/mock_services/mock_pacs.py` — Mock DICOM PACS with synthetic imaging
- `interop-testbed/mock_services/mock_identity.py` — Mock OIDC/JWT Identity Provider

#### Certification and Evidence Generation
- `tools/certification/__init__.py` — Package initialization
- `tools/certification/report_generator.py` — JSON, JUnit XML, HTML, Markdown conformance reports
- `tools/certification/evidence_pack.py` — SHA-256 hashed evidence bundles with manifest
- `tools/certification/site_certification.py` — Profile-based conformance level validation
- `tools/certification/schema_diff.py` — Breaking/non-breaking schema change detection

#### Performance Benchmarks
- `benchmarks/__init__.py` — Package initialization
- `benchmarks/latency_benchmark.py` — Audit hash and chain construction latency measurement
- `benchmarks/throughput_benchmark.py` — AuthZ, audit, provenance throughput benchmarks
- `benchmarks/chain_benchmark.py` — Chain construction at 10/50/100/500 records
- `benchmarks/concurrent_benchmark.py` — ThreadPool performance at 1/2/4/8 threads
- `benchmarks/report.py` — Report generation with baseline regression detection

### Changed
- `pyproject.toml` — Version 0.8.0, added `trialmcp-conformance` CLI entry point, added `benchmarks`, `interop_testbed`, `tools` to known-first-party, added `blackbox`, `adversarial`, `integration` pytest markers
- `.github/workflows/ci.yml` — Added 4 new jobs: `integration-tests`, `adversarial-tests`, `schema-compatibility`, `benchmark-smoke`; lint job ignores `conformance/integration` and `conformance/harness`
- `reference/python/schema_validator.py` — Changed `validate()` to use lazy import for `Draft202012Validator`
- `README.md` — v0.8.0 badges (457 conformance, 501 total, Testbed badge), new Black-Box Conformance Harness section, National Interoperability Testbed section, Certification section, Benchmarks section, updated CI pipeline (9 jobs), updated conformance test architecture, updated repository structure
- `prompts.md` — v0.8.0 prompt archived
- `releases.md` — v0.8.0 release notes added
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly across all Python files
- `pytest tests/` — 44 unit tests pass
- `pytest conformance/ --ignore=conformance/integration --ignore=conformance/harness` — 457 conformance tests pass (+ 1 skipped)
- All benchmarks run successfully without errors
- Total: 501 tests passing

---

## [0.7.0] — 2026-03-07

### Added

#### Production-Shaped MCP Server Packages
- `servers/__init__.py` — Package root for all 5 MCP domain servers
- `servers/common/` — Shared server infrastructure: MCP transport (stdin/stdout JSON-RPC 2.0), request routing, auth/audit middleware, 9-code error taxonomy, env var/YAML/JSON configuration management, structured JSON logging, health/readiness checker, schema validation utilities
- `servers/storage/` — Persistence layer: abstract base interface, in-memory adapter, SQLite adapter, PostgreSQL adapter interface, schema migration utilities, config-driven storage factory
- `servers/trialmcp_authz/` — Authorization server: deny-by-default RBAC policy engine with 6-actor matrix, SHA-256 token lifecycle, persistent policy/token stores, MCP server entrypoint with transport/routing/audit
- `servers/trialmcp_fhir/` — FHIR clinical data server: HIPAA Safe Harbor de-identification pipeline (18-identifier removal), HMAC-SHA256 pseudonymization, FHIR adapter interface (mock/HAPI/SMART), capability statement generation
- `servers/trialmcp_dicom/` — DICOM imaging server: role-based modality restrictions (MUST: CT, MR, PT; SHOULD: RTSTRUCT, RTPLAN), DICOM UID validation, patient name hashing (12-char SHA-256), retrieval-pointer handling
- `servers/trialmcp_ledger/` — Audit ledger server: hash-chained immutable audit ledger with SHA-256 canonical JSON, genesis block, chain verification, concurrency-safe locking, query/export tools
- `servers/trialmcp_provenance/` — Provenance server: DAG-based lineage graph with SHA-256 fingerprinting, W3C PROV alignment, forward/backward traversal, cycle detection, cross-site trace merging

#### Deployment Infrastructure
- `deploy/docker/Dockerfile.authz` through `Dockerfile.provenance` — Individual Dockerfiles for each server
- `deploy/docker/Dockerfile.allinone` — All-in-one image with all 5 servers
- `deploy/docker-compose.yml` — Single-site deployment with all 5 servers
- `deploy/docker-compose.multi-site.yml` — Multi-site deployment (Site A + Site B + shared ledger)
- `deploy/kubernetes/` — Reference Kubernetes manifests: namespace, configmap, secrets template, 5 deployment+service pairs
- `deploy/helm/trialmcp/` — Helm chart with Chart.yaml, values.yaml, templated deployment
- `deploy/config/` — Example YAML config files for each server, site-profile-example.yaml
- `deploy/.env.example` — Environment configuration template

#### End-to-End Demo
- `examples/quickstart/run_demo.py` — Complete 5-server workflow demo: token issuance → validation → authz → FHIR read → DICOM query → ledger append → provenance record → chain verification → DAG verification
- `examples/quickstart/demo_data/` — Synthetic FHIR Bundle (2 patients, 1 research study), DICOM metadata (3 studies: CT, MR, PT), site capability profile
- `examples/quickstart/README.md` — Step-by-step quickstart guide

#### TypeScript Expansion
- `reference/typescript/authz-server.ts` — TypeScript AuthZ server with full policy engine and token lifecycle
- `reference/typescript/ledger-server.ts` — TypeScript Ledger server with AuditChain class
- `reference/typescript/interfaces.ts` — Generated TypeScript interfaces for all 13 schemas
- `reference/typescript/authz-server.test.ts` — 12 Jest tests for AuthZ server
- `reference/typescript/ledger-server.test.ts` — 9 Jest tests for Ledger server
- `reference/typescript/jest.config.json` — Jest configuration for ts-jest

### Changed
- `pyproject.toml` — Version 0.7.0, added CLI entry points (`trialmcp-authz`, etc.), added optional dependency extras (`[fhir]`, `[dicom]`, `[dev]`, `[test]`, `[docs]`, `[all]`), added `servers` and `examples` to known-first-party imports
- `reference/python/core_server.py` — Version string 0.6.0 → 0.7.0
- `reference/typescript/core-server.ts` — Version string 0.6.0 → 0.7.0
- `reference/typescript/package.json` — Version 0.7.0, added test/lint scripts, added jest/ts-jest devDependencies
- `reference/typescript/tsconfig.json` — Added skipLibCheck, excluded test files from compilation
- `README.md` — v0.7.0 version/badges, new MCP Server Implementations section with Mermaid diagram, Deployment Infrastructure section, Quickstart Demo section, updated repository structure
- `prompts.md` — v0.7.0 prompt archived
- `releases.md` — v0.7.0 release notes added
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly across all 70 Python files
- `pytest tests/` — 44 unit tests pass
- `pytest conformance/` — 269 conformance tests pass (+ 1 skipped)
- All 13 schemas validate with `python reference/python/schema_validator.py`
- Generated models match committed models (`python scripts/generate_models.py`)
- End-to-end demo (`python examples/quickstart/run_demo.py`) completes full 5-server workflow
- All 5 server packages import and instantiate correctly

---

## [0.6.0] — 2026-03-07

### Fixed

#### Schema/Code Contract Alignment
- `reference/python/core_server.py` — `authz_evaluate()` now returns `allowed`, `effect`, `role`, `server`, `tool`, `matching_rules` (structured objects), `evaluated_at`, `deny_reason` per `authz-decision.schema.json` (previously returned `decision`, `resource_id`, `reason`, `matching_rules` as strings, `timestamp`)
- `reference/python/core_server.py` — `ledger_append()` now returns `audit_id`, `previous_hash` per `audit-record.schema.json` (previously returned `record_id`, `prev_hash`)
- `reference/python/core_server.py` — `health_status()` now returns `server_name`, `checked_at`, `dependencies` (array) per `health-status.schema.json` (previously returned `server`, `timestamp`, `dependencies` as object)
- `reference/python/core_server.py` — `error_response()` now accepts optional `server` parameter for schema-valid output
- `reference/python/core_server.py` — `ledger_verify()` now checks `previous_hash` field (was `prev_hash`)
- `reference/typescript/core-server.ts` — `authzEvaluate()` aligned to `authz-decision.schema.json`: `allowed`, `effect`, `matching_rules` as `MatchingRule[]`, `evaluated_at`, `deny_reason`
- `reference/typescript/core-server.ts` — `ledgerAppend()` aligned to `audit-record.schema.json`: `audit_id`, `previous_hash`
- `reference/typescript/core-server.ts` — `healthStatus()` aligned to `health-status.schema.json`: `server_name`, `checked_at`, `dependencies` as typed array
- `reference/typescript/core-server.ts` — `errorResponse()` aligned to `error-response.schema.json`: optional `server` parameter

#### Maturity Labeling
- `README.md` — "Normative Specification" → "Proposed Reference Standard"; "United States Industry Standard" → "United States"
- `README.md` — Added maturity callout explaining normative vs illustrative boundaries
- `README.md` — "Reference implementation" → "Level 1 illustrative implementation" throughout
- `README.md` — Removed "Passing" from static test count badges; replaced `brightgreen` with `blue` for count-only badges
- `reference/python/core_server.py` — Docstring updated: "NON-NORMATIVE Level 1 Illustrative Implementation"
- `reference/typescript/core-server.ts` — Docstring updated: "NON-NORMATIVE Level 1 Illustrative Implementation"

### Added

#### Typed Model Generation Pipeline
- `scripts/generate_models.py` — Reads all 13 `/schemas/*.schema.json` files, produces Python dataclasses (`models/python/generated_models.py`) and TypeScript interfaces (`models/typescript/generated_models.ts`)
- `models/python/generated_models.py` — Auto-generated dataclasses for all 13 schemas (audit-record, authz-decision, capability-descriptor, consent-status, dicom-query, error-response, fhir-read, fhir-search, health-status, provenance-record, robot-capability-profile, site-capability-profile, task-order)
- `models/typescript/generated_models.ts` — Auto-generated TypeScript interfaces for all 13 schemas

#### CI/CD Pipeline Hardening
- `.github/workflows/ci.yml` — Added `contract-consistency` job: regenerates models and fails if output differs from committed models; validates `core_server.py` runtime outputs against all relevant schemas
- `.github/workflows/ci.yml` — Added `typescript-build` job: runs `npx tsc --noEmit` to verify TypeScript compiles
- `.github/workflows/ci.yml` — `docs-lint` job: `sys.exit(0)` → `sys.exit(1 if errors else 0)` for broken link detection (now fails on errors)

#### Unit Tests
- `tests/test_core_server.py` — Expanded from 28 to 33 tests: added `test_deny_has_empty_matching_rules`, `test_deny_has_deny_reason`, `test_has_server_field`, `test_has_required_schema_fields`, `test_health_status_dependencies_is_array`, `test_health_status_server_name`; updated all assertions to use corrected field names (`effect`/`allowed`/`evaluated_at`/`audit_id`/`previous_hash`/`server_name`/`checked_at`)

### Changed
- `pyproject.toml` — Version 0.6.0, added `models` and `scripts` to known-first-party imports, updated description
- `README.md` — v0.6.0 version, updated badges (44 unit tests, 313 total, 3 contributors), updated CI pipeline table (5 jobs), updated repository structure (added `models/`, `scripts/`, `peer-review/`), updated unit test summary table
- `prompts.md` — v0.6.0 prompt archived
- `releases.md` — v0.6.0 release notes added
- `changelog.md` — This entry

### Verified
- `ruff check .` and `ruff format --check .` pass cleanly
- `pytest tests/` — 44 unit tests pass
- `pytest conformance/` — 269 conformance tests pass (+ 1 skipped)
- All 13 schemas validate with `python reference/python/schema_validator.py`
- Every `/spec/` file uses RFC 2119 MUST/SHOULD/MAY keywords
- Every `/reference/` implementation file labeled NON-NORMATIVE
- `.github/workflows/ci.yml` pipeline covers Python lint/test, TypeScript build, schema validation, contract consistency, and docs lint (with failure on errors)

---

## [0.5.2] — 2026-03-07

### Added

#### Peer Review Response
- `peer-review/response-A-2026-03-06.md` — Structured response tables for all recommendations from two ChatGPT 5.4 Thinking peer reviews (Feedback 1: 8 sections, 44 recommendations; Feedback 2: 17 sections, 56 recommendations), each categorized as Add/Fix/Remove with Implemented/Deferred status and prompt assignment

#### Implementation Roadmap Prompts
- `peer-review/claude-1-2026-03-06.md` — Prompt 1 (v0.6.0): Phase 1 — Correctness, contract alignment, schema-code drift resolution, generated typed models, CI hardening (TypeScript build/test, docs lint failure), maturity labeling
- `peer-review/claude-2-2026-03-06.md` — Prompt 2 (v0.7.0): Phase 2 — Real MCP server implementations for all 5 domains (authz, fhir, dicom, ledger, provenance), shared server infrastructure, persistence layer (SQLite/PostgreSQL adapters), deployment infrastructure (Docker/Kubernetes/Helm), end-to-end demo, TypeScript expansion
- `peer-review/claude-3-2026-03-06.md` — Prompt 3 (v0.8.0): Phase 3 — Black-box conformance harness with pluggable transport adapters, conformance suite refactoring (unit/integration/blackbox tiers), adversarial test packs (authz bypass, PHI leakage, replay attacks, chain tampering, rate limiting), national interoperability testbed (multi-site docker-compose, actor personas, mock EHR/PACS), certification and evidence generation, benchmarks
- `peer-review/claude-4-2026-03-06.md` — Prompt 4 (v0.9.0): Phase 4 — FHIR integration adapters (HAPI, SMART-on-FHIR, de-identification, terminology mapping, Bundle handling), DICOM integration adapters (Orthanc, dcm4chee, DICOMweb, RECIST validators), identity/security adapters (OIDC/JWT, mTLS, KMS), clinical operations adapters, robot safety boundaries (safety gate service, robot registry, task validator, approval checkpoints, e-stop, procedure state machine), privacy/regulatory modules, federated coordination
- `peer-review/claude-5-2026-03-06.md` — Prompt 5 (v1.0.0): Phase 5 — Python/TypeScript SDKs with actor-role examples, CLI tools (init, scaffold, validate, certify), code generation, stakeholder guides (hospital IT, robot vendor, sponsor/CRO, regulator/IRB, standards community), operational documentation (runbook, incident response, key management, backup/recovery, SLO guidance), governance evidence, architecture decision records, repository strategy

### Changed
- `prompts.md`: v0.5.2 prompt archived
- `releases.md`: v0.5.2 release notes added
- `changelog.md`: This entry
- `pyproject.toml`: Version 0.5.2, updated description

---

## [0.5.1] — 2026-03-07

### Added

#### Unit Test Suite
- `tests/__init__.py` — Package initialization for unit test directory
- `tests/test_core_server.py` — 28 unit tests for `reference.python.core_server`: AuthZ evaluate (6 tests), token lifecycle (7 tests), ledger operations (8 tests), health/error helpers (5 tests), policy matrix (1 test), genesis hash constant (1 test)
- `tests/test_schema_validator.py` — 6 unit tests for `reference.python.schema_validator`: schema loading (2 tests), schema listing (2 tests), schema validation (2 tests)
- `tests/test_conformance_runner.py` — 5 unit tests for `reference.python.conformance_runner`: pytest argument building (5 tests), level directory mapping (1 test)

### Changed
- `.github/workflows/ci.yml`: Added `pytest tests/ -v` step before conformance tests in `lint-and-format` job across Python 3.10, 3.11, 3.12
- `pyproject.toml`: Version 0.5.1, added `tests` to testpaths and `tests` to known-first-party isort imports, updated description
- `prompts.md`: v0.5.1 prompt archived
- `releases.md`: v0.5.1 release notes added
- `changelog.md`: This entry

### Verified
- `pytest tests/` — 39 unit tests pass
- `pytest conformance/` — 269 conformance tests pass
- `python reference/python/schema_validator.py` — All 13 schemas validate
- Every `/spec/` file uses RFC 2119 MUST/SHOULD/MAY keywords
- Every `/reference/` implementation file labeled NON-NORMATIVE
- `.github/workflows/ci.yml` pipeline validated
- `ruff check .` and `ruff format --check .` pass cleanly

---

## [0.5.0] — 2026-03-06

### Added

#### Reference Implementations (NON-NORMATIVE)
- `reference/python/__init__.py` — Package documentation for Python reference implementation
- `reference/python/core_server.py` — Minimal Core (Level 1) MCP server: deny-by-default RBAC with 6-actor policy matrix, SHA-256 token lifecycle (issue, validate, revoke), hash-chained audit ledger with canonical JSON serialization, health status and error response helpers
- `reference/python/schema_validator.py` — JSON Schema draft 2020-12 validation utilities: `load_schema`, `list_schemas`, `validate`, `validate_all_examples` wrapping `jsonschema` Draft202012Validator
- `reference/python/conformance_runner.py` — CLI conformance test runner: `--level` (1–5) for scoped validation, `--security` for security-only tests, `--no-verbose` flag, pytest integration
- `reference/typescript/core-server.ts` — Minimal Core server stub with ajv JSON Schema validation: AuthZ evaluation, hash-chained audit ledger, health status, error response, compile-time schema validation
- `reference/typescript/package.json` — Node.js package with ajv ^8.12.0, uuid ^9.0.0, typescript ^5.3.0
- `reference/typescript/tsconfig.json` — TypeScript configuration targeting ES2020
- `reference/typescript/README.md` — TypeScript reference documentation with quick start and schema validation guide

#### CI/CD Pipeline
- `.github/workflows/ci.yml` — Comprehensive CI/CD pipeline:
  - `lint-and-format` job: Matrix across Python 3.10, 3.11, 3.12 with ruff lint, ruff format check, pytest conformance suite
  - `schema-validation` job: All 13 JSON schemas validated for structure and example self-validation
  - `docs-lint` job: Required documentation file existence check, internal markdown link verification

#### Documentation
- `docs/architecture.md` — Five-server topology ASCII diagram, server responsibility table (23 tools, 5 servers), six-phase data flow diagram, hash-chained audit ledger architecture, cross-server audit coordination, national deployment topology
- `docs/adoption-roadmap.md` — Four-phase adoption roadmap: Phase 0 (Specification Review, 2–4 weeks), Phase 1 (Profile Selection, 4–8 weeks), Phase 2 (Conformance Validation, 8–12 weeks), Phase 3 (Pilot Deployment, 3–6 months)
- `docs/glossary.md` — Standard terminology: Protocol/Architecture, Actors, Clinical Data Standards, Security/Privacy, Audit/Provenance, Physical AI, Regulatory, Specification Language, Versioning/Governance

### Changed
- README: v0.5.0 version, CI and TypeScript badges, Reference Implementations section with Mermaid diagram, CI/CD Pipeline section with pipeline diagram, normative vs informative labels in repository structure, expanded Getting Started with adoption roadmap and glossary references
- `pyproject.toml`: Version 0.5.0, updated description, added `reference` to known-first-party imports
- `governance/CODEOWNERS`: Added `/reference/` and `/docs/` directory ownership
- `prompts.md`: v0.5.0 prompt archived
- `releases.md`: v0.5.0 release notes added
- `changelog.md`: This entry

---

## [0.4.0] — 2026-03-06

### Added

#### Conformance Test Suite
- `conformance/README.md` — Harness overview, directory structure, how to run tests, how to add tests, conformance level mapping
- `conformance/conftest.py` — Shared pytest fixtures, JSON Schema draft 2020-12 validation helpers (`validate_against_schema`, `assert_schema_valid`, `schema_has_required_fields`), schema loading, parametrized `each_schema` fixture
- `conformance/fixtures/audit_records.py` — Sample audit records, hash chain builders (`make_audit_chain`), genesis hash, error responses, health status fixtures, `compute_audit_hash` helper
- `conformance/fixtures/authz_decisions.py` — ALLOW/DENY decision builders, 6-actor default RBAC permission matrix, unauthorized access attempt fixtures
- `conformance/fixtures/clinical_resources.py` — De-identified FHIR patient builders, FHIR search/read response builders, DICOM query response builders, SSRF payload fixtures, invalid FHIR/DICOM ID fixtures, HIPAA Safe Harbor 18-identifier list
- `conformance/fixtures/provenance_records.py` — Provenance record builders, DAG pipeline builders (`make_provenance_dag`), cross-server provenance fixture, multi-server trace sequence fixture

#### Positive Conformance Tests
- `conformance/positive/test_core_conformance.py` — 27 tests: audit record production (9 fields, UUID format, ISO 8601 UTC, SHA-256 hash, chain links), error envelope (required fields, `error=true`, 9-code taxonomy), health check (required fields, valid status), authorization decisions (ALLOW/DENY structure, 6 roles, schema validation)
- `conformance/positive/test_clinical_read_conformance.py` — FHIR read/search responses, 18 HIPAA identifiers, name/address redaction, year-only birthDate, HMAC pseudonymization, search result capping, consent schema validation
- `conformance/positive/test_imaging_conformance.py` — DICOM query responses, MUST modalities (CT, MR, PT), SHOULD modalities (RTSTRUCT, RTPLAN), role-based query level permissions (4 roles), UID validation, patient name hashing (12-char SHA-256), year-only StudyDate

#### Negative Conformance Tests
- `conformance/negative/test_invalid_inputs.py` — Malformed FHIR IDs (spaces, @, /, XSS, empty, URLs, >1000 chars), invalid DICOM UIDs (letters, spaces, slashes), invalid query levels, invalid roles, input length limits (1000 chars, 50 keys, 100 elements), schema field mismatches (wrong server, wrong error code, wrong hash length, wrong timestamp format, wrong UUID format)
- `conformance/negative/test_unauthorized_access.py` — Deny-by-default enforcement, 6 known unauthorized access attempts, DENY decision schema validation, role boundary validation (sponsor minimal access, auditor no write, data_monitor read-only), DENY precedence over ALLOW

#### Security Conformance Tests
- `conformance/security/test_ssrf_prevention.py` — 7 SSRF payloads rejected, case-insensitive protocol detection, internal IP patterns (169.254.x, 127.0.0.1, localhost, ::1, 10.x, 192.168.x, 172.16.x), legitimate IDs accepted, data URI rejection, javascript URI rejection
- `conformance/security/test_token_lifecycle.py` — Token issuance (UUID v4, SHA-256 hash, hash matches raw, no plaintext), default expiry (3600s), max expiry (86400s), UTC timestamps, expiry enforcement, immediate revocation, revocation permanence, hash unchanged after revocation
- `conformance/security/test_chain_integrity.py` — Genesis hash (64 zeros), chain verification, tamper detection (modified result_summary, modified caller, modified parameters, modified timestamp, swapped records, deleted record, inserted foreign record), canonical JSON serialization (alphabetical keys, hash field excluded, UTF-8 encoding)

#### Interoperability Conformance Tests
- `conformance/interoperability/test_cross_server_trace.py` — Multi-server chain spanning 5 servers, chain integrity across server boundaries, operational order (authz → fhir → dicom → ledger → provenance), cross-server provenance DAG, source types, action types, SHA-256 fingerprints, federated audit coordination
- `conformance/interoperability/test_schema_validation.py` — All 13 schema files: existence, valid JSON, draft 2020-12 reference, $id field, title field, description field, schema example self-validation, audit record/error response/health status/authz decision/provenance record schema validation

#### Configuration
- `pyproject.toml` — Python project configuration: ruff lint rules (E, F, I, W), line length 100, target Python 3.10, pytest configuration with testpaths and markers

#### Documentation
- README: v0.4.0 badges (Version, Conformance Tests: 269 Passing), Conformance Test Suite section with Mermaid architecture diagram, conformance test summary table, national conformance validation flow text diagram, updated Table of Contents, updated repository structure, updated Getting Started
- Updated CODEOWNERS with `/conformance/` directory ownership
- `prompts.md` — v0.4.0 prompt archived

---

## [0.3.0] — 2026-03-06

### Added

#### Conformance Profiles
- `profiles/base-profile.md` — Core conformance profile: deny-by-default RBAC authorization, hash-chained audit ledger, 9-code error taxonomy, input validation requirements, 19 conformance tests
- `profiles/clinical-read.md` — Clinical Read profile: FHIR R4 read/search with mandatory HIPAA Safe Harbor de-identification, HMAC-SHA256 pseudonymization, year-only date generalization, 29 conformance tests
- `profiles/imaging-guided-oncology.md` — Imaging-Guided Oncology profile: DICOM query/retrieve with role-based modality restrictions (MUST: CT, MR, PT; SHOULD: RTSTRUCT, RTPLAN), RECIST 1.1 requirements, 39 conformance tests
- `profiles/multi-site-federated.md` — Multi-Site Federated profile: cross-site DAG-based data provenance, federated audit chain coordination, data residency policy enforcement, federated learning provenance tracking, 48 conformance tests
- `profiles/robot-assisted-procedure.md` — Robot-Assisted Procedure profile: robot capability registration with USL scoring, task-order contract lifecycle, pre-procedure safety matrix, six-step robot agent workflow, 58 conformance tests

#### Regulatory Overlay Profiles
- `profiles/state-us-ca.md` — California CCPA/CPRA overlay: Right to Know, Right to Delete, Right to Opt-Out, sensitive PI protections, data minimization requirements
- `profiles/state-us-ny.md` — New York health information overlay: PHL Article 27-F (HIV confidentiality), SHIELD Act security safeguards, MHL Article 33 (mental health records), DOH 10 NYCRR Parts 405/86
- `profiles/country-us-fda.md` — FDA 21 CFR Part 11 overlay: electronic records (Subpart B §11.10), electronic signatures (§11.50/§11.70/§11.100), SaMD classification guidance, Good Machine Learning Practice alignment

#### Documentation
- README: Profile architecture Mermaid diagram, profile summary tables, national profile deployment map, updated repository structure, Profiles badge
- Updated Getting Started section with profile-based implementation guidance and state overlay references
- Updated CODEOWNERS with `/profiles/` directory ownership
- `prompts.md` — v0.3.0 prompt archived

---

## [0.2.0] — 2026-03-06

### Added

#### Machine-Readable JSON Schemas
- `schemas/capability-descriptor.schema.json` — Server capability advertisement (name, version, tools, conformance level, regulatory certifications)
- `schemas/robot-capability-profile.schema.json` — Physical AI robot platform profile with USL scoring, safety prerequisites, simulation frameworks
- `schemas/site-capability-profile.schema.json` — Clinical site descriptor (jurisdiction, deployed servers, data residency, IRB approval)
- `schemas/task-order.schema.json` — Scheduled clinical trial task for Physical AI systems (procedure type, robot assignment, safety checks)
- `schemas/audit-record.schema.json` — Hash-chained 21 CFR Part 11 audit ledger record with SHA-256 chain linking
- `schemas/provenance-record.schema.json` — DAG-based data lineage record with SHA-256 fingerprinting
- `schemas/consent-status.schema.json` — Patient consent state machine with 6 granular consent categories
- `schemas/authz-decision.schema.json` — Deny-by-default RBAC authorization decision with matching rules
- `schemas/dicom-query.schema.json` — DICOM query input/output with role-based query level permissions
- `schemas/fhir-read.schema.json` — FHIR R4 single resource read with HIPAA Safe Harbor de-identification
- `schemas/fhir-search.schema.json` — FHIR R4 collection search with 100-result cap
- `schemas/error-response.schema.json` — Standardized error response format with 9-code taxonomy
- `schemas/health-status.schema.json` — Server health check with dependency status and operational metrics

All schemas use JSON Schema draft 2020-12 with `$id`, `title`, `description`, `required`, and `examples`.

#### Documentation
- README badges: Version, JSON Schema, Python, Protocol (MCP), Date, License, DOI, Contributors
- Updated architecture diagrams: Schema validation flow integrated into national deployment topology
- Updated Mermaid diagrams: Schema catalog visualization, updated conformance levels, actor model, security model
- Updated repository structure reflecting `/schemas/` directory
- `prompts.md` — v0.2.0 prompt archived

---

@kevinkawchak prompts.md prompt order modified 2026-03-06

---

## [0.1.0] — 2026-03-06

### Added

#### Specification
- `spec/core.md` — Protocol scope, design principles, three-tier national architecture, server topology
- `spec/actor-model.md` — Six-actor model (robot_agent, trial_coordinator, data_monitor, auditor, sponsor, CRO) with full RBAC permission matrix
- `spec/tool-contracts.md` — 23 tool contracts across 5 MCP servers (AuthZ, FHIR, DICOM, Ledger, Provenance) with input/output schemas, error codes, and audit requirements
- `spec/security.md` — Deny-by-default RBAC, SHA-256 token lifecycle, SSRF prevention, injection defenses, input validation regexes
- `spec/privacy.md` — HIPAA Safe Harbor 18-identifier removal, HMAC-SHA256 pseudonymization pipeline, year-only date generalization, minimum necessary principle
- `spec/provenance.md` — DAG-based data lineage graph, W3C PROV alignment, SHA-256 fingerprinting, five source types, five action types
- `spec/audit.md` — Hash-chained immutable ledger, genesis block specification, canonical JSON serialization, chain verification algorithm, replay trace
- `spec/conformance.md` — Five conformance levels (Core, Clinical Read, Imaging, Federated Site, Robot Procedure) with MUST/SHOULD/MAY matrix
- `spec/versioning.md` — SemVer policy, backward compatibility rules, deprecation lifecycle, extension namespace mechanism

#### Regulatory Overlays
- `regulatory/US_FDA.md` — FDA AI/ML medical device guidance mapping, predetermined change control plan alignment, SaMD classification
- `regulatory/HIPAA.md` — HIPAA Privacy Rule and Security Rule mapping to specification requirements, Safe Harbor method compliance
- `regulatory/CFR_PART_11.md` — 21 CFR Part 11 electronic records and signatures mapping, audit trail requirements, system validation
- `regulatory/IRB_SITE_POLICY_TEMPLATE.md` — IRB site policy template for Physical AI oncology trial deployments

#### Governance
- `governance/CHARTER.md` — Organization charter, mission, scope, membership, decision-making authority
- `governance/DECISION_PROCESS.md` — Three-tier decision process (editorial, minor enhancement, breaking change) with review periods
- `governance/EXTENSIONS.md` — Extension namespace rules (`x-{vendor}` prefix), registration process, conflict resolution
- `governance/VERSION_COMPATIBILITY.md` — Version compatibility policy, migration guidance, sunset timelines
- `governance/CODEOWNERS` — Code ownership assignments for specification modules

#### Community
- `.github/ISSUE_TEMPLATE/bug_report.md` — Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — Feature request template
- `.github/ISSUE_TEMPLATE/spec_change.md` — Specification change proposal template
- `.github/PULL_REQUEST_TEMPLATE.md` — Pull request template with conformance and regulatory checklists
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- `LICENSE` — MIT License

#### Documentation
- `README.md` — Comprehensive project overview with architecture diagrams, conformance summary, actor model, tool registry, regulatory matrix, and comparison tables
- `changelog.md` — This file
- `releases.md` — Release notes
- `prompts.md` — Prompt archive documenting AI-assisted development

---

- @kevinkawchak Exact v0.1.0 prompt replacement for prompts.md. Added DOI badge to main README. 2026-03-06
