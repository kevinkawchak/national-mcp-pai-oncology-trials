# Releases

Release notes for the National MCP-PAI Oncology Trials Standard.

---

v0.7.0 - Phase 2: Real Server Implementations, Persistence, and Deployment Infrastructure

## Summary

Transforms the repository from a specification-and-fixtures project into a repository containing real, runnable, production-shaped MCP server implementations for all five server domains (authz, fhir, dicom, ledger, provenance), backed by persistence abstractions (in-memory, SQLite, PostgreSQL) and deployable via Docker, Kubernetes, and Helm. Adds shared server infrastructure (`servers/common/`), a storage adapter layer (`servers/storage/`), deployment manifests (`deploy/`), an end-to-end quickstart demo (`examples/quickstart/`), expanded TypeScript server implementations with Jest tests, and CLI entry points for all five servers. All 313 existing tests continue to pass with clean ruff lint and format checks.

## Features

- **5 production-shaped MCP server packages** (`servers/`) — Each with MCP transport entrypoint, tool routing, audit hooks, health/readiness endpoints, structured JSON logging, and configuration management:
  - `trialmcp_authz/` — Deny-by-default RBAC policy engine (6-actor matrix), SHA-256 token lifecycle, persistent policy/token stores
  - `trialmcp_fhir/` — HIPAA Safe Harbor de-identification pipeline (18-identifier removal), HMAC-SHA256 pseudonymization, FHIR adapter interface (mock/HAPI/SMART)
  - `trialmcp_dicom/` — Role-based modality restrictions (MUST: CT, MR, PT; SHOULD: RTSTRUCT, RTPLAN), DICOM UID validation, patient name hashing (12-char SHA-256)
  - `trialmcp_ledger/` — Hash-chained immutable audit ledger with SHA-256 canonical JSON, genesis block, chain verification, concurrency-safe locking
  - `trialmcp_provenance/` — DAG-based lineage graph with SHA-256 fingerprinting, W3C PROV alignment, forward/backward traversal, cycle detection
- **Shared server infrastructure** (`servers/common/`) — MCP transport layer (stdin/stdout JSON-RPC 2.0), request routing, auth/audit middleware, 9-code error taxonomy, env var/YAML/JSON config, structured JSON logging, health checker, schema validation
- **Persistence layer** (`servers/storage/`) — Abstract base interface, in-memory adapter (testing), SQLite adapter (single-site), PostgreSQL adapter interface (production), migration utilities, config-driven factory
- **Docker deployment** (`deploy/docker/`) — Individual Dockerfiles for each server + all-in-one image, `docker-compose.yml` for single-site (5 servers), `docker-compose.multi-site.yml` for Site A + Site B + shared ledger
- **Kubernetes deployment** (`deploy/kubernetes/`) — Namespace, ConfigMap, Secrets template, Deployment + Service for each of the 5 servers
- **Helm chart** (`deploy/helm/trialmcp/`) — Configurable Helm chart with values for replicas, resources, storage backend, log level
- **Configuration files** (`deploy/config/`) — Example YAML config for each server, site-profile-example.yaml, .env.example
- **End-to-end quickstart demo** (`examples/quickstart/`) — `run_demo.py` script executing complete workflow: token issuance → validation → authz evaluation → FHIR read (de-identified) → DICOM query (hashed) → ledger append → provenance record → chain verification → DAG verification
- **Expanded TypeScript** (`reference/typescript/`) — AuthZ server (`authz-server.ts`) and Ledger server (`ledger-server.ts`) implementations, generated interfaces (`interfaces.ts`), Jest test suites (`*.test.ts`), npm test/lint scripts
- **CLI entry points** — `trialmcp-authz`, `trialmcp-fhir`, `trialmcp-dicom`, `trialmcp-ledger`, `trialmcp-provenance` via `pyproject.toml` scripts
- **Updated `pyproject.toml`** — Version 0.7.0, entry points, optional dependency extras (`[fhir]`, `[dicom]`, `[dev]`, `[test]`, `[docs]`, `[all]`), `servers` and `examples` in known-first-party imports
- **Updated `README.md`** — v0.7.0 badges (Docker, MCP Servers: 5), new MCP Server Implementations section with Mermaid diagram, Deployment Infrastructure section, Quickstart Demo section, updated repository structure
- **Updated `changelog.md`** — v0.7.0 changelog entry
- **Updated `releases.md`** — v0.7.0 release notes (this entry)
- **Updated `prompts.md`** — v0.7.0 prompt archived

