# Releases

Release notes for the National MCP-PAI Oncology Trials Standard.

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
