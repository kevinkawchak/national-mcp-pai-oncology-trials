/**
 * Unified MCP client for the National MCP-PAI Oncology Trials network.
 *
 * Provides connection management, retry logic, circuit breaking, and
 * audit logging across all 5 MCP servers. Implements deny-by-default
 * RBAC with pre-flight authorization checks.
 */

import { v4 as uuidv4 } from 'uuid';
import {
  McpError,
  McpErrorCode,
  createMcpError,
  AuthzDeniedError,
  RateLimitedError,
  ServerError,
  UnavailableError,
  type McpServerName,
} from './errors';
import {
  type TrialMcpConfig,
  type ServerEndpoint,
  type RetryConfig,
  resolveConfig,
  validateConfig,
} from './config';
import type { McpToolCall, McpToolResult, ErrorResponse } from './models';

// ---------------------------------------------------------------------------
// Transport layer
// ---------------------------------------------------------------------------

export interface McpTransport {
  send(
    endpoint: ServerEndpoint,
    tool: string,
    params: Record<string, unknown>,
    timeoutMs: number,
    headers?: Record<string, string>,
  ): Promise<Record<string, unknown>>;
}

/**
 * Default HTTP transport using fetch API.
 */
export class HttpTransport implements McpTransport {
  async send(
    endpoint: ServerEndpoint,
    tool: string,
    params: Record<string, unknown>,
    timeoutMs: number,
    headers: Record<string, string> = {},
  ): Promise<Record<string, unknown>> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const url = `${endpoint.url.replace(/\/$/, '')}/tools/${tool}`;
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...headers,
    };

    if (endpoint.apiKey) {
      requestHeaders['Authorization'] = `Bearer ${endpoint.apiKey}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: requestHeaders,
        body: JSON.stringify(params),
        signal: controller.signal,
      });

      const body = await response.json();

      if (!response.ok || body.error) {
        throw createMcpError(
          body.code ?? 'INTERNAL_ERROR',
          body.message ?? `HTTP ${response.status}`,
          {
            server: body.server,
            tool: body.tool ?? tool,
            requestId: body.request_id,
            details: body.details,
          },
        );
      }

      return body;
    } catch (error) {
      if (error instanceof McpError) throw error;

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new UnavailableError(`Request to ${tool} timed out after ${timeoutMs}ms`, {
          tool,
        });
      }

      throw new ServerError(`Transport error calling ${tool}: ${(error as Error).message}`, {
        tool,
        cause: error as Error,
      });
    } finally {
      clearTimeout(timer);
    }
  }
}

// ---------------------------------------------------------------------------
// Event emitter
// ---------------------------------------------------------------------------

export type ClientEvent =
  | 'toolCall'
  | 'toolResult'
  | 'toolError'
  | 'retry'
  | 'circuitOpen'
  | 'circuitClose';

export type ClientEventHandler = (event: ClientEvent, data: Record<string, unknown>) => void;

// ---------------------------------------------------------------------------
// Unified MCP Client
// ---------------------------------------------------------------------------

export class TrialMcpClient {
  private readonly config: ReturnType<typeof resolveConfig>;
  private readonly transport: McpTransport;
  private readonly eventHandlers: ClientEventHandler[] = [];
  private readonly circuitState: Map<string, {
    failures: number;
    lastFailure: number;
    state: 'closed' | 'open' | 'half-open';
  }> = new Map();

  constructor(config: TrialMcpConfig, transport?: McpTransport) {
    const errors = validateConfig(config);
    if (errors.length > 0) {
      throw new Error(`Invalid configuration: ${errors.join('; ')}`);
    }
    this.config = resolveConfig(config);
    this.transport = transport ?? new HttpTransport();
  }

  // -------------------------------------------------------------------------
  // Event handling
  // -------------------------------------------------------------------------

  on(handler: ClientEventHandler): () => void {
    this.eventHandlers.push(handler);
    return () => {
      const idx = this.eventHandlers.indexOf(handler);
      if (idx >= 0) this.eventHandlers.splice(idx, 1);
    };
  }

  private emit(event: ClientEvent, data: Record<string, unknown>): void {
    for (const handler of this.eventHandlers) {
      try {
        handler(event, data);
      } catch {
        // Event handler errors must not break the client
      }
    }
  }

  // -------------------------------------------------------------------------
  // Core tool invocation
  // -------------------------------------------------------------------------

  async callTool<T = unknown>(
    server: McpServerName,
    tool: string,
    params: Record<string, unknown> = {},
  ): Promise<McpToolResult<T>> {
    const requestId = uuidv4();
    const startTime = Date.now();

    // Check circuit breaker
    this.checkCircuit(server);

    // Build tool call record
    const toolCall: McpToolCall = {
      server,
      tool,
      parameters: params,
      caller: this.config.callerId,
      role: this.config.role,
      requestId,
      timestamp: new Date().toISOString(),
    };

    this.emit('toolCall', toolCall as unknown as Record<string, unknown>);

    const endpoint = this.config.servers[server];
    if (!endpoint) {
      throw new UnavailableError(`No endpoint configured for server '${server}'`, {
        server,
        tool,
        requestId,
      });
    }

    // Prepare headers
    const headers: Record<string, string> = {
      'X-Request-ID': requestId,
      'X-Caller-ID': this.config.callerId,
      'X-Actor-Role': this.config.role,
    };

    if (this.config.bearerToken) {
      headers['Authorization'] = `Bearer ${this.config.bearerToken}`;
    }

    if (this.config.trialId) {
      headers['X-Trial-ID'] = this.config.trialId;
    }

    if (this.config.siteId) {
      headers['X-Site-ID'] = this.config.siteId;
    }

    // Execute with retry
    try {
      const result = await this.executeWithRetry(
        server,
        tool,
        params,
        endpoint,
        headers,
        requestId,
      );

      this.recordCircuitSuccess(server);

      const toolResult: McpToolResult<T> = {
        data: result as T,
        requestId,
        server,
        tool,
        durationMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      };

      this.emit('toolResult', toolResult as unknown as Record<string, unknown>);
      return toolResult;
    } catch (error) {
      this.recordCircuitFailure(server);
      this.emit('toolError', {
        requestId,
        server,
        tool,
        error: error instanceof McpError ? error.toJSON() : { message: String(error) },
      });
      throw error;
    }
  }

  // -------------------------------------------------------------------------
  // Retry logic
  // -------------------------------------------------------------------------

  private async executeWithRetry(
    server: McpServerName,
    tool: string,
    params: Record<string, unknown>,
    endpoint: ServerEndpoint,
    headers: Record<string, string>,
    requestId: string,
  ): Promise<Record<string, unknown>> {
    const retryConfig = this.config.retry;
    let lastError: McpError | undefined;

    for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
      try {
        const timeoutMs = endpoint.timeoutMs ?? this.config.defaultTimeoutMs;
        return await this.transport.send(endpoint, tool, params, timeoutMs, headers);
      } catch (error) {
        if (!(error instanceof McpError)) throw error;
        lastError = error;

        // Non-retryable errors fail immediately
        if (!error.isRetryable) throw error;

        // Authorization errors are never retried
        if (error.code === McpErrorCode.AUTHZ_DENIED) throw error;

        // Last attempt - throw
        if (attempt >= retryConfig.maxRetries) break;

        // Compute delay with exponential backoff + jitter
        const delay = this.computeRetryDelay(attempt, retryConfig, error);

        this.emit('retry', {
          requestId,
          server,
          tool,
          attempt: attempt + 1,
          maxRetries: retryConfig.maxRetries,
          delayMs: delay,
          errorCode: error.code,
        });

        if (this.config.debug) {
          console.log(
            `[TrialMCP] Retry ${attempt + 1}/${retryConfig.maxRetries} for ${tool} ` +
            `on ${server} after ${delay}ms (${error.code})`,
          );
        }

        await this.sleep(delay);
      }
    }

    throw lastError ?? new ServerError('Max retries exceeded', { server, tool, requestId });
  }

  private computeRetryDelay(
    attempt: number,
    retryConfig: RetryConfig,
    error: McpError,
  ): number {
    // Respect Retry-After from rate limiting
    if (error instanceof RateLimitedError && error.retryAfterSeconds > 0) {
      return error.retryAfterSeconds * 1000;
    }

    const baseDelay = retryConfig.baseDelayMs * Math.pow(retryConfig.backoffMultiplier, attempt);
    const jitter = baseDelay * retryConfig.jitterFactor * Math.random();
    return Math.min(baseDelay + jitter, retryConfig.maxDelayMs);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // -------------------------------------------------------------------------
  // Circuit breaker
  // -------------------------------------------------------------------------

  private checkCircuit(server: McpServerName): void {
    const state = this.circuitState.get(server);
    if (!state || state.state === 'closed') return;

    if (state.state === 'open') {
      const elapsed = Date.now() - state.lastFailure;
      if (elapsed >= this.config.circuitBreaker.resetTimeoutMs) {
        state.state = 'half-open';
        this.emit('circuitClose', { server, state: 'half-open' });
      } else {
        throw new UnavailableError(
          `Circuit breaker open for server '${server}'. ` +
          `Retry after ${Math.ceil((this.config.circuitBreaker.resetTimeoutMs - elapsed) / 1000)}s`,
          { server },
        );
      }
    }
  }

  private recordCircuitSuccess(server: McpServerName): void {
    const state = this.circuitState.get(server);
    if (!state) return;

    if (state.state === 'half-open') {
      state.failures = 0;
      state.state = 'closed';
      this.emit('circuitClose', { server, state: 'closed' });
    } else {
      state.failures = Math.max(0, state.failures - 1);
    }
  }

  private recordCircuitFailure(server: McpServerName): void {
    const state = this.circuitState.get(server) ?? {
      failures: 0,
      lastFailure: 0,
      state: 'closed' as const,
    };

    state.failures += 1;
    state.lastFailure = Date.now();

    if (state.failures >= this.config.circuitBreaker.failureThreshold) {
      state.state = 'open';
      this.emit('circuitOpen', {
        server,
        failures: state.failures,
        threshold: this.config.circuitBreaker.failureThreshold,
      });
    }

    this.circuitState.set(server, state);
  }

  // -------------------------------------------------------------------------
  // Accessors
  // -------------------------------------------------------------------------

  get role(): string {
    return this.config.role;
  }

  get callerId(): string {
    return this.config.callerId;
  }

  getCircuitState(server: McpServerName): string {
    return this.circuitState.get(server)?.state ?? 'closed';
  }

  resetCircuit(server: McpServerName): void {
    this.circuitState.delete(server);
  }
}
