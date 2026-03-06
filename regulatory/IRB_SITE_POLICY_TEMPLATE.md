# IRB Site Policy Template

**National MCP-PAI Oncology Trials Standard — IRB Site Policy Template**
**Version**: 0.1.0

---

## Instructions

This template provides a framework for sites to document their MCP server deployment policies for IRB review. Sites MUST customize this template to reflect their specific deployment, personnel, and procedures. Bracketed text `[...]` indicates fields requiring site-specific information.

---

## 1. Site Information

| Field | Value |
|-------|-------|
| **Site Name** | [Institution Name] |
| **Site Identifier** | [Unique site ID in the national MCP network] |
| **Principal Investigator** | [Name, credentials] |
| **IT Security Officer** | [Name, credentials] |
| **IRB Protocol Number** | [IRB-assigned number] |
| **MCP Conformance Level** | [1-5, per spec/conformance.md] |
| **Effective Date** | [Date] |

---

## 2. System Description

### 2.1 MCP Server Deployment

This site operates MCP servers conforming to the National MCP-PAI Oncology Trials Standard version [X.Y.Z] at Conformance Level [N].

**Deployed Servers:**

| Server | Version | Status |
|--------|---------|--------|
| trialmcp-authz | [version] | [Active/Planned] |
| trialmcp-ledger | [version] | [Active/Planned] |
| trialmcp-fhir | [version] | [Active/Planned] |
| trialmcp-dicom | [version] | [Active/Planned] |
| trialmcp-provenance | [version] | [Active/Planned] |

### 2.2 Robot Platforms

| Platform | Manufacturer | Clinical Use | USL Score |
|----------|-------------|-------------|-----------|
| [Robot Name] | [Manufacturer] | [Procedure type] | [Score] |

### 2.3 Clinical Systems Integration

| System | Type | Integration |
|--------|------|-------------|
| [EHR System] | Electronic Health Record | FHIR R4 via trialmcp-fhir |
| [PACS System] | Picture Archiving | DICOM via trialmcp-dicom |

---

## 3. Access Control Policy

### 3.1 Authorized Personnel

| Role | Individuals | Access Scope |
|------|------------|-------------|
| Trial Coordinator | [Names] | [As per actor-model.md] |
| Data Monitor | [Names/Organization] | [As per actor-model.md] |
| Auditor | [Names/Organization] | [As per actor-model.md] |

### 3.2 Robot Agent Authorization

| Robot | Authorized Procedures | Token Duration | Supervision |
|-------|---------------------|----------------|-------------|
| [Robot ID] | [Procedure list] | [Duration] | [Supervision level] |

### 3.3 Additional Restrictions

[Document any site-specific restrictions beyond the standard's default policy. For example: restricted operating hours, required human supervision levels, geographic restrictions.]

---

## 4. Privacy Protections

### 4.1 De-identification

This site implements HIPAA Safe Harbor de-identification as mandated by the standard:
- All 18 PHI categories are removed or generalized before data leaves the FHIR server
- HMAC-SHA256 pseudonymization uses a site-specific salt stored in [key management system]
- DICOM patient names are hashed (SHA-256, 12-character truncation)

### 4.2 Data Locality

- Patient data remains within [institution name] systems at all times
- Only de-identified aggregate data crosses site boundaries for federated learning
- [Describe any additional data locality measures]

### 4.3 Salt Management

- HMAC salt is generated using [method]
- Salt is stored in [secure storage system]
- Salt rotation schedule: [frequency or conditions]

---

## 5. Audit and Monitoring

### 5.1 Audit Chain

- Hash-chained audit ledger records all MCP tool calls
- Chain verification is performed [frequency: daily/hourly/continuous]
- Audit records are retained for [duration] per 21 CFR Part 11

### 5.2 Monitoring Procedures

| Activity | Frequency | Responsible Party |
|----------|-----------|------------------|
| Chain verification | [frequency] | [role/name] |
| Access review | [frequency] | [role/name] |
| Security incident review | [frequency] | [role/name] |
| Token expiry review | [frequency] | [role/name] |

### 5.3 Incident Response

[Describe the site's incident response procedure for MCP-related security events, including escalation path and notification requirements.]

---

## 6. Patient Consent

### 6.1 Consent for Robot Procedures

Patients enrolled in trials involving Physical AI systems are informed of:
- The use of robotic systems in their care
- The MCP infrastructure mediating between robots and clinical systems
- De-identification measures protecting their data
- Their right to withdraw consent

### 6.2 Consent Documentation

Patient consent forms are stored in [system] and linked to the audit ledger through [mechanism].

---

## 7. Training Requirements

| Role | Training Topics | Frequency |
|------|----------------|-----------|
| Trial Coordinators | MCP tool usage, patient privacy, audit procedures | [frequency] |
| Data Monitors | Data access procedures, de-identification verification | [frequency] |
| Auditors | Chain verification, replay trace review, regulatory reporting | [frequency] |
| IT Staff | Server deployment, security configuration, incident response | [frequency] |

---

## 8. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Principal Investigator | | | |
| IT Security Officer | | | |
| IRB Chair/Designee | | | |

---

*This template is provided as part of the National MCP-PAI Oncology Trials Standard. Sites are responsible for customizing and completing this template in compliance with their institutional policies and applicable regulations.*
