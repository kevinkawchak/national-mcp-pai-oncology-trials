# Changelog

All notable changes to the National MCP-PAI Oncology Trials Standard are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) as described in [spec/versioning.md](spec/versioning.md).

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
