# Provenance Specification

**National MCP-PAI Oncology Trials Standard — spec/provenance.md**
**Version**: 0.1.0
**Status**: Draft

---

## 1. Overview

This specification defines the data provenance model for tracking lineage, access history, and integrity verification across the national MCP infrastructure. The provenance system implements a directed acyclic graph (DAG) derived from the reference `ProvenanceGraph` implementation, with `DataSource` and `ProvenanceRecord` as its core entities.

---

## 2. Data Model

### 2.1 DataSource

A DataSource represents a registered data origin in the provenance graph.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_id` | string | Generated | Unique identifier (UUID v4) |
| `source_type` | string | Yes | Category of data (e.g., `fhir_resource`, `dicom_study`, `model_parameters`, `robot_telemetry`) |
| `origin_server` | string | Yes | MCP server that owns this data source |
| `description` | string | Yes | Human-readable description |
| `metadata` | object | No | Additional properties specific to the source type |
| `registered_at` | string | Generated | ISO 8601 UTC timestamp of registration |

### 2.2 ProvenanceRecord

A ProvenanceRecord tracks a single data access or transformation event.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `record_id` | string | Generated | Unique identifier (UUID v4) |
| `source_id` | string | Yes | Reference to the DataSource being accessed |
| `action` | string | Yes | Operation performed (`read`, `transform`, `aggregate`, `derive`, `export`) |
| `actor_id` | string | Yes | Identifier of the actor performing the action |
| `actor_role` | string | Yes | Role of the actor (from the 6-actor model) |
| `tool_call` | string | Yes | MCP tool invocation that triggered this access |
| `input_hash` | string | Generated | SHA-256 fingerprint of input data |
| `output_hash` | string | Generated | SHA-256 fingerprint of output data |
| `timestamp` | string | Generated | ISO 8601 UTC timestamp |

---

## 3. DAG Lineage Model

### 3.1 Graph Structure

The provenance graph MUST be implemented as a directed acyclic graph (DAG) where:
- **Nodes** represent DataSources
- **Edges** represent ProvenanceRecords (data access or transformation events)
- Edges are directed from source to derived data
- Cycles MUST NOT exist in the graph

### 3.2 Forward Queries

Forward lineage queries traverse the DAG from a source to all derived data, answering: "What downstream data was produced from this source?"

### 3.3 Backward Queries

Backward lineage queries traverse the DAG from derived data back to original sources, answering: "What upstream sources contributed to this data?"

### 3.4 Actor History

Actor history queries collect all ProvenanceRecords for a given actor, answering: "What data operations has this actor performed?"

---

## 4. SHA-256 Fingerprinting

### 4.1 Data Integrity

All data access events MUST compute SHA-256 fingerprints for both input and output data. This enables:
- Verification that data has not been modified since the provenance record was created
- Detection of unauthorized data modifications
- Proof of data integrity for regulatory compliance

### 4.2 Fingerprint Computation

Fingerprints MUST be computed as follows:
1. Encode the data string as UTF-8 bytes
2. Compute SHA-256 hash of the encoded bytes
3. Store the hexadecimal digest (64 characters)

### 4.3 Integrity Verification

The `provenance_verify_integrity` tool MUST:
1. Accept a source ID and current data
2. Compute the SHA-256 fingerprint of the provided data
3. Compare against the most recent recorded fingerprint for that source
4. Return whether the fingerprints match

---

## 5. National-Scale Provenance

### 5.1 Site-Scoped Provenance

Each site MUST maintain its own provenance graph. Provenance records MUST NOT reference data sources at other sites directly.

### 5.2 Federated Provenance

When federated learning aggregation occurs:
- Each contributing site MUST register a DataSource for its model parameters
- The aggregation event MUST be recorded as a ProvenanceRecord with action `aggregate`
- The aggregated model MUST be registered as a new DataSource with references to contributing sites (by site identifier, not by patient data)

### 5.3 Cross-Site Lineage

Cross-site lineage queries MUST be answered through the federated coordination layer:
1. The requesting site sends a lineage query to the coordination layer
2. The coordination layer forwards the query to relevant sites
3. Each site returns its local lineage (without patient data)
4. The coordination layer merges the results into a unified lineage view

---

## 6. Provenance for Robot Procedures

### 6.1 Procedure Recording

When a robot agent executes a clinical procedure, the following provenance records MUST be created:
1. **Input registration**: Register the clinical data and imaging used to plan the procedure
2. **Procedure execution**: Record the procedure with input hashes from clinical data and output hashes from procedure evidence
3. **Evidence upload**: Register the procedure evidence (telemetry, images) as a new DataSource

### 6.2 Robot Agent Audit Trail

The combination of provenance records and audit ledger entries MUST provide a complete chain from clinical data retrieval through procedure execution to evidence recording, enabling full reconstruction of the robot's decision and action sequence.
