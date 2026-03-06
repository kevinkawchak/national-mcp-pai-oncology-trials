/**
 * NON-NORMATIVE Reference Implementation — Core (Level 1) MCP Server (TypeScript).
 *
 * Demonstrates the minimum viable MCP server satisfying Level 1 (Core)
 * conformance per spec/conformance.md.  Uses ajv for JSON Schema
 * validation against the schemas in /schemas/.
 *
 * This stub is INFORMATIVE — the normative requirements are in /spec/,
 * /schemas/, and /profiles/.
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
// AuthZ
// ---------------------------------------------------------------------------

interface AuthzDecision {
  decision: "ALLOW" | "DENY";
  role: string;
  tool: string;
  resource_id: string;
  reason: string;
  matching_rules: string[];
  timestamp: string;
}

function authzEvaluate(role: string, tool: string, resourceId = ""): AuthzDecision {
  const allowedTools = DEFAULT_POLICY[role] || [];
  const decision = allowedTools.includes(tool) ? "ALLOW" : "DENY";
  const result: AuthzDecision = {
    decision,
    role,
    tool,
    resource_id: resourceId,
    reason: `Role '${role}' is ${decision === "ALLOW" ? "permitted" : "denied"} access to tool '${tool}'.`,
    matching_rules: [`default_policy_${role}`],
    timestamp: new Date().toISOString(),
  };

  if (!validateAuthzDecision(result)) {
    console.error("AuthZ decision failed schema validation:", validateAuthzDecision.errors);
  }
  return result;
}

// ---------------------------------------------------------------------------
// Ledger
// ---------------------------------------------------------------------------

interface AuditRecord {
  record_id: string;
  timestamp: string;
  server: string;
  tool: string;
  caller: string;
  parameters: Record<string, unknown>;
  result_summary: string;
  prev_hash: string;
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
  prevHash: string = GENESIS_HASH,
  parameters: Record<string, unknown> = {}
): AuditRecord {
  const record: Record<string, unknown> = {
    record_id: uuidv4(),
    timestamp: new Date().toISOString(),
    server,
    tool,
    caller,
    parameters,
    result_summary: resultSummary,
    prev_hash: prevHash,
  };
  const hash = computeAuditHash(record, prevHash);
  const auditRecord = { ...record, hash } as AuditRecord;

  if (!validateAuditRecord(auditRecord)) {
    console.error("Audit record failed schema validation:", validateAuditRecord.errors);
  }
  return auditRecord;
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

function healthStatus(): Record<string, unknown> {
  const status = {
    server: "trialmcp-core-reference-ts",
    status: "healthy",
    version: "0.5.0",
    timestamp: new Date().toISOString(),
    uptime_seconds: 0,
    dependencies: {},
  };
  if (!validateHealthStatus(status)) {
    console.error("Health status failed schema validation:", validateHealthStatus.errors);
  }
  return status;
}

// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------

function errorResponse(code: string, message: string, tool = ""): Record<string, unknown> {
  const resp = {
    error: true,
    code,
    message,
    tool,
    timestamp: new Date().toISOString(),
  };
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
