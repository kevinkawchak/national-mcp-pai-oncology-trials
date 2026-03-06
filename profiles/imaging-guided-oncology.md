# Imaging-Guided Oncology Profile

**National MCP-PAI Oncology Trials Standard — profiles/imaging-guided-oncology.md**
**Version**: 0.3.0
**Status**: Normative

---

## 1. Purpose

The Imaging-Guided Oncology Profile defines the requirements for implementations that provide DICOM imaging query and retrieve capabilities with role-based modality restrictions. This profile builds on the [Clinical Read Profile](clinical-read.md) and is required for any deployment involving medical imaging data — CT, MRI, PET, and radiotherapy planning modalities — within Physical AI oncology clinical trials.

> Implementations claiming Imaging-Guided Oncology conformance MUST satisfy all Base Profile and Clinical Read Profile requirements AND all requirements defined in this profile.

---

## 2. Mandatory Tools

The Imaging-Guided Oncology Profile requires the `trialmcp-dicom` server in addition to all lower-profile servers.

| Tool | Requirement | Description |
|------|-------------|-------------|
| `dicom_query` | MUST | Query DICOM studies with role-based access control at PATIENT, STUDY, SERIES, or IMAGE level |
| `dicom_retrieve_pointer` | MUST | Generate time-limited retrieval tokens for DICOM study access |
| `dicom_study_metadata` | MUST | Return study-level metadata including modalities, series count, and description |
| `dicom_recist_measurements` | MUST | Return RECIST 1.1 tumor measurements and overall response assessment |

---

## 3. Modality Support Requirements

### 3.1 Mandatory Modalities (MUST)

Conforming implementations MUST support the following imaging modalities:

| Modality Code | Modality Name | Oncology Use |
|--------------|---------------|--------------|
| `CT` | Computed Tomography | Tumor staging, treatment planning, RECIST measurements |
| `MR` | Magnetic Resonance | Soft tissue characterization, brain/spine oncology |
| `PT` | Positron Emission Tomography | Metabolic assessment, staging, treatment response |

### 3.2 Recommended Modalities (SHOULD)

Conforming implementations SHOULD support the following radiotherapy planning modalities:

| Modality Code | Modality Name | Oncology Use |
|--------------|---------------|--------------|
| `RTSTRUCT` | RT Structure Set | Tumor and organ-at-risk contours for treatment planning |
| `RTPLAN` | RT Plan | Radiation treatment plan parameters and beam geometry |

### 3.3 Optional Modalities (MAY)

| Modality Code | Modality Name | Oncology Use |
|--------------|---------------|--------------|
| `RTDOSE` | RT Dose | Radiation dose distribution maps |
| `RTIMAGE` | RT Image | Portal imaging for treatment verification |
| `US` | Ultrasound | Image-guided biopsy and needle placement |
| `NM` | Nuclear Medicine | Functional imaging for therapy assessment |
| `DX` | Digital Radiography | Chest imaging and skeletal surveys |
| `CR` | Computed Radiography | Legacy imaging systems |
| `SEG` | Segmentation | AI-generated tumor segmentation masks |

---

## 4. Role-Based Modality Restrictions

### 4.1 Query Level Permissions

Access to DICOM query levels MUST be restricted by actor role:

| Actor Role | PATIENT | STUDY | SERIES | IMAGE |
|-----------|---------|-------|--------|-------|
| `trial_coordinator` | ALLOW | ALLOW | ALLOW | DENY |
| `robot_agent` | DENY | ALLOW | ALLOW | DENY |
| `data_monitor` | ALLOW | ALLOW | DENY | DENY |
| `auditor` | DENY | ALLOW | DENY | DENY |
| `sponsor` | DENY | DENY | DENY | DENY |
| `cro` | DENY | ALLOW | DENY | DENY |

### 4.2 Modality Access by Role

Certain roles MUST be restricted from specific modality access:

| Actor Role | CT | MR | PT | RTSTRUCT | RTPLAN | RTDOSE |
|-----------|----|----|----|---------:|-------:|-------:|
| `trial_coordinator` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| `robot_agent` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | DENY |
| `data_monitor` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| `auditor` | DENY | DENY | DENY | DENY | DENY | DENY |

### 4.3 Privacy at Query Levels

