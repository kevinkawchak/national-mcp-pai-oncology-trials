## Prompt v1.2.0

Based on the national-mcp-pai-oncology-trials repository, create a GitHub page titled “Demonstration: National MCP Servers for Physical AI Oncology Clinical Trial Systems” that serves as a reference architecture demonstration and interactive simulation. Make sure to clone the current repo. Include author Kevin Kawchak, the iD icon (with clickable link: https://orcid.org/0009-0007-5457-8667), Chief Executive Officer, ChemicalQDevice, kevink@chemicalqdevice.com, today's date (retrieve other specifics such as badges or references from the repository and the related paper). Mention Claude Code Opus 4.6 and ChatGPT 5.4 Thinking as contributors. No em dashes are allowed anywhere on the page. A balance of directory names, version numbers, and file names should be utilized strategically throughout the page. No dark mode images or dark mode diagrams are allowed.

Update all repository documentation, readmes, repository structures, text diagrams and mermaid diagrams, tocs (with correct urls and make sure it is in the right order.) Make sure the repository is fully up to date regarding badges, content, and context prior to the last release and new human commits. (Note: the current oncology clinical trial system should be referred to as the old OR prior OR previous system throughout the page). Make sure the GitHub page shows as a deployment in main.

Utilize information primarily from the following. Include web links to GitHub repositories where relevant.
1) kevinkawchak/national-mcp-pai-oncology-trials (10.5281/zenodo.18894758)
2) national-mcp-pai-oncology-trials/blob/main/paper/National_MCP_Servers_for_Physical_AI_Oncology_Clinical_Trial_Systems.tex
(paper doi: 10.5281/zenodo.18916731)

Be sure to implement quantitative data, code snippets, text diagrams (fix where needed, and make sure incorporation is suitable to the page). Make sure every section is properly formatted and is attractive to read (a mix of different paragraph lengths)(a mix of bullet points and numbered lists, and other types of formatting to avoid a large number of long paragraphs). Avoid large white empty spaces without text. Where large spacing between words exist throughout the paper, tables, and references: modify spacing to make positioning between words look equally and properly spaced.

Make sure text doesn’t run off the right side of the page anywhere. Perform the final formatting steps that a senior author would take by correcting white space formatting, removing and/or adding relevant text to make each section look properly formatted and self standing by itself. (Don’t overcrowd the page with text, some white space formatting is ok).

Provide a copy of this v1.2.0 prompt under the related prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as for docs-lint and Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below. Update other relevant documentation such as project structures. Update the main Readme diagrams, repository structure, etc. where necessary. Provide an updated changelog (v1.2.0).

Also output the GitHub page as a formatted pdf with file name "Demonstration: National MCP Servers for Physical AI Oncology Clinical Trial Systems" as a .pdf under main/site. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v1.2.0 - [Fill in Title Here]

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes






“START MAIN PROMPT”
Prompt Content Summary
Create a complete GitHub Pages site called “Demonstration: National MCP Servers for Physical AI Oncology Clinical Trial Systems" in a new site/ directory at the repository root (keeping docs/ untouched for its existing role as internal documentation).
1. File Manifest (what Claude Code must create)
* site/index.html - Main landing page (single-page application)
* site/css/style.css - Core styles (medical/clinical design system)
* site/css/diagrams.css - Diagram-specific styles and animations
* site/js/app.js - Main application logic, navigation, scroll behavior
* site/js/diagrams.js - Interactive SVG diagram rendering engine that converts the 7 process diagrams into animated/interactive web visuals
* site/js/simulator.js - National deployment topology simulator (deterministic simulation, not live system)
* site/js/conformance.js - Conformance level explorer with interactive 5-level hierarchy
* site/data/topology.json - National 3-tier deployment topology data (750+ sites across East/Central/West regions)
* site/data/servers.json - 5 MCP server metadata, 23 tools, schemas
* site/data/safety.json - 8 safety module definitions and state machines
* site/CNAME (optional, if custom domain)
* site/.nojekyll - Bypass Jekyll processing
* Root-level update: GitHub Pages configuration note in README.md
2. Seven Interactive Diagram Sections (from docs/mcp-process)
Each diagram file is explicitly referenced and converted to an interactive web component:
Source File	Web Section	Visualization Type
01-robot-procedure-lifecycle.md	Robot Procedure Lifecycle	Animated state machine with clickable states (SCHEDULED -> PRE_CHECK -> GATES_EVAL -> HUMAN_APPROVAL -> IN_PROGRESS -> COMPLETED/ABORTED), showing MCP server interactions per state transition
02-cross-site-mcp-communication.md	Cross-Site Communication	Animated network topology showing 5 MCP servers per site with cross-site audit chain sync and token exchange flows
03-clinical-system-integration.md	Clinical System Integration	Layered adapter diagram showing FHIR/DICOM/Identity integration pathways with EHR (Epic, Cerner, MEDITECH) and PACS connections
04-safety-gate-evaluation.md	Safety Gate Evaluation	Sequential gate visualization (5 gates: Patient Consent, Site Capability, Robot Capability, Protocol Compliance, Human Approval) with pass/fail/timeout states
05-federated-learning-coordination.md	Federated Learning	Multi-site federated round animation showing FedAvg/FedProx/SCAFFOLD aggregation with differential privacy budget tracking
06-audit-provenance-chain.md	Audit & Provenance Chain	Hash-chain visualization with SHA-256 block linking and DAG provenance graph with forward/backward lineage queries
07-privacy-deidentification.md	Privacy & De-identification	HIPAA Safe Harbor 18-identifier pipeline visualization with 3-stage flow (Direct IDs, Quasi-IDs, Technical IDs) and HMAC-SHA256 pseudonymization
3. Classification & Disclaimers (explicitly stated)
* What this IS: A reference architecture demonstration and interactive simulation of the proposed National MCP-PAI Oncology Trials Standard. It is an educational and stakeholder communication tool that visualizes the system described in the paper using deterministic simulations with pre-configured data.
* What this is NOT: This is NOT a deployed clinical system, NOT approved for use in actual oncology trials, NOT connected to real patient data, EHR systems, PACS, or robotic systems, and NOT a medical device or software as a medical device (SaMD).
* Simulation conditions/approximations: All data shown is synthetic. Network latencies, site counts, and response times are modeled approximations based on the paper's architecture. Federated learning rounds use illustrative aggregation, not real model weights. Hash chains demonstrate the algorithm with sample data.
* What is needed for actual trial use: (a) FDA review and recognition as a consensus standard, (b) Clinical pilot deployment at NCI-designated cancer centers, (c) Real EHR/PACS adapter validation with vendor systems (Epic, Cerner, Orthanc, dcm4chee), (d) Robot vendor certification program, (e) IRB approval at each participating site, (f) 21 CFR Part 11 compliance audit of deployed instances, (g) HIPAA security risk assessment.
* Current status: This is a proposed reference standard with a complete reference implementation (381 files, ~69,800 lines) that has not yet been deployed in clinical settings.
4. Landing Page Sections
1. Hero - Title, paper citation, Zenodo DOI badge, repository link
2. Abstract - Paper abstract with key metrics (5 servers, 23 tools, 668 tests, 381 files)
3. Architecture Overview - Interactive 5-server diagram with tool counts per server
4. Seven Process Diagrams - Interactive sections for each of the 7 docs/mcp-process files
5. National Deployment Topology - 3-tier map (National Governance -> 3 Regional Layers -> 750+ Sites) with animated data flow
6. Conformance Levels - Interactive 5-level hierarchy explorer (Core -> Clinical Read -> Imaging -> Federated Site -> Robot Procedure)
7. Safety Modules - 8 safety module visualization with E-Stop lifecycle animation
8. Repository Scale - Statistics dashboard (files, tests, adapters, schemas, etc.)
9. Adoption Roadmap - Stakeholder-specific pathways (Sponsors, CROs, Hospital IT, Regulators, Robot Vendors)
10. Classification & Status - Prominent disclaimer section as described above
11. Citation & Links - BibTeX, DOI, repository links, paper PDF
5. Perform 
* Create all files listed in the manifest above
* Commit with message referencing v1.2.0 GitHub Pages deployment
* Push to the repository
* Report back the full file tree of site/ and confirm GitHub Pages can be enabled by pointing to the site/ directory (or docs/ if reconfigured)


---

## Prompt v1.1.0 (Primary)

Your goal is to generate a 20 page paper titled “National MCP Servers for Physical AI Oncology Clinical Trial Systems” based on the entire national-mcp-pai-oncology-trials repository with a focus on a) prior oncology trial infrastructure being fragmented, site-specific, and inefficient across interoperability, auditability, privacy, and deployment, b) the national MCP Physical AI oncology trials system containing 5 MCP servers address these gaps through standardized, federated, and safety-governed MCP capabilities, including c) AI and robotics advances intended to improve patient safety and clinical effectiveness. Patient benefit is key in this new mcp system.
(Note: the current oncology clinical trial system should be referred to as the old or prior or previous system throughout the paper)

The paper should be written in LaTeX using 10.5281/zenodo.18916731 (https://doi.org/10.5281/zenodo.18916731) where appropriate. Use the kourgeorge/arxiv-style/blob/master/arxiv.sty - except remove the "A Preprint" from the top of the page, and don't add colored box frames around text, links, etc. (https://github.com/kourgeorge/arxiv-style). Include author Kevin Kawchak, the template’s iD icon (the icon needs to include the clickable link: https://orcid.org/0009-0007-5457-8667), Chief Executive Officer, ChemicalQDevice, kevink@chemicalqdevice.com, today's date, and 5 keywords. No em dashes are allowed in the paper. A balance of directory names, version numbers, and file names should be utilized strategically throughout the paper, as well as citing the 3 other repositories below that aided in the development of the current repository.

Make sure to clone the current repo. Utilize information from sources 1)-4) in the following order of importance. Use prior .tex files for additional context where needed. Include web links to GitHub repositories.
1) kevinkawchak/national-mcp-pai-oncology-trials (10.5281/zenodo.18894758)(paper doi: 10.5281/zenodo.18916731)
2) kevinkawchak/mcp-pai-oncology-trials (10.5281/zenodo.18869776)(paper .tex: mcp-pai-oncology-trials/tree/main/papers, paper doi: 10.5281/zenodo.18870961)
3) kevinkawchak/physical-ai-oncology-trials  (10.5281/zenodo.18445179)(paper .tex: kevinkawchak/physical-ai-oncology-trials/tree/main/unification/usl/paper)(paper doi: 10.5281/zenodo.18778220)
4) kevinkawchak/pai-oncology-trial-fl()(paper .tex: pai-oncology-trial-fl/tree/main/paper)(paper doi: 10.5281/zenodo.18795507)

Be sure to implement quantitative data, code snippets, text diagrams (fix where needed, and make sure incorporation is suitable to the paper), etc. where appropriate. It is imperative that all types of information utilized from across the repository be accurate and appropriate to each section of the paper. Make sure every section is properly formatted and is attractive to read (a mix of different paragraph lengths)(a mix of bullet points and numbered lists, and other types of formatting to avoid too many long paragraphs). Avoid large white empty spaces without text. Where large spacing between words exist throughout the paper, tables, and references: modify raggedright to make positioning between words look equally and properly spaced.

Paper Sections:
- Abstract: Focus on covering a)-c) from above using information from relevant sections of the repo. State that this is a proposed end-to-end mcp physical ai oncology trial system towards the end.
- Table of Contents
- Introduction: Provide a comprehensive overview of what brought oncology clinical trials to need this current system.
- Methods: Utilize prompts.md, changelog.md, and releases.md for insights regarding how the repository and paper (using this current prompt) was built. Include the author as the prompt creator, and AI manufacturers and models (primarily Anthropic Claude Code Opus 4.6 for generating the repository and this paper; and also OpenAI ChatGPT 5.4 Thinking used for peer review (under /peer-review). Be sure to provide both comprehensive and fine grained dates that are based on releases, such as total number of days (span), total number of days with an AI update, number of days of AI code recommendations, and the number of days of AI fixes (again using version ids throughout)
- Results: Stress the importance of the 5 mcp servers in the repository in terms of applicable to clinical trials, between other robots, between other clinical trials, etc. 
- Discussion: Write in detail about the significance of the 5 MCPs system as the oncology clinical trial standard; along with better AI and robot automation.
- Limitations and Future Work: (Be sure to describe the human, Claude Code, and OpenAI limitations throughout the entire process to date.) Future work for the author and industry includes increasing MCP physical ai trial automation.
- Conclusion: State that this is a proposed end-to-end mcp physical ai oncology trial system towards the beginning. Discuss why the prior point-to-point system couldn’t scale, and how this system will. Focus on the take home message of a)-c) from above using data from relevant sections of the repo.
- References (include references for 1)-4) GitHub links, Zenodo DOIs,and paper DOIs)
- Acknowledgments (see below)
- Ethical disclosures (see below)
- Rights and permissions (see below)
- Cite this article (see below)

Use an assortment of tables and text diagrams according to the paper’s style guide, making sure that some are comprehensive and complete. When doing these tables and diagrams, make sure there is not excessive white spacing in pages (use extra relevant text to make the paper look publication quality). Make sure text doesn’t run off the right side of the page anywhere. Perform the final formatting steps that a senior author would take by having proper white space formatting, removing and/or adding relevant text to make each of the 20 pages look properly formatted and self standing by itself. (Don’t overcrowd any page with text, some white space formatting is ok). Again, extra care is required for each of the 20 pages to make the end-to-end paper publication quality high: all text, tables, and diagrams context and visual formatting must reflect the best quality proof-reading and appearance practices.

Update all relevant documentation and readme throughout the repository text, diagrams, mermaid diagrams (don’t use mermaid diagrams or images in this paper), repository structure, etc. based on this paper (include a prominent Zenodo link in main readme). Provide a copy of this prompt under the related prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below. Update other relevant documentation such as project structures. Update the main Readme diagrams, repository structure, etc. where necessary. Provide an updated changelog (v1.1.0).

Output the finished paper with file name "National MCP Servers for Physical AI Oncology Clinical Trial Systems" as a .pdf under /main/paper. Output a zip file containing 4 files in /paper titled "Latex Source Code" under /paper: .tex,.sty, README, .bib. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v1.1.0 - [Fill in Title Here]

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes


Acknowledgments
The author would like to acknowledge Anthropic for providing access to Claude Code for repository and paper generations; and OpenAI for providing access to ChatGPT for peer-review.

Ethical disclosures
The author of the article declares no competing interests.

Rights and permissions
This article is distributed under the terms of the Creative Commons Attribution 4.0 International License (CC BY 4.0), which permits unrestricted use, distribution, and reproduction in any medium, provided the original author(s) and source are properly credited, a link to the Creative Commons license is provided, and any modifications made are indicated. To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/.

Cite this article
Kawchak K. National MCP Servers for Physical AI Oncology Clinical Trial Systems. Zenodo. 2026; 10.5281/zenodo.18916731.

---

## Prompt v1.1.0 (2nd)

Fix and update current PR.

---

## Prompt v1.1.0 (3rd)

