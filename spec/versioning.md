# Versioning Specification

**National MCP-PAI Oncology Trials Standard — spec/versioning.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the versioning policy for the national MCP-PAI oncology trials standard. The standard uses Semantic Versioning (SemVer 2.0.0) for specification releases and defines compatibility rules, extension namespaces, and deprecation procedures.

---

## 2. Semantic Versioning

### 2.1 Version Format

The standard version follows the format `MAJOR.MINOR.PATCH`:

- **MAJOR**: Incremented for backward-incompatible changes to tool contracts, actor model, or security requirements
- **MINOR**: Incremented for backward-compatible additions (new tools, new conformance requirements, new optional features)
- **PATCH**: Incremented for clarifications, typo fixes, and editorial changes that do not alter normative requirements

### 2.2 Pre-release Versions

Pre-release versions MAY use the format `MAJOR.MINOR.PATCH-label` (e.g., `0.2.0-draft`). Pre-release versions are not considered stable and MUST NOT be used for production conformance claims.

---

## 3. Compatibility Policy

### 3.1 Backward Compatibility

- MINOR version increments MUST NOT remove existing tools, parameters, or error codes
- MINOR version increments MUST NOT change the meaning of existing MUST requirements
- MINOR version increments MAY add new tools, parameters (with defaults), or error codes
- MINOR version increments MAY promote SHOULD requirements to MUST

### 3.2 Breaking Changes

- Only MAJOR version increments MAY introduce breaking changes
- Breaking changes MUST be documented in a migration guide
- Implementations conforming to version N.x.x SHOULD be given at least 12 months to migrate to version (N+1).0.0

### 3.3 Implementation Version Matching

- An implementation declaring conformance to version X.Y.Z MUST satisfy all MUST requirements of that version
- An implementation MAY conform to a MINOR version higher than the one it was originally validated against, provided it satisfies any new MUST requirements added in the later version
- Implementations MUST NOT claim conformance to a version they have not been validated against

---

## 4. Extension Namespace

### 4.1 Vendor Extensions

Vendors MAY extend the standard with custom tools, parameters, or metadata using the `x-{vendor}` namespace prefix:

- Tool names: `x-acme_custom_analysis`
- Parameter names: `x-acme_priority`
- Metadata keys: `x-acme_site_config`

### 4.2 Extension Rules

- Extensions MUST NOT conflict with standard tool names or parameter names
- Extensions MUST NOT modify the behavior of standard tools
- Extensions MUST be documented by the vendor
- Extensions SHOULD follow the same input validation and audit requirements as standard tools
- Extension tools SHOULD generate audit records in the standard ledger format

### 4.3 Extension Registration

Vendors SHOULD register their extension namespace with the governance body to avoid conflicts. Registration is not required but is strongly RECOMMENDED for interoperability.

### 4.4 Extension Promotion

Community-adopted extensions MAY be promoted to the standard in a future MINOR version. Promotion requires:
- Demonstrated adoption across multiple implementations
- Community review through the specification change process
- Compatibility with existing standard requirements

---

## 5. Deprecation

### 5.1 Deprecation Process

When a tool, parameter, or requirement is scheduled for removal:

1. **Deprecation Notice**: The MINOR version introduces the deprecation notice with a `deprecated` flag and a recommended replacement
2. **Grace Period**: The deprecated feature MUST remain functional for at least one additional MINOR version
3. **Removal**: The MAJOR version removes the deprecated feature

### 5.2 Deprecation Documentation

Deprecated features MUST be documented with:
- The version in which deprecation was announced
- The recommended replacement or migration path
- The earliest version in which removal may occur

---

## 6. Changelog Requirements

### 6.1 Format

Each version release MUST include a changelog entry with:
- Version number and release date
- Summary of changes categorized as: Added, Changed, Deprecated, Removed, Fixed, Security
- References to relevant specification change proposals

### 6.2 Migration Guides

MAJOR version releases MUST include a migration guide documenting:
- All breaking changes
- Required implementation modifications
- Timeline for migration
- Support availability for the previous major version
