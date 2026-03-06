# Decision Process

**National MCP-PAI Oncology Trials Standard — Decision Process**
**Version**: 0.1.0

---

## 1. Overview

This document defines the decision-making process for changes to the national MCP-PAI oncology trials standard. All specification changes, governance updates, and regulatory overlay modifications follow this process.

---

## 2. Change Categories

### 2.1 Editorial (Patch)

**Scope**: Typo fixes, clarifications, formatting improvements that do not alter normative requirements.

**Process**:
1. Submit a pull request with the `editorial` label
2. One maintainer review and approval
3. Merge within 7 days if no objections

### 2.2 Minor Enhancement (Minor)

**Scope**: New tools, new optional parameters, new conformance requirements, promotion of SHOULD to MUST.

**Process**:
1. Submit a specification change proposal using the [spec_change issue template](../.github/ISSUE_TEMPLATE/spec_change.md)
2. Community review period: 14 days minimum
3. Two maintainer reviews and approvals
4. No unresolved objections from maintainers
5. Merge after review period closes

### 2.3 Breaking Change (Major)

**Scope**: Removal of tools, changes to existing tool contracts, modifications to security model, changes to conformance level requirements.

**Process**:
1. Submit a specification change proposal with the `breaking` label
2. Community review period: 30 days minimum
3. All maintainer reviews and approvals
4. Migration guide must be included
5. Implementation impact assessment required
6. Merge after review period closes and all approvals received

---

## 3. Proposal Format

All specification change proposals MUST include:

1. **Summary**: One-paragraph description of the change
2. **Motivation**: Why the change is needed
3. **Specification**: The exact normative text to add, modify, or remove
4. **Conformance Impact**: Which conformance levels are affected
5. **Backward Compatibility**: Whether the change is backward-compatible
6. **Implementation Impact**: Estimated effort for existing implementations
7. **Regulatory Impact**: Whether regulatory overlays need updating

---

## 4. Review Process

### 4.1 Community Review

During the review period, any contributor or implementer MAY:
- Comment on the proposal with support, concerns, or suggestions
- Request changes to the proposed specification text
- Raise regulatory or safety concerns

### 4.2 Maintainer Review

Maintainers review proposals for:
- Technical correctness and completeness
- Alignment with design principles
- Regulatory compliance
- Implementation feasibility
- Compatibility with existing requirements

### 4.3 Conflict Resolution

If maintainers disagree:
1. Discussion period of 7 additional days
2. If consensus is not reached, a formal vote is held
3. Simple majority of maintainers decides for minor changes
4. Unanimous agreement required for breaking changes and charter amendments

---

## 5. Emergency Changes

Security vulnerabilities or regulatory compliance gaps MAY be addressed through an expedited process:

1. File a security advisory or urgent issue
2. Maintainer review within 48 hours
3. One maintainer approval sufficient for merge
4. Post-merge community notification within 24 hours
5. Retroactive community review within 14 days

---

## 6. Release Process

1. Maintainers designate a release candidate
2. Final review period: 7 days
3. Changelog and release notes prepared
4. Version number assigned per [spec/versioning.md](../spec/versioning.md)
5. Release published and conformance registry updated
