/**
 * NON-NORMATIVE Level 2 Illustrative Implementation — AuthZ MCP Server (TypeScript).
 *
 * Demonstrates a production-shaped authorization server satisfying
 * Level 1 (Core) conformance per spec/conformance.md.
 *
 * References:
 * 1. Kawchak, K. (2026). TrialMCP. DOI: 10.5281/zenodo.18869776
 * 2. Kawchak, K. (2026). Physical AI Oncology Trials. DOI: 10.5281/zenodo.18445179
 * 3. Kawchak, K. (2026). PAI Oncology Trial FL. DOI: 10.5281/zenodo.18840880
 */

import * as crypto from "crypto";
import { v4 as uuidv4 } from "uuid";

// ---------------------------------------------------------------------------
// Types
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

interface TokenMeta {
  role: string;
  issued_at: string;
  expires_at: string;
  revoked: boolean;
}

interface TokenIssuance {
  token_hash: string;
  role: string;
  issued_at: string;
  expires_at: string;
}

interface TokenValidation {
  valid: boolean;
  role?: string;
  reason?: string;
}

// ---------------------------------------------------------------------------
// Policy Matrix
// ---------------------------------------------------------------------------

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
// Token Store
// ---------------------------------------------------------------------------

const tokenStore: Map<string, TokenMeta> = new Map();

// ---------------------------------------------------------------------------
// AuthZ Server Implementation
// ---------------------------------------------------------------------------

export function authzEvaluate(
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

  return result;
}

export function authzIssueToken(
  role: string,
  expiresIn: number = 3600
): TokenIssuance {
  if (expiresIn > 86400) {
    expiresIn = 86400;
  }

  const raw = uuidv4().replace(/-/g, "");
  const tokenHash = crypto.createHash("sha256").update(raw).digest("hex");
  const now = new Date();
  const expiresAt = new Date(now.getTime() + expiresIn * 1000);

  tokenStore.set(tokenHash, {
    role,
    issued_at: now.toISOString(),
    expires_at: expiresAt.toISOString(),
    revoked: false,
  });

  return {
    token_hash: tokenHash,
    role,
    issued_at: now.toISOString(),
    expires_at: expiresAt.toISOString(),
  };
}

export function authzValidateToken(tokenHash: string): TokenValidation {
  const meta = tokenStore.get(tokenHash);
  if (!meta) {
    return { valid: false, reason: "TOKEN_NOT_FOUND" };
  }
  if (meta.revoked) {
    return { valid: false, reason: "TOKEN_REVOKED" };
  }
  if (new Date() > new Date(meta.expires_at)) {
    return { valid: false, reason: "TOKEN_EXPIRED" };
  }
  return { valid: true, role: meta.role };
}

export function authzRevokeToken(
  tokenHash: string
): { revoked: boolean; token_hash?: string; reason?: string } {
  const meta = tokenStore.get(tokenHash);
  if (!meta) {
    return { revoked: false, reason: "TOKEN_NOT_FOUND" };
  }
  meta.revoked = true;
  return { revoked: true, token_hash: tokenHash };
}

export { DEFAULT_POLICY };
