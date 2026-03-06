# Adoption Roadmap

> **Version 0.5.0** | **Informative** | **National MCP-PAI Oncology Trials Standard**

This document describes the four-phase adoption roadmap for the
National MCP-PAI Oncology Trials Standard, guiding U.S. clinical sites,
sponsors, CROs, and technology vendors from specification review through
production-scale deployment of MCP servers for Physical AI oncology
clinical trials.

---

## Phase Overview

```
┌────────────────────────────────────────────────────────────────────┐
│              NATIONAL ADOPTION ROADMAP                              │
│                                                                     │
│  Phase 0        Phase 1         Phase 2          Phase 3           │
│  ┌─────────┐   ┌───────────┐   ┌────────────┐   ┌─────────────┐  │
│  │  SPEC   │──▶│ PROFILES  │──▶│CONFORMANCE │──▶│   PILOTS    │  │
│  │         │   │           │   │            │   │             │  │
│  │ Review  │   │ Select    │   │ Validate   │   │ Deploy at   │  │
│  │ spec,   │   │ profile,  │   │ against    │   │ pilot sites │  │
│  │ schemas │   │ overlays  │   │ test suite │   │ nationwide  │  │
│  └─────────┘   └───────────┘   └────────────┘   └─────────────┘  │
│                                                                     │
│  Duration:                                                          │
│  2–4 weeks      4–8 weeks       8–12 weeks       Ongoing           │
└────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0 — Specification Review

**Goal**: Understand the normative specification and identify the
conformance level appropriate for your deployment.

### Activities

1. **Review core specification** — Read [spec/core.md](../spec/core.md)
   for protocol scope, design principles, and the five conformance
   levels.
2. **Understand the actor model** — Review
   [spec/actor-model.md](../spec/actor-model.md) to identify which of
   the six actors your system implements.
3. **Study tool contracts** — Examine
   [spec/tool-contracts.md](../spec/tool-contracts.md) for the 23 tool
   signatures across five MCP servers.
4. **Review JSON schemas** — Inspect the 13 schemas in
   [schemas/](../schemas/) that define machine-readable data contracts.
5. **Assess regulatory requirements** — Determine applicable regulatory
   overlays from [regulatory/](../regulatory/) (FDA, HIPAA, 21 CFR
   Part 11, IRB).

### Deliverables

- Conformance level target (Level 1–5)
- List of applicable regulatory overlays
- Stakeholder alignment on scope

### Duration

2–4 weeks

---

## Phase 1 — Profile Selection and Planning

**Goal**: Select the conformance profile(s) and regulatory overlays
that apply to your deployment, and plan the implementation.

### Activities

1. **Select a conformance profile** — Choose from the five core
   profiles in [profiles/](../profiles/):
   - [Base Profile](../profiles/base-profile.md) — Level 1 (Core)
   - [Clinical Read](../profiles/clinical-read.md) — Level 2
   - [Imaging-Guided Oncology](../profiles/imaging-guided-oncology.md)
     — Level 3
   - [Multi-Site Federated](../profiles/multi-site-federated.md) —
     Level 4
   - [Robot-Assisted Procedure](../profiles/robot-assisted-procedure.md)
     — Level 5
2. **Apply regulatory overlays** — Stack applicable overlays:
   - [FDA 21 CFR Part 11](../profiles/country-us-fda.md) — All sites
   - [California CCPA](../profiles/state-us-ca.md) — CA sites
   - [New York Health Info](../profiles/state-us-ny.md) — NY sites
3. **Map tools to your infrastructure** — For each mandatory tool in
   the selected profile, identify the backend clinical system (EHR,
   PACS, etc.) that will provide the data.
4. **Plan security implementation** — Design token lifecycle, RBAC
   policy configuration, and SSRF prevention per
   [spec/security.md](../spec/security.md).

### Deliverables

- Profile selection document
- Tool-to-system mapping
- Security architecture design
- Implementation timeline

### Duration

4–8 weeks

---

## Phase 2 — Conformance Validation

**Goal**: Implement the selected profile and validate conformance
against the national test suite.

### Activities

1. **Implement MCP servers** — Build or configure the required MCP
   servers (1–5 depending on level) per the tool contracts.
2. **Integrate schema validation** — Use the 13 JSON schemas for
   automated input/output validation.  See
   [reference/python/schema_validator.py](../reference/python/schema_validator.py)
   and [reference/typescript/](../reference/typescript/) for examples.
3. **Run conformance tests** — Execute the 269-test conformance suite:
   ```bash
   pip install pytest jsonschema
   pytest conformance/ -v
   ```
   Or use the conformance runner:
   ```bash
   python -m reference.python.conformance_runner --level 3
   ```
4. **Address failures** — Fix any test failures and re-run until all
   tests for your target level pass.
5. **Security validation** — Run the security test subset:
   ```bash
   pytest conformance/security/ -v
   ```

### Deliverables

- Passing conformance test report for target level
- Security test results
- Schema validation logs

### Duration

8–12 weeks

---

## Phase 3 — Pilot Deployment

**Goal**: Deploy conforming MCP servers at pilot clinical sites and
validate in real-world operational conditions.

### Activities

1. **Select pilot sites** — Choose 2–5 clinical sites representing
   different regions and conformance levels.
2. **Deploy MCP servers** — Install the five-server topology at each
   pilot site per [docs/architecture.md](architecture.md).
3. **Integrate with clinical systems** — Connect MCP servers to site
   EHR (FHIR R4) and PACS (DICOM) systems.
4. **Connect Physical AI platforms** — Configure robot agents to use
   MCP servers for authorization, data access, and audit.
5. **Monitor and audit** — Verify audit chain integrity, provenance
   DAG completeness, and regulatory compliance.
6. **Federated coordination** — If deploying at Level 4+, enable
   cross-site provenance and federated model aggregation.
7. **Report conformance** — Submit conformance reports to the national
   registry.

### Deliverables

- Operational pilot deployments
- Cross-site audit verification results
- Conformance certification submissions
- Lessons learned documentation

### Duration

Ongoing — initial pilots run 3–6 months, with continuous expansion
to additional sites

---

## Adoption Timeline Summary

| Phase | Name | Duration | Key Milestone |
|-------|------|----------|---------------|
| **0** | Specification Review | 2–4 weeks | Conformance level target selected |
| **1** | Profile Selection | 4–8 weeks | Profile and overlay selection finalized |
| **2** | Conformance Validation | 8–12 weeks | All conformance tests passing |
| **3** | Pilot Deployment | 3–6 months | First conforming site operational |

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

### Related Repositories

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework with USL scoring
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework
