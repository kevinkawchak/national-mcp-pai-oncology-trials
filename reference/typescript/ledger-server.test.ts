/**
 * Tests for the TypeScript Ledger server implementation.
 */

import { AuditChain, GENESIS_HASH, computeAuditHash } from "./ledger-server";

describe("AuditChain", () => {
  let chain: InstanceType<typeof AuditChain>;

  beforeEach(() => {
    chain = new AuditChain();
  });

  test("starts empty", () => {
    expect(chain.length).toBe(0);
  });

  test("appends records", () => {
    chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK");
    expect(chain.length).toBe(1);
  });

  test("chain links records", () => {
    const r1 = chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK");
    const r2 = chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK2");
    expect(r2.previous_hash).toBe(r1.hash);
  });

  test("verifies valid chain", () => {
    chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK");
    chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK2");
    const result = chain.verify();
    expect(result.valid).toBe(true);
    expect(result.length).toBe(2);
  });

  test("reports empty chain", () => {
    const result = chain.verify();
    expect(result.valid).toBe(false);
    expect(result.reason).toBe("EMPTY_CHAIN");
  });

  test("queries by server", () => {
    chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK");
    chain.append("trialmcp-fhir", "fhir_read", "user1", "OK");
    const results = chain.query({ server: "trialmcp-authz" });
    expect(results).toHaveLength(1);
  });

  test("exports all records", () => {
    chain.append("trialmcp-authz", "authz_evaluate", "user1", "OK");
    chain.append("trialmcp-ledger", "ledger_append", "user1", "OK");
    const exported = chain.export();
    expect(exported).toHaveLength(2);
  });
});

describe("computeAuditHash", () => {
  test("is deterministic", () => {
    const record = { server: "trialmcp-authz", tool: "test", caller: "user" };
    const h1 = computeAuditHash(record, GENESIS_HASH);
    const h2 = computeAuditHash(record, GENESIS_HASH);
    expect(h1).toBe(h2);
  });

  test("produces 64-char hex", () => {
    const record = { server: "trialmcp-authz", tool: "test", caller: "user" };
    const h = computeAuditHash(record, GENESIS_HASH);
    expect(h).toHaveLength(64);
    expect(h).toMatch(/^[0-9a-f]{64}$/);
  });
});

describe("GENESIS_HASH", () => {
  test("is 64 zeros", () => {
    expect(GENESIS_HASH).toBe("0".repeat(64));
  });
});
