# Next Steps: National Adoption and Execution Guide

**National MCP-PAI Oncology Trials Standard**
**Version**: 0.1.0 | **Status**: Published for Review

---

## Purpose

This document describes what each stakeholder group should do now that the National MCP-PAI Oncology Trials repository is publicly available and positioned as a proposed national reference standard for Model Context Protocol (MCP) infrastructure in Physical AI oncology clinical trials. Actions are organized by stakeholder group and sequenced into immediate, near-term, and medium-term phases.

---

## 1. Sponsors (Pharmaceutical and Medical Device Companies)

### Immediate Actions (Weeks 1-4)

1. Review the repository README and `spec/core.md` to understand the five-server architecture and 23-tool surface area.
2. Review `spec/actor-model.md` to confirm that the sponsor role scope and permission matrix align with your trial governance requirements.
3. Assess `profiles/base-profile.md` and `profiles/multi-site-federated.md` against your current multi-site trial data infrastructure.
4. Review `regulatory/US_FDA.md` and `regulatory/CFR_PART_11.md` to evaluate how the standard addresses 21 CFR Part 11 requirements relevant to your submissions.

### Near-Term Actions (Months 2-3)

1. Engage your CRO partners to evaluate the standard jointly, using `docs/guides/sponsor-cro.md` as a starting point.
2. Identify one candidate oncology trial for pilot adoption at the base profile level (Level 1).
3. Commission an internal gap analysis between your existing trial data infrastructure and the 13 schemas in `schemas/`.
4. Evaluate the SDK (`sdk/python/` or `sdk/typescript/`) for integration feasibility with your trial management platform.

### Medium-Term Actions (Months 4-8)

1. Fund a single-site pilot deployment using the Docker Compose configuration in `deploy/docker-compose.yml`.
2. Engage regulatory affairs to prepare a position document on MCP-PAI standard adoption for FDA pre-submission discussions.
3. Participate in the governance process defined in `governance/CHARTER.md` to influence standard evolution.

---

## 2. Contract Research Organizations (CROs)

### Immediate Actions (Weeks 1-4)

1. Review `docs/guides/sponsor-cro.md` and the CRO actor definition in `spec/actor-model.md`.
2. Review the six persona definitions in `interop-testbed/personas/` to understand the role-based access model.
3. Evaluate `conformance/README.md` to understand the conformance test categories and how they map to validation requirements.

### Near-Term Actions (Months 2-3)

1. Run the conformance test suite (`pytest conformance/ -v`) against a local deployment to assess implementation readiness.
2. Map your existing monitoring and data review workflows to the `data_monitor` role permissions in the actor model.
3. Evaluate the eight interoperability scenarios in `interop-testbed/scenarios/` for relevance to your multi-site coordination workflows.
4. Assess the integration adapters in `integrations/` (FHIR, DICOM, clinical, federation, identity, privacy) against your current systems.

### Medium-Term Actions (Months 4-8)

1. Develop internal SOPs for MCP-PAI standard adoption across your trial portfolio.
2. Train monitoring staff on the audit ledger verification tools (`ledger_verify`, `ledger_query`, `ledger_replay`).
3. Establish a multi-site pilot with at least two sponsor partners to validate cross-site MCP communication.

---

## 3. Academic Medical Centers

### Immediate Actions (Weeks 1-4)

1. Review the five conformance levels in `spec/conformance.md` and identify which level matches your institutional capabilities.
2. Review `profiles/clinical-read.md` (Level 2) as the likely starting point for sites with existing FHIR infrastructure.
3. Assess `docs/walkthroughs/base-profile.md` and `docs/walkthroughs/clinical-read.md` for practical onboarding guidance.
4. Review the IRB site policy template in `regulatory/IRB_SITE_POLICY_TEMPLATE.md`.

### Near-Term Actions (Months 2-3)

