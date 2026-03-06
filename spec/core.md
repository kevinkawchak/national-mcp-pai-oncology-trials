# Core Specification

**National MCP-PAI Oncology Trials Standard — spec/core.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Protocol Scope

This specification defines the normative requirements for Model Context Protocol (MCP) servers operating within United States Physical AI oncology clinical trial systems. The scope encompasses:

- **Robot-to-clinical-system communication** via standardized MCP tool contracts
- **Authorization and access control** for autonomous agents in regulated environments
- **Clinical data access** through FHIR R4 and DICOM interfaces with mandatory de-identification
- **Audit and provenance** for 21 CFR Part 11 compliance and data lineage tracking
- **Federated multi-site operations** enabling cross-institutional collaboration without centralized patient data

### 1.1 Out of Scope

- Robot control algorithms and motion planning
- Clinical decision support logic
- Electronic health record (EHR) system internals
- Network transport security (TLS configuration is an infrastructure concern)

---

## 2. Design Principles

### 2.1 Deny by Default

All access MUST be explicitly granted. The authorization server MUST deny any request that does not match an explicit ALLOW rule. Explicit DENY rules MUST take precedence over ALLOW rules.

### 2.2 Least Privilege

Each actor MUST receive only the minimum permissions required for their role. Robot agents MUST NOT receive broader access than their clinical task requires.

### 2.3 Audit Everything

Every tool invocation MUST produce a signed audit record appended to the hash-chained ledger. No tool call MAY execute without generating an audit entry.

### 2.4 Privacy by Design

Patient data MUST be de-identified before leaving the FHIR server boundary. HIPAA Safe Harbor 18-identifier removal MUST be applied. HMAC-SHA256 pseudonymization MUST maintain referential integrity across de-identified records.

### 2.5 Federated First

Patient data MUST remain at the originating site. Only aggregated, de-identified, or differentially private outputs MAY cross site boundaries. Federated learning aggregation (FedAvg, FedProx, SCAFFOLD) SHOULD be used for cross-site model training.

### 2.6 Vendor Neutral

The specification MUST NOT require any specific robot platform, EHR vendor, PACS system, or cloud provider. Tool contracts define interfaces, not implementations.

### 2.7 Standards Aligned

The specification MUST align with existing healthcare standards: FHIR R4, DICOM, HL7, LOINC, RxNorm, MedDRA, ICD-10. Regulatory mappings MUST cover FDA, HIPAA, 21 CFR Part 11, ICH-GCP E6(R2).

---

## 3. Conformance Levels

The standard defines five cumulative conformance levels. See [conformance.md](conformance.md) for the full MUST/SHOULD/MAY matrix.

| Level | Name | Description |
|-------|------|-------------|
| 1 | **Core** | Authorization and audit chain |
| 2 | **Clinical Read** | FHIR R4 clinical data access |
| 3 | **Imaging** | DICOM query and retrieve |
| 4 | **Federated Site** | Multi-site data lineage and aggregation |
| 5 | **Robot Procedure** | End-to-end autonomous clinical workflow |

### 3.1 Level Requirements

- Level 1 (Core) MUST implement `trialmcp-authz` and `trialmcp-ledger`
- Level 2 (Clinical Read) MUST implement Level 1 plus `trialmcp-fhir`
- Level 3 (Imaging) MUST implement Level 2 plus `trialmcp-dicom`
- Level 4 (Federated Site) MUST implement Level 3 plus `trialmcp-provenance`
- Level 5 (Robot Procedure) MUST implement all five servers and the reference robot agent workflow

---

## 4. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this specification are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### 4.1 Definitions

| Term | Definition |
|------|-----------|
| **MCP** | Model Context Protocol — the communication protocol between AI agents and tool servers |
| **Physical AI** | Autonomous robotic systems operating in physical clinical environments |
| **Tool** | A named operation exposed by an MCP server with defined input, output, and error contracts |
| **Actor** | An entity (human or autonomous) that interacts with MCP servers |
| **Site** | A clinical trial location (hospital, cancer center, research facility) |
| **Conforming Implementation** | An MCP server deployment that satisfies all MUST requirements for its declared conformance level |
| **De-identification** | Removal or generalization of protected health information per HIPAA Safe Harbor |
| **Pseudonymization** | Replacement of identifiers with consistent pseudonyms using HMAC-SHA256 |
| **Hash Chain** | An append-only sequence of records where each record includes the SHA-256 hash of the previous record |
| **DAG** | Directed acyclic graph — the data structure used for provenance lineage |
| **USL** | Unification Standard Level — a scoring framework (1.0–10.0) evaluating robotic readiness for unified multi-site oncology trials |

---

## 5. Protocol Architecture

### 5.1 Three-Layer Model

1. **Physical AI Layer**: Robot platforms (surgical, therapeutic, diagnostic, rehabilitative) executing clinical procedures
2. **MCP Protocol Layer**: Five standardized servers mediating access between robots and clinical systems
3. **Clinical Trial Layer**: EHR, PACS, regulatory systems, and trial management platforms

### 5.2 Server Registry

Every conforming deployment MUST implement the servers required by its declared conformance level:

| Server | Identifier | Required From |
|--------|-----------|---------------|
| Authorization | `trialmcp-authz` | Level 1 |
| Audit Ledger | `trialmcp-ledger` | Level 1 |
| Clinical Data | `trialmcp-fhir` | Level 2 |
| Imaging | `trialmcp-dicom` | Level 3 |
| Provenance | `trialmcp-provenance` | Level 4 |

### 5.3 Communication Model

- Clients (robot agents, coordinators) communicate with MCP servers via the Model Context Protocol
- MCP servers communicate with backend clinical systems via standard protocols (FHIR REST, DICOM network)
- Cross-site communication MUST occur only through the federated coordination layer
- All inter-server communication within a site MUST be authenticated

---

## 6. Error Handling

### 6.1 Error Code Registry

All conforming servers MUST use the following machine-readable error codes:

| Code | Meaning |
|------|---------|
| `AUTHZ_DENIED` | Authorization policy denied the request |
| `VALIDATION_FAILED` | Input validation failed (format, SSRF) |
| `NOT_FOUND` | Requested resource does not exist |
| `INTERNAL_ERROR` | Server-side processing failure |
| `TOKEN_EXPIRED` | Authentication token has expired |
| `TOKEN_REVOKED` | Authentication token has been revoked |
| `PERMISSION_DENIED` | Caller lacks required permission |
| `INVALID_INPUT` | Input parameters are malformed |
| `RATE_LIMITED` | Request rate exceeds configured limits |

### 6.2 Error Response Format

Error responses MUST include:
- `code`: One of the registered error codes
- `message`: Human-readable description
- `details` (OPTIONAL): Additional context for debugging

---

## 7. References

- [RFC 2119 — Key words for use in RFCs](https://www.rfc-editor.org/rfc/rfc2119)
- [HL7 FHIR R4](https://www.hl7.org/fhir/R4/)
- [DICOM Standard](https://www.dicomstandard.org/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
