# Releases

Release notes for the National MCP-PAI Oncology Trials Standard.

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
