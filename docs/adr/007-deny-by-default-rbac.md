# ADR-007: Deny-by-Default RBAC for Clinical Safety

**Status**: Accepted
**Date**: 2026-02-05
**Decision Makers**: Security Working Group
**Tracking**: DL-004 in `docs/governance/decision-log.md`

---

## Context

The national standard governs access control for autonomous Physical AI systems
operating in clinical environments. These systems include surgical robots, therapeutic
positioning systems, and diagnostic platforms that interact with patient data, medical
imaging, and clinical workflows.

The access control model must address several unique challenges:

### Autonomous Agent Risk

Robot agents operate with varying degrees of autonomy. Unlike human operators who
can exercise judgment about data access appropriateness, robot agents will access
exactly what their programming requests. An overly permissive access control model
could allow a robot agent to access patient data, imaging studies, or audit records
beyond what is required for its assigned clinical task.

### Safety-Critical Environment

Unauthorized access in oncology clinical trials has direct patient safety implications:

- A robot agent accessing incorrect imaging data could guide a procedure to the
  wrong anatomical location
- Unauthorized modification of audit records could mask adverse events
- Cross-role data access could violate patient consent boundaries
- Unauthorized cross-site data access could violate institutional data governance
  agreements

### Regulatory Requirements

- **HIPAA Security Rule** (45 CFR 164.312(a)(1)): Requires access controls that
  restrict access to electronic protected health information (ePHI) to authorized
  users and processes
- **21 CFR Part 11** (Section 11.10(d)): Requires "limiting system access to
  authorized individuals"
- **HIPAA Minimum Necessary Rule** (45 CFR 164.502(b)): Requires that access be
  limited to the minimum necessary to accomplish the intended purpose

### Six Actor Roles

The standard defines six actor roles with distinct trust levels and operational
scopes:

| Role | Trust Level | Scope |
|------|------------|-------|
| `robot_agent` | Constrained | Specific tools for assigned clinical tasks |
| `trial_coordinator` | Elevated | Full access to clinical and imaging data at their site |
| `data_monitor` | Read-only | Query clinical and imaging data, no raw images |
| `auditor` | Audit-scoped | Ledger operations only |
| `sponsor` | Governance | Policy configuration, aggregate reporting |
| `cro` | Coordination | Cross-site aggregate access |

---

## Decision

Implement deny-by-default role-based access control (RBAC) with the following
properties:

1. **Default deny**: All access requests that do not match an explicit ALLOW rule
   are denied
2. **Explicit DENY precedence**: If any matching rule has effect DENY, the request
   is denied regardless of ALLOW rules
3. **Role-scoped tokens**: All access tokens are scoped to exactly one role
4. **Policy evaluation order**: DENY rules evaluated before ALLOW rules; no match
   results in DENY
5. **Wildcard support**: Server and tool fields support wildcard matching (`*`)
   for policy rules
6. **Minimum baseline**: 9 default policy rules defining the baseline permission
   matrix (cannot be weakened by site-specific rules)
7. **Extension rules**: Sites MAY add rules that further restrict access or grant
   access to vendor extension tools

### Policy Evaluation Algorithm

```
function evaluate(role, server, tool):
    matching_rules = find_all_rules(role, server, tool)

    if any rule in matching_rules has effect == DENY:
        return DENIED

    if any rule in matching_rules has effect == ALLOW:
        return ALLOWED

    return DENIED  # deny-by-default
```

---

## Rationale

### Fail-Safe Over Fail-Open

In safety-critical clinical environments, the cost of unauthorized access far
exceeds the cost of denied legitimate access:

- **Unauthorized access cost**: Patient safety risk, regulatory violation, data
  breach, trial integrity compromise
- **Denied legitimate access cost**: Temporary operational delay (resolved by
  contacting the trial coordinator or system administrator)

Deny-by-default ensures that configuration errors, missing rules, or system
failures result in denied access, not unauthorized access. This is the fail-safe
behavior appropriate for clinical environments.

### DENY Precedence Prevents Privilege Escalation

Explicit DENY rules taking precedence over ALLOW rules prevents privilege
escalation through rule accumulation. Even if a site administrator adds an
overly broad ALLOW rule (e.g., `robot_agent, *, *, ALLOW`), a DENY rule for
specific sensitive tools (e.g., `robot_agent, trialmcp-ledger, ledger_append,
DENY` for direct ledger writes) will still be enforced.

This means the security baseline can only be maintained or strengthened by
additional rules, never weakened.

### Role Scoping Enforces Least Privilege

Each token is scoped to exactly one role. An actor cannot hold a token that
grants permissions from multiple roles simultaneously. This enforces the
principle of least privilege:

- A `robot_agent` token cannot access `auditor`-only tools
- A `data_monitor` token cannot access `trial_coordinator`-only tools
- A `sponsor` token cannot access patient-level clinical data

### Baseline Policy Rules

