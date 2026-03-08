# ADR-001: MCP as the Protocol Boundary for National Oncology Trial Interoperability

**Status**: Accepted
**Date**: 2026-01-15
**Decision Makers**: Architecture Working Group
**Tracking**: DL-001 in `docs/governance/decision-log.md`

---

## Context

The National MCP-PAI Oncology Trials Standard requires a protocol boundary between
Physical AI systems (surgical robots, therapeutic positioning systems, diagnostic
platforms) and the clinical trial infrastructure they interact with (EHR systems,
PACS, audit systems, regulatory reporting).

This boundary must satisfy several constraints simultaneously:

1. **Vendor neutrality**: No dependency on specific robot platforms, EHR vendors,
   or cloud providers
2. **Clinical safety**: Fail-safe behavior when the protocol boundary is unavailable
3. **Regulatory compliance**: Support for 21 CFR Part 11 audit trails, HIPAA
   de-identification, and ICH-GCP E6(R2) reporting
4. **Interoperability at national scale**: Hundreds of sites with diverse technology
   stacks must communicate through a common interface
5. **AI agent compatibility**: Robot agents operating autonomously must be able to
   discover, invoke, and compose operations through the protocol
6. **Minimal surface area**: The protocol boundary must be small enough to
   standardize nationally but expressive enough to cover all required operations

### Candidates Evaluated

**Custom REST API**: A bespoke RESTful API designed specifically for oncology trial
robot integration. This would provide maximum design flexibility but would create a
novel standard with no existing ecosystem. Each vendor would need to implement the
API from scratch, and there would be no tooling, SDK, or community support.

**gRPC with Protocol Buffers**: Strong typing, code generation, and streaming support.
However, gRPC is optimized for service-to-service communication, not for AI agent
tool discovery and invocation. The code generation dependency adds complexity to the
conformance testing process, and Protocol Buffer schema evolution rules are more
restrictive than needed.

**HL7 FHIR Messaging**: The healthcare industry standard for clinical data exchange.
FHIR Messaging provides a well-defined data model for clinical resources but lacks
semantics for robot control, audit chain operations, and provenance tracking. Using
FHIR as the sole protocol boundary would require extending the FHIR specification
beyond its design intent.

**Model Context Protocol (MCP)**: A tool-oriented protocol designed for AI agent
interaction with external systems. MCP provides structured tool definitions with
typed inputs and outputs, tool discovery, and a growing ecosystem of SDKs and
client implementations.

---

## Decision

Adopt the Model Context Protocol (MCP) as the sole protocol boundary for all
robot-to-clinical-system interactions in the national standard.

The standard defines five MCP servers, each exposing a set of tool contracts that
cover authorization, clinical data access, imaging, audit, and provenance. All
interactions between Physical AI systems and clinical infrastructure pass through
these MCP tool contracts.

---

## Rationale

### Tool Abstraction Aligns with Clinical Operations

MCP's tool abstraction maps naturally to clinical trial operations. Each tool
represents a discrete clinical action (read a FHIR resource, query DICOM studies,
append an audit record) with clear inputs, outputs, and error conditions. This
one-to-one mapping between MCP tools and clinical operations makes the standard
intuitive for clinical informaticists, regulatory reviewers, and robot engineers.

### AI Agent Native Protocol

MCP was designed for AI agent interaction. Robot agents can discover available tools,
evaluate their permissions, and compose multi-step clinical workflows without custom
integration code. This is critical for autonomous and semi-autonomous robot operation
in clinical environments.

### Vendor-Neutral Tool Contracts

MCP tool contracts define interfaces, not implementations. A tool contract specifies
what inputs are accepted and what outputs are produced, without prescribing how the
operation is implemented. This enables vendors to implement tool contracts using their
existing infrastructure (EHR integrations, PACS connections, database systems) while
maintaining protocol-level interoperability.

### Ecosystem Momentum

MCP has growing adoption among AI agent frameworks, with SDKs available in Python,
TypeScript, and other languages. This reduces the implementation burden for vendors
and sites, and provides a foundation of tooling (testing frameworks, protocol
validators, client libraries) that the standard can leverage.

### Conformance Testability

MCP's structured tool definitions enable automated conformance testing. Each tool
contract can be tested independently by providing valid inputs and verifying that
outputs match the specified schema. This is essential for a national standard that
must be verifiable across hundreds of implementations.

---

## Consequences

### Positive

- **Reduced implementation burden**: Vendors can use existing MCP SDKs rather than
  building protocol stacks from scratch
- **Natural AI agent integration**: Robot agents interact with clinical systems
  through the same protocol they use for other AI operations
- **Clear conformance boundary**: The 23 tool contracts provide a precise,
  testable surface area for conformance certification
- **Ecosystem leverage**: Growing MCP tooling and community support accelerates adoption
- **Protocol evolution**: MCP is actively maintained; improvements to the protocol
  benefit all implementations

### Negative

- **MCP protocol dependency**: The standard is coupled to MCP's protocol evolution.
  Breaking changes in MCP would require specification updates
- **Limited streaming support**: MCP's request-response model does not natively
  support high-frequency telemetry streaming (identified as known gap KG-1.2)
- **Nascent ecosystem**: MCP is younger than established healthcare interoperability
  protocols. Tooling and community may not yet match HL7/FHIR maturity
- **Transport abstraction**: MCP abstracts transport, which means the standard
  cannot specify transport-level security requirements (identified as non-goal NG-2.4)

### Risks

- **Protocol abandonment**: If MCP development ceases, the standard would need to
  migrate to an alternative protocol. Mitigation: the tool contract abstraction layer
  is protocol-independent; contracts could be mapped to another protocol with moderate
  effort
- **Performance constraints**: MCP's overhead may be unsuitable for sub-millisecond
  robot control loops. Mitigation: the standard explicitly excludes robot control
  algorithms from scope; MCP is used for clinical system integration, not real-time
  control

---

## Alternatives Rejected

### Custom REST API

Rejected because it would create a novel standard with no existing ecosystem, no SDK
support, and no community. The implementation burden on vendors would be significantly
higher, and conformance testing would require building all tooling from scratch.

### gRPC with Protocol Buffers

Rejected because gRPC's code generation model adds unnecessary complexity to the
conformance process, and its service-oriented design does not align with AI agent
tool discovery patterns. Additionally, Protocol Buffer schema evolution rules would
constrain the standard's ability to add optional fields in minor versions.

### HL7 FHIR Messaging

Rejected as the sole protocol boundary because FHIR Messaging lacks semantics for
authorization management, audit chain operations, provenance tracking, and DICOM
integration. FHIR R4 is used as the data model within the `trialmcp-fhir` server
but is not suitable as the overarching protocol boundary.

### Hybrid Approach (MCP + FHIR Messaging + DICOM WADO-RS)

Rejected because multiple protocol boundaries would fragment the conformance surface
area, increase implementation complexity, and create ambiguity about which protocol
to use for cross-cutting concerns (authorization, audit). A single protocol boundary
with domain-specific servers provides cleaner architecture.

---

## References

- MCP Specification: https://modelcontextprotocol.io
- `spec/core.md` Section 1 (Protocol Scope)
- `spec/tool-contracts.md` (23 tool contracts)
- `governance/CHARTER.md` Section 2 (Mission: vendor-neutral standard)
