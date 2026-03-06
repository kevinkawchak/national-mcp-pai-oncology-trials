## Prompt v0.1.0

Your goal in the new comprehensive national-mcp-pai-oncology-trials v0.1.0 release is to scale to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification. 

Create national specific documentation throughout the repo; the main readme needs to be disbursed with the following throughout: 3 relevant text diagrams and 3 relevant colored mermaid diagrams (make sure mermaid diagrams view well on smartphones, and don’t require excessive pan/zoom due to being too long in one dimension). State the features and benefits of this national approach opposed to the prior kevinkawchak/mcp-pai-oncology-trials repository, existing oncology trial approaches, and other known MCP/AI software servers approaches for oncology trials. After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.) 

“START MAIN PROMPT”
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
“END PROMPT”

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): “3 failing checks 
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... “ Place the new release notes in releases.md under main using the format below. Update changelog.md using v0.1.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

“FORMAT”
Release title 
v0.1.0 - 

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes
