# Quickstart Demo — National MCP-PAI Oncology Trials

5-minute local demo that starts all 5 MCP servers and executes a complete robot-assisted oncology trial workflow.

## Prerequisites

- Python 3.10 or later
- Clone this repository

## Quick Start

```bash
# From the repository root:
pip install -e .

# Run the demo:
python examples/quickstart/run_demo.py
```

## What the Demo Does

The demo executes the following workflow across all 5 MCP servers:

1. **Authorization (trialmcp-authz)** — Robot agent requests and validates a bearer token
2. **FHIR Read (trialmcp-fhir)** — De-identified patient data is read with HIPAA Safe Harbor applied
3. **DICOM Query (trialmcp-dicom)** — CT imaging studies are queried with patient name hashing
4. **Audit Ledger (trialmcp-ledger)** — Hash-chained audit record is appended and chain verified
5. **Provenance (trialmcp-provenance)** — Data lineage is recorded and DAG verified

## Demo Data

- `demo_data/fhir_bundle.json` — Synthetic FHIR Bundle with 2 patients and 1 research study
- `demo_data/dicom_metadata.json` — Synthetic DICOM study metadata (CT, MR, PT)
- `demo_data/site_profile.json` — Sample site capability profile

## Docker

```bash
# Build and run with Docker Compose:
cd deploy
docker-compose up
```
