# Standards Community Contribution Guide

**National MCP-PAI Oncology Trials Standard**
**Audience**: Implementers, Standards Body Members, Open-Source Contributors, Interoperability Engineers
**Version**: 0.1.0

---

## 1. Introduction

This guide describes how individuals and organizations can contribute to the evolution
of the National MCP-PAI Oncology Trials Standard. It covers the extension proposal
process, compatibility and versioning policies, schema evolution rules, the
contribution workflow for specification changes, and the review and approval process.

The standard is governed by the processes defined in:
- `governance/CHARTER.md` -- organizational charter
- `governance/DECISION_PROCESS.md` -- change decision procedures
- `governance/EXTENSIONS.md` -- vendor extension policies
- `governance/VERSION_COMPATIBILITY.md` -- version compatibility rules
- `governance/CODEOWNERS` -- maintainer assignments

---

## 2. Extension Proposal Process

### 2.1 Extension Namespace (x-{vendor})

All extensions MUST use the `x-{vendor}` namespace prefix as defined in
`governance/EXTENSIONS.md`. This prevents collisions between vendor-specific
additions and the normative standard.

**Namespace format:**

| Extension Type | Format | Example |
|---------------|--------|---------|
| Tool names | `x-{vendor}_tool_name` | `x-acme_haptic_calibration` |
| Parameter names | `x-{vendor}_param_name` | `x-acme_force_profile` |
| Error codes | `X_{VENDOR}_ERROR_NAME` | `X_ACME_CALIBRATION_FAILED` |
| Metadata keys | `x-{vendor}_config_key` | `x-acme_sensor_config` |

### 2.2 Vendor Identifier Rules

| Rule | Requirement |
|------|-------------|
| Character set | Lowercase alphanumeric with optional hyphens |
| Minimum length | 3 characters |
| Uniqueness | MUST NOT conflict with existing registered vendors |
| Recognizability | SHOULD be a recognizable abbreviation of the organization |

### 2.3 Reserved Prefixes

The following prefixes are reserved and MUST NOT be used by vendors:

| Prefix | Reserved For |
|--------|-------------|
| `x-std_` | Future standard use |
| `x-test_` | Conformance testing |
| `x-draft_` | Specification drafts |

### 2.4 Extension Registration Process

1. Submit a registration request via the spec change issue template
   (`.github/ISSUE_TEMPLATE/spec_change.md`)
2. Include in the request:
   - Vendor identifier (proposed)
   - Extension name and description
   - Documentation link or inline documentation
   - Conformance level alignment (which level the extension builds upon)
3. Governance body reviews for namespace conflicts within 14 days
4. Upon approval, vendor identifier is added to the registry

### 2.5 Extension Requirements

Extensions MUST:
- Use the `x-{vendor}` namespace prefix
- Not conflict with standard tool names, parameters, or error codes
- Not modify the behavior of standard tools
- Be documented with input parameters, output shape, and error codes
- Follow the same input validation rules as standard tools (FHIR ID format,
  DICOM UID format, SSRF prevention per `servers/common/validation.py`)

Extensions SHOULD:
- Generate audit records in the standard ledger format
- Use standard error codes where applicable
- Be registered with the governance body
- Include conformance level alignment

Extensions MAY:
- Define new error codes (with `X_` prefix)
- Define new actor roles
- Define new conformance sub-levels
- Include additional security requirements beyond the baseline

### 2.6 Extension Capability Descriptor

Extensions MUST be declared in the server's capability descriptor
(`schemas/capability-descriptor.schema.json`) using the `vendor_extensions` array:

```json
{
  "server_name": "trialmcp-dicom",
  "version": "1.2.0",
  "conformance_level": 3,
  "tools": ["dicom_query", "dicom_retrieve_pointer", "dicom_study_metadata", "dicom_recist_measurements"],
  "vendor_extensions": [
    "x-acme-haptic_calibration",
    "x-acme-force_profile_query"
  ],
  "regulatory_certifications": ["21_CFR_Part_11", "HIPAA", "IEC_80601"]
}
```

The `vendor_extensions` array items MUST match the pattern `^x-[a-z][a-z0-9]*-`.

---

## 3. Compatibility Policy and Versioning Rules

### 3.1 Semantic Versioning

The standard follows Semantic Versioning (SemVer). The current version is declared in
each specification document and in the capability descriptor schema.

| Component | Meaning | Example |
|-----------|---------|---------|
| MAJOR | Breaking changes | 1.0.0 -> 2.0.0 |
| MINOR | Additive, backward-compatible | 1.0.0 -> 1.1.0 |
| PATCH | Bug fixes, editorial | 1.0.0 -> 1.0.1 |

### 3.2 Compatibility Matrix

Per `governance/VERSION_COMPATIBILITY.md`:

| Relationship | Requirement |
|-------------|-------------|
| Server-to-server (same site) | MUST be same MAJOR version |
| Client-to-server | Client version X.Y MUST work with server version X.Z where Z >= Y |
| Cross-site (federated trial) | MUST be same MAJOR version; SHOULD be same MINOR version |
| MINOR version differences within site | Acceptable if lowest version satisfies declared conformance level |

### 3.3 Upgrade Policy

| Upgrade Type | Impact | Timeline | Requirements |
|-------------|--------|----------|-------------|
| PATCH | No implementation changes | Apply freely | No testing required |
| MINOR | New tools/parameters possible | 6 months to adopt | Conformance testing |
| MAJOR | Breaking changes possible | 12 months to migrate | Migration guide, full revalidation |

### 3.4 Multi-Version Support

During MAJOR version transitions:

| Phase | Duration | Status |
|-------|----------|--------|
| Active | Until next MAJOR release | Full support, new features |
| Maintenance | 12 months after next MAJOR release | Security patches only |
| End of Life | After maintenance period | No support |

### 3.5 Version Discovery

Servers MUST expose version information in health check responses per
`schemas/health-status.schema.json`. Clients SHOULD verify version compatibility
before making tool calls.

---

## 4. Schema Evolution Rules

### 4.1 Schema Governance

All message schemas are maintained in `schemas/` as JSON Schema (draft 2020-12) files.
The 13 normative schemas define the data contracts for the entire system.

### 4.2 Additive Changes (MINOR)

Additive changes are backward-compatible modifications that extend schemas without
breaking existing implementations.

**Permitted additive changes:**

| Change Type | Example | Backward Compatible |
|------------|---------|:-------------------:|
| New optional property | Add `x-acme_custom` to task order | Yes |
| New enum value | Add `cryo_ablation` to `procedure_type` | Yes |
| Relaxing a constraint | Increase `maximum` from 10 to 20 | Yes |
| New schema file | Add `robot-telemetry.schema.json` | Yes |

**Process for additive changes:**

1. Submit a spec change proposal with the `minor` label
2. Include before/after schema diff (use `tools/certification/schema_diff.py`)
3. Demonstrate backward compatibility by running existing conformance tests
   against the updated schema
4. 14-day community review period
5. Two maintainer approvals required

### 4.3 Breaking Changes (MAJOR)

Breaking changes modify existing contracts in ways that may require implementation updates.

**Examples of breaking changes:**

| Change Type | Example | Impact |
|------------|---------|--------|
| Remove required property | Remove `site_id` from task order | Existing implementations break |
| Change property type | Change `usl_score` from number to string | Existing implementations break |
| Add required property | Add new required field to audit record | Existing implementations break |
| Restrict enum values | Remove `patient_monitoring` from procedure_type | Existing implementations break |
| Tighten constraint | Reduce maximum from 100 to 50 | Some implementations break |

**Process for breaking changes:**

1. Submit a spec change proposal with the `breaking` label
2. Include migration guide
3. Include implementation impact assessment
4. 30-day community review period
5. All maintainer approvals required
6. 12-month migration period for existing implementations
7. Previous version receives security patches for 12 months

### 4.4 Deprecation Lifecycle

When a schema field, tool, or feature is being phased out:

| Stage | Duration | Action |
|-------|----------|--------|
| Deprecation notice | Announced in MINOR release | Mark as deprecated in schema and spec |
| Deprecation period | Minimum 2 MINOR releases or 12 months | Implementations warned but not broken |
| Removal | Next MAJOR release | Field/tool removed from schema and spec |

**Deprecation markers in schemas:**

```json
{
  "old_field_name": {
    "type": "string",
    "description": "DEPRECATED (since 1.2.0): Use new_field_name instead. Will be removed in 2.0.0.",
    "deprecated": true
  }
}
```

### 4.5 Schema Diff Tool

Use the schema diff tool to analyze changes between versions:

```bash
python tools/certification/schema_diff.py \
  --old schemas/task-order.schema.json@v1.0.0 \
  --new schemas/task-order.schema.json@v1.1.0
```

The diff tool identifies:
- Added properties (backward compatible)
- Removed properties (breaking)
- Type changes (breaking)
- Constraint changes (may be breaking)
- Enum value changes (adding is compatible; removing is breaking)

