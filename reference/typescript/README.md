# NON-NORMATIVE TypeScript Reference Implementation

> **Status**: NON-NORMATIVE — Informative reference only.  The
> authoritative requirements are defined in `/spec/`, `/schemas/`,
> and `/profiles/`.

This directory contains a minimal TypeScript stub that demonstrates
how to implement a Level 1 (Core) MCP server conforming to the
National MCP-PAI Oncology Trials Standard with
[ajv](https://ajv.js.org/) schema validation.

## Files

| File | Purpose |
|------|---------|
| `core-server.ts` | Minimal Core server stub (AuthZ + Ledger) |
| `package.json` | Dependencies (ajv, uuid) |
| `tsconfig.json` | TypeScript configuration |

## Quick Start

```bash
cd reference/typescript
npm install
npx tsc
node dist/core-server.js
```

## Schema Validation

The server uses [ajv](https://ajv.js.org/) to validate all inputs and
outputs against the 13 JSON schemas in `/schemas/`.  This ensures
conformance with the machine-readable data contracts defined by the
national standard.

## References

1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems*. DOI: [10.5281/zenodo.18869776](https://doi.org/10.5281/zenodo.18869776)
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End Framework for Robotic Systems in Clinical Trials*. DOI: [10.5281/zenodo.18445179](https://doi.org/10.5281/zenodo.18445179)
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning for Physical AI Oncology Trials*. DOI: [10.5281/zenodo.18840880](https://doi.org/10.5281/zenodo.18840880)

## Related

- [kevinkawchak/mcp-pai-oncology-trials](https://github.com/kevinkawchak/mcp-pai-oncology-trials) — Reference implementation
- [kevinkawchak/physical-ai-oncology-trials](https://github.com/kevinkawchak/physical-ai-oncology-trials) — Physical AI framework
- [kevinkawchak/pai-oncology-trial-fl](https://github.com/kevinkawchak/pai-oncology-trial-fl) — Federated learning framework
