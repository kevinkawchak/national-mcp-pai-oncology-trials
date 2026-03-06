# Changelog

All notable changes to the National MCP-PAI Oncology Trials Standard are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) as described in [spec/versioning.md](spec/versioning.md).

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
