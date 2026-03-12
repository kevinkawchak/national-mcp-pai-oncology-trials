# Oncology Clinical Trial Site Daily Automation Prompts

Two comprehensive Claude Code prompts for automating a single oncology
clinical trial site's complete daily operations using MCP servers,
Physical AI robots, federated learning, and generated synthetic data.

## Prompt Overview

| | Prompt A | Prompt B |
|---|---|---|
| **File** | `prompt_a_current_claude_code.md` | `prompt_b_future_claude_code.md` |
| **Target** | Today's Claude Code (Opus 4.6) | Future fully automated Claude Code |
| **Hours** | 06:00-22:00 (960 minutes) | 00:00-23:59 (1440 minutes) |
| **Human-in-Loop** | Required for safety gates, adverse events | Autonomous for validated procedures |
| **Concurrency** | Sequential operations | 3-8 parallel sub-agents |
| **Processing Time** | ~30-60 minutes (Opus 4.6) | Continuous 24-hour operation |

## Source Repositories

Both prompts draw from the complete architecture of three repositories:

1. **kevinkawchak/national-mcp-pai-oncology-trials** (v1.2.0)
   - 5 MCP servers: trialmcp-authz, trialmcp-fhir, trialmcp-dicom,
     trialmcp-ledger, trialmcp-provenance
   - 23 tool contracts, 8 safety modules, 13 JSON schemas
   - 381 files, ~69,800 LOC

2. **kevinkawchak/physical-ai-oncology-trials** (v2.2.0)
   - 10 robot types across 5 clinical categories
   - USL scoring framework (1.0-10.0 readiness)
   - 6 agentic AI examples, digital twin pipeline
   - 51 Python modules, 40,526 LOC

3. **kevinkawchak/pai-oncology-trial-fl** (v1.1.1)
   - Federated learning: FedAvg, FedProx, SCAFFOLD
   - Differential privacy, secure aggregation
   - Clinical analytics: survival, PK/PD, risk stratification
   - 235 Python modules, ~86,800 LOC

## Output Specification

Each prompt generates a CSV file with minute-by-minute entries covering:
- MCP server tool invocations (all 23 tools)
- Robot physical actions with quantitative parameters
- Patient interactions described in clinical detail
- Safety gate evaluations (5-gate matrix)
- Digital twin model states
- Federated learning round tracking
- Audit chain (SHA-256 hash-linked ledger)
- Provenance DAG (W3C PROV-aligned lineage)
- Regulatory compliance status (21 CFR Part 11, HIPAA, ICH E6(R3))

## Author

Kevin Kawchak, CEO, ChemicalQDevice
ORCID: https://orcid.org/0009-0007-5457-8667
Date: 2026-03-12
Version: v1.3.0-automation
