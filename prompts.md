# Prompt Archive

This document archives the AI-assisted development prompts used to create the National MCP-PAI Oncology Trials Standard specification. Transparency in AI-assisted authorship is a core principle of this project.

---

## Session 1 — Initial Specification Development (2026-03-06)

### Prompt Summary

**Objective**: Scale the single-site TrialMCP reference implementation (kevinkawchak/mcp-pai-oncology-trials v0.3.0) into a multi-site national standard for Physical AI oncology clinical trials.

**Input Context**:
- Analysis of kevinkawchak/mcp-pai-oncology-trials (5 MCP servers, 23 tools, 39 tests)
- Analysis of kevinkawchak/physical-ai-oncology-trials (v2.1.0, robotic systems framework)
- Analysis of kevinkawchak/pai-oncology-trial-fl (v1.1.1, federated learning framework)

**AI Tasks Performed**:
1. Researched all three prior repositories to extract architecture, tool contracts, security model, privacy pipeline, audit mechanism, and regulatory patterns
2. Designed a normative specification structure with 9 modules using RFC 2119 keywords
3. Expanded the 4-actor model to 6 actors (adding sponsor and CRO roles)
4. Created 5-level conformance model (Core, Clinical Read, Imaging, Federated Site, Robot Procedure)
5. Wrote regulatory overlay documents mapping specification requirements to FDA, HIPAA, 21 CFR Part 11, and IRB frameworks
6. Established governance framework (charter, decision process, extension namespaces, version compatibility)
7. Created community templates (issue templates, PR template, Code of Conduct)
8. Authored comprehensive README with architecture diagrams, comparison tables, and getting started guides

**Model**: Claude (Anthropic)

**Human Review**: All generated content is subject to human review, modification, and approval before finalization.

---

## Methodology

### AI-Assisted Standards Development Process

1. **Research Phase**: AI agent analyzes existing implementations, extracting patterns, contracts, and architectural decisions
2. **Synthesis Phase**: AI drafts normative text using established standards conventions (RFC 2119 keywords, conformance levels, regulatory mappings)
3. **Review Phase**: Human experts review all generated content for accuracy, completeness, and regulatory alignment
4. **Iteration Phase**: Feedback is incorporated through the governance decision process

### Transparency Principles

- All AI-generated content is clearly attributed in this archive
- Human review is required before any content is merged into the normative specification
- AI tools are used for drafting and analysis, not for making normative decisions
- The governance process (see [governance/DECISION_PROCESS.md](governance/DECISION_PROCESS.md)) applies equally to AI-generated and human-authored proposals
