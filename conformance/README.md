# Conformance Test Suite

**National MCP-PAI Oncology Trials Standard — Conformance Test Harness**

This directory contains the conformance test suite for validating implementations of the [National MCP-PAI Oncology Trials Standard](../README.md). The test harness verifies that MCP server deployments satisfy the normative requirements defined across the five conformance levels, eight profiles, and thirteen machine-readable JSON schemas.

---

## Overview

The conformance test suite is organized into four categories that together validate every MUST, SHOULD, and MAY requirement in the specification:

| Category | Directory | Purpose |
|----------|-----------|---------|
| **Positive** | `positive/` | Validates correct behavior: audit production, error envelopes, health checks, authorization, FHIR/DICOM conformance, and imaging requirements |
| **Negative** | `negative/` | Validates rejection of invalid inputs: malformed requests, schema mismatches, and unauthorized access attempts under deny-by-default RBAC |
| **Security** | `security/` | Validates security controls: SSRF prevention, token lifecycle management (expiry and revocation), and hash chain integrity |
| **Interoperability** | `interoperability/` | Validates multi-server coordination: cross-server audit trace linkage and schema validation of all outputs against `/schemas/` |

### Test File Inventory

```
conformance/
├── README.md                                     # This file
├── conftest.py                                   # Shared fixtures, schema validation helpers
├── fixtures/                                     # Test fixture data (extracted from schemas)
│   ├── __init__.py
│   ├── audit_records.py                          # Sample audit records and chains
│   ├── authz_decisions.py                        # Sample authorization decisions
│   ├── clinical_resources.py                     # Sample FHIR and DICOM resources
│   └── provenance_records.py                     # Sample provenance DAG records
├── positive/
│   ├── __init__.py
│   ├── test_core_conformance.py                  # Audit, error envelope, health, authz (Level 1)
│   ├── test_clinical_read_conformance.py         # FHIR + de-identification (Level 2)
│   └── test_imaging_conformance.py               # DICOM conformance (Level 3)
├── negative/
│   ├── __init__.py
│   ├── test_invalid_inputs.py                    # Malformed requests, schema mismatches
│   └── test_unauthorized_access.py               # Deny-by-default enforcement
├── security/
│   ├── __init__.py
│   ├── test_ssrf_prevention.py                   # URL injection prevention
│   ├── test_token_lifecycle.py                   # Token expiry and revocation
│   └── test_chain_integrity.py                   # Hash chain tampering detection
└── interoperability/
    ├── __init__.py
    ├── test_cross_server_trace.py                # Multi-server audit linkage
    └── test_schema_validation.py                 # All outputs validated against /schemas/
```

---

## How to Run

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Install test dependencies:

```bash
pip install pytest jsonschema
```

### Run All Conformance Tests

```bash
pytest conformance/ -v
```

### Run by Category

```bash
# Positive conformance tests
pytest conformance/positive/ -v

# Negative conformance tests
pytest conformance/negative/ -v

# Security conformance tests
pytest conformance/security/ -v

# Interoperability conformance tests
pytest conformance/interoperability/ -v
```

### Run by Conformance Level

```bash
# Level 1 — Core (authz + audit)
pytest conformance/positive/test_core_conformance.py -v

# Level 2 — Clinical Read (FHIR + de-identification)
pytest conformance/positive/test_clinical_read_conformance.py -v

# Level 3 — Imaging (DICOM)
pytest conformance/positive/test_imaging_conformance.py -v
```

### Run with Markers

```bash
# Run only security tests
pytest conformance/ -m security -v

# Run only interoperability tests
pytest conformance/ -m interoperability -v
```

---

## How to Add Tests

### Adding a New Conformance Test

1. Identify the appropriate category (`positive/`, `negative/`, `security/`, or `interoperability/`)
2. Create or extend a test file following the naming convention `test_<feature>_<category>.py`
3. Import shared fixtures from `conftest.py` and fixture data from `fixtures/`
4. Use the `validate_against_schema()` helper for JSON Schema validation
5. Tag tests with appropriate pytest markers (`@pytest.mark.security`, etc.)

### Adding New Fixtures

1. Add fixture data to the appropriate module in `fixtures/`
2. Register any new pytest fixtures in `conftest.py`
3. Ensure fixture data conforms to the schemas in `/schemas/`

### Conformance Level Mapping

Each test maps to a conformance level requirement:

| Conformance Level | Profile | Test Files |
|-------------------|---------|------------|
| Level 1 — Core | [Base Profile](../profiles/base-profile.md) | `test_core_conformance.py`, `test_invalid_inputs.py`, `test_unauthorized_access.py`, `test_chain_integrity.py` |
| Level 2 — Clinical Read | [Clinical Read](../profiles/clinical-read.md) | `test_clinical_read_conformance.py` |
| Level 3 — Imaging | [Imaging-Guided](../profiles/imaging-guided-oncology.md) | `test_imaging_conformance.py` |
| Level 4 — Federated | [Multi-Site Federated](../profiles/multi-site-federated.md) | `test_cross_server_trace.py`, `test_schema_validation.py` |
| Level 5 — Robot | [Robot-Assisted](../profiles/robot-assisted-procedure.md) | All tests combined |
| Security | All Profiles | `test_ssrf_prevention.py`, `test_token_lifecycle.py`, `test_chain_integrity.py` |

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

### Related Repositories

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation (single-site proof of concept)
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework with USL scoring and patient instructions
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework with privacy and regulatory modules