---

## 5. Contribution Workflow for Specification Changes

### 5.1 Issue Templates

All contributions begin with an issue in the repository:

| Template | Path | Use Case |
|----------|------|----------|
| Feature request | `.github/ISSUE_TEMPLATE/feature_request.md` | New capabilities |
| Specification change | `.github/ISSUE_TEMPLATE/spec_change.md` | Normative text changes |
| Bug report | `.github/ISSUE_TEMPLATE/bug_report.md` | Defects in spec or reference implementation |

### 5.2 Proposal Format

Per `governance/DECISION_PROCESS.md`, all specification change proposals MUST include:

1. **Summary**: One-paragraph description of the change
2. **Motivation**: Why the change is needed
3. **Specification**: The exact normative text to add, modify, or remove
4. **Conformance Impact**: Which conformance levels are affected
5. **Backward Compatibility**: Whether the change is backward-compatible
6. **Implementation Impact**: Estimated effort for existing implementations
7. **Regulatory Impact**: Whether regulatory overlays need updating

### 5.3 Contribution Steps

```
  1. Open Issue          2. Draft Proposal        3. Submit PR
  (feature_request.md    (spec text, schema       (code + spec +
   or spec_change.md)     changes, tests)          tests)
       |                      |                      |
       v                      v                      v
  4. Community Review    5. Maintainer Review     6. Merge
  (14 or 30 days per    (approvals per           (after review
   change category)      category)                period closes)
```

**Detailed steps:**

1. **Open an issue** using the appropriate template
2. **Draft the proposal** following the format in Section 5.2
3. **Implement changes** (if applicable):
   - Specification text in `spec/`
   - Schema changes in `schemas/`
   - Profile updates in `profiles/`
   - Reference implementation updates in `reference/`
   - Conformance tests in `conformance/`
4. **Submit a pull request** using the PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
5. **Community review period** begins (14 days for minor, 30 days for major)
6. **Address feedback** from reviewers
7. **Obtain required approvals** (1 for editorial, 2 for minor, all for major)
8. **Merge** after review period closes and approvals received

### 5.4 What to Include in a Pull Request

| Component | Required For | Location |
|-----------|-------------|----------|
| Specification text changes | All spec changes | `spec/*.md` |
| Schema updates | Tool contract or data model changes | `schemas/*.schema.json` |
| Profile updates | Conformance or regulatory changes | `profiles/*.md` |
| Conformance tests | All normative changes | `conformance/` |
| Reference implementation | Tool contract changes | `reference/python/`, `reference/typescript/` |
| Generated model updates | Schema changes | `models/python/`, `models/typescript/` |
| Changelog entry | All changes | `changelog.md` |
| Migration guide | Breaking changes | PR description |

### 5.5 Testing Requirements for Contributions

All contributions that modify normative requirements MUST include:

```bash
# Run existing conformance tests to verify no regressions
pytest conformance/ -v

# Run schema validation
python reference/python/schema_validator.py

# Run unit tests
pytest tests/ -v

# For reference implementation changes, run TypeScript tests
cd reference/typescript && npm test
```

---

## 6. Review and Approval Process

### 6.1 Review Criteria

Reviewers evaluate contributions against the following criteria:

| Criterion | Description |
|-----------|-------------|
| Correctness | Does the change accurately implement the intended behavior? |
| Completeness | Are all affected documents, schemas, and tests updated? |
| Backward compatibility | Is the change backward-compatible (if claimed)? |
| Regulatory alignment | Does the change maintain compliance with regulatory overlays? |
| Interoperability | Does the change affect cross-implementation compatibility? |
| Security | Does the change maintain or improve the security posture? |
| Clarity | Is the normative text clear and unambiguous? |
| Test coverage | Are conformance tests adequate for the change? |

### 6.2 Approval Requirements by Category

| Category | Review Period | Required Approvals | Objection Policy |
|----------|--------------|-------------------|------------------|
| Editorial (Patch) | 7 days | 1 maintainer | Merge if no objections |
| Minor Enhancement | 14 days minimum | 2 maintainers | No unresolved maintainer objections |
| Breaking Change (Major) | 30 days minimum | All maintainers | Must include migration guide |

### 6.3 Objection Resolution

If a maintainer raises an objection during review:

1. The objection MUST be documented in the PR discussion
2. The contributor MUST address the objection or provide a rebuttal
3. If consensus cannot be reached, escalate per `governance/DECISION_PROCESS.md`
4. The governance body makes a final determination per `governance/CHARTER.md`

### 6.4 CI Pipeline

