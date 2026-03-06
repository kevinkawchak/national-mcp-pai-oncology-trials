# Charter

**National MCP-PAI Oncology Trials Standard — Governance Charter**
**Version**: 0.1.0

---

## 1. Purpose

The National MCP-PAI Oncology Trials Standard Governance Charter establishes the organizational structure, decision-making authority, and operating procedures for the development and maintenance of the normative specification for Model Context Protocol servers in Physical AI oncology clinical trial systems across the United States.

---

## 2. Mission

To develop, maintain, and promote an open, vendor-neutral, nationally recognized standard that enables safe, interoperable, and regulatory-compliant deployment of Physical AI systems in oncology clinical trials throughout the United States.

---

## 3. Scope of Authority

The governance body has authority over:

- **Normative specification** (`spec/` directory): All protocol requirements, tool contracts, actor models, security baselines, and conformance levels
- **Regulatory overlays** (`regulatory/` directory): Mappings between the specification and U.S. regulatory requirements
- **Governance processes** (`governance/` directory): Decision-making procedures, extension policies, and version compatibility
- **Conformance registry**: Registration and validation of conforming implementations

The governance body does NOT have authority over:
- Individual implementation choices beyond conformance requirements
- Site-specific operational procedures
- Clinical trial protocols or medical decisions
- Robot platform design or selection

---

## 4. Roles

### 4.1 Maintainers

Maintainers are responsible for reviewing and merging specification changes, managing releases, and ensuring the quality of the standard.

**Responsibilities:**
- Review all pull requests for specification changes
- Ensure changes follow the decision process
- Manage version releases
- Maintain the conformance registry

### 4.2 Contributors

Contributors are individuals or organizations that propose specification changes, report issues, or participate in community review.

**Rights:**
- Submit specification change proposals
- Participate in community review periods
- Vote on non-binding community polls

### 4.3 Implementers

Implementers are organizations building MCP server deployments conforming to the standard.

**Rights:**
- Register conforming implementations
- Propose specification changes based on implementation experience
- Request clarification of normative requirements

---

## 5. Principles

1. **Open Process**: All specification development occurs in public repositories
2. **Consensus-Driven**: Major changes require community review and maintainer consensus
3. **Implementation-Informed**: Specification changes should be informed by implementation experience
4. **Regulatory Alignment**: All changes must maintain alignment with applicable U.S. regulations
5. **Vendor Neutrality**: The standard must not favor any specific vendor, platform, or technology
6. **Patient Safety**: Patient safety considerations take precedence in all decisions

---

## 6. Meetings

- Governance meetings SHOULD be held quarterly or as needed
- Meeting agendas MUST be published at least 7 days in advance
- Meeting minutes MUST be published within 14 days
- All meetings SHOULD be open to contributors and implementers

---

## 7. Amendments

This charter MAY be amended through the standard decision process described in [DECISION_PROCESS.md](DECISION_PROCESS.md). Charter amendments require approval from all maintainers.
