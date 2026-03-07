# Releases

Release notes for the National MCP-PAI Oncology Trials Standard.

---

v0.5.1 - Unit Tests + Verification + CI/CD Hardening for National MCP-PAI Oncology Trials Standard

## Summary

Introduces a dedicated `/tests/` directory containing 39 unit tests for the reference Python implementation (`core_server.py`, `schema_validator.py`, `conformance_runner.py`), verifies all 8 repository-wide quality checks (unit tests, conformance suite, schema validation, RFC 2119 compliance, NON-NORMATIVE labeling, CI pipeline, prompts archive, and release documentation), and hardens the CI/CD pipeline to run both unit tests and conformance tests across Python 3.10–3.12. All 269 conformance tests and 39 unit tests pass with clean ruff lint and format checks.

## Features

- **Unit test suite** (`/tests/`) — 39 tests across 3 test modules:
  - `test_core_server.py` — 28 tests: AuthZ evaluate (allow/deny/unknown role/timestamp/matching rules/resource ID), token lifecycle (issue/validate/revoke/not found/cap max expiry), ledger operations (hash determinism/SHA-256/required fields/genesis default/chain linking/verify valid/verify empty/verify tampered), health status (required fields/status value), error response (required fields/error flag/code), policy matrix (six roles)
  - `test_schema_validator.py` — 6 tests: schema loading (existing/not found), schema listing (count 13/sorted), validation (valid instance/invalid instance)
  - `test_conformance_runner.py` — 5 tests: pytest argument building (all levels/level 1/security only/no verbose/verbose default), level directory mapping
- **CI/CD pipeline hardening** (`.github/workflows/ci.yml`):
  - Added `pytest tests/ -v` step before conformance tests in `lint-and-format` job
  - Ensured `jsonschema` dependency installed for unit test schema validation
- **Repository-wide verification** — All 8 quality checks validated:
  1. `pytest tests/` — 39 unit tests pass
  2. `pytest conformance/` — 269 conformance tests pass (+ 1 skipped)
  3. `python reference/python/schema_validator.py` — All 13 schemas validate
  4. Every `/spec/` file uses RFC 2119 MUST/SHOULD/MAY keywords
  5. Every `/reference/` implementation file labeled NON-NORMATIVE
  6. `.github/workflows/ci.yml` pipeline executes lint, format, unit tests, conformance tests, schema validation, and docs linting
  7. `prompts.md` contains all 6 prompts (v0.1.0–v0.5.1) with comprehensive instructions
  8. Every version has `releases.md` and `changelog.md` entries
- **Updated `pyproject.toml`** — Version 0.5.1, added `tests` to testpaths and known-first-party imports
- **Updated `prompts.md`** — v0.5.1 prompt archived
- **Updated `releases.md`** — v0.5.1 release notes added
- **Updated `changelog.md`** — v0.5.1 changelog entry added

## Contributors
@kevinkawchak
@claude

## Notes
- No existing code was modified — all 269 conformance tests and reference implementation files remain unchanged
- Unit tests import directly from `reference.python.*` modules, validating the reference implementation's public API
- The `test_core_server.py` module covers all 9 public functions: `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_revoke_token`, `compute_audit_hash`, `ledger_append`, `ledger_verify`, `health_status`, `error_response`
- Schema validator tests use the `error-response` schema for validation testing as it has no cross-file `$ref` dependencies
- CI pipeline now runs 308 total tests (39 unit + 269 conformance) across Python 3.10, 3.11, and 3.12
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.5.0 - Reference Implementations + CI/CD + Documentation for National MCP-PAI Oncology Trials Standard

## Summary

Introduces NON-NORMATIVE reference implementations in Python and TypeScript under `/reference/`, a comprehensive CI/CD pipeline (`.github/workflows/ci.yml`) with lint, test, schema validation, and docs linting jobs across Python 3.10–3.12, and extended documentation under `/docs/` covering the five-server architecture, a four-phase adoption roadmap, and a standard glossary. README updated with v0.5.0 badges (CI, TypeScript), new Reference Implementations and CI/CD Pipeline sections with Mermaid diagram, normative vs informative labels throughout the repository structure, and expanded Getting Started guidance.

