/**
 * Tests for the unified TrialMcpClient.
 *
 * Validates connection management, retry logic, circuit breaking,
 * event handling, and configuration validation.
 */

import { TrialMcpClient, type McpTransport } from '../src/client';
import type { ServerEndpoint, TrialMcpConfig } from '../src/config';
import {
  McpError,
  McpErrorCode,
  ServerError,
  AuthzDeniedError,
  RateLimitedError,
  UnavailableError,
} from '../src/errors';

// ---------------------------------------------------------------------------
// Mock transport
// ---------------------------------------------------------------------------

class MockTransport implements McpTransport {
  public calls: Array<{
    endpoint: ServerEndpoint;
    tool: string;
    params: Record<string, unknown>;
    timeoutMs: number;
    headers?: Record<string, string>;
  }> = [];

  public responses: Record<string, unknown>[] = [];
  public errors: Error[] = [];
  private callIndex = 0;

  async send(
    endpoint: ServerEndpoint,
    tool: string,
    params: Record<string, unknown>,
    timeoutMs: number,
    headers?: Record<string, string>,
  ): Promise<Record<string, unknown>> {
    this.calls.push({ endpoint, tool, params, timeoutMs, headers });

    const idx = this.callIndex++;
    if (idx < this.errors.length && this.errors[idx]) {
      throw this.errors[idx];
    }
    return this.responses[idx] ?? { success: true };
  }

  reset(): void {
    this.calls = [];
    this.responses = [];
    this.errors = [];
    this.callIndex = 0;
  }
}

// ---------------------------------------------------------------------------
// Test config factory
// ---------------------------------------------------------------------------

