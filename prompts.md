## Prompt v0.5.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.5.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)


It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.5.0): Reference Implementations + CI/CD + Documentation
Creates: /reference/python/, /reference/typescript/, .github/workflows/ci.yml, /docs/ (3 files), updated README.md
* reference/python/ — NON-NORMATIVE. Minimal Core server, schema validator, conformance runner.
* reference/typescript/ — NON-NORMATIVE. Minimal Core server stub with ajv validation.
* .github/workflows/ci.yml — Lint (ruff), test (pytest), schema validation, conformance suite, docs linting.
* docs/architecture.md — 5-server topology, data flow, audit chain (ASCII diagrams).
* docs/adoption-roadmap.md — Phase 0 (spec) → Phase 1 (profiles) → Phase 2 (conformance) → Phase 3 (pilots).
* docs/glossary.md — Standard terminology.
* Updated README.md — Repository layout section, normative vs informative labels, CI badges.
"END PROMPT"

---

## Prompt v0.4.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.4.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.4.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.4.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.4.0): Conformance Test Suite
Creates: /conformance/ (README + conftest + fixtures + 4 test directories with actual test files)
* conformance/README.md — Harness overview, how to run, how to add tests
* conformance/conftest.py — Shared fixtures, schema validation helpers
* conformance/fixtures/ — Extracted from datasets/
* conformance/positive/test_core_conformance.py — Audit production, error envelope, health, authz (from tests/audit/)
* conformance/positive/test_clinical_read_conformance.py — FHIR + de-identification (from tests/integration/)
* conformance/positive/test_imaging_conformance.py — DICOM conformance
* conformance/negative/test_invalid_inputs.py — Malformed requests, schema mismatches
* conformance/negative/test_unauthorized_access.py — Deny-by-default (from tests/security/TestPermissionEscalation)
* conformance/security/test_ssrf_prevention.py — URL injection (from tests/security/TestSSRFPrevention)
* conformance/security/test_token_lifecycle.py — Expiry, revocation
* conformance/security/test_chain_integrity.py — Hash chain tampering
* conformance/interoperability/test_cross_server_trace.py — Multi-server audit linkage (from tests/integration/)
* conformance/interoperability/test_schema_validation.py — All outputs validated against /schemas/
"END PROMPT"

---

## Prompt v0.3.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.3.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.3.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.3.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.3.0): Profiles and Conformance Level Definitions
Creates: /profiles/ (8 markdown files)
* base-profile.md — Core conformance: authz + audit + error taxonomy. Every implementation MUST.
* clinical-read.md — FHIR read/search + HIPAA de-identification. MUST: fhir_read, fhir_search, fhir_patient_lookup, fhir_study_status.
* imaging-guided-oncology.md — DICOM query/retrieve + role-based modality restrictions. MUST: CT, MR, PT. SHOULD: RTSTRUCT, RTPLAN.
* multi-site-federated.md — Cross-site provenance, federated audit chain, data residency policy.
* robot-assisted-procedure.md — Robot capability profile, task-order contract, safety matrix, USL scoring. References schemas.
* state-us-ca.md — California CCPA overlay.
* state-us-ny.md — New York health info overlay.
* country-us-fda.md — FDA 21 CFR Part 11 overlay.
Each profile: mandatory tools, optional tools, forbidden ops, required schemas, regulatory overlays, conformance test subset.
"END PROMPT"

---

## Prompt v0.2.0

