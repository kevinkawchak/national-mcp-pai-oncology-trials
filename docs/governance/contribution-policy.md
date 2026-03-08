# Contribution Policy

**National MCP-PAI Oncology Trials Standard — Contribution Policy**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This document defines the contribution policy for the National MCP-PAI Oncology Trials
Standard. It governs how regulators, vendors, healthcare providers, contract research
organizations (CROs), standards bodies, and other stakeholders may contribute to the
specification, reference implementation, and supporting materials.

---

## 1. Contributor Categories

### 1.1 Regulators

| Attribute | Detail |
|-----------|--------|
| **Who** | FDA CDRH, ONC, state health departments, IRBs |
| **Contribution Scope** | Regulatory overlay documents, compliance mappings, guidance alignment reviews |
| **Review Authority** | Regulatory overlays (`regulatory/` directory) |
| **Process** | Formal liaison through the Regulatory Advisory Committee |
| **IP Terms** | Government contributions are public domain (per 17 U.S.C. Section 105) |

Regulatory contributors provide authoritative input on compliance requirements. Their
contributions are subject to the standard governance review process but carry advisory
weight on regulatory interpretation matters.

### 1.2 Medical Device and Robotics Vendors

| Attribute | Detail |
|-----------|--------|
| **Who** | Robot platform manufacturers, medical device companies, AI system developers |
| **Contribution Scope** | Reference implementation code, conformance test cases, vendor extension definitions, interoperability testing |
| **Review Authority** | Implementation code (`servers/`, `tests/`), vendor extensions |
| **Process** | Standard pull request process with mandatory peer review |
| **IP Terms** | Apache 2.0 license; contributors must sign CLA |

Vendor contributions MUST NOT introduce proprietary dependencies, vendor-specific
requirements, or features that advantage a single vendor's products. All contributions
MUST maintain the vendor-neutral design principle.

### 1.3 Healthcare Providers

| Attribute | Detail |
|-----------|--------|
| **Who** | Cancer centers, hospital systems, academic medical centers, clinical trial sites |
| **Contribution Scope** | Clinical workflow validation, use case documentation, deployment guides, safety requirements, site-specific profile overlays |
| **Review Authority** | Clinical documentation, profile overlays, safety modules |
| **Process** | Standard pull request process; clinical safety contributions require Safety Working Group review |
| **IP Terms** | Apache 2.0 license; contributors must sign CLA |

Provider contributions are particularly valuable for validating that tool contracts
and conformance profiles align with real-world clinical workflows. Clinical safety
contributions (safety module changes, procedure state machine modifications) require
additional review by the Safety Working Group.

### 1.4 Contract Research Organizations (CROs)

| Attribute | Detail |
|-----------|--------|
| **Who** | IQVIA, Syneos Health, PPD, Parexel, and other clinical trial management organizations |
| **Contribution Scope** | Multi-site trial coordination patterns, data monitoring workflows, regulatory submission templates, cross-site federated operations |
| **Review Authority** | Multi-site documentation, federated workflow specifications |
| **Process** | Standard pull request process |
| **IP Terms** | Apache 2.0 license; contributors must sign CLA |

CRO contributions are critical for ensuring that the standard supports efficient
multi-site trial operations. CROs have unique insight into cross-site coordination
challenges, data monitoring requirements, and regulatory submission workflows.

### 1.5 Standards Bodies

| Attribute | Detail |
|-----------|--------|
| **Who** | HL7 International, DICOM Standards Committee, IHE, CDISC, Anthropic (MCP specification) |
| **Contribution Scope** | Cross-standard harmonization, terminology alignment, interoperability profiles, protocol specification review |
| **Review Authority** | Standards alignment sections, external compatibility documentation |
| **Process** | Formal liaison through the Standards Liaison Committee |
| **IP Terms** | Per reciprocal licensing agreements with each standards body |

Standards body contributions ensure alignment with the broader healthcare
interoperability ecosystem. Contributions that affect normative alignment with
FHIR R4, DICOM, or MCP protocol specifications require Standards Liaison Committee
approval.

### 1.6 Academic and Research Institutions

| Attribute | Detail |
|-----------|--------|
| **Who** | Universities, research labs, NIH-funded investigators |
| **Contribution Scope** | Formal verification, security analysis, performance benchmarking, privacy-preserving techniques, peer review |
| **Review Authority** | Research documentation, benchmark methodology, formal proofs |
| **Process** | Standard pull request process; formal verification contributions require Architecture Working Group review |
| **IP Terms** | Apache 2.0 license; contributors must sign CLA. Patent grants per Apache 2.0 Section 3 |

---

## 2. Contribution Process

### 2.1 Issue-First Policy

All contributions MUST begin with an issue filed in the repository. Contributors
MUST NOT submit pull requests without a corresponding issue. This ensures that
proposed changes are discussed and scoped before implementation work begins.

