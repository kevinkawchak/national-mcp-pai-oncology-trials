# Changelog

All notable changes to the National MCP-PAI Oncology Trials Standard are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) as described in [spec/versioning.md](spec/versioning.md).

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
