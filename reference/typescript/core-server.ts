/**
 * NON-NORMATIVE Level 1 Illustrative Implementation -- Core MCP Server (TypeScript).
 *
 * Demonstrates the minimum viable MCP server satisfying Level 1 (Core)
 * conformance per spec/conformance.md.  Uses ajv for JSON Schema
 * validation against the schemas in /schemas/.
 *
 * IMPORTANT: This is an illustrative implementation only.  It is
 * provided to demonstrate schema-compliant payload shapes and is not
 * suitable for production deployment.  The normative requirements are
 * defined in /spec/, /schemas/, and /profiles/.
 *
 * References:
 * 1. Kawchak, K. (2026). TrialMCP. DOI: 10.5281/zenodo.18869776
 * 2. Kawchak, K. (2026). Physical AI Oncology Trials. DOI: 10.5281/zenodo.18445179
 * 3. Kawchak, K. (2026). PAI Oncology Trial FL. DOI: 10.5281/zenodo.18840880
 */

import * as crypto from "crypto";
import * as fs from "fs";
import * as path from "path";
import Ajv from "ajv";
import { v4 as uuidv4 } from "uuid";

// ---------------------------------------------------------------------------
// Schema Validator
// ---------------------------------------------------------------------------

const SCHEMA_DIR = path.resolve(__dirname, "..", "..", "schemas");

const ajv = new Ajv({ allErrors: true });

/**
 * Load and compile a JSON Schema from the repository's /schemas/ directory.
 */
function loadSchema(name: string): ReturnType<typeof ajv.compile> {
  const filePath = path.join(SCHEMA_DIR, `${name}.schema.json`);
  const schema = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  return ajv.compile(schema);
}

// Pre-compile commonly used validators
const validateAuditRecord = loadSchema("audit-record");
const validateAuthzDecision = loadSchema("authz-decision");
const validateErrorResponse = loadSchema("error-response");
const validateHealthStatus = loadSchema("health-status");

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GENESIS_HASH = "0".repeat(64);

/** Deny-by-default policy matrix per spec/actor-model.md. */
const DEFAULT_POLICY: Record<string, string[]> = {
  robot_agent: [
    "fhir_read",
    "dicom_query",
    "dicom_retrieve_pointer",
    "ledger_append",
    "provenance_record_access",
  ],
  trial_coordinator: [
    "fhir_read",
    "fhir_search",
    "fhir_patient_lookup",
    "fhir_study_status",
    "dicom_query",
    "dicom_retrieve_pointer",
    "dicom_study_metadata",
    "authz_list_policies",
  ],
  data_monitor: ["fhir_read", "fhir_search", "dicom_query", "dicom_study_metadata"],
  auditor: ["ledger_query", "ledger_verify", "ledger_replay", "ledger_chain_status"],
  sponsor: ["authz_list_policies"],
  cro: ["authz_list_policies", "fhir_study_status"],
};

// ---------------------------------------------------------------------------
// AuthZ — aligned to schemas/authz-decision.schema.json
// ---------------------------------------------------------------------------

interface MatchingRule {
  role: string;
  server: string;
  tool: string;
  effect: "ALLOW" | "DENY";
}

interface AuthzDecision {
  allowed: boolean;
  effect: "ALLOW" | "DENY";
  role: string;
  server: string;
  tool: string;
  matching_rules: MatchingRule[];
  evaluated_at: string;
  deny_reason?: string;
}

function authzEvaluate(
  role: string,
  tool: string,
  server: string = "trialmcp-authz"
): AuthzDecision {
  const allowedTools = DEFAULT_POLICY[role] || [];
  const effect = allowedTools.includes(tool) ? "ALLOW" : "DENY";
  const allowed = effect === "ALLOW";
  const result: AuthzDecision = {
    allowed,
    effect,
    role,
    server,
    tool,
    matching_rules: allowed
      ? [{ role, server, tool, effect: "ALLOW" }]
      : [],
    evaluated_at: new Date().toISOString(),
  };

  if (!allowed) {
    result.deny_reason = `Role '${role}' is denied access to tool '${tool}' by default policy.`;
  }

  if (!validateAuthzDecision(result)) {
    console.error("AuthZ decision failed schema validation:", validateAuthzDecision.errors);
  }
  return result;
}

// ---------------------------------------------------------------------------
// Ledger — aligned to schemas/audit-record.schema.json
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

function canonicalJson(record: Record<string, unknown>): string {
  const filtered: Record<string, unknown> = {};
  for (const key of Object.keys(record).sort()) {
    if (key !== "hash") {
      filtered[key] = record[key];
    }
  }
  return JSON.stringify(filtered);
}

function computeAuditHash(record: Record<string, unknown>, prevHash: string): string {
  const canonical = canonicalJson(record);
  return crypto.createHash("sha256").update(prevHash + canonical).digest("hex");
}

function ledgerAppend(
  server: string,
  tool: string,
  caller: string,
  resultSummary: string,
  previousHash: string = GENESIS_HASH,
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
    previous_hash: previousHash,
  };
  const hash = computeAuditHash(record, previousHash);
  const auditRecord = { ...record, hash } as AuditRecord;

  if (!validateAuditRecord(auditRecord)) {
    console.error("Audit record failed schema validation:", validateAuditRecord.errors);
  }
  return auditRecord;
}

// ---------------------------------------------------------------------------
// Health — aligned to schemas/health-status.schema.json
// ---------------------------------------------------------------------------

interface HealthStatus {
  server_name: string;
  status: string;
  version: string;
  uptime_seconds: number;
  checked_at: string;
  dependencies: Array<{ name: string; status: string; latency_ms?: number }>;
}

function healthStatus(serverName: string = "trialmcp-ledger"): HealthStatus {
  const status: HealthStatus = {
    server_name: serverName,
    status: "healthy",
    version: "0.6.0",
    uptime_seconds: 0,
    checked_at: new Date().toISOString(),
    dependencies: [],
  };
  if (!validateHealthStatus(status)) {
    console.error("Health status failed schema validation:", validateHealthStatus.errors);
  }
  return status;
}

// ---------------------------------------------------------------------------
// Error — aligned to schemas/error-response.schema.json
// ---------------------------------------------------------------------------

function errorResponse(
  code: string,
  message: string,
  tool: string = "",
  server: string = ""
): Record<string, unknown> {
  const resp: Record<string, unknown> = {
    error: true,
    code,
    message,
  };
  if (server) {
    resp.server = server;
  }
  if (tool) {
    resp.tool = tool;
  }
  resp.timestamp = new Date().toISOString();

  if (!validateErrorResponse(resp)) {
    console.error("Error response failed schema validation:", validateErrorResponse.errors);
  }
  return resp;
}

// ---------------------------------------------------------------------------
// Exports (for programmatic use)
// ---------------------------------------------------------------------------

export {
  authzEvaluate,
  ledgerAppend,
  computeAuditHash,
  healthStatus,
  errorResponse,
  GENESIS_HASH,
  DEFAULT_POLICY,
};