The standard defines 9 baseline policy rules that constitute the minimum
permission matrix. These rules MUST be present in every conforming implementation
and MUST NOT be weakened by site-specific extensions:

| # | Role | Server | Tool | Effect |
|---|------|--------|------|--------|
| 1 | `robot_agent` | `trialmcp-fhir` | `*` | ALLOW |
| 2 | `robot_agent` | `trialmcp-dicom` | `*` | ALLOW |
| 3 | `trial_coordinator` | `*` | `*` | ALLOW |
| 4 | `data_monitor` | `trialmcp-fhir` | `*` | ALLOW |
| 5 | `data_monitor` | `trialmcp-dicom` | `dicom_query` | ALLOW |
| 6 | `data_monitor` | `trialmcp-dicom` | `dicom_study_metadata` | ALLOW |
| 7 | `auditor` | `trialmcp-ledger` | `*` | ALLOW |
| 8 | `auditor` | `trialmcp-provenance` | `*` | ALLOW |
| 9 | `robot_agent` | `trialmcp-authz` | `authz_validate_token` | ALLOW |

Note: `sponsor` and `cro` roles have governance-level access defined through
organizational policies that operate above the tool-level RBAC. Their access
patterns are policy-configured rather than baseline-defined.

### Audit of Authorization Decisions

Every authorization evaluation is recorded in the audit ledger via `authz_evaluate`.
This creates a complete record of all access attempts (both granted and denied),
satisfying HIPAA Security Rule requirements for access monitoring and
21 CFR Part 11 requirements for access logging.

---

## Consequences

### Positive

- **Fail-safe behavior**: Configuration errors result in denied access, not
  unauthorized access
- **Privilege escalation prevention**: DENY precedence prevents rule accumulation
  attacks
- **Regulatory compliance**: Directly satisfies HIPAA Security Rule, HIPAA Minimum
  Necessary Rule, and 21 CFR Part 11 access control requirements
- **Clear permission model**: The role-tool permission matrix is explicit and
  auditable
- **Site extensibility**: Sites can add restrictions without weakening the baseline
- **Autonomous agent safety**: Robot agents are constrained to their assigned
  operational scope

### Negative

- **Operational friction**: Deny-by-default may initially cause legitimate access
  denials during deployment, requiring careful policy configuration
- **Policy debugging complexity**: When access is denied, determining which missing
  rule caused the denial requires examining the policy set and the evaluation
  algorithm
- **No dynamic permissions**: Role permissions are statically defined. There is
  no mechanism for temporary permission elevation (e.g., emergency access) in v0.1.0
- **Organizational role limitations**: `sponsor` and `cro` roles have coarse-grained
  access patterns that may not fit all organizational structures

### Mitigations

- `authz_evaluate` returns `matching_rules` in its response, enabling policy
  debugging by showing which rules matched (or that no rules matched)
- `authz_list_policies` allows administrators to inspect the active policy set
- Deployment guides include policy configuration checklists for each conformance
  level
- Emergency access procedures are planned for v0.2.0 with mandatory post-hoc
  audit review

---

## Alternatives Rejected

### Allow-by-Default with Explicit Deny

Default to allowing access, with explicit DENY rules for restricted operations.
Rejected because:
- Fails unsafe: configuration errors or missing rules result in unauthorized access
- Incompatible with HIPAA Minimum Necessary Rule
- Particularly dangerous with autonomous robot agents that will access whatever
  is permitted

### Attribute-Based Access Control (ABAC)

Access decisions based on attributes of the subject, resource, action, and
environment. Rejected for v0.1.0 because:
- ABAC is more expressive but significantly more complex to implement, test,
  and audit
- Role-based access is sufficient for the six-actor model in v0.1.0
- ABAC may be introduced in a future version if the actor model requires
  finer-grained access decisions

### Capability-Based Access Control

Distributing unforgeable capability tokens that grant specific permissions.
Rejected because:
- Capability tokens are harder to revoke than role-based tokens
- Capability delegation (one agent passing its capability to another) creates
  uncontrolled permission propagation
- Regulatory auditors expect role-based access models

### OAuth 2.0 Scopes

Using OAuth 2.0 scope strings to define permissions. Rejected as the primary
mechanism because:
- OAuth scopes are string-based and lack the structured evaluation logic
  (DENY precedence, wildcard matching) required for clinical safety
- OAuth 2.0 is primarily an authorization framework for web applications,
  not for autonomous agent access control in clinical environments
- Token issuance and validation in the standard are simpler than full OAuth 2.0
  and do not require external identity providers

---

## References

- HIPAA Security Rule (45 CFR 164.312)
- HIPAA Minimum Necessary Rule (45 CFR 164.502(b))
- 21 CFR Part 11 Section 11.10(d) (Limiting System Access)
- `spec/security.md` Section 2 (Authorization Model)
- `spec/actor-model.md` (Actor definitions and trust levels)
- `spec/tool-contracts.md` Section 3 (AuthZ tools)
