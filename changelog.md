# Changelog

All notable changes to the National MCP-PAI Oncology Trials Standard are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) as described in [spec/versioning.md](spec/versioning.md).

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