Update the current branch with another commit that creates a whole new paper and set of pdf and latex files under /paper (create a “prior” directory under /paper for all of the prior paper files)
1) make each of the page headings “National MCP Servers for Physical AI Oncology Clinical Trial Systems” an appropriately smaller font size to fit on one line, center justified.
2) the introduction must start after keywords on the first page, then the entire toc starts on page 2 (where it currently is), then the rest of the introduction comes after the end of toc. (Update the toc and other relevant paper information based on this new commit)
3) current page 6 repository names column entries overlaps with date range entries (same problem with the server column on page 7) (same problem with tool column on page 9) (same problem with schema file column on page 12).
4) avoid diagrams from being split between pages.
5) Re-evaluate the entire finished pdf to verify these issues are fixed, then make any other necessary formatting fixes. Make sure all checks will pass.

---

## Prompt v1.0.1

For national-mcp-pai-oncology-trials: the following two prompts were processed in v1.0.0: but not all tasks were completed fully and accurately. For instance, the stats.md and next-steps.md need to be fully up to date and correct throughout paragraphs, lists, and bullet points (v1.0.1 is to be used, not v0.1.0.) Also the main readme did not update badges, diagrams, documentation, etc. Update all documentation repo wide to be accurate and comprehensive based on the following prompts. The “Original Prompt” and “Follow-up Prompt” below must be fully applied and correct throughout the repo.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): “3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... “ Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v1.0.1. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

“FORMAT”
Release title
v1.0.1 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes









“Original Prompt”
Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Change the last version’s /mcp-process-diagrams to /mcp-process and move the directory with readme to main. Update relevant readme files and documentation throughout the repo (including /mcp-process) based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): “3 failing checks 
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... “ Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v1.0.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

“FORMAT”
Release title 
v1.0.0 - 

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes


“START MAIN PROMPT”
v1.0.0 - Phase 5: SDKs, Stakeholder Guides, Governance, and Operational Readiness

Your goal is to make national-mcp-pai-oncology-trials fully adoptable by institutions, vendors, and regulators by adding versioned SDKs, stakeholder-specific implementation guides, operational runbooks, governance evidence, and production-readiness documentation. This is the stakeholder-readiness phase that transforms the repository from a technical resource into a national adoption-ready platform. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. Python SDK**

Create `sdk/python/` with a complete client SDK:

- `sdk/python/trialmcp_client/` — Python client package:
  - `client.py` — Unified MCP client with connection management, retry logic, circuit breaker
  - `authz.py` — AuthZ client (evaluate, issue_token, validate_token, revoke_token)
  - `fhir.py` — FHIR client (read, search, patient_lookup, study_status)
  - `dicom.py` — DICOM client (query, retrieve)
  - `ledger.py` — Ledger client (append, verify, query, export)
  - `provenance.py` — Provenance client (record, query_forward, query_backward, verify)
  - `models.py` — Re-exported generated typed models from `models/python/`
  - `exceptions.py` — Typed exception hierarchy matching 9-code error taxonomy
  - `config.py` — Client configuration (server addresses, auth credentials, timeouts, retry policy)
  - `middleware/` — Pluggable middleware:
    - `auth_middleware.py` — Automatic token management and refresh
    - `audit_middleware.py` — Client-side audit logging
    - `retry_middleware.py` — Configurable retry with exponential backoff
    - `circuit_breaker.py` — Circuit breaker for clinical dependency resilience
- `sdk/python/examples/` — Example scripts for each actor role:
  - `robot_agent_example.py` — Complete robot agent workflow
  - `trial_coordinator_example.py` — Trial coordinator study management
  - `data_monitor_example.py` — Data monitor review workflow
  - `auditor_example.py` — Auditor chain verification and replay
  - `sponsor_example.py` — Sponsor cross-site oversight
  - `cro_example.py` — CRO multi-site validation
- `sdk/python/setup.py` / `pyproject.toml` — Installable package with versioned releases

**2. TypeScript SDK**

Create `sdk/typescript/` with a complete client SDK:

- `sdk/typescript/src/` — TypeScript client package:
  - `client.ts` — Unified MCP client with connection management
  - `authz.ts`, `fhir.ts`, `dicom.ts`, `ledger.ts`, `provenance.ts` — Domain clients
  - `models/` — Re-exported generated TypeScript interfaces
  - `errors.ts` — Typed error classes matching 9-code error taxonomy
  - `config.ts` — Client configuration
  - `middleware/` — Auth, audit, retry, circuit breaker middleware
- `sdk/typescript/examples/` — Example scripts for each actor role
- `sdk/typescript/package.json` — npm package with versioned releases
- `sdk/typescript/tsconfig.json` — TypeScript configuration
- `sdk/typescript/jest.config.js` — Test configuration
- `sdk/typescript/tests/` — SDK tests

**3. CLI and Code Generation Tools**

Create `tools/cli/` with developer tooling:

- `tools/cli/trialmcp_cli.py` — Main CLI entry point:
  - `trialmcp init` — Initialize a new implementation project with profile selection
  - `trialmcp scaffold` — Generate server scaffolding from profile requirements
  - `trialmcp validate` — Validate a server implementation against conformance criteria
  - `trialmcp certify` — Run certification suite and generate evidence pack
  - `trialmcp schema diff` — Compare schema versions for compatibility
  - `trialmcp config generate` — Generate configuration templates for site/server
- `tools/codegen/` — Schema code generation:
  - `tools/codegen/generate_python.py` — Generate Python dataclasses/Pydantic models from schemas
  - `tools/codegen/generate_typescript.py` — Generate TypeScript interfaces from schemas
  - `tools/codegen/generate_openapi.py` — Generate OpenAPI specs from tool contracts
  - `tools/codegen/templates/` — Jinja2 templates for code generation

**4. Stakeholder-Specific Implementation Guides**

Create `docs/guides/` with role-specific adoption paths:

- `docs/guides/hospital-it.md` — Hospital IT / Cancer Center guide:
  - Site deployment checklist (prerequisites, infrastructure, network, identity)
  - PACS/EHR integration path (FHIR R4 + DICOMweb connectivity)
  - PHI boundary and retention controls
  - Network segmentation requirements
  - Identity provider integration (OIDC, AD/LDAP)
  - Monitoring and alerting setup
  - Data backup and recovery procedures
  - Staff training requirements

- `docs/guides/robot-vendor.md` — Robot vendor guide:
  - Capability descriptor requirements and examples
  - Task-order semantics and lifecycle
  - Safety gate expectations and certification
  - Simulator-to-clinical promotion path (USL scoring progression)
  - Integration testing requirements
  - Firmware/software update procedures
  - Incident reporting obligations

- `docs/guides/sponsor-cro.md` — Sponsor/CRO guide:
  - Cross-site reporting interfaces
  - Provenance and audit review procedures
  - State/federal regulatory overlay implications by jurisdiction
  - Multi-site deployment coordination
  - Data quality monitoring
  - Study close-out procedures

- `docs/guides/regulator-irb.md` — Regulator/IRB guide:
  - Evidence package structure and contents
  - Conformance artifact interpretation
  - Audit replay package format
  - Change control and validation package
  - Inspection readiness checklist
  - Regulatory submission guidance

- `docs/guides/standards-community.md` — Standards community guide:
  - Extension proposal process (x-{vendor} namespace)
  - Compatibility policy and versioning rules
  - Schema evolution rules (additive changes, deprecation lifecycle)
  - Contribution workflow for specification changes
  - Review and approval process

**5. Operational Documentation**

Create comprehensive operational docs:

- `docs/operations/runbook.md` — Production operations runbook:
  - Server startup/shutdown procedures
  - Health check monitoring
  - Log analysis and troubleshooting
  - Common failure scenarios and resolutions
  - Performance tuning guidance
  - Capacity planning

- `docs/operations/incident-response.md` — Incident response playbook:
  - Severity classification (P1-P4)
  - Escalation paths
  - Communication templates
  - Post-incident review process
  - Evidence preservation procedures

- `docs/operations/key-management.md` — Key management guide:
  - Key generation and storage requirements
  - Token signing key lifecycle
  - Audit record signing key management
  - mTLS certificate management
  - Key rotation procedures and schedules
  - KMS/HSM integration guidance
  - Secrets rotation automation

- `docs/operations/backup-recovery.md` — Backup and recovery procedures:
  - Audit chain backup and integrity verification
  - Provenance graph backup
  - Configuration backup
  - Disaster recovery procedures
  - Recovery time objectives (RTO) and recovery point objectives (RPO)

- `docs/deployment/local-dev.md` — Local development setup guide
- `docs/deployment/hospital-site.md` — Hospital site deployment guide
- `docs/deployment/multi-site-federated.md` — Multi-site federated deployment guide

**6. SLO/SLA Guidance**

Create `docs/operations/slo-guidance.md`:

- Uptime targets per server and per conformance level
- Latency budgets (P50, P95, P99) for each tool
- Fail-safe modes and degraded operation rules
- Data recovery procedures and timelines
- Availability requirements during active procedures
- Monitoring and alerting thresholds

**7. Governance and Adoption Evidence**

Create governance artifacts:

- `docs/governance/decision-log.md` — Decision log of accepted/declined changes with rationale
- `docs/governance/implementation-status.md` — Implementation status matrix (normative section → implementation status → test coverage)
- `docs/governance/roadmap.md` — Roadmap with target adopters, milestones, and timelines
- `docs/governance/compatibility-matrix.md` — Compatibility matrix by version, profile, and conformance level
- `docs/governance/known-gaps.md` — Known gaps, non-goals, and future work
- `docs/governance/contribution-policy.md` — Contribution policy for regulators, vendors, providers, CROs, and standards bodies

**8. Architecture Decision Records**

Create `docs/adr/` with key architectural decisions:

- `docs/adr/001-mcp-protocol-boundary.md` — Why MCP is the right protocol boundary for national oncology trial interoperability
- `docs/adr/002-five-server-architecture.md` — Why these 5 servers were chosen (authz, fhir, dicom, ledger, provenance)
- `docs/adr/003-twenty-three-tools.md` — Why 23 tools are the minimal stable surface area
- `docs/adr/004-profile-conformance-levels.md` — Why profiles map to clinical deployment tiers
- `docs/adr/005-hash-chained-audit.md` — Why hash-chained audit ledger for 21 CFR Part 11 compliance
- `docs/adr/006-dag-provenance.md` — Why DAG-based provenance over linear lineage
- `docs/adr/007-deny-by-default-rbac.md` — Why deny-by-default RBAC for clinical safety

**9. Repository Strategy**

Create `docs/repository-strategy.md`:

- What stays in each repository across the four repos
- What graduates into the national repo
- What is mirrored vs imported vs referenced
- What becomes deprecated
- What becomes the canonical implementation source
- Migration timeline and criteria

**10. Security Documentation**

Create security-focused documentation:

- `docs/security/threat-model.md` — Threat model document covering all attack surfaces
- `docs/security/sbom.md` — SBOM generation guidance and dependency scanning policy
- `docs/security/tamper-evident-storage.md` — Tamper-evident storage design for audit and provenance
- `docs/security/signed-releases.md` — Signed release and release provenance policy

**11. Production Concerns Documentation**

Create `docs/operations/production-concerns.md`:

- Retries and circuit breakers for clinical dependencies
- Idempotency behavior for write-like actions
- Concurrency and locking strategy for ledger writes
- Backpressure and queueing patterns
- Observability standards (metrics, traces, logs)
- Audit export and archival flows
- Log redaction defaults for PHI protection

**12. Profile Walkthroughs**

Create one complete end-to-end walkthrough per profile:

- `docs/walkthroughs/base-profile.md` — Core AuthZ + Audit walkthrough
- `docs/walkthroughs/clinical-read.md` — FHIR read/search with de-identification walkthrough
- `docs/walkthroughs/imaging-guided.md` — DICOM query with modality restrictions walkthrough
- `docs/walkthroughs/multi-site-federated.md` — Cross-site provenance and audit walkthrough
- `docs/walkthroughs/robot-procedure.md` — Complete robot-assisted procedure walkthrough

**13. Update CI Pipeline**

Add CI jobs for:

- SDK build and test (Python + TypeScript)
- CLI tool smoke tests
- Code generation consistency check
- Security scanning (dependency audit)
- SBOM generation
- Documentation build and link validation

**14. Verify Repository-Wide Quality**

After all changes:
1. Python SDK installs and all example scripts run
2. TypeScript SDK builds and all tests pass
3. CLI tool executes all subcommands
4. All stakeholder guides are complete and internally consistent
5. All operational docs reference actual code and configuration
6. All ADRs are well-structured and reference the relevant specification sections
7. All existing tests still pass
8. `ruff check .` and `ruff format --check .` pass cleanly
“Original Prompt”




“Follow-up Prompt”
Also add the following two files to main branch:
main/next-steps.md
main/stats.md

A) Create a comprehensive next-steps.md that explains, in practical and nationally relevant terms, what all stakeholder groups are expected to do now that the repository is publicly available and usable as a proposed national reference standard.

The document should be written for a nationwide audience and should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

The content should be action-oriented, specific, and organized for real-world adoption. It should clearly describe immediate, near-term, and medium-term actions for major stakeholder groups, including sponsors, CROs, academic medical centers, community oncology sites, hospital IT and security teams, robotics vendors, EHR and FHIR integration teams, imaging and PACS and DICOM teams, privacy and compliance and legal and regulatory teams, principal investigators, trial coordinators, auditors, data monitors, and standards contributors or open-source maintainers.

The document should include, where appropriate, what each stakeholder should review first in the repository, what each stakeholder should deploy, validate, or evaluate next, which profiles, schemas, tools, safety modules, governance materials, and test assets are most relevant to them, recommended sequencing of adoption activities, dependencies between technical, operational, clinical, and regulatory workstreams, expected readiness checkpoints for pilot adoption, expectations for documentation, conformance validation, and evidence generation, what should happen at single-site, multi-site, and national coordination levels, and a clear distinction between actions to take now, actions to plan next, and actions that require formal validation before production or clinical use.

The document should read like an adoption and execution guide rather than a vague summary. It should be comprehensive but concise, and it should reflect the repository’s positioning as a national MCP and Physical AI oncology trials standard.

B) Create a comprehensive stats.md that presents repository statistics and quantitative summary data in a way that is useful to technical, clinical, compliance, standards, and interoperability audiences.

The document should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

It should be metrics-heavy and use quantitative data throughout wherever the repository supports it. The document should be written for readers interested in MCP ecosystems, interoperability maturity, and Physical AI oncology trials.

At minimum, include clearly labeled sections covering repository scale and scope, number and categories of tests, test types and what they validate, number of tools and their distribution by MCP server, MCP server count and server types, schema count and schema categories, profile count and profile types, integration adapter count and categories, safety module count and categories, benchmark and certification tooling count, deployment targets and infrastructure options, languages used across the repository, approximate lines of code if determinable from the repository contents, directory and artifact counts where meaningful, key takeaways, concise executive summary, notable strengths, differentiators, and maturity signals, and any other metrics likely to interest people working in MCPs, healthcare AI infrastructure, interoperability, federated systems, clinical robotics, and oncology trial operations.

