/**
 * Tests for the TypeScript AuthZ server implementation.
 */

import {
  authzEvaluate,
  authzIssueToken,
  authzValidateToken,
  authzRevokeToken,
  DEFAULT_POLICY,
} from "./authz-server";

// AuthZ Evaluate tests
describe("authzEvaluate", () => {
  test("allows permitted tool", () => {
    const result = authzEvaluate("auditor", "ledger_query");
    expect(result.allowed).toBe(true);
    expect(result.effect).toBe("ALLOW");
  });

  test("denies unpermitted tool", () => {
    const result = authzEvaluate("auditor", "fhir_read");
    expect(result.allowed).toBe(false);
    expect(result.effect).toBe("DENY");
  });

  test("denies unknown role", () => {
    const result = authzEvaluate("unknown_role", "fhir_read");
    expect(result.allowed).toBe(false);
    expect(result.effect).toBe("DENY");
  });

  test("returns ISO timestamp", () => {
    const result = authzEvaluate("auditor", "ledger_query");
    expect(result.evaluated_at).toContain("T");
  });

  test("returns matching rules for allow", () => {
    const result = authzEvaluate("auditor", "ledger_query");
    expect(result.matching_rules.length).toBeGreaterThan(0);
    expect(result.matching_rules[0]).toHaveProperty("role");
    expect(result.matching_rules[0]).toHaveProperty("effect");
  });

  test("returns empty matching rules for deny", () => {
    const result = authzEvaluate("auditor", "fhir_read");
    expect(result.matching_rules).toEqual([]);
  });

  test("includes deny_reason for denied requests", () => {
    const result = authzEvaluate("auditor", "fhir_read");
    expect(result.deny_reason).toBeDefined();
    expect(result.deny_reason!.length).toBeGreaterThan(0);
  });
});

// Token lifecycle tests
describe("token lifecycle", () => {
  test("issues token with hash", () => {
    const result = authzIssueToken("robot_agent");
    expect(result.token_hash).toHaveLength(64);
    expect(result.role).toBe("robot_agent");
  });

  test("validates issued token", () => {
    const issued = authzIssueToken("auditor");
    const result = authzValidateToken(issued.token_hash);
    expect(result.valid).toBe(true);
    expect(result.role).toBe("auditor");
  });

  test("returns not found for unknown token", () => {
    const result = authzValidateToken("nonexistent");
    expect(result.valid).toBe(false);
    expect(result.reason).toBe("TOKEN_NOT_FOUND");
  });

  test("revokes token", () => {
    const issued = authzIssueToken("sponsor");
    const revoked = authzRevokeToken(issued.token_hash);
    expect(revoked.revoked).toBe(true);
    const validation = authzValidateToken(issued.token_hash);
    expect(validation.valid).toBe(false);
    expect(validation.reason).toBe("TOKEN_REVOKED");
  });
});

// Policy matrix tests
describe("policy matrix", () => {
  test("has six roles", () => {
    expect(Object.keys(DEFAULT_POLICY)).toHaveLength(6);
  });
});
