/**
 * Circuit breaker middleware for the National MCP-PAI Oncology Trials SDK.
 *
 * Implements the circuit breaker pattern to prevent cascading failures
 * across the 5 MCP servers. When a server exceeds its failure threshold,
 * the circuit opens and subsequent calls fail fast without hitting the
 * server, allowing it time to recover.
 *
 * States:
 *   CLOSED  - Normal operation, requests pass through
 *   OPEN    - Failing fast, no requests sent to server
 *   HALF_OPEN - Probe mode, limited requests to test recovery
 */

import { UnavailableError, isMcpError } from '../errors';
import type { CircuitBreakerConfig } from '../config';
import { DEFAULT_CIRCUIT_BREAKER_CONFIG } from '../config';
import type { McpServerName } from '../errors';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

export interface CircuitBreakerStats {
  state: CircuitState;
  failures: number;
  successes: number;
  totalRequests: number;
  lastFailureTime: number | null;
  lastSuccessTime: number | null;
  openedAt: number | null;
  halfOpenProbes: number;
}

export interface CircuitBreakerEvent {
  type: 'state_change' | 'request_blocked' | 'probe_success' | 'probe_failure';
  server: string;
  previousState?: CircuitState;
  newState?: CircuitState;
  timestamp: number;
}

export type CircuitBreakerListener = (event: CircuitBreakerEvent) => void;

export interface CircuitBreakerMiddlewareConfig extends CircuitBreakerConfig {
  /** Per-server overrides */
  serverOverrides: Partial<Record<McpServerName, Partial<CircuitBreakerConfig>>>;
  /** Event listener for state changes */
  onEvent?: CircuitBreakerListener;
}

// ---------------------------------------------------------------------------
// Per-server circuit
// ---------------------------------------------------------------------------

class ServerCircuit {
  private state: CircuitState = CircuitState.CLOSED;
  private failures: number = 0;
  private successes: number = 0;
  private totalRequests: number = 0;
  private halfOpenProbes: number = 0;
  private lastFailureTime: number | null = null;
  private lastSuccessTime: number | null = null;
  private openedAt: number | null = null;

  constructor(
    private readonly server: string,
    private readonly config: CircuitBreakerConfig,
    private readonly onEvent?: CircuitBreakerListener,
  ) {}

  getState(): CircuitState {
    return this.state;
  }

  getStats(): CircuitBreakerStats {
    return {
      state: this.state,
      failures: this.failures,
      successes: this.successes,
      totalRequests: this.totalRequests,
      lastFailureTime: this.lastFailureTime,
      lastSuccessTime: this.lastSuccessTime,
      openedAt: this.openedAt,
      halfOpenProbes: this.halfOpenProbes,
    };
  }

  /**
   * Check if a request should be allowed through.
   * Throws UnavailableError if circuit is open.
   */
  checkRequest(): void {
    this.totalRequests++;

    switch (this.state) {
      case CircuitState.CLOSED:
        return;

      case CircuitState.OPEN: {
        const elapsed = Date.now() - (this.openedAt ?? 0);
        if (elapsed >= this.config.resetTimeoutMs) {
          this.transitionTo(CircuitState.HALF_OPEN);
          this.halfOpenProbes = 0;
          return;
        }

        const remainingMs = this.config.resetTimeoutMs - elapsed;
        throw new UnavailableError(
          `Circuit breaker OPEN for '${this.server}'. ` +
            `${this.failures} consecutive failures. ` +
            `Retry after ${Math.ceil(remainingMs / 1000)}s.`,
          { server: this.server as McpServerName },
        );
      }

      case CircuitState.HALF_OPEN:
        // Allow limited probes
        return;
    }
  }

  /**
   * Record a successful request.
   */
  recordSuccess(): void {
    this.successes++;
    this.lastSuccessTime = Date.now();

    switch (this.state) {
      case CircuitState.HALF_OPEN:
        this.halfOpenProbes++;
        this.emitEvent({ type: 'probe_success', server: this.server, timestamp: Date.now() });

        if (this.halfOpenProbes >= this.config.successThreshold) {
          this.failures = 0;
          this.transitionTo(CircuitState.CLOSED);
        }
        break;

      case CircuitState.CLOSED:
        // Decay failure count on success
        this.failures = Math.max(0, this.failures - 1);
        break;
    }
  }

