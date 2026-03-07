/**
 * NON-NORMATIVE Level 2 Illustrative Implementation — Ledger MCP Server (TypeScript).
 *
 * Demonstrates a production-shaped audit ledger server with hash-chained
 * immutable records satisfying spec/audit.md requirements.
 *
 * References:
 * 1. Kawchak, K. (2026). TrialMCP. DOI: 10.5281/zenodo.18869776
 * 2. Kawchak, K. (2026). Physical AI Oncology Trials. DOI: 10.5281/zenodo.18445179
 * 3. Kawchak, K. (2026). PAI Oncology Trial FL. DOI: 10.5281/zenodo.18840880
 */

import * as crypto from "crypto";
import { v4 as uuidv4 } from "uuid";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GENESIS_HASH = "0".repeat(64);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AuditRecord {
  audit_id: string;
  timestamp: string;
  server: string;
  tool: string;
  caller: string;
  parameters: Record<string, unknown>;
  result_summary: string;
  previous_hash: string;
  hash: string;
}

interface VerifyResult {
  valid: boolean;
  reason?: string;
  length?: number;
  index?: number;
}

// ---------------------------------------------------------------------------
// Core Functions
// ---------------------------------------------------------------------------

function canonicalJson(record: Record<string, unknown>): string {
  const filtered: Record<string, unknown> = {};
  for (const key of Object.keys(record).sort()) {
    if (key !== "hash") {
      filtered[key] = record[key];
    }
  }
  return JSON.stringify(filtered);
}

function computeAuditHash(
  record: Record<string, unknown>,
  prevHash: string
): string {
  const canonical = canonicalJson(record);
  return crypto
    .createHash("sha256")
    .update(prevHash + canonical)
    .digest("hex");
}

// ---------------------------------------------------------------------------
// Audit Chain
// ---------------------------------------------------------------------------

class AuditChain {
  private chain: AuditRecord[] = [];
  private lastHash: string = GENESIS_HASH;

  get length(): number {
    return this.chain.length;
  }

  append(
    server: string,
    tool: string,
    caller: string,
    resultSummary: string,
    parameters: Record<string, unknown> = {}
  ): AuditRecord {
    const record: Record<string, unknown> = {
      audit_id: uuidv4(),
      timestamp: new Date().toISOString(),
      server,
      tool,
      caller,
      parameters,
      result_summary: resultSummary,
      previous_hash: this.lastHash,
    };

    const hash = computeAuditHash(record, this.lastHash);
    const auditRecord = { ...record, hash } as AuditRecord;
    this.chain.push(auditRecord);
    this.lastHash = hash;
    return auditRecord;
  }

  verify(): VerifyResult {
    if (this.chain.length === 0) {
      return { valid: false, reason: "EMPTY_CHAIN" };
    }

    let prev = GENESIS_HASH;
    for (let i = 0; i < this.chain.length; i++) {
      const record = this.chain[i];
      const expected = computeAuditHash(
        record as unknown as Record<string, unknown>,
        prev
      );
      if (record.hash !== expected) {
        return { valid: false, reason: `HASH_MISMATCH at index ${i}`, index: i };
      }
      if (record.previous_hash !== prev) {
        return {
          valid: false,
          reason: `PREV_HASH_MISMATCH at index ${i}`,
          index: i,
        };
      }
      prev = record.hash;
    }
    return { valid: true, length: this.chain.length };
  }

  query(
    filters: { server?: string; tool?: string; caller?: string } = {},
    limit: number = 100
  ): AuditRecord[] {
    let results = [...this.chain];
    if (filters.server) {
      results = results.filter((r) => r.server === filters.server);
    }
    if (filters.tool) {
      results = results.filter((r) => r.tool === filters.tool);
    }
    if (filters.caller) {
      results = results.filter((r) => r.caller === filters.caller);
    }
    return results.slice(0, limit);
  }

  export(): AuditRecord[] {
    return [...this.chain];
  }
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

export {
  AuditChain,
  computeAuditHash,
  canonicalJson,
  GENESIS_HASH,
};
export type { AuditRecord, VerifyResult };