Issue templates are provided for:
- **Bug reports** (`.github/ISSUE_TEMPLATE/bug_report.md`)
- **Specification changes** (`.github/ISSUE_TEMPLATE/spec_change.md`)
- **Feature requests** (`.github/ISSUE_TEMPLATE/feature_request.md`)

### 2.2 Pull Request Requirements

All pull requests MUST:

1. Reference the corresponding issue number
2. Include a clear description of the change and its rationale
3. Pass all automated checks (linting, tests, conformance validation)
4. Include test coverage for code changes
5. Update relevant documentation if behavior changes
6. Follow the pull request template (`.github/PULL_REQUEST_TEMPLATE.md`)

### 2.3 Review Requirements

| Change Type | Required Reviewers | Approval Threshold |
|------------|-------------------|-------------------|
| Normative specification (`spec/`) | 2 Maintainers + Architecture WG | Unanimous maintainer approval |
| Regulatory overlay (`regulatory/`) | 1 Maintainer + Regulatory Advisory | Majority approval |
| Reference implementation (`servers/`) | 2 Maintainers | 2 approvals |
| Tests (`tests/`) | 1 Maintainer | 1 approval |
| Documentation (`docs/`) | 1 Maintainer | 1 approval |
| Safety modules (`safety/`) | 2 Maintainers + Safety WG | Unanimous maintainer approval |
| Conformance profiles (`profiles/`) | 2 Maintainers + Conformance WG | Unanimous maintainer approval |

### 2.4 Normative Change Process

Changes to normative specification text (`spec/` directory) follow an elevated process:

1. **Proposal**: File a specification change issue with detailed rationale
2. **Discussion**: Minimum 14-day public comment period
3. **ADR**: Architecture Decision Record drafted for significant changes
4. **Implementation**: Reference implementation updated to reflect the change
5. **Testing**: Conformance test suite updated
6. **Review**: Full review per the table above
7. **Decision Log**: Entry added to `docs/governance/decision-log.md`

### 2.5 Fast-Track Process

Minor clarifications, typo corrections, and non-behavioral changes may use a
fast-track process with a 3-day comment period and single maintainer approval.
Fast-track eligibility is determined by a maintainer.

---

## 3. Contributor License Agreement (CLA)

### 3.1 Requirement

All non-governmental contributors MUST sign the Contributor License Agreement before
their first contribution can be merged. The CLA grants the project a perpetual,
irrevocable license to use the contribution under the project's Apache 2.0 license.

### 3.2 Corporate CLA

Organizations contributing through multiple individuals SHOULD sign a Corporate CLA
that covers all authorized contributors from the organization.

### 3.3 Patent Grant

Per Apache 2.0 Section 3, contributors grant a patent license for any patent claims
licensable by the contributor that are necessarily infringed by their contribution.

---

## 4. Code of Conduct

All contributors are subject to the project Code of Conduct (`CODE_OF_CONDUCT.md`).
Violations are handled by the governance body. Repeated violations may result in
temporary or permanent exclusion from the project.

---

## 5. Working Groups

### 5.1 Architecture Working Group

- **Scope**: Core specification, tool contracts, server architecture
- **Membership**: Open to all contributor categories
- **Meetings**: Biweekly, minutes published in repository

### 5.2 Security Working Group

- **Scope**: Security specification, threat modeling, access control
- **Membership**: Open to all contributor categories
- **Meetings**: Biweekly, minutes published in repository

### 5.3 Safety Working Group

- **Scope**: Robot safety modules, procedure state machines, e-stop
- **Membership**: Requires clinical safety expertise or robotics engineering background
- **Meetings**: Weekly during active development, biweekly otherwise

### 5.4 Conformance Working Group

- **Scope**: Conformance profiles, certification criteria, test suites
- **Membership**: Open to all contributor categories
- **Meetings**: Biweekly, minutes published in repository

### 5.5 Regulatory Advisory Committee

- **Scope**: Regulatory overlay accuracy, compliance interpretation
- **Membership**: Regulatory affairs professionals from any contributor category
- **Meetings**: Monthly, minutes published in repository

### 5.6 Standards Liaison Committee

- **Scope**: Cross-standard harmonization with HL7, DICOM, IHE, CDISC, MCP
- **Membership**: Representatives from participating standards bodies
- **Meetings**: Quarterly, minutes published in repository

---

## 6. Recognition

Contributors are recognized in the following ways:

- **Git history**: All contributions are attributed through Git commit authorship
- **CONTRIBUTORS file**: Significant contributors are listed (with consent)
- **Release notes**: Contributors to each release are acknowledged in `releases.md`
- **Conformance certificates**: Vendors achieving conformance certification are listed in the conformance registry

---

## 7. Conflict of Interest

Contributors MUST disclose any conflicts of interest that may affect their
contributions. Conflicts include but are not limited to:

- Financial interest in a competing standard or product
- Employment by a vendor whose products would be advantaged by a change
- Regulatory authority over systems that would be affected by a change

Disclosed conflicts do not disqualify contributions but are considered during
review. Undisclosed conflicts discovered after merge may result in contribution
reversion and contributor sanctions.