1. Engage your institutional IT and security teams to review the deployment architecture in `docs/architecture.md`.
2. Evaluate the FHIR integration adapters in `integrations/fhir/` against your EHR environment (HAPI FHIR, SMART on FHIR).
3. Run the unit test suite (`pytest tests/ -v`) and the positive conformance tests (`pytest conformance/positive/ -v`) locally.
4. Identify a principal investigator and trial coordinator to participate in a pilot evaluation.

### Medium-Term Actions (Months 4-8)

1. Deploy a single-site instance using Kubernetes manifests in `deploy/kubernetes/` or Docker in `deploy/docker/`.
2. Conduct a formal institutional review of the privacy and de-identification modules in `integrations/privacy/` and `safety/`.
3. Generate conformance evidence using `tools/certification/evidence_pack.py` for institutional approval.

---

## 4. Community Oncology Sites

### Immediate Actions (Weeks 1-4)

1. Review `profiles/base-profile.md` to understand the minimum requirements for participation.
2. Review `docs/guides/hospital-it.md` for site-level IT guidance.
3. Assess whether your site has the prerequisites: Python 3.10+, network connectivity for MCP transport, and access to FHIR or DICOM endpoints.

### Near-Term Actions (Months 2-3)

1. Engage your IT vendor or managed services provider to evaluate the all-in-one Docker deployment (`deploy/docker/Dockerfile.allinone`).
2. Review the site capability profile schema (`schemas/site-capability-profile.schema.json`) to understand what capabilities your site would need to declare.
3. Coordinate with your affiliated academic medical center or CRO for shared infrastructure planning.

### Medium-Term Actions (Months 4-8)

1. Deploy a base profile (Level 1) instance for evaluation in a non-production environment.
2. Complete the site onboarding scenario defined in `interop-testbed/scenarios/site_onboarding.py`.
3. Generate a site certification report using `tools/certification/site_certification.py`.

---

## 5. Hospital IT and Security Teams

### Immediate Actions (Weeks 1-4)

1. Review `docs/guides/hospital-it.md` for deployment architecture, network requirements, and security considerations.
2. Review `spec/security.md` for the security model, including mTLS, OIDC, token lifecycle, and SSRF prevention.
3. Review `docs/operations/key-management.md` for cryptographic key management requirements.
4. Assess the deny-by-default RBAC model in `spec/actor-model.md` and ADR `docs/adr/007-deny-by-default-rbac.md`.

### Near-Term Actions (Months 2-3)

1. Run the security conformance tests (`pytest conformance/security/ -v`) to understand the security validation surface.
2. Evaluate the identity integration adapters in `integrations/identity/` (OIDC, mTLS, KMS, policy engine).
3. Review `docs/operations/incident-response.md` and `docs/operations/backup-recovery.md` for operational readiness.
4. Assess the deployment configurations in `deploy/config/` for each server (authz, FHIR, DICOM, ledger, provenance).

### Medium-Term Actions (Months 4-8)

1. Conduct a formal security assessment of the deployed infrastructure against your institutional security policies.
2. Integrate the MCP authorization server with your existing identity provider using the OIDC adapter.
3. Establish monitoring using the SLO guidance in `docs/operations/slo-guidance.md` and the operational runbook in `docs/operations/runbook.md`.
4. Validate the circuit breaker and retry middleware in the Python and TypeScript SDKs.

---

## 6. Robotics Vendors

### Immediate Actions (Weeks 1-4)

1. Review `docs/guides/robot-vendor.md` for vendor-specific integration guidance.
2. Review `profiles/robot-assisted-procedure.md` (Level 5) to understand the full conformance requirements for robotic systems.
3. Review the robot capability profile schema (`schemas/robot-capability-profile.schema.json`).
4. Review the safety modules in `safety/` — especially `estop.py`, `procedure_state.py`, `robot_registry.py`, and `task_validator.py`.

### Near-Term Actions (Months 2-3)

1. Map your robot control API to the MCP tool contracts in `spec/tool-contracts.md`.
2. Evaluate the robot workflow scenario in `interop-testbed/scenarios/robot_workflow.py`.
3. Run the adversarial tests (`pytest conformance/adversarial/ -v`) to understand the security testing surface for robotic agents.
4. Assess the task order schema (`schemas/task-order.schema.json`) against your procedure planning data model.

### Medium-Term Actions (Months 4-8)

1. Develop an MCP adapter for your robotic platform using the SDK as a reference.
2. Implement the safety gate integration defined in `safety/gate_service.py` and `safety/approval_checkpoint.py`.
3. Generate conformance evidence at Level 5 using the certification tooling in `tools/certification/`.

---

## 7. EHR and FHIR Integration Teams

### Immediate Actions (Weeks 1-4)

1. Review the FHIR integration adapters in `integrations/fhir/` — specifically `hapi_adapter.py`, `smart_adapter.py`, and `base_adapter.py`.
2. Review `schemas/fhir-read.schema.json` and `schemas/fhir-search.schema.json` for the FHIR data schemas used by the standard.
3. Review `profiles/clinical-read.md` (Level 2) for FHIR-specific conformance requirements.

### Near-Term Actions (Months 2-3)

1. Test the FHIR server (`servers/trialmcp_fhir/`) against your FHIR R4 endpoint.
2. Evaluate the de-identification pipeline in `integrations/fhir/deidentification.py` and `integrations/privacy/deidentification_pipeline.py`.
3. Run the FHIR-specific blackbox tests (`pytest conformance/blackbox/test_fhir_conformance.py -v`).
4. Assess the terminology service adapter in `integrations/fhir/terminology.py`.

### Medium-Term Actions (Months 4-8)

1. Deploy the FHIR MCP server alongside your existing FHIR infrastructure.
2. Validate patient filtering (`integrations/fhir/patient_filter.py`) and bundle handling (`integrations/fhir/bundle_handler.py`) against your data.
3. Conduct end-to-end testing with the clinical read walkthrough in `docs/walkthroughs/clinical-read.md`.

---

## 8. Imaging, PACS, and DICOM Teams

### Immediate Actions (Weeks 1-4)

1. Review the DICOM integration adapters in `integrations/dicom/` — specifically `dcm4chee_adapter.py`, `orthanc_adapter.py`, and `dicomweb.py`.
2. Review `schemas/dicom-query.schema.json` and `profiles/imaging-guided-oncology.md` (Level 3).
3. Review the RECIST measurement module in `integrations/dicom/recist.py`.

### Near-Term Actions (Months 2-3)

1. Test the DICOM MCP server (`servers/trialmcp_dicom/`) against your PACS environment.
2. Run the DICOM-specific blackbox tests (`pytest conformance/blackbox/test_dicom_conformance.py -v`).
3. Evaluate the modality filter (`integrations/dicom/modality_filter.py`) and safety checks (`integrations/dicom/safety.py`).
4. Assess the metadata normalizer (`integrations/dicom/metadata_normalizer.py`) for compatibility with your imaging data model.

### Medium-Term Actions (Months 4-8)

1. Deploy the DICOM MCP server alongside your PACS infrastructure.
2. Validate the imaging-guided workflow using `docs/walkthroughs/imaging-guided.md`.
3. Conduct integration testing with real DICOM data in a non-production environment.

---

## 9. Privacy, Compliance, Legal, and Regulatory Teams

### Immediate Actions (Weeks 1-4)

1. Review `regulatory/US_FDA.md`, `regulatory/HIPAA.md`, `regulatory/CFR_PART_11.md`, and `regulatory/IRB_SITE_POLICY_TEMPLATE.md`.
2. Review `spec/privacy.md` for the privacy architecture, including de-identification, consent management, and data residency.
3. Review `docs/guides/regulator-irb.md` for regulatory and IRB-specific guidance.
4. Assess the privacy integration modules in `integrations/privacy/` — especially `privacy_budget.py`, `data_residency.py`, and `access_control.py`.

### Near-Term Actions (Months 2-3)

1. Evaluate the consent status schema (`schemas/consent-status.schema.json`) against your IRB requirements.
2. Review the adversarial PHI leakage tests (`conformance/adversarial/test_phi_leakage.py`) to understand how the standard validates PHI protection.
3. Conduct a HIPAA gap analysis using the controls documented in `regulatory/HIPAA.md`.
4. Evaluate the de-identification pipeline end-to-end: `integrations/fhir/deidentification.py` through `integrations/privacy/deidentification_pipeline.py`.

### Medium-Term Actions (Months 4-8)

1. Develop an institutional privacy impact assessment for MCP-PAI adoption.
2. Generate regulatory evidence using `tools/certification/evidence_pack.py` and `tools/certification/report_generator.py`.
3. Engage with FDA or other regulatory bodies using the conformance evidence and regulatory overlay profiles (`profiles/country-us-fda.md`, `profiles/state-us-ca.md`, `profiles/state-us-ny.md`).

---

## 10. Principal Investigators and Trial Coordinators

### Immediate Actions (Weeks 1-4)

1. Review the README for a high-level understanding of what the standard provides.
2. Review the `trial_coordinator` role definition in `spec/actor-model.md` to understand your permissions and responsibilities.
3. Review `docs/walkthroughs/robot-procedure.md` if your trial involves robotic procedures.

### Near-Term Actions (Months 2-3)

1. Work with your site IT team to evaluate the quickstart example in `examples/quickstart/`.
2. Review the scheduling adapter (`integrations/clinical/scheduling_adapter.py`) and e-consent adapter (`integrations/clinical/econsent_adapter.py`).
3. Participate in a tabletop exercise using the interoperability scenarios in `interop-testbed/scenarios/`.

### Medium-Term Actions (Months 4-8)

1. Participate in a single-site pilot deployment with your institutional IT and security teams.
2. Validate clinical workflows end-to-end using the deployed MCP infrastructure.
3. Provide feedback on usability, workflow integration, and clinical relevance through the governance process.

---

## 11. Auditors and Data Monitors

### Immediate Actions (Weeks 1-4)

1. Review the `auditor` and `data_monitor` role definitions and permission matrices in `spec/actor-model.md`.
2. Review `spec/audit.md` for the hash-chained audit trail architecture and ADR `docs/adr/005-hash-chained-audit.md`.
3. Review `spec/provenance.md` and ADR `docs/adr/006-dag-provenance.md` for the provenance DAG model.

### Near-Term Actions (Months 2-3)

1. Evaluate the ledger server tools: `ledger_verify`, `ledger_query`, and `ledger_replay`.
2. Run the chain integrity security test (`pytest conformance/security/test_chain_integrity.py -v`).
3. Review the audit replay interoperability scenario (`interop-testbed/scenarios/audit_replay.py`).
4. Assess the provenance export module (`integrations/clinical/provenance_export.py`).

### Medium-Term Actions (Months 4-8)

1. Validate audit trail integrity using the ledger replay tools against a pilot deployment.
2. Generate audit evidence packs using `tools/certification/evidence_pack.py`.
3. Develop audit procedures aligned with the standard's hash-chained audit model.

---

## 12. Standards Contributors and Open-Source Maintainers

### Immediate Actions (Weeks 1-4)

1. Review `docs/guides/standards-community.md` for community contribution guidance.
2. Review `governance/CHARTER.md` and `governance/DECISION_PROCESS.md` to understand the governance model.
3. Review the seven ADRs in `docs/adr/` to understand key architectural decisions and their rationale.
4. Review `docs/governance/known-gaps.md` and `docs/governance/roadmap.md` to identify areas needing contribution.

### Near-Term Actions (Months 2-3)

1. Fork the repository and run the full test suite to validate your development environment.
2. Review the extension mechanism in `governance/EXTENSIONS.md` and `spec/versioning.md`.
3. Identify conformance gaps or missing test coverage by reviewing `docs/governance/implementation-status.md`.
4. Submit issues using the templates in `.github/ISSUE_TEMPLATE/` (bug reports, feature requests, spec changes).

### Medium-Term Actions (Months 4-8)

1. Contribute conformance tests, integration adapters, or documentation improvements via pull requests.
2. Participate in governance decisions using the process defined in `governance/DECISION_PROCESS.md`.
3. Propose extensions using the `x-{vendor}` namespace defined in `spec/versioning.md`.
4. Review and comment on peer review artifacts in `peer-review/` to support standard maturation.

---

## Cross-Cutting Adoption Sequencing

### Phase 1: Review and Assessment (Weeks 1-4)

- All stakeholders review relevant documentation, schemas, and profiles.
- IT and security teams conduct initial architecture and security assessments.
- Regulatory and compliance teams begin gap analyses.
- No production deployments during this phase.

### Phase 2: Local Validation (Months 2-3)

- Single-site deployments in non-production environments.
- Conformance test execution against local instances.
- Integration testing with site-specific EHR, PACS, and identity systems.
- Stakeholder feedback collection through governance channels.

### Phase 3: Pilot Adoption (Months 4-6)

- Single-site pilot deployments with real (non-production) clinical workflows.
- Multi-site coordination pilots with at least two sites.
- Conformance evidence generation using the certification tooling.
- Regulatory engagement with generated evidence packs.

### Phase 4: Multi-Site Coordination (Months 7-12)

- Multi-site federated deployments using `deploy/docker-compose.multi-site.yml`.
- Cross-site provenance validation using `interop-testbed/scenarios/cross_site_provenance.py`.
- National coordination discussions among early adopter sites.
- Standard refinement based on pilot feedback.

---

## Dependencies Between Workstreams

1. **Technical readiness** (IT deployment, security review) must precede **clinical validation** (PI and coordinator workflows).
2. **Regulatory assessment** (HIPAA, FDA, IRB) should proceed in parallel with technical readiness but must complete before **production use**.
3. **Identity integration** (OIDC, mTLS) is a prerequisite for **multi-site federation**.
4. **FHIR integration** is a prerequisite for Level 2 (Clinical Read) conformance.
5. **DICOM integration** is a prerequisite for Level 3 (Imaging-Guided) conformance.
6. **Safety module validation** is a prerequisite for Level 5 (Robot-Assisted) conformance.
7. **Conformance evidence generation** is a prerequisite for **regulatory submissions**.

---

## Readiness Checkpoints

### Single-Site Readiness

- All unit tests pass (`pytest tests/ -v`).
- Base profile conformance tests pass (`pytest conformance/positive/test_core_conformance.py -v`).
- Security tests pass (`pytest conformance/security/ -v`).
- Identity provider integrated and tested.
- Site capability profile declared and validated against schema.

### Multi-Site Readiness

- All single-site readiness criteria met at each participating site.
- Cross-site MCP transport validated.
- Interoperability tests pass (`pytest conformance/interoperability/ -v`).
- Federated learning coordination validated using `integrations/federation/`.
- Site harmonization completed using `integrations/federation/site_harmonization.py`.

### National Coordination Readiness

- Multiple multi-site pilots completed with conformance evidence.
- Governance participation from at least three stakeholder categories.
- Regulatory feedback incorporated from FDA or relevant bodies.
- Standard versioning and compatibility policies validated in practice.

---

## Actions to Take Now vs. Actions Requiring Formal Validation

### Do Now

- Read documentation, schemas, profiles, and spec files.
- Run test suites locally.
- Deploy in non-production environments.
- Conduct gap analyses and security reviews.
- Engage internal stakeholders and governance participants.
- Submit issues and feedback through GitHub.

### Plan Next

- Single-site pilot deployments with institutional approval.
- Integration with site-specific EHR, PACS, and identity systems.
- Regulatory pre-submission discussions.
- Multi-site coordination agreements.
- SOPs and training materials for clinical and operational staff.

### Requires Formal Validation Before Production or Clinical Use

- Any deployment processing real patient data.
- Any integration with production EHR or PACS systems.
- Any use in an active clinical trial.
- Any submission to regulatory bodies as part of a trial dossier.
- Any robotic procedure execution using MCP-coordinated safety gates.

---

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

### Related Repositories

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation (single-site proof of concept)
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework with USL scoring and patient instructions
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework with privacy and regulatory modules