The repository CI pipeline (`.github/workflows/ci.yml`) automatically validates:

- Schema validation passes
- Conformance tests pass
- Unit tests pass
- Reference implementation tests pass (Python and TypeScript)
- No regressions in existing tests

PRs MUST pass CI before merging.

---

## 7. Repository Structure Reference

For contributors, the repository is organized as follows:

```
national-mcp-pai-oncology-trials/
  spec/                          # Normative specification documents
    core.md                      # Core architecture specification
    tool-contracts.md            # 23 tool contracts across 5 servers
    actor-model.md               # 6 actor roles and permission matrix
    conformance.md               # 5 conformance levels
    security.md                  # Security requirements
    privacy.md                   # Privacy and de-identification
    audit.md                     # Audit trail requirements
    provenance.md                # Data lineage requirements
    versioning.md                # Versioning specification
  schemas/                       # 13 JSON Schema (draft 2020-12) files
  profiles/                      # 5 conformance + 3 regulatory overlay profiles
  governance/                    # Charter, decision process, extensions, compatibility
  regulatory/                    # FDA, HIPAA, CFR Part 11, IRB templates
  servers/                       # Server implementations (5 servers + common + storage)
  safety/                        # Safety modules (gate, registry, validator, etc.)
  integrations/                  # External system adapters (FHIR, DICOM, identity, etc.)
  conformance/                   # Conformance test suite
  reference/                     # Reference implementations (Python + TypeScript)
  tools/                         # Certification and utility tools
  interop-testbed/               # Multi-vendor interoperability testing
  examples/                      # Quickstart and demo materials
  benchmarks/                    # Performance benchmark suite
  deploy/                        # Docker, Kubernetes, Helm deployment configs
  models/                        # Generated model classes (Python + TypeScript)
  docs/                          # Architecture, process docs, glossary, guides
  tests/                         # Unit and integration tests
```

---

## 8. Governance Bodies and Communication

### 8.1 Roles

| Role | Responsibility | Reference |
|------|---------------|-----------|
| Maintainer | Review and merge contributions; enforce standards | `governance/CODEOWNERS` |
| Contributor | Propose changes, submit PRs, participate in reviews | Open to all |
| Governance body | Resolve disputes, approve major changes | `governance/CHARTER.md` |

### 8.2 Communication Channels

| Channel | Purpose |
|---------|---------|
| GitHub Issues | Feature requests, bug reports, spec change proposals |
| GitHub Pull Requests | Code and specification reviews |
| GitHub Discussions | General questions, design discussions |
| Peer review | Formal specification review (`peer-review/`) |

### 8.3 Code of Conduct

All participants MUST adhere to the project Code of Conduct (`CODE_OF_CONDUCT.md`).

---

## 9. Promoting Extensions to Standard

### 9.1 Promotion Criteria

A vendor extension MAY be proposed for promotion to the normative standard when:

1. Multiple independent implementations exist
2. The extension addresses a broadly applicable use case
3. Interoperability testing demonstrates cross-vendor compatibility
4. No patent or licensing encumbrances
5. Community consensus supports standardization

### 9.2 Promotion Process

1. Submit a spec change proposal (minor or major, depending on scope)
2. Remove the `x-{vendor}` prefix and assign a standard name
3. Add the tool/parameter/error code to the appropriate normative document
4. Update conformance tests
5. Update the permission matrix in `spec/actor-model.md`
6. Follow the standard review and approval process (Section 6)

### 9.3 Interoperability Validation

Before promotion, the proposed standard tool must pass:

- Cross-server trace tests (`conformance/interoperability/test_cross_server_trace.py`)
- Schema validation tests (`conformance/interoperability/test_schema_validation.py`)
- Multi-vendor testing in the interop testbed (`interop-testbed/`)
- Schema drift scenario (`interop-testbed/scenarios/schema_drift.py`)

---

## 10. Contributor Checklist

- [ ] Read `governance/CHARTER.md` and `governance/DECISION_PROCESS.md`
- [ ] Review `governance/EXTENSIONS.md` if proposing an extension
- [ ] Review `governance/VERSION_COMPATIBILITY.md` for versioning rules
- [ ] Open an issue using the appropriate template
- [ ] Draft proposal with all seven required sections (Section 5.2)
- [ ] Implement changes with conformance tests
- [ ] Run CI locally before submitting PR
- [ ] Submit PR using the PR template
- [ ] Respond to reviewer feedback during review period
- [ ] Await required approvals per change category
- [ ] Update changelog (`changelog.md`) with change description