function createTestConfig(overrides: Partial<TrialMcpConfig> = {}): TrialMcpConfig {
  return {
    role: 'robot_agent',
    callerId: 'test-robot-001',
    servers: {
      'trialmcp-authz': { url: 'https://authz.test.local' },
      'trialmcp-fhir': { url: 'https://fhir.test.local' },
      'trialmcp-dicom': { url: 'https://dicom.test.local' },
      'trialmcp-ledger': { url: 'https://ledger.test.local' },
      'trialmcp-provenance': { url: 'https://prov.test.local' },
    },
    retry: { maxRetries: 2, baseDelayMs: 10, maxDelayMs: 50, jitterFactor: 0 },
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('TrialMcpClient', () => {
  let transport: MockTransport;

  beforeEach(() => {
    transport = new MockTransport();
  });

  describe('construction', () => {
    it('should create a client with valid config', () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      expect(client.role).toBe('robot_agent');
      expect(client.callerId).toBe('test-robot-001');
    });

    it('should reject invalid config with no servers', () => {
      expect(() => {
        new TrialMcpClient(
          { role: 'robot_agent', callerId: 'test', servers: {} },
          transport,
        );
      }).toThrow('Invalid configuration');
    });

    it('should reject invalid role', () => {
      expect(() => {
        new TrialMcpClient(
          createTestConfig({ role: 'invalid_role' as any }),
          transport,
        );
      }).toThrow('Invalid configuration');
    });

    it('should reject empty callerId', () => {
      expect(() => {
        new TrialMcpClient(
          createTestConfig({ callerId: '' }),
          transport,
        );
      }).toThrow('Invalid configuration');
    });

    it('should reject invalid server URL', () => {
      expect(() => {
        new TrialMcpClient(
          createTestConfig({
            servers: { 'trialmcp-authz': { url: 'not-a-url' } },
          }),
          transport,
        );
      }).toThrow('Invalid configuration');
    });
  });

  describe('callTool', () => {
    it('should send tool call to correct server', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.responses = [{ result: 'ok' }];

      const result = await client.callTool('trialmcp-fhir', 'fhir_read', {
        resource_type: 'Patient',
        resource_id: 'test-123',
      });

      expect(result.server).toBe('trialmcp-fhir');
      expect(result.tool).toBe('fhir_read');
      expect(result.data).toEqual({ result: 'ok' });
      expect(result.requestId).toBeDefined();
      expect(result.durationMs).toBeGreaterThanOrEqual(0);

      expect(transport.calls).toHaveLength(1);
      expect(transport.calls[0].tool).toBe('fhir_read');
      expect(transport.calls[0].params).toEqual({
        resource_type: 'Patient',
        resource_id: 'test-123',
      });
    });

    it('should include caller headers', async () => {
      const client = new TrialMcpClient(
        createTestConfig({ trialId: 'NCT-001', siteId: 'site-01' }),
        transport,
      );
      transport.responses = [{ ok: true }];

      await client.callTool('trialmcp-fhir', 'fhir_read', {});

      const headers = transport.calls[0].headers!;
      expect(headers['X-Request-ID']).toBeDefined();
      expect(headers['X-Caller-ID']).toBe('test-robot-001');
      expect(headers['X-Actor-Role']).toBe('robot_agent');
      expect(headers['X-Trial-ID']).toBe('NCT-001');
      expect(headers['X-Site-ID']).toBe('site-01');
    });

    it('should include bearer token if configured', async () => {
      const client = new TrialMcpClient(
        createTestConfig({ bearerToken: 'my-token-123' }),
        transport,
      );
      transport.responses = [{ ok: true }];

      await client.callTool('trialmcp-authz', 'authz_evaluate', {});

      expect(transport.calls[0].headers!['Authorization']).toBe('Bearer my-token-123');
    });

    it('should throw UnavailableError for unconfigured server', async () => {
      const client = new TrialMcpClient(
        createTestConfig({ servers: { 'trialmcp-authz': { url: 'https://authz.test.local' } } }),
        transport,
      );

      await expect(
        client.callTool('trialmcp-fhir', 'fhir_read', {}),
      ).rejects.toThrow(UnavailableError);
    });
  });

  describe('retry logic', () => {
    it('should retry on retryable errors', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.errors = [
        new ServerError('temporary failure'),
        new ServerError('temporary failure'),
      ];
      transport.responses = [
        {} as any,
        {} as any,
        { recovered: true },
      ];

      const result = await client.callTool('trialmcp-fhir', 'fhir_read', {});

      expect(result.data).toEqual({ recovered: true });
      expect(transport.calls).toHaveLength(3); // original + 2 retries
    });

    it('should not retry non-retryable errors', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.errors = [
        new AuthzDeniedError('access denied'),
      ];

      await expect(
        client.callTool('trialmcp-authz', 'authz_evaluate', {}),
      ).rejects.toThrow(AuthzDeniedError);

      expect(transport.calls).toHaveLength(1); // No retries
    });

    it('should exhaust retries and throw', async () => {
      const client = new TrialMcpClient(
        createTestConfig({ retry: { maxRetries: 2, baseDelayMs: 1, maxDelayMs: 5, jitterFactor: 0, backoffMultiplier: 1 } }),
        transport,
      );
      transport.errors = [
        new ServerError('fail 1'),
        new ServerError('fail 2'),
        new ServerError('fail 3'),
      ];

      await expect(
        client.callTool('trialmcp-fhir', 'fhir_read', {}),
      ).rejects.toThrow(ServerError);

      expect(transport.calls).toHaveLength(3);
    });
  });

  describe('circuit breaker', () => {
    it('should track circuit state per server', () => {
      const client = new TrialMcpClient(createTestConfig(), transport);

      expect(client.getCircuitState('trialmcp-fhir')).toBe('closed');
    });

    it('should allow resetting circuit state', () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      client.resetCircuit('trialmcp-fhir');
      expect(client.getCircuitState('trialmcp-fhir')).toBe('closed');
    });
  });

  describe('event handling', () => {
    it('should emit toolCall events', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.responses = [{ ok: true }];

      const events: Array<{ event: string; data: Record<string, unknown> }> = [];
      client.on((event, data) => events.push({ event, data }));

      await client.callTool('trialmcp-fhir', 'fhir_read', {});

      const toolCallEvent = events.find((e) => e.event === 'toolCall');
      expect(toolCallEvent).toBeDefined();
      expect(toolCallEvent!.data.tool).toBe('fhir_read');
    });

    it('should emit toolResult events on success', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.responses = [{ result: 42 }];

      const events: string[] = [];
      client.on((event) => events.push(event));

      await client.callTool('trialmcp-fhir', 'fhir_read', {});

      expect(events).toContain('toolCall');
      expect(events).toContain('toolResult');
    });

    it('should emit toolError events on failure', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.errors = [new AuthzDeniedError('denied')];

      const events: string[] = [];
      client.on((event) => events.push(event));

      await expect(
        client.callTool('trialmcp-fhir', 'fhir_read', {}),
      ).rejects.toThrow();

      expect(events).toContain('toolCall');
      expect(events).toContain('toolError');
    });

    it('should support unsubscribing', async () => {
      const client = new TrialMcpClient(createTestConfig(), transport);
      transport.responses = [{ ok: true }, { ok: true }];

      let callCount = 0;
      const unsubscribe = client.on(() => { callCount++; });

      await client.callTool('trialmcp-fhir', 'fhir_read', {});
      expect(callCount).toBeGreaterThan(0);

      const countAfterFirst = callCount;
      unsubscribe();

      await client.callTool('trialmcp-fhir', 'fhir_read', {});
      expect(callCount).toBe(countAfterFirst); // No new events
    });
  });
});