  /**
   * Record a failed request.
   */
  recordFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();

    switch (this.state) {
      case CircuitState.CLOSED:
        if (this.failures >= this.config.failureThreshold) {
          this.transitionTo(CircuitState.OPEN);
        }
        break;

      case CircuitState.HALF_OPEN:
        this.emitEvent({ type: 'probe_failure', server: this.server, timestamp: Date.now() });
        this.transitionTo(CircuitState.OPEN);
        break;
    }
  }

  /**
   * Force-reset the circuit to closed state.
   */
  reset(): void {
    this.failures = 0;
    this.halfOpenProbes = 0;
    this.transitionTo(CircuitState.CLOSED);
  }

  private transitionTo(newState: CircuitState): void {
    const previousState = this.state;
    this.state = newState;

    if (newState === CircuitState.OPEN) {
      this.openedAt = Date.now();
    }

    this.emitEvent({
      type: 'state_change',
      server: this.server,
      previousState,
      newState,
      timestamp: Date.now(),
    });
  }

  private emitEvent(event: CircuitBreakerEvent): void {
    if (this.onEvent) {
      try {
        this.onEvent(event);
      } catch {
        // Listener errors must not break the circuit
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Circuit Breaker Middleware
// ---------------------------------------------------------------------------

export class CircuitBreakerMiddleware {
  private readonly config: CircuitBreakerMiddlewareConfig;
  private readonly circuits: Map<string, ServerCircuit> = new Map();

  constructor(config: Partial<CircuitBreakerMiddlewareConfig> = {}) {
    this.config = {
      ...DEFAULT_CIRCUIT_BREAKER_CONFIG,
      serverOverrides: config.serverOverrides ?? {},
      onEvent: config.onEvent,
      ...config,
    };
  }

  /**
   * Execute a function through the circuit breaker for a given server.
   */
  async execute<T>(server: string, fn: () => Promise<T>): Promise<T> {
    const circuit = this.getOrCreateCircuit(server);

    circuit.checkRequest();

    try {
      const result = await fn();
      circuit.recordSuccess();
      return result;
    } catch (error) {
      if (isMcpError(error) && error.isRetryable) {
        circuit.recordFailure();
      }
      throw error;
    }
  }

  /**
   * Get the current state of a server's circuit.
   */
  getState(server: string): CircuitState {
    return this.circuits.get(server)?.getState() ?? CircuitState.CLOSED;
  }

  /**
   * Get statistics for a server's circuit.
   */
  getStats(server: string): CircuitBreakerStats | null {
    return this.circuits.get(server)?.getStats() ?? null;
  }

  /**
   * Get statistics for all tracked circuits.
   */
  getAllStats(): Record<string, CircuitBreakerStats> {
    const result: Record<string, CircuitBreakerStats> = {};
    for (const [server, circuit] of this.circuits) {
      result[server] = circuit.getStats();
    }
    return result;
  }

  /**
   * Force-reset a server's circuit to closed state.
   */
  reset(server: string): void {
    this.circuits.get(server)?.reset();
  }

  /**
   * Reset all circuits.
   */
  resetAll(): void {
    for (const circuit of this.circuits.values()) {
      circuit.reset();
    }
  }

  // -------------------------------------------------------------------------
  // Private
  // -------------------------------------------------------------------------

  private getOrCreateCircuit(server: string): ServerCircuit {
    let circuit = this.circuits.get(server);
    if (!circuit) {
      const serverConfig = {
        ...this.config,
        ...this.config.serverOverrides[server as McpServerName],
      };
      circuit = new ServerCircuit(server, serverConfig, this.config.onEvent);
      this.circuits.set(server, circuit);
    }
    return circuit;
  }
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export function createCircuitBreaker(
  config: Partial<CircuitBreakerMiddlewareConfig> = {},
): CircuitBreakerMiddleware {
  return new CircuitBreakerMiddleware(config);
}
