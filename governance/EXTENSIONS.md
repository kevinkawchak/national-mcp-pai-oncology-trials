# Extensions Policy

**National MCP-PAI Oncology Trials Standard — Extensions Policy**
**Version**: 0.1.0

---

## 1. Overview

This document defines the policy for vendor and community extensions to the national MCP-PAI oncology trials standard. Extensions allow implementers to add functionality beyond the normative specification without breaking interoperability.

---

## 2. Extension Namespace

### 2.1 Format

All extensions MUST use the `x-{vendor}` namespace prefix where `{vendor}` is a unique identifier for the extending organization:

- **Tool names**: `x-acme_custom_tool`
- **Parameter names**: `x-acme_custom_param`
- **Error codes**: `X_ACME_CUSTOM_ERROR`
- **Metadata keys**: `x-acme_config_key`

### 2.2 Vendor Identifier Rules

- Vendor identifiers MUST be lowercase alphanumeric with optional hyphens
- Vendor identifiers MUST be at least 3 characters
- Vendor identifiers MUST NOT conflict with existing registered vendors
- Vendor identifiers SHOULD be recognizable abbreviations of the organization name

### 2.3 Reserved Prefixes

The following prefixes are reserved and MUST NOT be used by vendors:
- `x-std_` — reserved for future standard use
- `x-test_` — reserved for conformance testing
- `x-draft_` — reserved for specification drafts

---

## 3. Extension Requirements

### 3.1 MUST Requirements

Extensions MUST:
- Use the `x-{vendor}` namespace prefix
- Not conflict with standard tool names, parameters, or error codes
- Not modify the behavior of standard tools
- Be documented with input parameters, output shape, and error codes
- Follow the same input validation rules as standard tools (FHIR ID format, DICOM UID format, SSRF prevention)

### 3.2 SHOULD Requirements

Extensions SHOULD:
- Generate audit records in the standard ledger format
- Use standard error codes where applicable
- Be registered with the governance body
- Include conformance level alignment (which level the extension builds upon)

### 3.3 MAY Requirements

Extensions MAY:
- Define new error codes (with `X_` prefix)
- Define new actor roles
- Define new conformance sub-levels
- Include additional security requirements beyond the standard baseline

---

## 4. Extension Registration

### 4.1 Registration Process

1. Submit a registration request via the [spec_change issue template](../.github/ISSUE_TEMPLATE/spec_change.md)
2. Include: vendor identifier, extension name, description, and documentation link
3. Governance body reviews for namespace conflicts within 14 days
4. Upon approval, vendor identifier is added to the registry

### 4.2 Registry Contents

The extension registry contains:
- Vendor identifier
- Organization name and contact
- List of registered extensions
- Documentation links
- Registration date

---

## 5. Extension Promotion

### 5.1 Criteria

An extension MAY be promoted to the standard when:
- It has been adopted by at least three independent implementations
- It addresses a common need across the national deployment
- It is compatible with all existing standard requirements
- The extending vendor agrees to transfer governance to the standard body

### 5.2 Promotion Process

1. Promotion proposal submitted through the standard decision process
2. Community review period (30 days for new standard tools)
3. Namespace migration plan (from `x-{vendor}` to standard namespace)
4. All maintainer approvals required
5. Extension becomes part of the next MINOR version release

---

## 6. Extension Deprecation

If an extension conflicts with a future standard requirement:
1. The governance body notifies the vendor
2. Vendor has 90 days to propose a resolution
3. If unresolved, the extension MUST be renamed to avoid conflict
4. Existing deployments using the extension SHOULD migrate within one MAJOR version cycle