Where possible, quantify and break down items such as total tests passed by suite and subtype, unit versus conformance versus integration versus adversarial versus black-box coverage, counts by server, tool family, schema family, and profile level, number of deployment modes, number of interoperability scenarios, number of actor types, number of regulatory overlays, number of benchmark categories, and number of certification or evidence-generation utilities.

Where exact runtime verification is not available from the current environment, use repository-documented counts and label them clearly as repository-reported or documented metrics rather than claiming fresh CI execution.

The document should also include concise summaries of what the metrics imply about technical maturity, why the statistics matter for national interoperability and oncology trial readiness, why these metrics are meaningful to MCP practitioners, and why the quantitative profile is notable for Physical AI clinical trial infrastructure.

For both files, keep the writing professional, concrete, and repository-specific. Avoid filler language. Use headings and subheadings for readability. Use numbered lists when describing sequences, phases, or responsibilities. Use concise bullets for checklists, role-based actions, and metric breakdowns. Prefer precise wording over promotional wording. Keep the tone suitable for a standards-oriented public GitHub repository. Make the documents readable both by technical implementers and non-engineering stakeholders. Ensure the content is comprehensive enough to be useful immediately after publication.

Append this 2nd prompt to the first prompt used in this conversation in prompts.md
“Follow-up Prompt”

---

## Prompt v1.0.0

Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Change the last version's /mcp-process-diagrams to /mcp-process and move the directory with readme to main. Update relevant readme files and documentation throughout the repo (including /mcp-process) based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v1.0.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v1.0.0 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"START MAIN PROMPT"
v1.0.0 - Phase 5: SDKs, Stakeholder Guides, Governance, and Operational Readiness

Your goal is to make national-mcp-pai-oncology-trials fully adoptable by institutions, vendors, and regulators by adding versioned SDKs, stakeholder-specific implementation guides, operational runbooks, governance evidence, and production-readiness documentation. This is the stakeholder-readiness phase that transforms the repository from a technical resource into a national adoption-ready platform. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. Python SDK**

Create `sdk/python/` with a complete client SDK:

- `sdk/python/trialmcp_client/` — Python client package:
  - `client.py` — Unified MCP client with connection management, retry logic, circuit breaker
  - `authz.py` — AuthZ client (evaluate, issue_token, validate_token, revoke_token)
  - `fhir.py` — FHIR client (read, search, patient_lookup, study_status)
  - `dicom.py` — DICOM client (query, retrieve)
  - `ledger.py` — Ledger client (append, verify, query, export)
  - `provenance.py` — Provenance client (record, query_forward, query_backward, verify)
  - `models.py` — Re-exported generated typed models from `models/python/`
  - `exceptions.py` — Typed exception hierarchy matching 9-code error taxonomy
  - `config.py` — Client configuration (server addresses, auth credentials, timeouts, retry policy)
  - `middleware/` — Pluggable middleware:
    - `auth_middleware.py` — Automatic token management and refresh
    - `audit_middleware.py` — Client-side audit logging
    - `retry_middleware.py` — Configurable retry with exponential backoff
    - `circuit_breaker.py` — Circuit breaker for clinical dependency resilience
- `sdk/python/examples/` — Example scripts for each actor role:
  - `robot_agent_example.py` — Complete robot agent workflow
  - `trial_coordinator_example.py` — Trial coordinator study management
  - `data_monitor_example.py` — Data monitor review workflow
  - `auditor_example.py` — Auditor chain verification and replay
  - `sponsor_example.py` — Sponsor cross-site oversight
  - `cro_example.py` — CRO multi-site validation
- `sdk/python/setup.py` / `pyproject.toml` — Installable package with versioned releases

**2. TypeScript SDK**

Create `sdk/typescript/` with a complete client SDK:

- `sdk/typescript/src/` — TypeScript client package:
  - `client.ts` — Unified MCP client with connection management
  - `authz.ts`, `fhir.ts`, `dicom.ts`, `ledger.ts`, `provenance.ts` — Domain clients
  - `models/` — Re-exported generated TypeScript interfaces
  - `errors.ts` — Typed error classes matching 9-code error taxonomy
  - `config.ts` — Client configuration
  - `middleware/` — Auth, audit, retry, circuit breaker middleware
- `sdk/typescript/examples/` — Example scripts for each actor role
- `sdk/typescript/package.json` — npm package with versioned releases
- `sdk/typescript/tsconfig.json` — TypeScript configuration
- `sdk/typescript/jest.config.js` — Test configuration
- `sdk/typescript/tests/` — SDK tests

**3. CLI and Code Generation Tools**

Create `tools/cli/` with developer tooling:

- `tools/cli/trialmcp_cli.py` — Main CLI entry point:
  - `trialmcp init` — Initialize a new implementation project with profile selection
  - `trialmcp scaffold` — Generate server scaffolding from profile requirements
  - `trialmcp validate` — Validate a server implementation against conformance criteria
  - `trialmcp certify` — Run certification suite and generate evidence pack
  - `trialmcp schema diff` — Compare schema versions for compatibility
  - `trialmcp config generate` — Generate configuration templates for site/server
- `tools/codegen/` — Schema code generation:
  - `tools/codegen/generate_python.py` — Generate Python dataclasses/Pydantic models from schemas
  - `tools/codegen/generate_typescript.py` — Generate TypeScript interfaces from schemas
  - `tools/codegen/generate_openapi.py` — Generate OpenAPI specs from tool contracts
  - `tools/codegen/templates/` — Jinja2 templates for code generation

**4. Stakeholder-Specific Implementation Guides**

Create `docs/guides/` with role-specific adoption paths:

- `docs/guides/hospital-it.md` — Hospital IT / Cancer Center guide:
  - Site deployment checklist (prerequisites, infrastructure, network, identity)
  - PACS/EHR integration path (FHIR R4 + DICOMweb connectivity)
  - PHI boundary and retention controls
  - Network segmentation requirements
  - Identity provider integration (OIDC, AD/LDAP)
  - Monitoring and alerting setup
  - Data backup and recovery procedures
  - Staff training requirements

- `docs/guides/robot-vendor.md` — Robot vendor guide:
  - Capability descriptor requirements and examples
  - Task-order semantics and lifecycle
  - Safety gate expectations and certification
  - Simulator-to-clinical promotion path (USL scoring progression)
  - Integration testing requirements
  - Firmware/software update procedures
  - Incident reporting obligations

- `docs/guides/sponsor-cro.md` — Sponsor/CRO guide:
  - Cross-site reporting interfaces
  - Provenance and audit review procedures
  - State/federal regulatory overlay implications by jurisdiction
  - Multi-site deployment coordination
  - Data quality monitoring
  - Study close-out procedures

- `docs/guides/regulator-irb.md` — Regulator/IRB guide:
  - Evidence package structure and contents
  - Conformance artifact interpretation
  - Audit replay package format
  - Change control and validation package
  - Inspection readiness checklist
  - Regulatory submission guidance

- `docs/guides/standards-community.md` — Standards community guide:
  - Extension proposal process (x-{vendor} namespace)
  - Compatibility policy and versioning rules
  - Schema evolution rules (additive changes, deprecation lifecycle)
  - Contribution workflow for specification changes
  - Review and approval process

**5. Operational Documentation**

Create comprehensive operational docs:

- `docs/operations/runbook.md` — Production operations runbook:
  - Server startup/shutdown procedures
  - Health check monitoring
  - Log analysis and troubleshooting
  - Common failure scenarios and resolutions
  - Performance tuning guidance
  - Capacity planning

- `docs/operations/incident-response.md` — Incident response playbook:
  - Severity classification (P1-P4)
  - Escalation paths
  - Communication templates
  - Post-incident review process
  - Evidence preservation procedures

- `docs/operations/key-management.md` — Key management guide:
  - Key generation and storage requirements
  - Token signing key lifecycle
  - Audit record signing key management
  - mTLS certificate management
  - Key rotation procedures and schedules
  - KMS/HSM integration guidance
  - Secrets rotation automation

- `docs/operations/backup-recovery.md` — Backup and recovery procedures:
  - Audit chain backup and integrity verification
  - Provenance graph backup
  - Configuration backup
  - Disaster recovery procedures
  - Recovery time objectives (RTO) and recovery point objectives (RPO)

- `docs/deployment/local-dev.md` — Local development setup guide
- `docs/deployment/hospital-site.md` — Hospital site deployment guide
- `docs/deployment/multi-site-federated.md` — Multi-site federated deployment guide

**6. SLO/SLA Guidance**

Create `docs/operations/slo-guidance.md`:

- Uptime targets per server and per conformance level
- Latency budgets (P50, P95, P99) for each tool
- Fail-safe modes and degraded operation rules
- Data recovery procedures and timelines
- Availability requirements during active procedures
- Monitoring and alerting thresholds

**7. Governance and Adoption Evidence**

Create governance artifacts:

- `docs/governance/decision-log.md` — Decision log of accepted/declined changes with rationale
- `docs/governance/implementation-status.md` — Implementation status matrix (normative section → implementation status → test coverage)
- `docs/governance/roadmap.md` — Roadmap with target adopters, milestones, and timelines
- `docs/governance/compatibility-matrix.md` — Compatibility matrix by version, profile, and conformance level
- `docs/governance/known-gaps.md` — Known gaps, non-goals, and future work
- `docs/governance/contribution-policy.md` — Contribution policy for regulators, vendors, providers, CROs, and standards bodies

**8. Architecture Decision Records**

Create `docs/adr/` with key architectural decisions:

- `docs/adr/001-mcp-protocol-boundary.md` — Why MCP is the right protocol boundary for national oncology trial interoperability
- `docs/adr/002-five-server-architecture.md` — Why these 5 servers were chosen (authz, fhir, dicom, ledger, provenance)
- `docs/adr/003-twenty-three-tools.md` — Why 23 tools are the minimal stable surface area
- `docs/adr/004-profile-conformance-levels.md` — Why profiles map to clinical deployment tiers
- `docs/adr/005-hash-chained-audit.md` — Why hash-chained audit ledger for 21 CFR Part 11 compliance
- `docs/adr/006-dag-provenance.md` — Why DAG-based provenance over linear lineage
- `docs/adr/007-deny-by-default-rbac.md` — Why deny-by-default RBAC for clinical safety

**9. Repository Strategy**

Create `docs/repository-strategy.md`:

- What stays in each repository across the four repos
- What graduates into the national repo
- What is mirrored vs imported vs referenced
- What becomes deprecated
- What becomes the canonical implementation source
- Migration timeline and criteria

**10. Security Documentation**

Create security-focused documentation:

- `docs/security/threat-model.md` — Threat model document covering all attack surfaces
- `docs/security/sbom.md` — SBOM generation guidance and dependency scanning policy
- `docs/security/tamper-evident-storage.md` — Tamper-evident storage design for audit and provenance
- `docs/security/signed-releases.md` — Signed release and release provenance policy

**11. Production Concerns Documentation**

Create `docs/operations/production-concerns.md`:

- Retries and circuit breakers for clinical dependencies
- Idempotency behavior for write-like actions
- Concurrency and locking strategy for ledger writes
- Backpressure and queueing patterns
- Observability standards (metrics, traces, logs)
- Audit export and archival flows
- Log redaction defaults for PHI protection

**12. Profile Walkthroughs**

Create one complete end-to-end walkthrough per profile:

- `docs/walkthroughs/base-profile.md` — Core AuthZ + Audit walkthrough
- `docs/walkthroughs/clinical-read.md` — FHIR read/search with de-identification walkthrough
- `docs/walkthroughs/imaging-guided.md` — DICOM query with modality restrictions walkthrough
- `docs/walkthroughs/multi-site-federated.md` — Cross-site provenance and audit walkthrough
- `docs/walkthroughs/robot-procedure.md` — Complete robot-assisted procedure walkthrough

**13. Update CI Pipeline**

Add CI jobs for:

- SDK build and test (Python + TypeScript)
- CLI tool smoke tests
- Code generation consistency check
- Security scanning (dependency audit)
- SBOM generation
- Documentation build and link validation

**14. Verify Repository-Wide Quality**

After all changes:
1. Python SDK installs and all example scripts run
2. TypeScript SDK builds and all tests pass
3. CLI tool executes all subcommands
4. All stakeholder guides are complete and internally consistent
5. All operational docs reference actual code and configuration
6. All ADRs are well-structured and reference the relevant specification sections
7. All existing tests still pass
8. `ruff check .` and `ruff format --check .` pass cleanly

---

## Prompt v1.0.0 (2nd Prompt)

Continue and Finish.

Also add the following two files to main branch:
main/next-steps.md
main/stats.md

A) Create a comprehensive next-steps.md that explains, in practical and nationally relevant terms, what all stakeholder groups are expected to do now that the repository is publicly available and usable as a proposed national reference standard.

The document should be written for a nationwide audience and should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

The content should be action-oriented, specific, and organized for real-world adoption. It should clearly describe immediate, near-term, and medium-term actions for major stakeholder groups, including sponsors, CROs, academic medical centers, community oncology sites, hospital IT and security teams, robotics vendors, EHR and FHIR integration teams, imaging and PACS and DICOM teams, privacy and compliance and legal and regulatory teams, principal investigators, trial coordinators, auditors, data monitors, and standards contributors or open-source maintainers.

The document should include, where appropriate, what each stakeholder should review first in the repository, what each stakeholder should deploy, validate, or evaluate next, which profiles, schemas, tools, safety modules, governance materials, and test assets are most relevant to them, recommended sequencing of adoption activities, dependencies between technical, operational, clinical, and regulatory workstreams, expected readiness checkpoints for pilot adoption, expectations for documentation, conformance validation, and evidence generation, what should happen at single-site, multi-site, and national coordination levels, and a clear distinction between actions to take now, actions to plan next, and actions that require formal validation before production or clinical use.

The document should read like an adoption and execution guide rather than a vague summary. It should be comprehensive but concise, and it should reflect the repository’s positioning as a national MCP and Physical AI oncology trials standard.

B) Create a comprehensive stats.md that presents repository statistics and quantitative summary data in a way that is useful to technical, clinical, compliance, standards, and interoperability audiences.

The document should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

It should be metrics-heavy and use quantitative data throughout wherever the repository supports it. The document should be written for readers interested in MCP ecosystems, interoperability maturity, and Physical AI oncology trials.

At minimum, include clearly labeled sections covering repository scale and scope, number and categories of tests, test types and what they validate, number of tools and their distribution by MCP server, MCP server count and server types, schema count and schema categories, profile count and profile types, integration adapter count and categories, safety module count and categories, benchmark and certification tooling count, deployment targets and infrastructure options, languages used across the repository, approximate lines of code if determinable from the repository contents, directory and artifact counts where meaningful, key takeaways, concise executive summary, notable strengths, differentiators, and maturity signals, and any other metrics likely to interest people working in MCPs, healthcare AI infrastructure, interoperability, federated systems, clinical robotics, and oncology trial operations.

