# Roadmap

**National MCP-PAI Oncology Trials Standard — Roadmap**
**Version**: 0.1.0
**Last Updated**: 2026-03-08

---

## Purpose

This roadmap defines the target adopters, milestones, and timelines for the National
MCP-PAI Oncology Trials Standard. It covers the progression from initial draft through
pilot deployments, regulatory engagement, and national-scale adoption.

---

## Target Adopters

### Tier 1 — Early Adopters (2026 Q1–Q2)

| Adopter Type | Examples | Motivation |
|-------------|----------|------------|
| NCI-Designated Cancer Centers | MD Anderson, Memorial Sloan Kettering, Dana-Farber | Leadership in AI-assisted oncology trials |
| Medical Robotics Vendors | Intuitive Surgical, Medtronic Robotics, Stryker | Standardized integration with trial infrastructure |
| Academic Health Systems | Mayo Clinic, Johns Hopkins, UCSF | Research-grade interoperability |
| Clinical Trial CROs | IQVIA, Syneos Health, PPD | Multi-site trial coordination |

### Tier 2 — Growth Adopters (2026 Q3–Q4)

| Adopter Type | Examples | Motivation |
|-------------|----------|------------|
| Community Cancer Networks | US Oncology Network, NCCN Member Institutions | Access to advanced trial protocols |
| EHR Vendors | Epic, Cerner/Oracle Health, MEDITECH | FHIR R4 integration certification |
| PACS/VNA Vendors | Philips, GE Healthcare, Fujifilm | DICOM interoperability certification |
| Pharmaceutical Sponsors | Roche, Pfizer, Merck, Bristol-Myers Squibb | Standardized trial data collection |

### Tier 3 — National Scale (2027 Q1–Q2)

| Adopter Type | Examples | Motivation |
|-------------|----------|------------|
| Federal Agencies | FDA CDRH, NCI CTEP, ONC | Regulatory framework alignment |
| Standards Bodies | HL7, DICOM Committee, IHE | Cross-standard harmonization |
| Health Information Exchanges | Carequality, CommonWell, eHealth Exchange | National data infrastructure |
| State Health Departments | CA, NY, TX, FL regulatory bodies | State-level trial oversight |

---

## Milestones

### Phase 1: Foundation (2026 Q1) — CURRENT

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|-------------|
| M1.1: Core specification draft | 2026-01-31 | Complete | `spec/core.md`, `spec/actor-model.md` |
| M1.2: Tool contracts v0.1.0 | 2026-02-15 | Complete | `spec/tool-contracts.md` (23 tools) |
| M1.3: Security baseline | 2026-02-28 | Complete | `spec/security.md`, `spec/privacy.md` |
| M1.4: Reference implementation | 2026-03-15 | In Progress | 5 MCP servers in `servers/` |
| M1.5: Conformance test suite | 2026-03-31 | In Progress | `tests/` and `conformance/` |
| M1.6: Peer review cycle 1 | 2026-03-15 | Complete | `peer-review/` responses |

### Phase 2: Validation (2026 Q2)

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|-------------|
| M2.1: Interoperability testbed | 2026-04-15 | Planned | `interop-testbed/` framework |
| M2.2: Pilot site onboarding (3 sites) | 2026-04-30 | Planned | Deployment guides |
| M2.3: Safety module validation | 2026-05-15 | Planned | E-stop, gate service certification |
| M2.4: Regulatory pre-submission | 2026-05-31 | Planned | FDA CDRH pre-submission package |
| M2.5: v0.1.0 stable release | 2026-06-15 | Planned | Tagged, signed release |
| M2.6: Conformance certification program | 2026-06-30 | Planned | Certification process document |

### Phase 3: Pilot Deployment (2026 Q3)

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|-------------|
| M3.1: Pilot site go-live (3 sites) | 2026-07-31 | Planned | Production deployment |
| M3.2: Multi-site federated trial pilot | 2026-08-15 | Planned | Cross-site data lineage |
| M3.3: Robot-assisted procedure pilot | 2026-08-31 | Planned | Level 5 conformance demo |
| M3.4: Adverse event reporting integration | 2026-09-15 | Planned | MedWatch data flow |
| M3.5: Pilot evaluation report | 2026-09-30 | Planned | Findings and recommendations |

### Phase 4: Expansion (2026 Q4)

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|-------------|
| M4.1: v0.2.0 specification release | 2026-10-15 | Planned | Federated learning, extensions |
| M4.2: Vendor certification (5 vendors) | 2026-10-31 | Planned | Certified implementations |
| M4.3: EHR integration certification | 2026-11-15 | Planned | Epic, Cerner integrations |
| M4.4: Expanded site deployment (10 sites) | 2026-11-30 | Planned | Regional coverage |
| M4.5: Standards body liaison | 2026-12-15 | Planned | HL7, DICOM committee engagement |

### Phase 5: National Scale (2027 Q1–Q2)

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|-------------|
| M5.1: v1.0.0 specification release | 2027-01-31 | Planned | Normative standard |
| M5.2: FDA guidance alignment | 2027-02-28 | Planned | Regulatory framework |
| M5.3: National deployment (50+ sites) | 2027-03-31 | Planned | Nationwide availability |
| M5.4: International liaison (EU, UK, JP) | 2027-04-30 | Planned | Cross-border harmonization |
| M5.5: Long-term governance transition | 2027-06-30 | Planned | Permanent governance body |

---

## Version Timeline

```
2026 Q1    Q2         Q3          Q4         2027 Q1    Q2
  |---------|----------|-----------|----------|---------|
  v0.1.0-   v0.1.0    Pilot       v0.2.0     v1.0.0   National
  draft     stable    deploy      release    normative scale
  |         |         |           |          |         |
  Core      3-site    Robot       Federated  FDA       50+ sites
  spec      pilot     procedure   learning   guidance
            begin     pilot       spec       alignment
```

---

## Success Criteria

### v0.1.0 (2026 Q2)

- All 23 tool contracts implemented and tested in reference implementation
- At least 3 pilot sites successfully onboarded
- Conformance test suite covers all MUST requirements
- FDA pre-submission feedback received
- Security audit completed with no critical findings

### v0.2.0 (2026 Q4)

- At least 5 vendor implementations certified
- Multi-site federated trial pilot completed successfully
- Robot-assisted procedure pilot completed with safety validation
- EHR integration certified for at least 2 major vendors
- 10+ sites in production deployment

### v1.0.0 (2027 Q1)

- Normative standard ratified by governance body
- FDA guidance document references the standard
- 50+ sites in production or onboarding
- At least 3 international standards bodies engaged
- Long-term governance body established and funded

---

## Risk Factors

| Risk | Impact | Mitigation |
|------|--------|------------|
| FDA regulatory uncertainty | High | Early pre-submission engagement |
| Vendor adoption resistance | Medium | Certification incentive program |
| Robot safety incidents during pilot | High | Independent safety modules, staged rollout |
| EHR vendor integration delays | Medium | FHIR R4 standard compliance leverage |
| Multi-site data governance conflicts | Medium | Federated-first architecture |
| Insufficient pilot site diversity | Low | Geographic and demographic targeting |
| Specification scope creep | Medium | Strict ADR-based change governance |

---

## Governance Review Cycle

The roadmap is reviewed and updated quarterly by the Governance Board. Milestone dates
are targets, not commitments. Changes to milestones require a governance decision log
entry (see `decision-log.md`). Additions of new phases or fundamental scope changes
require a formal ADR.