## Contributors
@kevinkawchak
@claude
@openai

## Notes
- All 313 tests pass (44 unit + 269 conformance) across Python 3.10, 3.11, 3.12 with clean ruff lint and format checks
- The 5 server packages implement all 23 tool contracts from spec/tool-contracts.md across their respective domains
- Each server follows the same architectural pattern: config → storage → domain logic → router → transport → middleware
- The persistence layer supports 3 backends: memory (testing), SQLite (single-site), PostgreSQL (production) — selected via config
- Docker Compose files support both single-site (5 servers) and multi-site (Site A + Site B + shared ledger) topologies
- The quickstart demo runs entirely in-process without network dependencies, exercising all 5 servers end-to-end
- TypeScript implementation expanded from 1 file (core-server.ts) to 6 files including dedicated authz and ledger servers with Jest test coverage
- Server entry points are registered as console_scripts in pyproject.toml, installable via `pip install -e .`
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.6.0 - Phase 1: Correctness, Contract Alignment, and Schema-Code Drift Resolution

## Summary

Comprehensively fixes all schema/code/test drift and contract mismatches across the entire repository, establishing a single canonical source of truth for all data contracts. Introduces a typed model generation pipeline (`scripts/generate_models.py`) that produces Python dataclasses and TypeScript interfaces from the 13 JSON schemas, adds contract-consistency and TypeScript build CI jobs, and tightens maturity labeling throughout all documentation. All reference implementation outputs now validate against their canonical schemas end-to-end.

## Features

- **Schema/code contract alignment** — All 4 core functions (`authz_evaluate`, `ledger_append`, `health_status`, `error_response`) in both Python and TypeScript now produce schema-valid output:
  - `authz_evaluate()`: `decision`/`resource_id`/`reason`/`timestamp` → `allowed`/`effect`/`server`/`evaluated_at` with structured `matching_rules` objects per `authz-decision.schema.json`
  - `ledger_append()`: `record_id`/`prev_hash` → `audit_id`/`previous_hash` per `audit-record.schema.json`
  - `health_status()`: `server`/`timestamp`/`dependencies{}` → `server_name`/`checked_at`/`dependencies[]` per `health-status.schema.json`
  - `error_response()`: added optional `server` parameter for schema-valid output
- **Typed model generation pipeline** (`scripts/generate_models.py`) — Reads all 13 schemas, produces `models/python/generated_models.py` (dataclasses) and `models/typescript/generated_models.ts` (interfaces)
- **CI/CD pipeline hardening** (`.github/workflows/ci.yml`) — 3 new jobs:
  - `contract-consistency`: regenerates models (fail if drift), validates runtime outputs against schemas
  - `typescript-build`: `tsc --noEmit` compile check
  - `docs-lint`: broken link check now fails on errors (`sys.exit(1 if errors else 0)`)
- **Maturity labeling** — "Normative Specification" → "Proposed Reference Standard"; "reference implementation" → "Level 1 illustrative implementation"; added maturity callout in README distinguishing normative specs from illustrative code
- **Expanded unit tests** — 28 → 44 tests covering corrected field names, structured matching rules, deny reasons, dependency arrays, server names
- **Updated `pyproject.toml`** — Version 0.6.0, added `models` and `scripts` to known-first-party imports
- **Updated `README.md`** — v0.6.0 badges, 5-job CI pipeline table, updated repository structure, updated test counts
- **Updated `changelog.md`** — v0.6.0 changelog entry
- **Updated `releases.md`** — v0.6.0 release notes (this entry)
- **Updated `prompts.md`** — v0.6.0 prompt archived

## Contributors
@kevinkawchak
@claude
@openai

## Notes
- All 313 tests pass (44 unit + 269 conformance) across Python 3.10, 3.11, 3.12 with clean ruff lint and format checks
- The typed model generation pipeline is the canonical contract source — CI fails if generated output differs from committed models
- Contract-consistency CI validates that `authz_evaluate`, `ledger_append`, `health_status`, and `error_response` runtime outputs pass JSON Schema validation against their respective schemas
- TypeScript build CI ensures the TypeScript reference compiles without errors
- The docs-lint job now fails on broken internal links (previously exited with 0 regardless)
- Maturity labeling distinguishes normative specifications (`/spec/`, `/schemas/`, `/profiles/`) from illustrative implementations (`/reference/`) and clarifies the path from specification to validated deployment
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

---

v0.5.2 - Peer Review Response + Implementation Roadmap Prompts for National MCP-PAI Oncology Trials Standard

## Summary

Responds to two comprehensive external peer reviews (ChatGPT 5.4 Thinking) with structured response tables documenting Implemented/Deferred status for all recommendations, creates 5 comprehensive implementation prompts (`claude-1` through `claude-5`) targeting future 1M token processing sessions to transform the repository from a specification-and-fixtures repo into a canonical national implementation source, and archives the v0.5.2 development prompt in `prompts.md`.

## Features

- **Peer review response tables** (`/peer-review/response-A-2026-03-06.md`) — Structured response to all recommendations from two ChatGPT 5.4 Thinking reviews:
  - Feedback 1 (8 sections, 44 recommendations): candid repo review covering contract mismatches, conformance testing, operational credibility, code surface expansion, packaging, governance, and restructuring plan
  - Feedback 2 (17 sections, 56 recommendations): strategic gap analysis covering canonical integration repo, server consolidation, integration adapters, interoperability testbed, deployment artifacts, stakeholder guides, SDKs, benchmarks, robot safety, documentation quality, and software engineering hygiene
  - Each recommendation categorized as Add/Fix/Remove with Implemented/Deferred status and prompt assignment
- **5 comprehensive implementation prompts** (`/peer-review/claude-1-2026-03-06.md` through `claude-5-2026-03-06.md`):
  - Prompt 1 (v0.6.0): Phase 1 — Correctness, contract alignment, schema-code drift resolution, CI hardening, maturity labeling
  - Prompt 2 (v0.7.0): Phase 2 — Real server implementations for all 5 domains, persistence layer, deployment infrastructure (Docker/Kubernetes/Helm), end-to-end demo
  - Prompt 3 (v0.8.0): Phase 3 — Black-box conformance harness, national interoperability testbed, adversarial test packs, certification/evidence generation, benchmarks
  - Prompt 4 (v0.9.0): Phase 4 — Integration adapters (FHIR/DICOM/identity/clinical), robot safety boundaries, clinical safety guardrails, privacy/regulatory modules, federated coordination
  - Prompt 5 (v1.0.0): Phase 5 — Python/TypeScript SDKs, CLI tools, stakeholder guides, operational documentation, governance evidence, architecture decision records, repository strategy
- **Updated `prompts.md`** — v0.5.2 prompt archived
- **Updated `releases.md`** — v0.5.2 release notes added
- **Updated `changelog.md`** — v0.5.2 changelog entry added

## Contributors
@kevinkawchak
@claude
@openai

## Notes
- This release contains no code changes to existing reference implementations, conformance tests, or schemas — all 308 tests (39 unit + 269 conformance) remain passing
- The 5 prompts collectively address 100 specific recommendations across both peer reviews, with only 1 recommendation deferred (renaming `reference/` → `examples/minimal-reference/` deferred for user continuity)
- Prompts are designed for sequential execution in separate 1M token Claude Code Opus 4.6 sessions, each building on the prior phase
- The phased roadmap aligns with both peer reviews' recommended restructuring plans: Phase 1 (correctness) → Phase 2 (runnable source) → Phase 3 (conformance credibility) → Phase 4 (integration + safety) → Phase 5 (stakeholder readiness)
- References: [TrialMCP](https://doi.org/10.5281/zenodo.18869776), [Physical AI Oncology Trials](https://doi.org/10.5281/zenodo.18445179), [PAI Oncology Trial FL](https://doi.org/10.5281/zenodo.18840880)

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