Where possible, quantify and break down items such as total tests passed by suite and subtype, unit versus conformance versus integration versus adversarial versus black-box coverage, counts by server, tool family, schema family, and profile level, number of deployment modes, number of interoperability scenarios, number of actor types, number of regulatory overlays, number of benchmark categories, and number of certification or evidence-generation utilities.

Where exact runtime verification is not available from the current environment, use repository-documented counts and label them clearly as repository-reported or documented metrics rather than claiming fresh CI execution.

The document should also include concise summaries of what the metrics imply about technical maturity, why the statistics matter for national interoperability and oncology trial readiness, why these metrics are meaningful to MCP practitioners, and why the quantitative profile is notable for Physical AI clinical trial infrastructure.

For both files, keep the writing professional, concrete, and repository-specific. Avoid filler language. Use headings and subheadings for readability. Use numbered lists when describing sequences, phases, or responsibilities. Use concise bullets for checklists, role-based actions, and metric breakdowns. Prefer precise wording over promotional wording. Keep the tone suitable for a standards-oriented public GitHub repository. Make the documents readable both by technical implementers and non-engineering stakeholders. Ensure the content is comprehensive enough to be useful immediately after publication.

Append this 2nd prompt to the first prompt used in this conversation in prompts.md

---

## Prompt v0.9.0

Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.) Make sure all text diagrams are professional and line up throughout diagrams properly, with no jagged edges. Similarly, transform all the simple cartoon like mermaid diagrams into publication-quality conceptual schematics with clear hierarchies and explicit labels, resulting in diagrams that are more square like.

A new (if no suitable directory) or existing directory under main that contains several (>5) professional detailed text diagrams (that are properly formatted with no jagged edges) of all of the comprehensive mcp processes throughout the entire repo is required. This could be detailed diagrams indicating mcps used between robots, between servers, between clinical trial sites, between different clinical trials (These are simply examples, choose the best diagrams based on the repo contents).

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.9.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.9.0 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"START MAIN PROMPT"
v0.9.0 - Phase 4: Integration Adapters, Clinical Safety Guardrails, and Robot Execution Boundaries

Your goal is to add real integration adapters for clinical systems (FHIR, DICOM, identity), implement clinical safety guardrails and robot execution boundaries with runnable policy layers, and consolidate the strongest privacy, regulatory, and federated coordination patterns from the companion repositories into the national standard. This phase makes the repository practically connectable to real hospital infrastructure and enforceably safe for Physical AI operations. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. FHIR Integration Adapters**

Create `integrations/fhir/` with production-grade FHIR connectivity:

- `integrations/fhir/base_adapter.py` — Abstract FHIR adapter interface (read, search, patient_lookup, study_status, capability_statement)
- `integrations/fhir/mock_adapter.py` — Mock FHIR adapter with synthetic patient data for local testing
- `integrations/fhir/hapi_adapter.py` — HAPI FHIR server adapter with REST client
- `integrations/fhir/smart_adapter.py` — SMART-on-FHIR / OAuth2 adapter with token management
- `integrations/fhir/deidentification.py` — Complete HIPAA Safe Harbor de-identification pipeline:
  - All 18 HIPAA identifiers removal with test corpus
  - HMAC-SHA256 pseudonymization with configurable keys
  - Year-only date generalization
  - Name/address redaction
  - Verification suite that tests de-identification completeness
- `integrations/fhir/capability.py` — FHIR capability statement generation and ingestion
- `integrations/fhir/terminology.py` — Terminology mapping hooks (ICD-10, SNOMED CT, LOINC, RxNorm)
- `integrations/fhir/bundle_handler.py` — Realistic FHIR Bundle handling (transaction, batch, search result bundles)
- `integrations/fhir/patient_filter.py` — Patient/resource access filters based on consent status and authorization

**2. DICOM Integration Adapters**

Create `integrations/dicom/` with imaging system connectivity:

- `integrations/dicom/base_adapter.py` — Abstract DICOM adapter interface (query, retrieve metadata, modality validation)
- `integrations/dicom/mock_adapter.py` — Mock DICOM adapter with synthetic imaging metadata
- `integrations/dicom/orthanc_adapter.py` — Orthanc DICOM server adapter
- `integrations/dicom/dcm4chee_adapter.py` — dcm4chee DICOM archive adapter
- `integrations/dicom/dicomweb.py` — DICOMweb support (QIDO-RS query, WADO-RS retrieve, STOW-RS store)
- `integrations/dicom/metadata_normalizer.py` — DICOM metadata normalization (tag harmonization, encoding normalization)
- `integrations/dicom/modality_filter.py` — Role-based modality restriction enforcement
- `integrations/dicom/recist.py` — RECIST 1.1 measurement payload examples and validators:
  - Target lesion measurement validation
  - Non-target lesion assessment
  - New lesion detection
  - Overall response calculation (CR, PR, SD, PD)
  - Timepoint comparison
- `integrations/dicom/safety.py` — Image reference safety constraints (no pixel data transfer, metadata-only pointers, retrieval authorization)

**3. Identity and Security Adapters**

Create `integrations/identity/` with enterprise identity connectivity:

- `integrations/identity/base_adapter.py` — Abstract identity adapter interface
- `integrations/identity/oidc_adapter.py` — OIDC/JWT token validation adapter
- `integrations/identity/mtls.py` — mTLS support utilities and certificate validation
- `integrations/identity/policy_engine.py` — External policy engine integration (OPA-compatible interface)
- `integrations/identity/kms.py` — KMS/HSM-backed signing key hooks for audit record signing and token signing

**4. Clinical Operations Adapters**

Create `integrations/clinical/` with trial operations connectivity:

- `integrations/clinical/econsent_adapter.py` — eConsent/IRB metadata adapter (consent status tracking, IRB approval verification)
- `integrations/clinical/scheduling_adapter.py` — Scheduling/task-order adapter (procedure scheduling, robot assignment, time window management)
- `integrations/clinical/provenance_export.py` — Provenance export adapter (W3C PROV-N export, graph visualization data, lineage report generation)

**5. Robot Safety and Execution Boundaries**

Create `servers/trialmcp_safety/` (or extend existing servers) with Physical AI safety enforcement:

- `safety/gate_service.py` — Safety gate service / policy layer:
  - Pre-procedure safety matrix evaluation
  - Multi-condition gate checking (patient consent, site capability, robot capability, trial protocol compliance, human approval)
  - Gate decision audit trail
- `safety/robot_registry.py` — Robot capability registry:
  - Robot platform registration with USL scoring
  - Capability descriptor validation against `robot-capability-profile.schema.json`
  - Robot-to-procedure eligibility matching
  - Simulation vs clinical certification status tracking
- `safety/task_validator.py` — Task-order validator with safety constraints:
  - Task-order validation against `task-order.schema.json`
  - Precondition verification contracts (patient identity confirmed, consent valid, site cleared, robot calibrated)
  - Post-procedure evidence capture contracts (completion status, measurements, adverse events)
  - Trial protocol constraint enforcement
- `safety/approval_checkpoint.py` — Human-approval checkpoint patterns:
  - Mandatory human-in-the-loop approval gates for specified procedure types
  - Approval request/response protocol
  - Approval timeout handling
  - Escalation paths for denied or timed-out approvals
- `safety/estop.py` — Emergency stop / override semantics:
  - E-stop signal propagation to all active servers
  - Abort procedure workflow with state preservation
  - Post-abort evidence capture
  - Recovery and re-authorization procedures
- `safety/procedure_state.py` — Procedure state machine:
  - States: SCHEDULED → PRE_CHECK → APPROVED → IN_PROGRESS → POST_CHECK → COMPLETED / ABORTED / FAILED
  - State transition validation
  - State persistence and recovery
  - Simulation-only vs clinical-mode flags with enforcement
- `safety/site_verifier.py` — Site capability verification:
  - Site capability profile validation against `site-capability-profile.schema.json`
  - Required infrastructure verification (servers, storage, network, regulatory overlay compliance)
  - Procedure eligibility determination based on site capabilities

**6. Privacy and Regulatory Modules**

Create `integrations/privacy/` consolidating patterns from companion repositories:

- `integrations/privacy/access_control.py` — Reusable access control manager (role-based + attribute-based access control, data classification enforcement)
- `integrations/privacy/deidentification_pipeline.py` — Unified de-identification pipeline (FHIR + DICOM + free-text de-identification, configurable per data type)
- `integrations/privacy/privacy_budget.py` — Privacy budget accounting (epsilon tracking for differential privacy, budget allocation per query/site)
- `integrations/privacy/data_residency.py` — Data residency enforcement (site-level data boundary policies, cross-site transfer authorization, jurisdiction-specific retention rules)

**7. Federated Coordination**

Create `integrations/federation/` consolidating patterns from pai-oncology-trial-fl:

- `integrations/federation/coordinator.py` — Federated coordinator abstractions (site enrollment, round management, aggregation coordination)
- `integrations/federation/secure_aggregation.py` — Secure aggregation hooks (aggregation protocol interface, privacy-preserving result combination)
- `integrations/federation/site_harmonization.py` — Site data harmonization interfaces (schema mapping, value set alignment, temporal alignment)
- `integrations/federation/policy_enforcement.py` — Site-level federation policy enforcement (what data participates, what computations are allowed, result release authorization)

**8. Verify Repository-Wide Quality**

After all changes:
1. All existing tests still pass
2. Each integration adapter has unit tests with mock backends
3. Safety gate service passes all safety scenarios
4. Robot registry validates against schema correctly
5. Procedure state machine handles all transitions correctly
6. De-identification pipeline removes all 18 HIPAA identifiers
7. `ruff check .` and `ruff format --check .` pass cleanly

---

## Prompt v0.8.0

Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.8.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.8.0 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"START MAIN PROMPT"
v0.8.0 — Phase 3: Black-Box Conformance, National Interoperability Testbed, and Evidence Generation

Your goal is to replace the current fixture-based conformance testing with a true black-box conformance harness and build a national interoperability testbed that proves cross-site behavior, deployment consistency, and failure modes. This phase makes the repository's conformance claims verifiable against real server deployments rather than internal fixture validation alone. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. Build Black-Box Conformance Harness**

Create `conformance/harness/` with a test harness that can target real server deployments:

- `conformance/harness/client.py` — MCP client that can connect to:
  - A local process (stdin/stdout MCP)
  - A containerized deployment (Docker socket or HTTP)
  - A staging URL (remote server)
  - A vendor implementation (any conforming MCP endpoint)
- `conformance/harness/config.py` — Harness configuration:
  - Target server URLs/addresses for each of the 5 servers
  - Authentication credentials for test sessions
  - Test data seeding options
  - Profile/level selection
  - Output format selection (JSON, JUnit XML, HTML)
- `conformance/harness/adapters/` — Pluggable transport adapters:
  - `stdin_adapter.py` — stdin/stdout MCP transport
  - `http_adapter.py` — HTTP transport adapter
  - `docker_adapter.py` — Docker container management adapter
  - `auth_adapter.py` — Authenticated session management
- `conformance/harness/data_seeder.py` — Test data seeding for target environments
- `conformance/harness/runner.py` — CLI runner with `--target`, `--profile`, `--level`, `--output-format` flags

**2. Refactor Existing Conformance Suite**

Reorganize the existing 269 conformance tests into three tiers:

- `conformance/unit/` — Unit tests for fixtures and helpers (tests that validate fixture construction and schema shapes — these remain fast and local)
- `conformance/integration/` — Integration tests for reference servers (tests that exercise the real server packages from Phase 2 via in-process calls)
- `conformance/blackbox/` — Black-box conformance tests for external implementations (tests that use the harness client to target any MCP server deployment):
  - `blackbox/test_authz_conformance.py` — AuthZ server conformance (token lifecycle, RBAC evaluation, deny-by-default enforcement)
  - `blackbox/test_fhir_conformance.py` — FHIR server conformance (read, search, de-identification, consent)
  - `blackbox/test_dicom_conformance.py` — DICOM server conformance (query, modality restrictions, UID validation)
  - `blackbox/test_ledger_conformance.py` — Ledger server conformance (append, verify, chain integrity, genesis)
  - `blackbox/test_provenance_conformance.py` — Provenance server conformance (record, query, DAG integrity)
  - `blackbox/test_cross_server_workflow.py` — End-to-end workflow conformance (robot token → FHIR → DICOM → ledger → provenance)

**3. Add Negative and Adversarial Test Packs**

Expand test coverage with adversarial scenarios:

- `conformance/adversarial/test_authz_bypass.py` — Authorization bypass attempts (role escalation, token reuse after revocation, expired token acceptance, forged tokens)
- `conformance/adversarial/test_phi_leakage.py` — PHI leakage detection (de-identification completeness, search result filtering, error message data exposure, log data exposure)
- `conformance/adversarial/test_replay_attacks.py` — Replay attack detection (duplicated audit records, replayed authorization requests, duplicated provenance records)
- `conformance/adversarial/test_chain_tampering.py` — Audit chain tampering (modified records, inserted foreign records, deleted records, reordered records, hash collision attempts)
- `conformance/adversarial/test_malformed_inputs.py` — Malformed clinical data handling (invalid FHIR resources, malformed DICOM UIDs, oversized payloads, injection attempts in all fields)
- `conformance/adversarial/test_rate_limiting.py` — Rate limiting and abuse (rapid token issuance, bulk query flooding, concurrent write contention)

**4. Build National Interoperability Testbed**

Create `interop-testbed/` with a multi-site simulation environment:

- `interop-testbed/docker-compose.yml` — Multi-site cluster:
  - Site A (hospital): all 5 servers + mock EHR (FHIR) + mock PACS (DICOM)
  - Site B (hospital): all 5 servers + mock EHR + mock PACS
  - Sponsor: authz + ledger + provenance servers
  - CRO: authz + fhir + ledger servers
  - Auditor: read-only ledger + provenance access
- `interop-testbed/personas/` — Actor persona configurations:
  - `robot_agent.yaml` — Robot agent credentials and capabilities
  - `trial_coordinator.yaml` — Trial coordinator access profile
  - `data_monitor.yaml` — Data monitor permissions
  - `auditor.yaml` — Auditor read-only profile
  - `sponsor.yaml` — Sponsor access profile
  - `cro.yaml` — CRO access profile
- `interop-testbed/scenarios/` — Test scenario definitions:
  - `cross_site_provenance.py` — Cross-site provenance trace and DAG merge
  - `audit_replay.py` — Auditor audit chain replay and verification
  - `token_exchange.py` — Token exchange and revocation across sites
  - `partial_outage.py` — Partial site outage and graceful degradation
  - `schema_drift.py` — Schema version mismatch detection between sites
  - `state_overlay.py` — California/New York/FDA regulatory overlay enforcement
  - `robot_workflow.py` — End-to-end robot procedure workflow across sites
  - `site_onboarding.py` — New site onboarding certification flow
- `interop-testbed/mock_services/` — Mock clinical system backends:
  - `mock_ehr.py` — Mock FHIR R4 server with synthetic patient data
  - `mock_pacs.py` — Mock DICOMweb server with synthetic imaging metadata
  - `mock_identity.py` — Mock OIDC/JWT identity provider