Include more Readme badges such as version, language(s), tests, protocol, date, and contributors. Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version, don't use the format from releases.md). Update changelog.md using v0.2.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.2.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.2.0): Machine-Readable JSON Schemas
Creates: /schemas/ (13 JSON Schema files)
Each schema extracted from existing server code structures:
* capability-descriptor.schema.json — Server capability ad (name, version, tools, conformance level)
* robot-capability-profile.schema.json — From trial_robot_agent.py (platform, robot_type) + trial_schedule.json (usl_score, safety prerequisites)
* site-capability-profile.schema.json — Site descriptor (jurisdiction, servers, data residency)
* task-order.schema.json — From datasets/scheduling/trial_schedule.json structure
* audit-record.schema.json — From ledger_server.py AuditRecord dataclass fields
* provenance-record.schema.json — From provenance_server.py ProvenanceRecord fields
* consent-status.schema.json — Consent state machine
* authz-decision.schema.json — From authz_server.py evaluate return shape
* dicom-query.schema.json — From dicom_server.py dicom_query params/output
* fhir-read.schema.json — From fhir_server.py fhir_read params/output
* fhir-search.schema.json — From fhir_server.py fhir_search params/output
* error-response.schema.json — From servers/common/__init__.py error_response()
* health-status.schema.json — From servers/common/__init__.py health_status()
All use JSON Schema draft 2020-12 with $id, title, description, required, examples.
"END PROMPT"

---

## Prompt v0.1.0

Your goal in the new comprehensive national-mcp-pai-oncology-trials v0.1.0 release is to scale to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Create national specific documentation throughout the repo; the main readme needs to be disbursed with the following throughout: 3 relevant text diagrams and 3 relevant colored mermaid diagrams (make sure mermaid diagrams view well on smartphones, and don't require excessive pan/zoom due to being too long in one dimension). State the features and benefits of this national approach opposed to the prior kevinkawchak/mcp-pai-oncology-trials repository, existing oncology trial approaches, and other known MCP/AI software servers approaches for oncology trials. After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

"START MAIN PROMPT"
(v0.1.0): Normative Specification + Governance + Regulatory Overlays + Community Files
Creates: /spec/ (9 files), /governance/ (5 files), /regulatory/ (4 files), .github/ (templates), CODE_OF_CONDUCT.md
Key spec files and their source material from existing code:
* spec/core.md — Protocol scope, design principles, 5 conformance levels (Core, Clinical Read, Imaging, Federated Site, Robot Procedure). Uses RFC 2119 MUST/SHOULD/MAY.
* spec/actor-model.md — 6 actors extracted from servers/trialmcp_authz/src/authz_server.pyDEFAULT_POLICY roles (robot_agent, trial_coordinator, data_monitor, auditor) plus sponsor and CRO.
* spec/tool-contracts.md — All 23 tool signatures from the 5 servers' handle_tool_call methods, with input params, output shape, error codes, and audit requirements.
* spec/security.md — Deny-by-default RBAC from authz_server.py PolicyEngine, token lifecycle, SSRF prevention from servers/common/__init__.py validators.
* spec/privacy.md — HIPAA Safe Harbor de-identification from fhir_server.py _deidentify_resource(), HMAC-SHA256 pseudonymization, DICOM patient hashing from dicom_server.py.
* spec/provenance.md — DAG lineage model from provenance_server.py DataSource/ProvenanceRecord, SHA-256 fingerprinting, forward/backward queries.
* spec/audit.md — Hash-chained ledger from ledger_server.py, genesis hash, chain verification, replay trace, 21 CFR Part 11 mapping.
* spec/conformance.md — 5 conformance levels with MUST/SHOULD/MAY per level, mandatory tool sets per level.
* spec/versioning.md — SemVer, compatibility policy, extension namespace x-{vendor}, deprecation rules.
* governance/CHARTER.md, DECISION_PROCESS.md, EXTENSIONS.md, VERSION_COMPATIBILITY.md, CODEOWNERS
* regulatory/US_FDA.md, HIPAA.md, CFR_PART_11.md, IRB_SITE_POLICY_TEMPLATE.md
* .github/ISSUE_TEMPLATE/bug_report.md, feature_request.md, spec_change.md; .github/PULL_REQUEST_TEMPLATE.md
* CODE_OF_CONDUCT.md (Contributor Covenant)
"END PROMPT"

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below. Update changelog.md using v0.1.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.1.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes
