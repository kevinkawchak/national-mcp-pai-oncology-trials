# ADR-006: DAG-Based Provenance Over Linear Lineage

**Status**: Accepted
**Date**: 2026-02-12
**Decision Makers**: Data Lineage Working Group
**Tracking**: DL-006 in `docs/governance/decision-log.md`

---

## Context

Oncology clinical trials involve complex data flows that are inherently non-linear:

1. **Fan-out**: A single DICOM imaging study generates multiple downstream analyses
   (RECIST measurements, radiation planning contours, AI-generated segmentation masks,
   quality control reports). Each derived artifact has a distinct lineage from the
   same source.

2. **Fan-in**: Federated learning aggregation merges model parameters from multiple
   sites into a single aggregated model. The aggregated model has multiple parent
   sources, one from each contributing site.

3. **Multi-step derivation**: A robot-assisted procedure may involve a chain of data
   transformations: FHIR patient lookup produces pseudonymized demographics, which
   are combined with DICOM imaging data, which guides robot trajectory planning,
   which produces telemetry data that feeds back into the audit trail.

4. **Cross-server lineage**: Data flows across all five MCP servers. A single clinical
   operation may touch AuthZ (permission check), FHIR (patient data), DICOM (imaging),
   Ledger (audit record), and Provenance (lineage entry). The lineage model must span
   server boundaries.

5. **Regulatory requirement**: ICH-GCP E6(R2) requires that data lineage be traceable
   from source to final report. FDA guidance on data integrity requires that "data
   should be attributable, legible, contemporaneous, original, and accurate" (ALCOA+).
   Forward and backward lineage queries are essential for regulatory inspection.

The standard must define a provenance model that accurately represents these data flow
patterns and supports the lineage queries required by regulators.

---

## Decision

Implement provenance as a directed acyclic graph (DAG) with the following properties:

1. **Nodes**: DataSource entities (registered via `provenance_register_source`)
2. **Edges**: ProvenanceRecord entries (created via `provenance_record_access`)
3. **Direction**: Edges point from source data to derived data
4. **Acyclicity**: Cycles MUST NOT exist in the graph (enforced by the implementation)
5. **Forward queries**: Traverse from source to all derived data ("what was produced
   from this source?")
6. **Backward queries**: Traverse from derived data to all source data ("where did
   this data come from?")
7. **Fingerprinting**: SHA-256 hashes of input and output data at each transformation
   step for integrity verification

---

## Rationale

### DAG Accurately Models Clinical Data Flows

A directed acyclic graph is the correct mathematical structure for clinical trial
data lineage because:

- **Fan-out is natural**: A single DataSource node can have multiple outgoing edges,
  each representing a distinct derivation. This models the imaging study that produces
  multiple analyses.

- **Fan-in is natural**: A single DataSource node can have multiple incoming edges,
  each representing a contributing source. This models federated aggregation.

- **Multi-step chains are natural**: Paths through the DAG represent multi-step
  derivation chains. The longest path from a source node to a leaf node represents
  the complete derivation history.

- **No cycles by construction**: Clinical data derivation is inherently temporal.
  Data cannot be derived from its own derivatives (this would violate causality).
  The DAG constraint enforces this invariant.

### Forward and Backward Queries

The DAG supports two fundamental query directions:

**Forward lineage** (`provenance_get_lineage` with `direction: forward`):
Starting from a DataSource, traverse all outgoing edges to discover every artifact
derived from that source. Use case: "A data quality issue was found in Patient X's
FHIR record. What downstream analyses, robot procedures, and reports used this data?"

**Backward lineage** (`provenance_get_lineage` with `direction: backward`):
Starting from a DataSource, traverse all incoming edges to discover every source
that contributed to that artifact. Use case: "This robot trajectory plan needs
verification. What imaging studies, patient records, and calibration data
contributed to it?"

Both query directions are essential for regulatory compliance. FDA inspectors
performing data integrity audits need forward queries to assess the impact of
data issues. Clinical researchers need backward queries to verify the provenance
of derived results.

### SHA-256 Fingerprinting for Integrity

Each ProvenanceRecord includes SHA-256 fingerprints of input and output data.
This enables integrity verification at each transformation step:

1. **Input fingerprint**: SHA-256 hash of the data consumed by the operation
2. **Output fingerprint**: SHA-256 hash of the data produced by the operation

If the input data at any step does not match its expected fingerprint, the
integrity chain is broken and the discrepancy is detectable. This satisfies
ALCOA+ "Accurate" and "Original" requirements.

### Separation from Audit Ledger

The provenance DAG is distinct from the audit ledger (hash chain):

| Property | Audit Ledger | Provenance DAG |
|----------|-------------|----------------|
| Structure | Linear hash chain | Directed acyclic graph |
| Purpose | What happened (actions) | Where data came from (lineage) |
| Query pattern | Sequential replay | Graph traversal (forward/backward) |
| Integrity model | Chain continuity | Per-edge fingerprint verification |
| Regulatory focus | 21 CFR Part 11 | ICH-GCP E6(R2), ALCOA+ |
| Granularity | Per-tool-invocation | Per-data-transformation |

These are complementary models. The audit ledger records that `fhir_read` was
called at time T by actor A. The provenance DAG records that DataSource X was
read by actor A and contributed to the derivation of DataSource Y.

---

## Consequences

### Positive

- **Accurate lineage representation**: Fan-out and fan-in patterns are modeled
  correctly, unlike linear lineage which would require artificial linearization
- **Efficient regulatory queries**: Forward and backward traversals directly
  answer the lineage questions that FDA inspectors and IRB auditors ask
- **Cross-server lineage**: The DAG spans all five MCP servers, providing a
  unified view of data flow across authorization, clinical, imaging, audit, and
  provenance domains
- **Integrity verification**: SHA-256 fingerprinting at each edge enables
  per-step integrity verification without requiring access to the full data
- **Federated learning support**: Fan-in edges naturally model federated
  aggregation from multiple sites

### Negative

- **Graph complexity**: DAGs are more complex to implement than linear chains.
  Graph traversal, cycle detection, and efficient storage require more
  sophisticated data structures
- **Visualization difficulty**: Large DAGs are harder to visualize and present
  to non-technical stakeholders (regulatory reviewers, clinicians) compared to
  linear timelines
- **Cross-site DAG merging**: Merging DAGs from multiple sites for federated
  provenance is a non-trivial operation not fully specified in v0.1.0 (see
  `docs/governance/known-gaps.md`)
- **Storage growth**: DAG edges accumulate over the lifetime of a trial. Long-
  running trials with many data transformations may produce large provenance
  graphs

### Mitigations

- Reference implementation includes efficient graph traversal using adjacency
  lists with O(V+E) traversal complexity
- Visualization tools are planned for v0.2.0 to render DAGs as interactive
  lineage diagrams
- Cross-site DAG merging will be specified in v0.2.0 with the federated
  learning aggregation specification
- Storage guidelines recommend archiving completed trial provenance graphs
  with retention policies aligned to regulatory requirements (typically 2 years
  after trial completion per 21 CFR 312.62)

---

## Alternatives Rejected

### Linear Lineage Chain

A simple sequential list of data access events, similar to the audit ledger
but for provenance. Rejected because:

- Cannot represent fan-out (one source, many derivatives)
- Cannot represent fan-in (many sources, one aggregate)
- Federated learning aggregation is inherently non-linear
- Would require artificial linearization of concurrent data flows, losing
  structural information

### Relational Model (Tables with Foreign Keys)

Provenance stored as relational tables with foreign key relationships.
Rejected because:

- Graph traversal queries (find all ancestors of node X) are inefficient
  in relational models without recursive CTEs
- The relational model imposes a schema that may not accommodate future
  provenance record types without schema migration
- The DAG model is conceptually cleaner and maps directly to the lineage
  queries needed

### W3C PROV-DM

The W3C Provenance Data Model (PROV-DM) is a comprehensive provenance
ontology with Entity, Activity, and Agent concepts. Rejected as the
primary model because:

- PROV-DM's generality adds complexity without proportionate benefit for
  the specific use case of MCP tool-invocation lineage
- The DataSource/ProvenanceRecord model is simpler and sufficient
- PROV-DM compatibility can be achieved through a mapping layer if needed
  for interoperability with PROV-DM-based systems

### Blockchain-Based Provenance

Provenance stored on a distributed ledger (Hyperledger, Ethereum). Rejected
for the same reasons as blockchain-based audit (see ADR-005): unnecessary
consensus complexity, regulatory unfamiliarity, and performance overhead.

---

## References

- `spec/provenance.md` (Full provenance specification)
- `spec/tool-contracts.md` Section 7 (Provenance tools)
- ICH-GCP E6(R2) Section 5.5 (Data Integrity)
- FDA Data Integrity Guidance (ALCOA+ principles)
- W3C PROV-DM: https://www.w3.org/TR/prov-dm/