**5. Add Certification and Evidence Generation**

Create `tools/certification/` with evidence-generation tooling:

- `tools/certification/report_generator.py` — Machine-readable conformance reports:
  - JSON conformance report with test results, timestamps, environment details
  - JUnit XML output for CI integration
  - HTML dashboard report with pass/fail summary per profile/level
  - Markdown summary for pull request comments
- `tools/certification/evidence_pack.py` — Evidence bundle export:
  - Conformance test results with full trace logs
  - Schema validation results
  - Audit chain integrity verification results
  - Environment configuration snapshot
  - Reproducible certification manifest (hash of all evidence artifacts)
- `tools/certification/site_certification.py` — Site certification report generator:
  - Site capability profile validation
  - Required server deployment verification
  - Regulatory overlay compliance check
  - Conformance level determination
- `tools/certification/schema_diff.py` — Schema compatibility diff tool:
  - Compare schema versions for breaking/non-breaking changes
  - Detect field additions, removals, type changes, constraint changes
  - Generate compatibility report

**6. Add Benchmarks**

Create `benchmarks/` with performance measurement tools:

- `benchmarks/latency_benchmark.py` — Latency benchmarks for each server/tool
- `benchmarks/throughput_benchmark.py` — Throughput benchmarks (requests/second per server)
- `benchmarks/chain_benchmark.py` — Audit chain verification performance at scale
- `benchmarks/concurrent_benchmark.py` — Concurrent access patterns and contention
- `benchmarks/report.py` — Benchmark report generator with historical comparison

**7. Update CI Pipeline**

Extend `.github/workflows/ci.yml`:

- Add integration test job that runs reference servers and exercises them via harness
- Add adversarial test job (security-focused)
- Add schema compatibility check (ensure no breaking changes without version bump)
- Add benchmark smoke test (ensure no major performance regressions)
- Add migration/version upgrade tests
- Add fuzz/property tests for schema edge cases

**8. Verify Repository-Wide Quality**

After all changes:
1. All existing unit tests and conformance tests still pass
2. Black-box conformance harness can target the reference server deployment
3. Interoperability testbed starts via `docker-compose up` and all scenarios pass
4. Certification report generator produces valid JSON/HTML/Markdown output
5. Benchmark suite runs without errors
6. `ruff check .` and `ruff format --check .` pass cleanly

Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

---

## Prompt v0.7.0

Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.7.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.7.0 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"START MAIN PROMPT"
v0.7.0 - Phase 2: Real Server Implementations, Persistence, and Deployment Infrastructure

Your goal is to transform national-mcp-pai-oncology-trials from a specification-and-fixtures repository into a repository containing real, runnable, production-shaped MCP server implementations for all five server domains, backed by persistence abstractions and deployable via Docker. This is the phase that makes the repository credible as the canonical national implementation source. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. Implement All Five MCP Server Packages**

Create `servers/` with production-shaped server packages for each domain:

- `servers/trialmcp_authz/` — Authorization server:
  - Real MCP server entrypoint with transport support (stdin/stdout MCP protocol)
  - Request routing for all authz tools: `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_revoke_token`
  - Deny-by-default RBAC policy engine with 6-actor policy matrix
  - SHA-256 token lifecycle with configurable expiry
  - Persistent token store interface (in-memory default + SQLite/PostgreSQL adapter)
  - Persistent policy store interface
  - Audit hook emission for all authorization decisions
  - Health/readiness endpoints, structured error responses
  - Configuration loading (environment variables, YAML/JSON config files)
  - Structured JSON logging

- `servers/trialmcp_fhir/` — FHIR clinical data server:
  - MCP server entrypoint with transport support
  - Tools: `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status`
  - HIPAA Safe Harbor de-identification pipeline (18-identifier removal)
  - HMAC-SHA256 pseudonymization
  - Patient/resource access filters
  - Capability statement generation
  - Adapter interface for backend FHIR sources (mock, HAPI FHIR, SMART-on-FHIR)
  - Synthetic FHIR Bundle loading for local testing
  - Audit hooks, health/readiness, structured errors, config, logging

- `servers/trialmcp_dicom/` — DICOM imaging server:
  - MCP server entrypoint with transport support
  - Tools: `dicom_query`, `dicom_retrieve`
  - Role-based modality restrictions (MUST: CT, MR, PT; SHOULD: RTSTRUCT, RTPLAN)
  - DICOM UID validation
  - Patient name hashing (12-char SHA-256)
  - Retrieval-pointer handling (metadata only, no pixel data transfer)
  - Adapter interface for backend DICOM sources (mock, Orthanc, dcm4chee)
  - Audit hooks, health/readiness, structured errors, config, logging

- `servers/trialmcp_ledger/` — Audit ledger server:
  - MCP server entrypoint with transport support
  - Tools: `ledger_append`, `ledger_verify`, `ledger_query`, `ledger_export`
  - Hash-chained immutable audit ledger with SHA-256 canonical JSON serialization
  - Genesis block initialization
  - Chain verification algorithm
  - Persistent audit storage interface (in-memory default + SQLite/PostgreSQL adapter)
  - Concurrency and locking strategy for ledger writes
  - Idempotency behavior for append operations
  - Audit hooks, health/readiness, structured errors, config, logging

- `servers/trialmcp_provenance/` — Provenance server:
  - MCP server entrypoint with transport support
  - Tools: `provenance_record`, `provenance_query_forward`, `provenance_query_backward`, `provenance_verify`
  - DAG-based lineage graph creation and management
  - SHA-256 fingerprinting
  - W3C PROV alignment
  - Cross-site trace merging support
  - Persistent provenance graph storage interface
  - Audit hooks, health/readiness, structured errors, config, logging

**2. Add Shared Infrastructure**

- `servers/common/` — Shared server infrastructure:
  - MCP transport layer (stdin/stdout protocol handling)
  - Request routing and dispatching
  - Authentication/authorization middleware
  - Audit emission middleware
  - Health/readiness endpoint base
  - Structured error response helpers
  - Configuration management (env vars, config files, defaults)
  - Structured JSON logging setup
  - Storage interface base classes (abstract adapters for SQLite, PostgreSQL)
  - Schema validation utilities (import from generated models)

**3. Add Persistence Layer**

- `servers/storage/` — Storage adapters:
  - Abstract base storage interface
  - In-memory storage adapter (for testing and local development)
  - SQLite storage adapter (for single-site deployment)
  - PostgreSQL storage adapter interface (for production deployment)
  - Migration utilities for schema versioning
  - Storage factory with config-driven selection

**4. Add Deployment Infrastructure**

- `deploy/docker/` — Dockerfiles for each server and an all-in-one image
- `deploy/docker-compose.yml` — Single-site deployment with all 5 servers, SQLite storage, mock FHIR/DICOM backends
- `deploy/docker-compose.multi-site.yml` — Multi-site deployment with Site A, Site B, shared ledger
- `deploy/kubernetes/` — Reference Kubernetes manifests (Deployments, Services, ConfigMaps, Secrets templates)
- `deploy/helm/` — Helm chart for configurable deployment
- `deploy/.env.example` — Example environment configuration
- `deploy/config/` — Example YAML configuration files for each server
- `deploy/config/site-profile-example.yaml` — Sample site capability profile configuration

**5. Add End-to-End Demo**

- `examples/quickstart/` — 5-minute local demo:
  - `run_demo.py` — Script that starts all 5 servers, executes a complete workflow (robot requests token → token validated → FHIR read → DICOM query → ledger append → provenance record), and prints results
  - `demo_data/` — Seeded synthetic FHIR Bundles, DICOM metadata, site profiles
  - `README.md` — Step-by-step quickstart guide

**6. Package Layout and Dependencies**

- Update `pyproject.toml` with:
  - Entry points / CLI scripts for each server (`trialmcp-authz`, `trialmcp-fhir`, etc.)
  - Runtime dependencies (structured separately from test dependencies)
  - Extras for `[fhir]`, `[dicom]`, `[dev]`, `[test]`, `[docs]`, `[all]`
  - Package discovery including `servers/`, `models/`
- Add proper `__init__.py` files for all new packages
- Add typed configuration dataclasses
- Add package boundaries and dependency rules

**7. Update TypeScript to Maintained Implementation**

Expand `reference/typescript/` from a stub into a maintained implementation:
- Add TypeScript server entrypoints for at least authz and ledger servers
- Add proper npm scripts for build, test, lint
- Add TypeScript tests with a testing framework (jest or vitest)
- Add generated TypeScript interfaces from schemas

**8. Verify Repository-Wide Quality**

After all changes:
1. `ruff check .` and `ruff format --check .` pass cleanly across all Python files
2. All existing unit tests and conformance tests still pass
3. New server packages can be imported and instantiated
4. Docker build succeeds for all images
5. `docker-compose up` starts all 5 servers successfully
6. End-to-end demo script completes the full workflow
7. All generated models match their source schemas

---

## Prompt v0.6.0

Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)(contributors=3)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.6.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.6.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes


"START MAIN PROMPT"
v0.6.0 - Phase 1: Correctness, Contract Alignment, and Schema-Code Drift Resolution
Your goal is to comprehensively fix all schema/code/test drift and contract mismatches across the entire national-mcp-pai-oncology-trials repository, establishing a single canonical source of truth for all data contracts and making the CI pipeline rigorous enough to catch any future drift. This is the foundational correctness phase — every subsequent phase depends on the contracts being accurate and verifiable. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.
1. Fix All Schema/Code Contract Mismatches
Resolve every field-name and structural mismatch between the 13 JSON schemas (/schemas/), the Python reference implementation (/reference/python/core_server.py), the TypeScript reference (/reference/typescript/core-server.ts), the conformance test fixtures (/conformance/fixtures/), and the unit tests (/tests/):
* authz_evaluate() currently returns decision, resource_id, reason, matching_rules(strings), timestamp — align to schema fields: allowed, effect, role, server, tool, evaluated_at, with matching_rules as structured objects per authz-decision.schema.json
* ledger_append() currently returns record_id, prev_hash — align to schema fields: audit_id, previous_hash per audit-record.schema.json
* health_status() currently returns server, timestamp, dependencies (object) — align to schema fields: server_name, checked_at, dependencies (array of typed objects) per health-status.schema.json
* Apply the same fixes to the TypeScript reference (core-server.ts) for authzEvaluate(), ledgerAppend(), computeAuditHash(), healthStatus(), errorResponse()
* Rename and normalize fields consistently across all repository artifacts: record_id → audit_id, prev_hash → previous_hash, server → server_name where schema requires it, timestamp → checked_at or evaluated_atwhere schema specifies, unify decision/effect and allowedsemantics
2. Generate Typed Models from Schemas
Create a canonical contract generation pipeline:
* Add models/python/ with generated typed dataclasses or Pydantic models for all 13 schemas
* Add models/typescript/ with generated TypeScript interfaces for all 13 schemas
* Add a scripts/generate_models.py that reads /schemas/*.schema.jsonand produces both Python and TypeScript typed models
* Ensure all reference implementations import from the generated models rather than hand-maintaining payload shapes
* Remove duplicate hand-maintained payload definitions in fixtures once generated canonical models exist
3. Add Contract Validation to CI
Extend .github/workflows/ci.ymlwith:
* Schema-to-code consistency check: a CI step that regenerates models and fails if generated output differs from committed models
* Snapshot tests for all example payloads in all 13 schemas
* Contract tests that validate every runtime output from core_server.py and core-server.ts against the corresponding schema
* TypeScript build, lint, and test steps (the current CI only validates Python)
* Docs lint that actually fails on broken links (change sys.exit(0)to sys.exit(1 if errors else 0) in the docs-lint job)
4. Tighten Scope and Maturity Labeling
Throughout the repository:
* Clarify what is normative, what is reference implementation, what is mock/synthetic only, what is planned, what is demonstrated, and what is validated
* Where applicable, revise "reference implementation" to "Level 1 illustrative implementation"
* Frame "national standard" as "proposed national standard / reference standard" unless multi-stakeholder governance and adoption evidence exists
* Distinguish "schema coverage" from "production readiness" and "federated architecture defined" from "federated coordination implementation supplied"
* Remove or soften any static maturity signals (badges, claims) that read more mature than the current code supports
* Reduce generic marketing language that is not paired with actionable implementation guidance
* Add clear normative vs informative boundary markers throughout all docs
5. Update All Affected Tests
* Update all 39 unit tests in /tests/to align with the corrected field names and structures
* Update all 269 conformance tests in /conformance/ to use the corrected field names
* Update all fixture data in /conformance/fixtures/ to match the corrected schemas
* Add new contract-validation tests that round-trip reference implementation outputs through schema validation
* Ensure all tests pass with pytest tests/ -v and pytest conformance/ -v
6. Verify Repository-Wide Quality
After all changes:
1. ruff check . and ruff format --check . pass cleanly
2. pytest tests/ — all unit tests pass
3. pytest conformance/ — all conformance tests pass
4. All 13 schemas validate with python reference/python/schema_validator.py
5. Every /spec/ file uses RFC 2119 MUST/SHOULD/MAY keywords
6. Every /reference/implementation file labeled NON-NORMATIVE
7. .github/workflows/ci.ymlpipeline covers Python lint/test, TypeScript build/test, schema validation, contract consistency, and docs lint (with failure on errors)

---

## Prompt v0.5.2

Your goal is to create 5 comprehensive prompts for national-mcp-pai-oncology-trials that will be run in separate conversations based on the two following sets of feedback (For future comprehensive 1M token processing using Claude Code Opus 4.6). The biggest concern is to make the codebase comprehensive and appropriate for national-level physical ai oncology trials mcp servers. The primary focus is to make the repository more practical, useful, and substantive in code (with any supporting code documentation needed). Do not process the 5 prompt's instructions.

For each of the prompts, consistently include these statements where most appropriate:
"Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)" "It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale."

Include all of the claude "Implemented"/"Deferred" responses to the openai recommendations as tables in a response-A-2026-03-06.md under /peer-review in this format:
## Claude Code Opus 4.6 Responses to ChatGPT 5.4 Thinking
(no text here)
### Response
(tables here)

Place each of the 5 prompts into separate .md files under /peer-review with format claude-#-2026-03-06.md (# = 1-5) with the following content format:
## Claude Code Opus 4.6 [Prompt Only]
(no text here)
### Prompt
(text here)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.2. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.2 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes

"START FEEDBACK 1"
Here's a candid repo review based on the repository's current files and implementation shape.

The main gap is that the repo already reads like a national standard, but the codebase is still mostly a specification-and-fixtures repository rather than a practical, adoptable source implementation. The README positions it as a "Normative Specification" and "United States Industry Standard"  , but the executable artifacts that stakeholders would expect for a national source repo are still thin: the Python reference is a single in-memory Level 1 stub, the TypeScript reference is also a stub, and the conformance suite mostly validates fixture objects and schemas rather than black-box behavior of real MCP servers        .

1. Highest-priority changes: make it an implementation repo, not just a spec repo

Add
	1.	A real runnable MCP server stack, not just helper functions.
The Python reference currently exposes plain functions like authz_evaluate, ledger_append, and health_status, backed by an in-memory token store  . To be credible as a national source, the repo should add:
	•	a real MCP server entrypoint
	•	transport support
	•	request routing
	•	configuration loading
	•	structured logging
	•	persistent storage adapters
	•	health/readiness endpoints
	•	a Docker-based local deployment
	2.	A complete reference implementation for all five server domains.
The README claims five servers and 23 tools as the standard surface  , but the reference code only implements a minimal Level 1 core example in Python and TypeScript      . Add actual reference servers for:
	•	authz
	•	fhir
	•	dicom
	•	ledger
	•	provenance
	3.	A deployment model that hospitals and vendors can actually evaluate.
Add:
	•	docker-compose.yml for a single-site deployment
	•	Kubernetes manifests or Helm chart
	•	example secrets/config templates
	•	local mock services for FHIR, DICOM, and audit storage
	•	sample site profile configs
	4.	A persistence layer.
The current token handling is explicitly in-memory and non-production  . Add durable implementations for:
	•	token store
	•	policy store
	•	audit ledger storage
	•	provenance graph storage
	•	site capability registry

Fix
	1.	Turn the "reference implementation" into a real reference architecture.
Right now it is more a code sketch than a reference system. The code needs:
	•	package layout by server/domain
	•	interfaces and adapters
	•	config management
	•	environment-based bootstrapping
	•	proper exception handling and error mapping
	•	versioned API compatibility tests
	2.	Add end-to-end workflows.
Stakeholders will want to see practical workflows, such as:
	•	robot requests token → token validated → FHIR read → DICOM query → ledger append → provenance record
	•	trial coordinator study lookup
	•	auditor replay and chain verification
	•	multi-site provenance trace

Remove or de-emphasize

Until those pieces exist, remove or soften positioning that implies the repo is already the national implementation source. The current README's "United States Industry Standard" framing is ahead of what the code supports  .

2. Fix internal contract mismatches immediately

This is the most important code-quality issue. The repository currently contains schema/code/test drift.

Examples of drift

In Python:
	•	authz_evaluate() returns decision, resource_id, reason, matching_rules as strings, and timestamp
	•	but the schema requires allowed, effect, role, server, tool, and evaluated_at, with matching_rules as structured objects

In Python:
	•	ledger_append() returns record_id and prev_hash
	•	but the audit schema requires audit_id and previous_hash

In Python:
	•	health_status() returns server, timestamp, and dependencies as an object
	•	but the health schema requires server_name, checked_at, and dependencies as an array of typed objects

The same mismatch pattern exists in TypeScript, where the stub returns decision/timestamp and record_id/prev_hash shapes that do not match the normative schemas      .

Add

Create a single canonical contract source of truth:
	•	either schemas generate code models
	•	or code models generate schemas
	•	but not both manually

Add:
	•	generated typed models for Python and TypeScript
	•	schema-to-code consistency checks in CI
	•	snapshot tests for all example payloads
	•	contract tests that validate runtime outputs against schemas

Fix

Rename and normalize fields across repo artifacts:
	•	record_id → audit_id
	•	prev_hash → previous_hash
	•	server → server_name where appropriate
	•	timestamp → checked_at or evaluated_at where schema requires it
	•	unify decision/effect and allowed semantics

Remove

Remove duplicate hand-maintained payload definitions in fixtures once generated canonical models exist.

3. Replace fixture-based conformance with black-box conformance

The current conformance suite is useful, but it is mostly validating fixture objects and helper outputs. For example, test_core_conformance.py imports sample fixtures and local helper constructors rather than exercising a real deployment boundary  . The conformance runner just builds pytest paths; it does not target a remote server, base URL, MCP transport, or deployment manifest  .

Add
	1.	Real black-box conformance harness
Add a test harness that can point at:
	•	a local process
	•	a containerized deployment
	•	a staging URL
	•	a vendor implementation
	2.	Test adapters
Add pluggable adapters for:
	•	stdin/stdout MCP
	•	HTTP transport if used
	•	authenticated sessions
	•	seeded test data
	3.	Certification-style output
Add:
	•	machine-readable test reports
	•	profile pass/fail summary
	•	evidence bundle export
	•	reproducible certification manifest
	4.	Negative and adversarial test packs
Expand into:
	•	authz bypass attempts
	•	PHI leakage checks
	•	replay attacks
	•	tampered audit chain imports
	•	malformed DICOM/FHIR resource handling
	•	rate limiting and abuse cases

Fix

Refactor the existing conformance suite into:
	•	unit tests for fixtures and helpers
	•	integration tests for reference servers
	•	black-box conformance tests for external implementations

Remove

Stop counting fixture-validation tests as the primary measure of implementation maturity. "269 passing" is not yet equivalent to "deployable national conformance" if most tests do not cross a real server boundary    .

4. Make the repository operationally credible

Add
	1.	Security implementation details
The spec is strong on intent, but the code should add:
	•	key management strategy
	•	signed audit records
	•	token signing and verification
	•	mTLS guidance
	•	secrets rotation
	•	tamper-evident storage design
	•	SBOM and dependency scanning
	•	threat model document
	•	incident response runbook
	2.	Production concerns
Add:
	•	retries and circuit breakers for clinical dependencies
	•	idempotency behavior for write-like actions
	•	concurrency and locking strategy for ledger writes
	•	backpressure and queueing
	•	observability standards
	•	audit export and archival flows
	3.	Reliability docs
Add SLO/SLA guidance:
	•	uptime targets
	•	latency budgets
	•	fail-safe modes
	•	degraded operation rules
	•	data recovery procedures

Fix

The current CI is not enough for stakeholder confidence.
	•	It installs Python lint/test dependencies only
	•	It does not build or test the TypeScript reference
	•	The docs link checker prints broken links but exits with 0 regardless, so it won't fail the build on broken links

Add CI jobs for:
	•	TypeScript build/test/lint
	•	container build
	•	schema/code drift
	•	API contract snapshots
	•	end-to-end conformance runs
	•	security scanning
	•	docs lint that actually fails on errors

5. Expand the code surface where stakeholders will care most

Add
	1.	Real FHIR handling
Add:
	•	SMART-on-FHIR or equivalent auth integration patterns
	•	patient/resource access filters
	•	de-identification implementation with test corpus
	•	capability statements
	•	terminology mapping strategy
	•	realistic Bundle handling
	2.	Real DICOM handling
Add:
	•	QIDO/WADO/STOW guidance if relevant
	•	retrieval-pointer handling
	•	modality restrictions
	•	metadata normalization
	•	image reference safety constraints
	•	RECIST measurement payload examples and validators
	3.	Real provenance and federated functions
The README claims a federated layer and provenance DAGs  , but this needs runnable code for:
	•	lineage graph creation
	•	integrity verification
	•	cross-site trace merging
	•	privacy budget accounting
	•	site-level federation policy enforcement
	4.	Clinical safety guardrails
For "Physical AI oncology clinical trial systems," add executable policy layers for:
	•	procedure eligibility checks
	•	site capability verification
	•	trial protocol constraints
	•	robot capability gating
	•	mandatory human-approval gates
	•	emergency stop / override semantics
	•	simulation-only mode

6. Strengthen packaging and developer usability

Add
	1.	Proper installable packages and CLIs
The Python project currently declares only basic project metadata and optional test dependencies  . Add:
	•	entry points / CLI scripts
	•	runtime dependencies
	•	extras for FHIR/DICOM/dev/test/docs
	•	versioned release artifacts
	2.	Developer quickstarts
Add:
	•	5-minute local demo
	•	local single-site sandbox
	•	"run first request" example
	•	seeded demo data
	•	sample config bundles for site/sponsor/CRO
	3.	SDKs or starter kits
Add:
	•	Python client
	•	TypeScript client
	•	profile scaffolding tool
	•	policy authoring templates
	•	schema codegen helpers

Fix

The TypeScript package is very minimal: just build and start, with no tests, lint, or publishing shape  . It should become a maintained implementation, not a stub.

7. Tighten governance and documentation for stakeholder trust

Add
	1.	Adoption evidence
To be taken seriously as a national source repo, add:
	•	decision log of accepted/declined changes
	•	implementation status matrix
	•	roadmap with target adopters and milestones
	•	compatibility matrix by version/profile
	•	list of known gaps and non-goals
	•	contribution policy for regulators, vendors, providers, CROs
	2.	Architecture decision records
Explain why:
	•	MCP is the right protocol boundary
	•	these 5 servers were chosen
	•	these 23 tools are the minimal stable surface
	•	profiles map to clinical deployment tiers
	3.	Clear labeling of normative vs informative
The repo already uses those terms in README structure  , but it still needs much sharper boundaries so implementers know what is binding, experimental, or placeholder.

Fix

Revise docs to be more honest about maturity:
	•	"reference implementation" should say "Level 1 illustrative implementation" where applicable
	•	"national standard" should be framed as a proposed standard unless there is multi-stakeholder governance and adoption evidence
	•	separate "current state" from "target state"

Remove

Remove static maturity signals that can be read as proof of broad adoption when they are really repository-local indicators. The README's status badge stack is polished, but several items read more mature than the code currently supports  .

8. Recommended restructuring plan

Phase 1: correctness
	•	fix schema/code/test drift
	•	fix CI gaps
	•	make docs lint fail properly
	•	align field names and examples everywhere

Phase 2: runnable source
	•	add real Python reference servers
	•	add persistence and config
	•	add dockerized deployment
	•	add end-to-end demo

Phase 3: conformance credibility
	•	build black-box harness
	•	generate signed reports
	•	add vendor-targetable test adapters
	•	publish profile certification criteria

Phase 4: stakeholder readiness
	•	add operational runbooks
	•	add governance evidence
	•	add interoperability demos
	•	reduce overclaiming in README until adoption catches up

Bottom line

To be considered by more stakeholders as the source repo for national MCP servers, this repository needs to move from "well-written normative proposal + schemas + fixtures" to "reference standard plus deployable, testable, black-box-verifiable implementation."

The biggest concrete issues today are:
	•	too little runnable code for the breadth of claims
	•	clear schema/code mismatches in core payloads
	•	conformance testing that is still mostly internal/fixture-based rather than deployment-based
	•	CI that does not yet validate the full stated surface area, especially TypeScript and docs correctness

I can turn this into a prioritized gap table with "add / remove / fix / rationale / suggested file changes" format next.





"START FEEDBACK 2"
Below is a practical gap-analysis outline for kevinkawchak/national-mcp-pai-oncology-trials aimed at making it credible to more stakeholders as the source repository for National MCP servers for Physical AI oncology clinical trial systems.
My overall read: the repository is already strong as a normative standard/specification repo with profiles, schemas, governance, and conformance language, but it is still too thin in executable substance to serve as the canonical source most implementers, hospital IT teams, vendors, regulators, and standards bodies would rely on. The repo itself says the implementations are "NON-NORMATIVE reference implementations," and the Python/TypeScript examples are minimal Level-1 stubs rather than deployable national-grade servers    . By contrast, the companion repos already contain much richer operational code for FHIR, DICOM, privacy, agent interfaces, and federated coordination      .
1. Biggest strategic change: make this repo the canonical integration and reference implementation repo, not just the spec repo
What to add
Create a clear two-layer structure:
* Normative layer: current spec/, schemas/, profiles/, regulatory/, governance/
* Reference implementation layer: production-shaped packages for the five MCP servers, integration adapters, deployment manifests, validation tools, and realistic examples
Suggested top-level additions:
* servers/trialmcp_authz/
* servers/trialmcp_fhir/
* servers/trialmcp_dicom/
* servers/trialmcp_ledger/
* servers/trialmcp_provenance/
* integrations/fhir/
* integrations/dicom/
* integrations/ros2/
* integrations/federation/
* deploy/
* examples/
* benchmarks/
* sdk/python/
* sdk/typescript/
What to remove or demote
Keep reference/, but stop presenting it as the main practical implementation surface. The current Python core server is an in-memory Level-1 demo with in-memory token storage and helper functions, not a deployable MCP service  . The TypeScript version is also explicitly a stub  .
Rename or reposition:
* reference/ → examples/minimal-reference/
* badge/README emphasis should move away from "passing conformance tests" toward "reference servers + deployment guides + interoperability testbed"
Why this matters
Stakeholders deciding whether a repo should become a national source will ask:
* Where are the actual servers?
* How do I deploy them?
* What does site integration look like?
* How do I certify and operate them?
Right now the companion repo mcp-pai-oncology-trials looks more like the implementation source because it already has server code and a reference agent  .



2. Promote and consolidate the real server code from
mcp-pai-oncology-trials
The most immediate way to make the national repo substantive is to fold in or vendor the working server code patterns from kevinkawchak/mcp-pai-oncology-trials.
What to add
Port or adapt these into the national repo as the official reference implementation baseline:
* FHIR server patterns from servers/trialmcp_fhir/src/fhir_server.py:
    * read/search/patient lookup/study status
    * de-identification pipeline
    * synthetic bundle loading
    * audit hooks
    * validation/error patterns
* Equivalent DICOM, ledger, authz, provenance server packages from that repo
* The reference robot agent workflow, but rewritten as a national interoperability demo, not a standalone proof of concept
What to fix during import
Do not copy them over unchanged. Harden them.
Examples:
* replace in-memory stores with storage interfaces
* replace direct synthetic-only assumptions with adapter layers
* separate transport, domain logic, policy, and schema validation
* convert server handlers into actual MCP server entrypoints
* add typed models and explicit config management
What to remove
Remove duplicated spec text inside implementation docstrings where possible. Keep implementation code focused on behavior, and point to normative spec sections for requirements.
Why this matters
The FHIR server in the implementation repo already contains more realistic clinical-domain behavior than the national repo's current Level-1 examples, including supported resource types, de-identification, search logic, and audit emission  . That is the substance stakeholders will expect to see in the national source.



3. Expand from "Level 1 Core" examples to all five server implementations and all five conformance levels
The national repo currently highlights Level-1/Core examples and conformance framing, but a national source needs end-to-end implementable paths for all major profiles.
What to add
For each server, provide:
* MCP transport entrypoint
* schema-bound request/response models
* authn/authz middleware
* audit hooks
* health/readiness
* structured errors
* persistence abstraction
* adapter interfaces
* test fixtures
* deployment examples
For each conformance level:
* L1 Core: AuthZ + Ledger
* L2 Clinical Read: FHIR implementation with de-identification
* L3 Imaging: DICOM query/retrieve metadata + RECIST path
* L4 Federated Site: provenance + site federation coordination
* L5 Robot Procedure: safety-gated workflow orchestration and robot/task order execution
What to fix
The current repository has extensive profile language, but too little runnable code behind Levels 2–5. That mismatch weakens credibility with engineering stakeholders.
What to remove
Reduce claims that imply operational completeness where only schema/spec completeness exists.



4. Add real integration adapters, not just abstract contracts
A standards repo becomes practical when it shows how to connect to real systems.
What to add
FHIR adapters
* HAPI FHIR adapter
* generic SMART-on-FHIR/OAuth2 adapter
* synthetic/mock adapter for local testing
* capability statement ingestion
* terminology mapping hooks
DICOM adapters
* Orthanc adapter
* dcm4chee adapter
* study metadata and retrieve-pointer generation
* DICOMweb support path
Identity/security adapters
* OIDC/JWT validation
* mTLS support
* external policy engine integration option
* KMS/HSM-backed signing key hooks
Clinical operations adapters
* eConsent/IRB metadata adapter
* scheduling/task-order adapter
* provenance export adapter
Context from companion repos
The implementation repo already points toward production FHIR and DICOM proxy directions in its milestones; the national repo should absorb that trajectory and make it official rather than leaving it implied  .
Why this matters
Hospitals and vendors will not adopt a "national source" unless they can see a practical bridge from standard to installed systems.



5. Pull in the strongest privacy, regulatory, and governance code from
physical-ai-oncology-trials
 and
pai-oncology-trial-fl
The national repo is strong in policy text, but weaker in operational compliance tooling than the companion repos.
What to add
From physical-ai-oncology-trials:
* reusable privacy modules
* access control manager patterns
* de-identification pipeline patterns
* IRB/FDA/GCP support tools
* deployment readiness checks
* unified agent/tool interface patterns
From pai-oncology-trial-fl:
* federated coordinator abstractions
* secure aggregation hooks
* differential privacy hooks
* site enrollment and data harmonization interfaces
* clinical analytics/reporting patterns where relevant to multi-site trial coordination
What to fix
These should not be copied wholesale into the national repo as broad research modules. They need to be narrowed to what directly supports the MCP national standard.
What to remove
Avoid importing unrelated breadth that turns the national repo into a giant umbrella "all oncology AI" repository. Keep only modules that materially strengthen MCP server operation, interoperability, compliance, or federation.
Why this matters
The FL repo already contains a more substantive multi-site orchestration story than the national repo's current federated layer narrative alone  .



6. Add a true "national interoperability testbed"
Conformance tests are good, but stakeholders will want more than unit-style assertions.
What to add
Create interop-testbed/ with:
* multi-site docker-compose or k8s local cluster
* Site A / Site B / Sponsor / CRO / Auditor personas
* mock EHR/PACS services
* cross-site provenance and audit replay
* token exchange and revocation scenarios
* partial outage scenarios
* schema drift scenarios
* state overlay tests (CA, NY, FDA)
* end-to-end robot workflow simulations
Add test categories:
* conformance
* interoperability
* resilience
* security abuse cases
* site onboarding certification
* upgrade compatibility
* extension compatibility
What to fix
The current conformance suite is useful, but it is still centered on contract validation. National adoption requires proving cross-site behavior, deployment consistency, and failure modes.



7. Add deployment artifacts and operating model docs
A national source repo needs to answer "how do I run this safely?"
What to add
* Dockerfiles for each server
* Helm charts / Kustomize
* reference Kubernetes manifests
* example .env.example and config schemas
* production configuration matrix
* observability stack examples
* log redaction defaults
* key rotation and signing key guidance
* backup/restore and chain recovery procedures
* upgrade playbooks
* site bootstrap scripts
Add docs:
* docs/deployment/local-dev.md
* docs/deployment/hospital-site.md
* docs/deployment/multi-site-federated.md
* docs/operations/runbook.md
* docs/operations/incident-response.md
* docs/operations/key-management.md
What to fix
The current repo is organized like a standard, not like an operable system source. That is fine for a spec repo, but not enough for a canonical national source.



8. Add stakeholder-specific implementation guides
The README speaks broadly to sites, sponsors, CROs, and vendors, but the repository needs role-specific paths.
What to add
Create dedicated guides for:
* Hospital IT / Cancer Center
    * site deployment checklist
    * network and identity requirements
    * PACS/EHR integration path
    * PHI boundary and retention controls
* Robot vendor
    * capability descriptor requirements
    * task-order semantics
    * safety gate expectations
    * simulator-to-clinical promotion path
* Sponsor/CRO
    * cross-site reporting interfaces
    * provenance and audit review
    * state/federal overlay implications
* Regulator/IRB
    * evidence package structure
    * conformance artifacts
    * audit replay package
    * change control and validation package
* Standards community
    * extension proposal process
    * compatibility policy
    * schema evolution rules
What to remove
Reduce generic marketing language that is not paired with actionable stakeholder guidance.



9. Tighten scope and prune claims that exceed current code reality
The repo is ambitious, but some statements read more mature than the implementation appears.
What to fix
Clarify throughout the README and docs:
* what is normative
* what is reference implementation
* what is mock/synthetic only
* what is planned
* what is demonstrated
* what is validated
Examples of likely fixes
* replace "industry standard" tone with "proposed national standard / reference standard" unless there is formal adoption
* distinguish "schema coverage" from "production readiness"
* distinguish "federated architecture defined" from "federated coordination implementation supplied"
What to remove
* any implication that the repo already provides deployable national infrastructure when much of the implementation is still minimal or imported by reference from sibling repos
This is one of the biggest credibility gains available.



10. Add a formal migration and consolidation plan across the four repositories
Right now the value is fragmented:
* national-mcp-pai-oncology-trials = spec/governance/conformance center
* mcp-pai-oncology-trials = most concrete MCP server implementation surface
* physical-ai-oncology-trials = broader robotics, privacy, regulatory, digital twin tooling
* pai-oncology-trial-fl = substantive federation/privacy/regulatory infrastructure
What to add
A docs/repository-strategy.md that says exactly:
* what stays in each repo
* what graduates into the national repo
* what is mirrored vs imported vs referenced
* what becomes deprecated
* what becomes the canonical implementation source
Recommended direction
Make the national repo the canonical home for:
* normative artifacts
* official server implementations
* official testbed
* official deployment patterns
* official SDKs
* official examples
Leave the other repos as:
* research incubators
* broader frameworks
* companion experiments
* upstream module sources until stabilized



11. Add versioned SDKs and generated client/server bindings
A national standard becomes more adoptable when people can generate against it.
What to add
* Python SDK
* TypeScript SDK
* generated schema bindings
* server scaffolding CLI
* profile-aware code generation
* example clients for each actor role
Suggested outputs:
* typed request/response classes from schemas
* client stubs for 23 tools
* policy templates
* example middleware for auth/audit/error handling
What to fix
The current TypeScript code is mainly a small stub around AJV validation and helper functions  . That should evolve into a usable SDK and server starter kit.



12. Add benchmark, validation, and evidence-pack generation
National stakeholders will want objective evidence, not only passing tests.
What to add
* latency and throughput benchmarks by server/tool
* conformance report generator
* site certification report generator
* evidence pack generator for IRB/FDA/internal compliance review
* schema compatibility diff tool
* audit chain integrity report exporter
* provenance graph exporter
Borrow from companion repos
The FL repo already has stronger notions of coordinator summaries and operational reporting patterns that can inform evidence generation  .



13. Add robot-facing safety and execution boundaries
Because this is for Physical AI, not just software agents, the national source needs more explicit execution-control substance.
What to add
* safety gate service or policy layer
* robot capability registry
* task-order validator with safety constraints
* human-approval checkpoint patterns
* e-stop and abort semantics
* procedure-state machine
* simulation-only vs clinical-mode flags
* precondition verification contracts
* post-procedure evidence capture contracts
Context from companion repos
The physical-ai repo's unified agent/tool patterns and robotics-oriented tool abstractions are useful starting points for this layer, even if many are still mock-like today  .
What to fix
Right now "robot procedure" appears more strongly in the standard language than in the codebase substance.



14. Improve documentation quality by replacing breadth with adoption-grade depth
The repo already has a lot of docs. The problem is not volume; it is that some key docs need to become more operational.
Highest-value docs to add or rewrite
* architecture decision records
* one complete walkthrough per profile
* "how a hospital site goes live"
* "how a vendor becomes conformant"
* "how a CRO validates a multi-site deployment"
* "how schemas map to running services"
* "how to extend without breaking national compatibility"
* "what data may never leave site boundaries"
* "how audit/provenance differ and interact"
What to remove
Reduce repetitive diagrams and README-level summary material once deeper docs exist. Replace some broad narrative with precise onboarding sequences.



15. Add stronger software engineering hygiene around the implementation layer
What to add
* package boundaries and dependency rules
* typed configs
* migration/version upgrade tests
* fuzz/property tests for schema edges
* secret scanning
* SBOM generation
* signed releases
* release provenance
* compatibility matrix by version/profile
What to fix
The national repo's CI and conformance messaging are good, but the implementation layer needs production software practices once real servers are brought in.



16. A concrete prioritized roadmap
Phase 1: make the repo believable as the national implementation source
* import and harden the five real server packages from mcp-pai-oncology-trials
* add deployment artifacts
* add integration adapters
* add multi-site testbed
* rewrite README to distinguish spec vs implementation
Phase 2: make it adoptable by institutions
* add SDKs
* add stakeholder guides
* add certification/evidence tooling
* add config/deployment/runbook docs
* add hospital/vendor reference deployments
Phase 3: make it governable as a national standard source
* formal repository strategy across sibling repos
* extension registry process
* compatibility guarantees
* versioned implementation baselines
* deprecation policy for non-canonical sibling components



17. The shortest honest summary
To be considered by more stakeholders as the source for national MCP servers, this repository needs to evolve from:
* excellent standard/specification repo
into
* standard + canonical reference implementation + deployment + interoperability + evidence repo
The fastest path is not to invent all of that from scratch here. It is to promote, narrow, harden, and consolidate the strongest implementation pieces already present in:
* kevinkawchak/mcp-pai-oncology-trials for the MCP servers and workflow surface
* kevinkawchak/physical-ai-oncology-trials for privacy/regulatory/agentic/robotics integration patterns
* kevinkawchak/pai-oncology-trial-fl for federation, privacy, secure aggregation, and reporting infrastructure
At the moment, the national repo looks like the right governance/spec home, but not yet the strongest implementation home. That is the core issue to fix.
I can turn this into a sharper deliverable next, such as a repo-by-repo migration matrix or a proposed new directory tree with file-level recommendations.

---

## Prompt v0.5.1

Perform tests and fix code for national-mcp-pai-oncology-trials based on the following verifications and other comprehensive checks/tests repository wide. Make note of any changes made throughout relevant documentation. If necessary, create a new directory(s) on main.:
1. pytest tests/ — All 39 existing tests still pass (no existing code modified)
2. pytest conformance/ — Conformance suite runs against reference implementation
3. python reference/python/schema_validator.py — All schemas validate
4. Every /spec/ file uses RFC 2119 MUST/SHOULD/MAY
5. Every /reference/ file labeled NON-NORMATIVE
6. .github/workflows/ci.yml executes successfully
7. prompts.md contains all 5 new prompts with comprehensive instructions
8. Each version has releases.md entry and changelog.md entry

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.1. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.1 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

---

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

---

## Prompt v0.1.0 — Part 2

Also add the following two files to main branch:
main/next-steps.md
main/stats.md

A) Create a comprehensive next-steps.md that explains, in practical and nationally relevant terms, what all stakeholder groups are expected to do now that the repository is publicly available and usable as a proposed national reference standard.

The document should be written for a nationwide audience and should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

The content should be action-oriented, specific, and organized for real-world adoption. It should clearly describe immediate, near-term, and medium-term actions for major stakeholder groups, including sponsors, CROs, academic medical centers, community oncology sites, hospital IT and security teams, robotics vendors, EHR and FHIR integration teams, imaging and PACS and DICOM teams, privacy and compliance and legal and regulatory teams, principal investigators, trial coordinators, auditors, data monitors, and standards contributors or open-source maintainers.

The document should include, where appropriate, what each stakeholder should review first in the repository, what each stakeholder should deploy, validate, or evaluate next, which profiles, schemas, tools, safety modules, governance materials, and test assets are most relevant to them, recommended sequencing of adoption activities, dependencies between technical, operational, clinical, and regulatory workstreams, expected readiness checkpoints for pilot adoption, expectations for documentation, conformance validation, and evidence generation, what should happen at single-site, multi-site, and national coordination levels, and a clear distinction between actions to take now, actions to plan next, and actions that require formal validation before production or clinical use.

The document should read like an adoption and execution guide rather than a vague summary. It should be comprehensive but concise, and it should reflect the repository's positioning as a national MCP and Physical AI oncology trials standard.

B) Create a comprehensive stats.md that presents repository statistics and quantitative summary data in a way that is useful to technical, clinical, compliance, standards, and interoperability audiences.

The document should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

It should be metrics-heavy and use quantitative data throughout wherever the repository supports it. The document should be written for readers interested in MCP ecosystems, interoperability maturity, and Physical AI oncology trials.

At minimum, include clearly labeled sections covering repository scale and scope, number and categories of tests, test types and what they validate, number of tools and their distribution by MCP server, MCP server count and server types, schema count and schema categories, profile count and profile types, integration adapter count and categories, safety module count and categories, benchmark and certification tooling count, deployment targets and infrastructure options, languages used across the repository, approximate lines of code if determinable from the repository contents, directory and artifact counts where meaningful, key takeaways, concise executive summary, notable strengths, differentiators, and maturity signals, and any other metrics likely to interest people working in MCPs, healthcare AI infrastructure, interoperability, federated systems, clinical robotics, and oncology trial operations.

Where possible, quantify and break down items such as total tests passed by suite and subtype, unit versus conformance versus integration versus adversarial versus black-box coverage, counts by server, tool family, schema family, and profile level, number of deployment modes, number of interoperability scenarios, number of actor types, number of regulatory overlays, number of benchmark categories, and number of certification or evidence-generation utilities.

Where exact runtime verification is not available from the current environment, use repository-documented counts and label them clearly as repository-reported or documented metrics rather than claiming fresh CI execution.

The document should also include concise summaries of what the metrics imply about technical maturity, why the statistics matter for national interoperability and oncology trial readiness, why these metrics are meaningful to MCP practitioners, and why the quantitative profile is notable for Physical AI clinical trial infrastructure.

For both files, keep the writing professional, concrete, and repository-specific. Avoid filler language. Use headings and subheadings for readability. Use numbered lists when describing sequences, phases, or responsibilities. Use concise bullets for checklists, role-based actions, and metric breakdowns. Prefer precise wording over promotional wording. Keep the tone suitable for a standards-oriented public GitHub repository. Make the documents readable both by technical implementers and non-engineering stakeholders. Ensure the content is comprehensive enough to be useful immediately after publication.

---

## Prompt v1.0.1

For national-mcp-pai-oncology-trials: the following two prompts were processed in v1.0.0: but not all tasks were completed fully and accurately. For instance, the stats.md and next-steps.md need to be fully up to date and correct throughout paragraphs, lists, and bullet points (v1.0.1 is to be used, not v0.1.0.) Also the main readme did not update badges, diagrams, documentation, etc. Update all documentation repo wide to be accurate and comprehensive based on the following prompts. The "Original Prompt" and "Follow-up Prompt" below must be fully applied and correct throughout the repo.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v1.0.1. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v1.0.1 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"Original Prompt"
Your goal for national-mcp-pai-oncology-trials is to implement the main prompt below  comprehensively for the physical ai oncology trials industry. It is imperative that all types of information utilized for the repository be accurate and appropriate for the national scale. Change the last version's /mcp-process-diagrams to /mcp-process and move the directory with readme to main. Update relevant readme files and documentation throughout the repo (including /mcp-process) based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v1.0.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v1.0.0 -

\## Summary

\## Features

\## Contributors
@kevinkawchak
@claude
@openai

\## Notes


"START MAIN PROMPT"
v1.0.0 - Phase 5: SDKs, Stakeholder Guides, Governance, and Operational Readiness

Your goal is to make national-mcp-pai-oncology-trials fully adoptable by institutions, vendors, and regulators by adding versioned SDKs, stakeholder-specific implementation guides, operational runbooks, governance evidence, and production-readiness documentation. This is the stakeholder-readiness phase that transforms the repository from a technical resource into a national adoption-ready platform. It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale.

**1. Python SDK**

Create `sdk/python/` with a complete client SDK:

- `sdk/python/trialmcp_client/` — Python client package:
  - `client.py` — Unified MCP client with connection management, retry logic, circuit breaker
  - `authz.py` — AuthZ client (evaluate, issue_token, validate_token, revoke_token)
  - `fhir.py` — FHIR client (read, search, patient_lookup, study_status)
  - `dicom.py` — DICOM client (query, retrieve)
  - `ledger.py` — Ledger client (append, verify, query, export)
  - `provenance.py` — Provenance client (record, query_forward, query_backward, verify)
  - `models.py` — Re-exported generated typed models from `models/python/`
  - `exceptions.py` — Typed exception hierarchy matching 9-code error taxonomy
  - `config.py` — Client configuration (server addresses, auth credentials, timeouts, retry policy)
  - `middleware/` — Pluggable middleware:
    - `auth_middleware.py` — Automatic token management and refresh
    - `audit_middleware.py` — Client-side audit logging
    - `retry_middleware.py` — Configurable retry with exponential backoff
    - `circuit_breaker.py` — Circuit breaker for clinical dependency resilience
- `sdk/python/examples/` — Example scripts for each actor role:
  - `robot_agent_example.py` — Complete robot agent workflow
  - `trial_coordinator_example.py` — Trial coordinator study management
  - `data_monitor_example.py` — Data monitor review workflow
  - `auditor_example.py` — Auditor chain verification and replay
  - `sponsor_example.py` — Sponsor cross-site oversight
  - `cro_example.py` — CRO multi-site validation
- `sdk/python/setup.py` / `pyproject.toml` — Installable package with versioned releases

**2. TypeScript SDK**

Create `sdk/typescript/` with a complete client SDK:

- `sdk/typescript/src/` — TypeScript client package:
  - `client.ts` — Unified MCP client with connection management
  - `authz.ts`, `fhir.ts`, `dicom.ts`, `ledger.ts`, `provenance.ts` — Domain clients
  - `models/` — Re-exported generated TypeScript interfaces
  - `errors.ts` — Typed error classes matching 9-code error taxonomy
  - `config.ts` — Client configuration
  - `middleware/` — Auth, audit, retry, circuit breaker middleware
- `sdk/typescript/examples/` — Example scripts for each actor role
- `sdk/typescript/package.json` — npm package with versioned releases
- `sdk/typescript/tsconfig.json` — TypeScript configuration
- `sdk/typescript/jest.config.js` — Test configuration
- `sdk/typescript/tests/` — SDK tests

**3. CLI and Code Generation Tools**

Create `tools/cli/` with developer tooling:

- `tools/cli/trialmcp_cli.py` — Main CLI entry point:
  - `trialmcp init` — Initialize a new implementation project with profile selection
  - `trialmcp scaffold` — Generate server scaffolding from profile requirements
  - `trialmcp validate` — Validate a server implementation against conformance criteria
  - `trialmcp certify` — Run certification suite and generate evidence pack
  - `trialmcp schema diff` — Compare schema versions for compatibility
  - `trialmcp config generate` — Generate configuration templates for site/server
- `tools/codegen/` — Schema code generation:
  - `tools/codegen/generate_python.py` — Generate Python dataclasses/Pydantic models from schemas
  - `tools/codegen/generate_typescript.py` — Generate TypeScript interfaces from schemas
  - `tools/codegen/generate_openapi.py` — Generate OpenAPI specs from tool contracts
  - `tools/codegen/templates/` — Jinja2 templates for code generation

**4. Stakeholder-Specific Implementation Guides**

Create `docs/guides/` with role-specific adoption paths:

- `docs/guides/hospital-it.md` — Hospital IT / Cancer Center guide:
  - Site deployment checklist (prerequisites, infrastructure, network, identity)
  - PACS/EHR integration path (FHIR R4 + DICOMweb connectivity)
  - PHI boundary and retention controls
  - Network segmentation requirements
  - Identity provider integration (OIDC, AD/LDAP)
  - Monitoring and alerting setup
  - Data backup and recovery procedures
  - Staff training requirements

- `docs/guides/robot-vendor.md` — Robot vendor guide:
  - Capability descriptor requirements and examples
  - Task-order semantics and lifecycle
  - Safety gate expectations and certification
  - Simulator-to-clinical promotion path (USL scoring progression)
  - Integration testing requirements
  - Firmware/software update procedures
  - Incident reporting obligations

- `docs/guides/sponsor-cro.md` — Sponsor/CRO guide:
  - Cross-site reporting interfaces
  - Provenance and audit review procedures
  - State/federal regulatory overlay implications by jurisdiction
  - Multi-site deployment coordination
  - Data quality monitoring
  - Study close-out procedures

- `docs/guides/regulator-irb.md` — Regulator/IRB guide:
  - Evidence package structure and contents
  - Conformance artifact interpretation
  - Audit replay package format
  - Change control and validation package
  - Inspection readiness checklist
  - Regulatory submission guidance

- `docs/guides/standards-community.md` — Standards community guide:
  - Extension proposal process (x-{vendor} namespace)
  - Compatibility policy and versioning rules
  - Schema evolution rules (additive changes, deprecation lifecycle)
  - Contribution workflow for specification changes
  - Review and approval process

**5. Operational Documentation**

Create comprehensive operational docs:

- `docs/operations/runbook.md` — Production operations runbook:
  - Server startup/shutdown procedures
  - Health check monitoring
  - Log analysis and troubleshooting
  - Common failure scenarios and resolutions
  - Performance tuning guidance
  - Capacity planning

- `docs/operations/incident-response.md` — Incident response playbook:
  - Severity classification (P1-P4)
  - Escalation paths
  - Communication templates
  - Post-incident review process
  - Evidence preservation procedures

- `docs/operations/key-management.md` — Key management guide:
  - Key generation and storage requirements
  - Token signing key lifecycle
  - Audit record signing key management
  - mTLS certificate management
  - Key rotation procedures and schedules
  - KMS/HSM integration guidance
  - Secrets rotation automation

- `docs/operations/backup-recovery.md` — Backup and recovery procedures:
  - Audit chain backup and integrity verification
  - Provenance graph backup
  - Configuration backup
  - Disaster recovery procedures
  - Recovery time objectives (RTO) and recovery point objectives (RPO)

- `docs/deployment/local-dev.md` — Local development setup guide
- `docs/deployment/hospital-site.md` — Hospital site deployment guide
- `docs/deployment/multi-site-federated.md` — Multi-site federated deployment guide

**6. SLO/SLA Guidance**

Create `docs/operations/slo-guidance.md`:

- Uptime targets per server and per conformance level
- Latency budgets (P50, P95, P99) for each tool
- Fail-safe modes and degraded operation rules
- Data recovery procedures and timelines
- Availability requirements during active procedures
- Monitoring and alerting thresholds

**7. Governance and Adoption Evidence**

Create governance artifacts:

- `docs/governance/decision-log.md` — Decision log of accepted/declined changes with rationale
- `docs/governance/implementation-status.md` — Implementation status matrix (normative section → implementation status → test coverage)
- `docs/governance/roadmap.md` — Roadmap with target adopters, milestones, and timelines
- `docs/governance/compatibility-matrix.md` — Compatibility matrix by version, profile, and conformance level
- `docs/governance/known-gaps.md` — Known gaps, non-goals, and future work
- `docs/governance/contribution-policy.md` — Contribution policy for regulators, vendors, providers, CROs, and standards bodies

**8. Architecture Decision Records**

Create `docs/adr/` with key architectural decisions:

- `docs/adr/001-mcp-protocol-boundary.md` — Why MCP is the right protocol boundary for national oncology trial interoperability
- `docs/adr/002-five-server-architecture.md` — Why these 5 servers were chosen (authz, fhir, dicom, ledger, provenance)
- `docs/adr/003-twenty-three-tools.md` — Why 23 tools are the minimal stable surface area
- `docs/adr/004-profile-conformance-levels.md` — Why profiles map to clinical deployment tiers
- `docs/adr/005-hash-chained-audit.md` — Why hash-chained audit ledger for 21 CFR Part 11 compliance
- `docs/adr/006-dag-provenance.md` — Why DAG-based provenance over linear lineage
- `docs/adr/007-deny-by-default-rbac.md` — Why deny-by-default RBAC for clinical safety

**9. Repository Strategy**

Create `docs/repository-strategy.md`:

- What stays in each repository across the four repos
- What graduates into the national repo
- What is mirrored vs imported vs referenced
- What becomes deprecated
- What becomes the canonical implementation source
- Migration timeline and criteria

**10. Security Documentation**

Create security-focused documentation:

- `docs/security/threat-model.md` — Threat model document covering all attack surfaces
- `docs/security/sbom.md` — SBOM generation guidance and dependency scanning policy
- `docs/security/tamper-evident-storage.md` — Tamper-evident storage design for audit and provenance
- `docs/security/signed-releases.md` — Signed release and release provenance policy

**11. Production Concerns Documentation**

Create `docs/operations/production-concerns.md`:

- Retries and circuit breakers for clinical dependencies
- Idempotency behavior for write-like actions
- Concurrency and locking strategy for ledger writes
- Backpressure and queueing patterns
- Observability standards (metrics, traces, logs)
- Audit export and archival flows
- Log redaction defaults for PHI protection

**12. Profile Walkthroughs**

Create one complete end-to-end walkthrough per profile:

- `docs/walkthroughs/base-profile.md` — Core AuthZ + Audit walkthrough
- `docs/walkthroughs/clinical-read.md` — FHIR read/search with de-identification walkthrough
- `docs/walkthroughs/imaging-guided.md` — DICOM query with modality restrictions walkthrough
- `docs/walkthroughs/multi-site-federated.md` — Cross-site provenance and audit walkthrough
- `docs/walkthroughs/robot-procedure.md` — Complete robot-assisted procedure walkthrough

**13. Update CI Pipeline**

Add CI jobs for:

- SDK build and test (Python + TypeScript)
- CLI tool smoke tests
- Code generation consistency check
- Security scanning (dependency audit)
- SBOM generation
- Documentation build and link validation

**14. Verify Repository-Wide Quality**

After all changes:
1. Python SDK installs and all example scripts run
2. TypeScript SDK builds and all tests pass
3. CLI tool executes all subcommands
4. All stakeholder guides are complete and internally consistent
5. All operational docs reference actual code and configuration
6. All ADRs are well-structured and reference the relevant specification sections
7. All existing tests still pass
8. `ruff check .` and `ruff format --check .` pass cleanly
"Original Prompt"




"Follow-up Prompt"
Also add the following two files to main branch:
main/next-steps.md
main/stats.md

A) Create a comprehensive next-steps.md that explains, in practical and nationally relevant terms, what all stakeholder groups are expected to do now that the repository is publicly available and usable as a proposed national reference standard.

The document should be written for a nationwide audience and should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

The content should be action-oriented, specific, and organized for real-world adoption. It should clearly describe immediate, near-term, and medium-term actions for major stakeholder groups, including sponsors, CROs, academic medical centers, community oncology sites, hospital IT and security teams, robotics vendors, EHR and FHIR integration teams, imaging and PACS and DICOM teams, privacy and compliance and legal and regulatory teams, principal investigators, trial coordinators, auditors, data monitors, and standards contributors or open-source maintainers.

The document should include, where appropriate, what each stakeholder should review first in the repository, what each stakeholder should deploy, validate, or evaluate next, which profiles, schemas, tools, safety modules, governance materials, and test assets are most relevant to them, recommended sequencing of adoption activities, dependencies between technical, operational, clinical, and regulatory workstreams, expected readiness checkpoints for pilot adoption, expectations for documentation, conformance validation, and evidence generation, what should happen at single-site, multi-site, and national coordination levels, and a clear distinction between actions to take now, actions to plan next, and actions that require formal validation before production or clinical use.

The document should read like an adoption and execution guide rather than a vague summary. It should be comprehensive but concise, and it should reflect the repository's positioning as a national MCP and Physical AI oncology trials standard.

B) Create a comprehensive stats.md that presents repository statistics and quantitative summary data in a way that is useful to technical, clinical, compliance, standards, and interoperability audiences.

The document should use a balanced distribution of short paragraphs, numbered lists, and concise bullet points.

It should be metrics-heavy and use quantitative data throughout wherever the repository supports it. The document should be written for readers interested in MCP ecosystems, interoperability maturity, and Physical AI oncology trials.

At minimum, include clearly labeled sections covering repository scale and scope, number and categories of tests, test types and what they validate, number of tools and their distribution by MCP server, MCP server count and server types, schema count and schema categories, profile count and profile types, integration adapter count and categories, safety module count and categories, benchmark and certification tooling count, deployment targets and infrastructure options, languages used across the repository, approximate lines of code if determinable from the repository contents, directory and artifact counts where meaningful, key takeaways, concise executive summary, notable strengths, differentiators, and maturity signals, and any other metrics likely to interest people working in MCPs, healthcare AI infrastructure, interoperability, federated systems, clinical robotics, and oncology trial operations.

Where possible, quantify and break down items such as total tests passed by suite and subtype, unit versus conformance versus integration versus adversarial versus black-box coverage, counts by server, tool family, schema family, and profile level, number of deployment modes, number of interoperability scenarios, number of actor types, number of regulatory overlays, number of benchmark categories, and number of certification or evidence-generation utilities.

Where exact runtime verification is not available from the current environment, use repository-documented counts and label them clearly as repository-reported or documented metrics rather than claiming fresh CI execution.

The document should also include concise summaries of what the metrics imply about technical maturity, why the statistics matter for national interoperability and oncology trial readiness, why these metrics are meaningful to MCP practitioners, and why the quantitative profile is notable for Physical AI clinical trial infrastructure.

For both files, keep the writing professional, concrete, and repository-specific. Avoid filler language. Use headings and subheadings for readability. Use numbered lists when describing sequences, phases, or responsibilities. Use concise bullets for checklists, role-based actions, and metric breakdowns. Prefer precise wording over promotional wording. Keep the tone suitable for a standards-oriented public GitHub repository. Make the documents readable both by technical implementers and non-engineering stakeholders. Ensure the content is comprehensive enough to be useful immediately after publication.
"Follow-up Prompt"
