# Releases

Release notes for the National MCP-PAI Oncology Trials Standard.

---

## v0.1.0 — Initial Specification Draft (2026-03-06)

**Status**: Draft for Community Review

### Overview

First public release of the National MCP-PAI Oncology Trials Standard — a normative specification for deploying Model Context Protocol (MCP) servers across federated Physical AI oncology clinical trial systems in the United States.

### What's Included

**9 Specification Modules**
- Core architecture with three-tier national deployment topology
- Six-actor model with deny-by-default RBAC permission matrix
- 23 tool contracts across 5 MCP servers (AuthZ, FHIR, DICOM, Ledger, Provenance)
- Security baseline: RBAC, token lifecycle, SSRF/injection prevention
- Privacy framework: HIPAA Safe Harbor, HMAC-SHA256 pseudonymization
- Provenance: DAG-based data lineage with W3C PROV alignment
- Audit: Hash-chained immutable ledger with 21 CFR Part 11 compliance
- 5-level conformance model (Core through Robot Procedure)
- SemVer versioning with extension namespace mechanism

**4 Regulatory Overlays**
- FDA AI/ML medical device guidance mapping
- HIPAA Privacy and Security Rule mapping
- 21 CFR Part 11 electronic records mapping
- IRB site policy template

**Governance Framework**
- Charter, decision process, extension rules, version compatibility
- GitHub issue templates and PR template
- Contributor Covenant Code of Conduct

### Relationship to Reference Implementation

This specification is derived from analysis of [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) (TrialMCP v0.3.0), scaling the single-site proof of concept into a multi-site national standard with formal conformance levels, regulatory overlays, and governance processes.

### Next Steps

- Community review period (30 days)
- Gather feedback from clinical sites, sponsors, CROs, and technology vendors
- Develop conformance test suite
- Pilot conformance assessment with 2-3 reference implementations