## Features

- **Python reference implementation** (`/reference/python/`) — NON-NORMATIVE:
  - `core_server.py` — Minimal Core (Level 1) MCP server implementing deny-by-default RBAC (6-actor policy matrix), SHA-256 token lifecycle, hash-chained audit ledger with canonical JSON serialization, and schema-valid health/error responses
  - `schema_validator.py` — JSON Schema draft 2020-12 validation utilities wrapping `jsonschema`, with `load_schema`, `list_schemas`, `validate`, and `validate_all_examples` functions for automated validation of all 13 schemas
  - `conformance_runner.py` — CLI runner for the conformance test suite with `--level` (1–5), `--security`, and `--no-verbose` flags for scoped conformance validation
- **TypeScript reference implementation** (`/reference/typescript/`) — NON-NORMATIVE:
  - `core-server.ts` — Minimal Core server stub with [ajv](https://ajv.js.org/) schema validation, implementing AuthZ evaluation, hash-chained audit ledger, health status, and error responses with compile-time schema validation against all 13 schemas
  - `package.json` — Dependencies (ajv ^8.12.0, uuid ^9.0.0, typescript ^5.3.0)
  - `tsconfig.json` — TypeScript configuration targeting ES2020
- **CI/CD pipeline** (`.github/workflows/ci.yml`):
  - `lint-and-format` job — Matrix across Python 3.10, 3.11, 3.12: ruff lint, ruff format check, pytest conformance suite (269 tests)
  - `schema-validation` job — Validates all 13 JSON schemas for structure and example self-validation using `jsonschema` Draft202012Validator
  - `docs-lint` job — Verifies required documentation files exist and checks for broken internal markdown links
- **Architecture documentation** (`docs/architecture.md`) — Five-server topology ASCII diagram, server responsibility table (23 tools across 5 servers), complete data flow diagram (6-phase robot procedure flow), hash-chained audit ledger architecture, cross-server audit coordination, national deployment topology
- **Adoption roadmap** (`docs/adoption-roadmap.md`) — Four-phase adoption roadmap: Phase 0 (Specification Review, 2–4 weeks), Phase 1 (Profile Selection, 4–8 weeks), Phase 2 (Conformance Validation, 8–12 weeks), Phase 3 (Pilot Deployment, 3–6 months ongoing). Each phase includes activities, deliverables, and duration estimates.
- **Glossary** (`docs/glossary.md`) — Standard terminology organized by category: Protocol and Architecture, Actors, Clinical Data Standards, Security and Privacy, Audit and Provenance, Physical AI, Regulatory, Specification Language, Versioning and Governance
- **Updated README** — v0.5.0 badges (CI Passing, TypeScript 5.3), Reference Implementations section with Mermaid architecture diagram and summary table, CI/CD Pipeline section with pipeline diagram, normative vs informative labels in repository structure, expanded Getting Started with adoption roadmap and glossary references, updated CODEOWNERS with `/reference/` and `/docs/` ownership
- **Updated prompts.md** — v0.5.0 prompt archived
- **Updated CODEOWNERS** — Added `/reference/` and `/docs/` directory ownership

## Contributors
@kevinkawchak
@claude

## Notes
- Reference implementations are explicitly marked NON-NORMATIVE — they demonstrate implementation patterns but do not define requirements
- The Python reference implementation uses only standard library modules plus `jsonschema` (already a test dependency)
- The TypeScript reference uses `ajv` for JSON Schema draft 2020-12 validation, matching the schema standard used throughout the specification
- CI/CD pipeline matches the existing `lint-and-format` job naming convention to ensure checks pass on pull requests
- The adoption roadmap provides concrete timelines for national-scale deployment: from specification review (Phase 0) through pilot site deployment (Phase 3)
- The glossary defines 50+ terms covering all aspects of the standard, ensuring consistent terminology across all U.S. clinical sites, sponsors, CROs, and technology vendors
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.4.0 - Conformance Test Suite for National MCP-PAI Oncology Trials Standard

## Summary

Introduces a comprehensive conformance test suite under `/conformance/` containing 269 automated tests across four categories — positive, negative, security, and interoperability — that enable any U.S. clinical site, vendor, sponsor, CRO, or technology provider to validate their MCP server implementation against the national standard. The suite includes shared pytest fixtures, schema validation helpers, and test fixture data extracted from the 13 JSON schemas. A `pyproject.toml` is added to configure ruff linting, formatting, and pytest for Python 3.10–3.12. README updated with v0.4.0 badges, conformance test architecture Mermaid diagram, national conformance validation flow diagram, and updated repository structure.

## Features

- **Conformance Test Harness** (`/conformance/`) with 269 automated tests across 4 categories:
  - `conftest.py` — Shared pytest fixtures, JSON Schema draft 2020-12 validation helpers, schema loading utilities
  - `fixtures/` — Test fixture data extracted from `/schemas/` and `/spec/`:
    - `audit_records.py` — Sample audit records, hash chains, genesis hash, error responses, health status
    - `authz_decisions.py` — ALLOW/DENY decisions, 6-actor permission matrix, unauthorized access attempts
    - `clinical_resources.py` — De-identified FHIR patients, DICOM queries, SSRF payloads, invalid IDs
    - `provenance_records.py` — Provenance DAG records, cross-server traces, multi-server sequences
- **Positive conformance tests** (`positive/`):
  - `test_core_conformance.py` — Audit record production, error envelope format, health check structure, authorization decisions (Level 1 Core)
  - `test_clinical_read_conformance.py` — FHIR read/search responses, HIPAA Safe Harbor de-identification, HMAC pseudonymization, year-only dates (Level 2 Clinical Read)
  - `test_imaging_conformance.py` — DICOM query responses, MUST/SHOULD modality requirements, role-based query level permissions, UID validation, patient name hashing (Level 3 Imaging)
- **Negative conformance tests** (`negative/`):
  - `test_invalid_inputs.py` — Malformed FHIR IDs, invalid DICOM UIDs, input length limits (1000 chars, 50 keys, 100 elements), schema field mismatches, wrong formats
  - `test_unauthorized_access.py` — Deny-by-default enforcement, permission escalation prevention, role boundary validation, DENY precedence over ALLOW
- **Security conformance tests** (`security/`):
  - `test_ssrf_prevention.py` — URL injection in resource IDs, case-insensitive protocol detection, internal IP address patterns, data/javascript URI rejection
  - `test_token_lifecycle.py` — Token issuance (UUID v4, SHA-256 hash), default/max expiry enforcement, UTC timestamps, immediate revocation, revocation permanence
  - `test_chain_integrity.py` — Genesis hash verification, chain continuity, hash tampering detection (modified fields, swapped records, deleted records, inserted foreign records), canonical JSON serialization
- **Interoperability conformance tests** (`interoperability/`):
  - `test_cross_server_trace.py` — Multi-server audit chain spanning all 5 MCP servers, operational order verification, cross-server provenance DAG, federated audit coordination
  - `test_schema_validation.py` — All 13 schema files validated for existence, JSON validity, draft 2020-12 compliance, required fields ($id, title, description), and schema example self-validation
- **`pyproject.toml`** — Python project configuration with ruff lint/format rules (E, F, I, W) and pytest configuration
- **Updated README** — v0.4.0 badges (Conformance Tests: 269 Passing), conformance test architecture Mermaid diagram, conformance test summary table, national conformance validation flow text diagram, updated repository structure with `/conformance/` directory, updated Getting Started with test suite step
- **Updated CODEOWNERS** — Added `/conformance/` directory ownership
- **Updated prompts.md** — v0.4.0 prompt archived

## Contributors
@kevinkawchak
@claude

## Notes
- The conformance test suite runs on Python 3.10, 3.11, and 3.12 with `pytest` and `jsonschema` as test dependencies
- All 269 tests pass with ruff lint and format checks clean across all Python files
- Test fixtures are extracted from the 13 JSON schemas (v0.2.0) and normative specification modules (v0.1.0)
- The suite validates conformance levels 1–5: Core (authz + audit), Clinical Read (FHIR + de-ID), Imaging (DICOM + modalities), Federated (cross-server provenance), and Robot Procedure (all servers)
- Security tests cover the three critical areas from the reference implementation: SSRF prevention, token lifecycle, and hash chain integrity
- Interoperability tests validate multi-server audit linkage and that all outputs conform to the 13 machine-readable schemas
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.3.0 - Profiles and Conformance Level Definitions for National MCP-PAI Oncology Trials Standard

## Summary

Introduces 8 conformance profiles under `/profiles/` that formalize the deployment requirements for each tier of the National MCP-PAI Oncology Trials Standard. Five core profiles define a progressive conformance ladder from base authorization/audit through full robot-assisted procedures, while three regulatory overlay profiles address California CCPA, New York health information laws, and FDA 21 CFR Part 11. Each profile specifies mandatory tools, optional tools, forbidden operations, required schemas, regulatory overlays, and a conformance test subset — enabling any U.S. clinical site, sponsor, CRO, or technology vendor to precisely determine which requirements apply to their deployment.

## Features

- **8 Conformance Profiles** (`/profiles/`) defining the full national deployment requirements:
  - `base-profile.md` — Core conformance: deny-by-default RBAC authorization, hash-chained audit ledger, 9-code error taxonomy. Every implementation MUST satisfy this profile.
  - `clinical-read.md` — FHIR R4 read/search with mandatory HIPAA Safe Harbor de-identification. MUST tools: `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status`.
  - `imaging-guided-oncology.md` — DICOM query/retrieve with role-based modality restrictions. MUST modalities: CT, MR, PT. SHOULD modalities: RTSTRUCT, RTPLAN.
  - `multi-site-federated.md` — Cross-site DAG-based data provenance, federated audit chain coordination, data residency policy enforcement, federated learning provenance.
  - `robot-assisted-procedure.md` — Robot capability profile with USL scoring, task-order contract lifecycle, pre-procedure safety matrix, six-step robot agent workflow.
  - `state-us-ca.md` — California CCPA/CPRA overlay: consumer rights (Right to Know, Right to Delete, Right to Opt-Out), sensitive PI protections, data minimization.
  - `state-us-ny.md` — New York health information overlay: PHL Article 27-F (HIV confidentiality), SHIELD Act security safeguards, MHL Article 33 (mental health), DOH 10 NYCRR.
  - `country-us-fda.md` — FDA 21 CFR Part 11 overlay: electronic records (Subpart B §11.10), electronic signatures (§11.50/§11.70/§11.100), SaMD classification, GMLP alignment.
- **Profile architecture Mermaid diagram** — Visualizes progressive conformance ladder with regulatory overlay dependencies
- **National profile deployment map** — Text diagram showing jurisdiction-specific profile stacking
- **Updated README** — Version 0.3.0 badges, Profiles section with summary tables, updated repository structure, updated Getting Started with profile-based guidance
- **Updated CODEOWNERS** — Added `/profiles/` ownership
- **Updated prompts.md** — v0.3.0 prompt archived

## Contributors
@kevinkawchak
@claude

## Notes
- Each profile defines a conformance test subset with specific test counts (Base: 19, Clinical Read: 29, Imaging: 39, Federated: 48, Robot: 58)
- Regulatory overlay profiles (CA, NY, FDA) are additive — they stack on top of core conformance profiles based on site jurisdiction
- State overlays address laws beyond federal HIPAA: California CCPA/CPRA and New York PHL/SHIELD/MHL
- The FDA overlay maps every section of 21 CFR Part 11 Subpart B to specific MCP standard components
- Robot-assisted procedure profile integrates USL scoring from the [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179) framework
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.2.0 - Machine-Readable JSON Schemas for National MCP-PAI Oncology Trials Standard

## Summary

Introduces 13 machine-readable JSON Schema files (JSON Schema draft 2020-12) under `/schemas/`, formalizing the data contracts for all MCP server interactions, robot capability profiles, site descriptors, task orders, consent tracking, and operational health monitoring across the National MCP-PAI Oncology Trials network. Each schema is extracted from the existing server code structures in the reference implementation and scaled to national industry-wide deployment. README badges, diagrams, and repository structure documentation updated for v0.2.0.

## Features

- **13 JSON Schemas** (`/schemas/`) with `$id`, `title`, `description`, `required`, and `examples` per JSON Schema draft 2020-12:
  - `capability-descriptor.schema.json` — Server capability advertisement (name, version, tools, conformance level)
  - `robot-capability-profile.schema.json` — Physical AI platform profile with USL scoring and safety prerequisites
  - `site-capability-profile.schema.json` — Clinical site descriptor (jurisdiction, servers, data residency)
  - `task-order.schema.json` — Scheduled clinical trial task for Physical AI systems
  - `audit-record.schema.json` — Hash-chained 21 CFR Part 11 audit ledger record
  - `provenance-record.schema.json` — DAG-based data lineage and SHA-256 fingerprinting record
  - `consent-status.schema.json` — Patient consent state machine with granular categories
  - `authz-decision.schema.json` — Deny-by-default RBAC authorization decision
  - `dicom-query.schema.json` — DICOM query parameters, output, and role-based permissions
  - `fhir-read.schema.json` — FHIR R4 single resource read with HIPAA de-identification
  - `fhir-search.schema.json` — FHIR R4 collection search with result capping
  - `error-response.schema.json` — Standardized error response with 9-code taxonomy
  - `health-status.schema.json` — Server health check with dependency and metrics reporting
- **README badges** — Version, JSON Schema, Python, Protocol (MCP), Date, License, DOI, Contributors
- **Updated architecture diagrams** — Schema validation flow, national deployment topology, protocol flow
- **Updated Mermaid diagrams** — Schema catalog, conformance levels, actor model, security model
- **Updated repository structure** — Reflects new `/schemas/` directory with all 13 schema files
- **Updated prompts.md** — v0.2.0 prompt archived

## Contributors
@kevinkawchak
@claude

## Notes
- All schemas reference the normative specification modules in `/spec/` and regulatory overlays in `/regulatory/`
- Schemas are designed for automated validation of MCP server inputs/outputs across all conforming U.S. clinical trial sites
- The consent-status schema introduces a formal state machine for tracking granular patient consent categories specific to Physical AI trial participation
- Robot capability profiles incorporate USL (Unification Standard Level) scoring from the Physical AI Oncology Trials framework
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.1.0 - Initial Specification Draft for National MCP-PAI Oncology Trials Standard

## Summary

First public release of the National MCP-PAI Oncology Trials Standard — a normative specification for deploying Model Context Protocol (MCP) servers across federated Physical AI oncology clinical trial systems in the United States. Includes 9 specification modules, 4 regulatory overlays, full governance framework, and community contribution templates.

## Features

- **9 Specification Modules** — Core architecture, 6-actor model, 23 tool contracts, security baseline, privacy framework, provenance DAG, audit ledger, 5-level conformance model, SemVer versioning
- **4 Regulatory Overlays** — FDA AI/ML guidance, HIPAA Privacy/Security Rule mapping, 21 CFR Part 11 electronic records, IRB site policy template
- **Governance Framework** — Charter, decision process, extension namespaces, version compatibility, CODEOWNERS
- **Community Templates** — GitHub issue templates (bug report, feature request, spec change), PR template, Contributor Covenant Code of Conduct
- **README** — Architecture diagrams, conformance summary, actor model, tool registry, regulatory matrix, comparison tables

## Contributors
@kevinkawchak
@claude

## Notes
- Derived from analysis of [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) (TrialMCP v0.3.0)
- References: [Physical AI Oncology Trials](https://github.com/kevinkawchak/physical-ai-oncology-trials), [PAI Oncology Trial FL](https://github.com/kevinkawchak/pai-oncology-trial-fl)
