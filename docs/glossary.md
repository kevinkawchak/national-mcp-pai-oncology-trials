# Glossary

> **Version 0.5.0** | **Informative** | **National MCP-PAI Oncology Trials Standard**

Standard terminology used throughout the National MCP-PAI Oncology
Trials Standard specification, schemas, profiles, and conformance
suite.

---

## Protocol and Architecture

| Term | Definition |
|------|-----------|
| **MCP** | Model Context Protocol — an open protocol for connecting AI agents to external tools and data sources. |
| **MCP Server** | A service that exposes tools via the MCP protocol. The national standard defines five MCP servers: trialmcp-authz, trialmcp-fhir, trialmcp-dicom, trialmcp-ledger, trialmcp-provenance. |
| **Tool** | A discrete operation exposed by an MCP server. The standard defines 23 tools across 5 servers. |
| **Tool Contract** | The normative specification of a tool's input parameters, output schema, error codes, and audit requirements (see [spec/tool-contracts.md](../spec/tool-contracts.md)). |
| **Conformance Level** | One of five cumulative tiers (Core, Clinical Read, Imaging, Federated Site, Robot Procedure) that define required servers and capabilities (see [spec/conformance.md](../spec/conformance.md)). |
| **Profile** | A document specifying the mandatory tools, optional tools, forbidden operations, required schemas, and regulatory overlays for a conformance level or jurisdiction (see [profiles/](../profiles/)). |

## Actors

| Term | Definition |
|------|-----------|
| **Robot Agent** | An autonomous Physical AI system executing clinical procedures within an oncology trial. |
| **Trial Coordinator** | Clinical site staff managing trial operations, with full FHIR and DICOM access. |
| **Data Monitor** | A CRO or sponsor representative reviewing trial data with read-only access. |
| **Auditor** | A compliance officer verifying regulatory adherence through ledger queries. |
| **Sponsor** | A pharmaceutical or device company funding the clinical trial. |
| **CRO** | Contract Research Organization managing multi-site trial operations. |
| **RBAC** | Role-Based Access Control — authorization model where permissions are assigned to roles, not individuals. The standard uses deny-by-default RBAC. |

## Clinical Data Standards

| Term | Definition |
|------|-----------|
| **FHIR** | Fast Healthcare Interoperability Resources — HL7 standard for exchanging electronic health records. The standard uses FHIR R4. |
| **DICOM** | Digital Imaging and Communications in Medicine — standard for medical imaging data. |
| **EHR** | Electronic Health Record — digital system for storing patient clinical data. |
| **PACS** | Picture Archiving and Communication System — medical imaging storage and retrieval. |
| **RECIST** | Response Evaluation Criteria in Solid Tumors — standardized criteria for measuring tumor response. The standard supports RECIST 1.1. |

## Security and Privacy

| Term | Definition |
|------|-----------|
| **Deny-by-Default** | Security model where all access is denied unless explicitly permitted by policy. |
| **SSRF** | Server-Side Request Forgery — an attack where a server is tricked into making requests to internal resources. The standard mandates SSRF prevention on all inputs. |
| **HIPAA Safe Harbor** | De-identification method that removes 18 specific identifiers from patient data. |
| **Pseudonymization** | Replacing identifying information with reversible tokens. The standard uses HMAC-SHA256 for pseudonymization. |
| **De-identification** | Removing or obscuring personal health information to prevent identification of individuals. |
| **Token** | A bearer credential issued by trialmcp-authz, scoped to a role with a UTC expiry. Tokens are stored as SHA-256 hashes. |

## Audit and Provenance

| Term | Definition |
|------|-----------|
| **Audit Record** | An immutable entry in the hash-chained ledger recording a tool invocation and its outcome. |
| **Hash Chain** | A sequence of records where each record's hash includes the previous record's hash, ensuring tamper detection. |
| **Genesis Hash** | The initial hash value (64 zeros) that anchors the audit chain. |
| **Canonical JSON** | A deterministic JSON serialization (alphabetical keys, hash field excluded, UTF-8) used for computing audit hashes. |
| **Provenance** | A DAG (Directed Acyclic Graph) recording the lineage and transformations of data across the trial. |
| **DAG** | Directed Acyclic Graph — a graph structure used for provenance tracking where nodes represent data sources and edges represent transformations. |
| **SHA-256** | Secure Hash Algorithm producing 256-bit (64-character hex) digests. Used for audit chain hashing, token storage, and data fingerprinting. |

## Physical AI

| Term | Definition |
|------|-----------|
| **Physical AI** | AI systems operating in the physical world through robotic platforms — surgical robots, therapeutic positioning systems, diagnostic needle-placement platforms, and rehabilitative exoskeletons. |
| **USL** | Unification Standard Level — a scoring framework for evaluating Physical AI platform readiness across simulation fidelity, safety controls, and clinical validation. |
| **Task Order** | A scheduled clinical trial task assigned to a Physical AI system, including procedure type, robot assignment, and safety checks. |
| **Robot Capability Profile** | A machine-readable description of a Physical AI platform's capabilities, safety prerequisites, and USL score. |

## Regulatory

| Term | Definition |
|------|-----------|
| **FDA** | U.S. Food and Drug Administration — federal agency regulating medical devices and AI/ML software. |
| **HIPAA** | Health Insurance Portability and Accountability Act — U.S. federal law protecting patient health information. |
| **21 CFR Part 11** | FDA regulation governing electronic records and electronic signatures in clinical trials. |
| **SaMD** | Software as a Medical Device — software intended for medical purposes that is itself a medical device. |
| **IRB** | Institutional Review Board — committee that reviews and approves research involving human subjects. |
| **ICH-GCP** | International Council for Harmonisation - Good Clinical Practice — international quality standard for clinical trials. |
| **CCPA/CPRA** | California Consumer Privacy Act / California Privacy Rights Act — California state privacy laws. |
| **SHIELD Act** | New York Stop Hacks and Improve Electronic Data Security Act — New York state data security law. |

## Specification Language

| Term | Definition |
|------|-----------|
| **MUST** | An absolute requirement of the specification (RFC 2119). |
| **SHOULD** | A recommendation that may be ignored with justification (RFC 2119). |
| **MAY** | A truly optional element (RFC 2119). |
| **Normative** | Content that defines requirements that conforming implementations MUST satisfy. |
| **Non-normative** | Content that is informative — examples, explanations, and reference implementations that do not define requirements. |
| **RFC 2119** | IETF Best Current Practice defining the keywords MUST, SHOULD, MAY for use in specifications. |

## Versioning and Governance

| Term | Definition |
|------|-----------|
| **SemVer** | Semantic Versioning — version numbering scheme (MAJOR.MINOR.PATCH) used by the standard. |
| **Extension Namespace** | Vendor-specific extensions use the `x-{vendor}` prefix to avoid conflicts with the normative specification. |
| **Conformance Registry** | National registry of implementations that have passed conformance testing. |
| **CODEOWNERS** | GitHub file defining ownership of repository directories for review routing. |

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)
