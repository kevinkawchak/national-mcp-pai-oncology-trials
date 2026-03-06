# FDA Regulatory Overlay

**National MCP-PAI Oncology Trials Standard — US FDA Mapping**
**Version**: 0.1.0

---

## 1. Overview

This document maps the national MCP-PAI oncology trials standard to applicable FDA guidance and regulations for AI/ML-based software used in clinical trial settings with physical AI (robotic) systems.

---

## 2. Applicable FDA Guidance

### 2.1 AI/ML-Based Software as a Medical Device (SaMD)

MCP servers mediating between robot agents and clinical systems may constitute Software as a Medical Device when they influence clinical decisions. The following FDA guidance documents apply:

- **Artificial Intelligence and Machine Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan** (January 2021)
- **Predetermined Change Control Plans for Machine Learning-Enabled Device Software Functions** (April 2023)
- **Marketing Submission Recommendations for a Predetermined Change Control Plan for AI/ML-Enabled Device Software Functions** (December 2024)

### 2.2 Computer Software Assurance

- **Computer Software Assurance for Production and Quality System Software** (September 2022)
- Applies to MCP server validation and quality management

### 2.3 Clinical Decision Support

- **Clinical Decision Support Software — Guidance for Industry and FDA Staff** (September 2022)
- Applies when MCP tool outputs inform clinical decisions

---

## 3. FDA Pathway Mapping

### 3.1 Regulatory Classification

| MCP Component | Potential Classification | Pathway |
|--------------|------------------------|---------|
| AuthZ Server (access control only) | Not a medical device | N/A |
| FHIR Server (data access) | May be Class II SaMD | 510(k) or De Novo |
| DICOM Server (imaging access) | May be Class II SaMD | 510(k) or De Novo |
| Ledger Server (audit only) | Not a medical device | N/A |
| Provenance Server (lineage only) | Not a medical device | N/A |
| End-to-end robot workflow | Class II or III | 510(k), De Novo, or PMA |

### 3.2 Predetermined Change Control Plan (PCCP)

For MCP servers classified as SaMD, a Predetermined Change Control Plan SHOULD address:

1. **Description of Modifications**: Planned changes to tool contracts, conformance levels, or security requirements
2. **Modification Protocol**: The governance decision process for specification changes
3. **Impact Assessment**: How changes affect the safety and effectiveness of the device
4. **Verification and Validation**: Conformance testing requirements for updates

---

## 4. Specification-to-FDA Mapping

### 4.1 Quality System Regulation (21 CFR 820)

| 21 CFR 820 Section | Specification Coverage |
|--------------------|-----------------------|
| § 820.30 Design Controls | Conformance levels define design inputs and outputs |
| § 820.40 Document Controls | SemVer versioning with compatibility policy |
| § 820.50 Purchasing Controls | Vendor extension namespace with registration |
| § 820.70 Production Controls | Input validation, SSRF prevention, error handling |
| § 820.90 Nonconforming Product | Error code taxonomy, chain verification failure handling |
| § 820.180 Records | Hash-chained audit ledger with retention requirements |
| § 820.198 Complaint Files | Issue templates for bug reports and spec changes |

### 4.2 21 CFR Part 11 (Electronic Records)

See [CFR_PART_11.md](CFR_PART_11.md) for the complete mapping.

### 4.3 Good Clinical Practice (GCP)

| GCP Requirement | Specification Coverage |
|----------------|----------------------|
| Data integrity | SHA-256 hash chains, provenance fingerprinting |
| Audit trail | Append-only ledger with replay trace |
| Access control | Deny-by-default RBAC with role-scoped tokens |
| Source data verification | Provenance lineage queries |
| Subject privacy | HIPAA Safe Harbor de-identification |

---

## 5. Breakthrough Device Program

Physical AI systems in oncology trials MAY qualify for FDA's Breakthrough Device Program if they:
- Provide more effective treatment or diagnosis of life-threatening diseases
- Represent breakthrough technology with no approved alternatives
- Offer significant advantages over existing approved devices

MCP server conformance at Level 5 (Robot Procedure) demonstrates the regulatory infrastructure required for Breakthrough Device submissions.

---

## 6. Post-Market Requirements

### 6.1 Real-World Performance Monitoring

Conforming implementations SHOULD support post-market surveillance through:
- Continuous audit ledger analysis for safety signals
- Provenance tracking of model performance across sites
- Federated analysis of adverse event patterns

### 6.2 Adverse Event Reporting

The audit ledger and provenance system MUST retain sufficient detail to support:
- Medical Device Reporting (MDR) per 21 CFR 803
- MedWatch submissions
- Recall documentation if necessary

---

## 7. References

- FDA. (2021). *Artificial Intelligence/Machine Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan.* U.S. Food and Drug Administration.
- FDA. (2024). *Marketing Submission Recommendations for a Predetermined Change Control Plan for AI/ML-Enabled Device Software Functions.* U.S. Food and Drug Administration.
- [21 CFR Part 820 — Quality System Regulation](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820)
- [21 CFR Part 11 — Electronic Records; Electronic Signatures](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11)