- Patient names at the `PATIENT` query level MUST be hashed using SHA-256, truncated to 12 characters
- Patient identifiers in audit records MUST use pseudonymized values
- DICOM Study Instance UIDs MUST be validated against the pattern `^[\d.]+$`
- DICOM UIDs containing embedded URLs MUST be rejected (SSRF prevention)

---

## 5. Retrieval Token Requirements

| Requirement | Specification |
|------------|---------------|
| Token expiry | MUST default to 3600 seconds |
| Token storage | MUST store hash only, not plaintext |
| Token scope | MUST be scoped to a single study instance UID |
| Token validation | MUST verify expiry, scope, and revocation status before granting access |
| Concurrent tokens | SHOULD support multiple active retrieval tokens per actor |
| Token renewal | MAY support token renewal before expiry |

---

## 6. RECIST 1.1 Requirements

For tumor response assessment:

| Requirement | Keyword | Description |
|------------|---------|-------------|
| Target lesion measurement | MUST | Report individual lesion diameters in millimeters |
| Overall response | MUST | Classify as CR (Complete Response), PR (Partial Response), SD (Stable Disease), or PD (Progressive Disease) |
| Lesion identification | MUST | Use stable lesion identifiers across timepoints |
| Measurement audit | MUST | Record all measurements in the audit ledger |
| Non-target lesion tracking | SHOULD | Track non-target lesion presence/absence |
| New lesion detection | SHOULD | Flag new lesions for PD assessment |
| Measurement history | MAY | Return measurement timeseries for longitudinal analysis |

---

## 7. Optional Tools

| Tool | Requirement | Description |
|------|-------------|-------------|
| `dicom_series_metadata` | MAY | Series-level metadata retrieval |
| `dicom_modality_worklist` | MAY | Modality worklist management for scheduled procedures |
| `dicom_ai_segmentation_query` | MAY | Query AI-generated segmentation results (SEG modality) |

---

## 8. Forbidden Operations

| Operation | Reason |
|-----------|--------|
| IMAGE-level query access | Security: no actor may query at IMAGE level to prevent bulk data exfiltration |
| Unhashed patient names in query results | Privacy: patient names at PATIENT level MUST always be hashed |
| Indefinite retrieval tokens | Security: all retrieval tokens MUST have a finite expiry |
| Direct PACS access bypass | Architecture: all imaging access MUST route through trialmcp-dicom |
| Modality access outside role permissions | Security: role-based modality restrictions MUST be enforced |

---

## 9. Required Schemas

In addition to lower-profile schemas, Imaging-Guided Oncology implementations MUST validate against:

| Schema | File | Purpose |
|--------|------|---------|
| DICOM Query | `schemas/dicom-query.schema.json` | Query parameters, output, and role-based permissions |
| Robot Capability Profile | `schemas/robot-capability-profile.schema.json` | Robot platform modality capabilities |

---

## 10. Regulatory Overlays

| Regulation | Relevant Section | Coverage |
|-----------|-----------------|----------|
| HIPAA Privacy Rule | §164.514(b) Safe Harbor | Patient name hashing in DICOM queries |
| 21 CFR Part 11 | §11.10(e) Audit trails | All DICOM access audited in hash-chained ledger |
| FDA AI/ML Guidance | Data integrity | Imaging data provenance for AI/ML training and inference |
| IEC 80601-2-77 | Robot-assisted surgery | Imaging integration for surgical navigation |
| DICOM Standard PS3.15 | Security profiles | DICOM confidentiality and integrity |

---

## 11. Conformance Test Subset

Implementations claiming Imaging-Guided Oncology conformance MUST pass:

| Test Category | Test Count | Description |
|--------------|------------|-------------|
| Clinical Read Profile tests | 29 | All lower-profile conformance tests |
| DICOM query role enforcement | 3 | Role-based query level restrictions |
| Patient name hashing | 1 | SHA-256 hash at PATIENT level |
| Retrieval token lifecycle | 3 | Issue, expire, validate |
| DICOM UID validation | 1 | Format validation and SSRF rejection |
| RECIST measurements | 1 | Correct response classification |
| Modality restriction enforcement | 1 | Role-based modality access control |
| **Total** | **39** | |

---

*This profile is part of the [National MCP-PAI Oncology Trials Standard](../README.md). See [spec/tool-contracts.md](../spec/tool-contracts.md) for the full DICOM tool contract specifications.*
