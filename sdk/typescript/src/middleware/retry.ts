/**
 * Retry middleware for the National MCP-PAI Oncology Trials SDK.
 *
 * Provides configurable retry logic with exponential backoff,
 * jitter, and per-error-code policies. Designed for the MCP
 * server network where transient failures (RATE_LIMITED,
 * SERVER_ERROR, UNAVAILABLE) are expected under load.
 */

import {
  McpError,
  McpErrorCode,
  RateLimitedError,
  isRetryable,
  isMcpError,
} from '../errors';
import type { RetryConfig } from '../config';
import { DEFAULT_RETRY_CONFIG } from '../config';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RetryPolicy {
  /** Maximum retries for this error code (overrides global config) */
  maxRetries?: number;
  /** Fixed delay in ms (overrides backoff calculation) */
  fixedDelayMs?: number;
  /** Whether this error code should be retried at all */
  retry: boolean;
}

export interface RetryMiddlewareConfig extends RetryConfig {
  /** Per-error-code retry policies */
  policies: Partial<Record<McpErrorCode, RetryPolicy>>;
  /** Callback invoked before each retry attempt */
  onRetry?: (attempt: number, error: McpError, delayMs: number) => void;
  /** Callback invoked when all retries are exhausted */
  onExhausted?: (error: McpError, totalAttempts: number) => void;
}

export interface RetryResult<T> {
  data: T;
  attempts: number;
  totalDelayMs: number;
}

// ---------------------------------------------------------------------------
// Default per-code policies
// ---------------------------------------------------------------------------

const DEFAULT_POLICIES: Partial<Record<McpErrorCode, RetryPolicy>> = {
  [McpErrorCode.AUTHZ_DENIED]: { retry: false },
  [McpErrorCode.AUTHZ_EXPIRED]: { retry: false },
  [McpErrorCode.INVALID_INPUT]: { retry: false },
  [McpErrorCode.NOT_FOUND]: { retry: false },
  [McpErrorCode.CHAIN_BROKEN]: { retry: false },
  [McpErrorCode.PHI_LEAK]: { retry: false },
  [McpErrorCode.RATE_LIMITED]: { retry: true, maxRetries: 5 },
  [McpErrorCode.SERVER_ERROR]: { retry: true, maxRetries: 3 },
  [McpErrorCode.UNAVAILABLE]: { retry: true, maxRetries: 3 },
};

// ---------------------------------------------------------------------------
// Retry Middleware
// ---------------------------------------------------------------------------

export class RetryMiddleware {
  private readonly config: RetryMiddlewareConfig;

  constructor(config: Partial<RetryMiddlewareConfig> = {}) {
    this.config = {
      ...DEFAULT_RETRY_CONFIG,
      ...config,
      policies: {
        ...DEFAULT_POLICIES,
        ...config.policies,
      },
    };
  }

  /**
   * Execute a function with retry logic.
   *
   * The function is retried on transient errors with exponential
   * backoff and jitter. Non-retryable errors (AUTHZ_DENIED,
   * INVALID_INPUT, etc.) are thrown immediately.
   *
   * @param fn - Async function to execute
   * @returns Result with retry metadata
   */
  async execute<T>(fn: () => Promise<T>): Promise<RetryResult<T>> {
    let lastError: McpError | undefined;
    let totalDelayMs = 0;

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        const data = await fn();
        return { data, attempts: attempt + 1, totalDelayMs };
      } catch (error) {
        if (!isMcpError(error)) throw error;
        lastError = error;

        // Check per-code policy
        if (!this.shouldRetry(error, attempt)) {
          break;
        }

        // Last attempt
        if (attempt >= this.getMaxRetries(error)) {
          break;
        }

        const delay = this.computeDelay(attempt, error);
        totalDelayMs += delay;

        if (this.config.onRetry) {
          this.config.onRetry(attempt + 1, error, delay);
        }

        await this.sleep(delay);
      }
    }

    if (this.config.onExhausted && lastError) {
      this.config.onExhausted(lastError, this.getMaxRetries(lastError) + 1);
    }

    throw lastError;
  }

  /**
   * Wrap a function to add retry behavior.
   * Returns a new function with built-in retry logic.
   */
  wrap<TArgs extends unknown[], TResult>(
    fn: (...args: TArgs) => Promise<TResult>,
  ): (...args: TArgs) => Promise<RetryResult<TResult>> {
    return async (...args: TArgs) => {
      return this.execute(() => fn(...args));
    };
  }

  /**
   * Check if an error should be retried based on policy.
   */
  shouldRetry(error: McpError, attempt: number): boolean {
    const policy = this.config.policies[error.code];

    if (policy && !policy.retry) return false;
    if (!isRetryable(error)) return false;

    return attempt < this.getMaxRetries(error);
  }

  /**
   * Get the maximum retry count for a given error.
   */
  getMaxRetries(error: McpError): number {
    const policy = this.config.policies[error.code];
    return policy?.maxRetries ?? this.config.maxRetries;
  }

  /**
   * Compute the delay before the next retry attempt.
   */
  computeDelay(attempt: number, error: McpError): number {
    // Check for fixed delay in policy
    const policy = this.config.policies[error.code];
    if (policy?.fixedDelayMs !== undefined) {
      return policy.fixedDelayMs;
    }

    // Respect Retry-After header from rate limiting
    if (error instanceof RateLimitedError && error.retryAfterSeconds > 0) {
      return error.retryAfterSeconds * 1000;
    }

    // Exponential backoff with jitter
    const baseDelay =
      this.config.baseDelayMs * Math.pow(this.config.backoffMultiplier, attempt);
    const jitter = baseDelay * this.config.jitterFactor * Math.random();
    return Math.min(baseDelay + jitter, this.config.maxDelayMs);
  }

  // -------------------------------------------------------------------------
  // Private
  // -------------------------------------------------------------------------

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ---------------------------------------------------------------------------
// Convenience factory
// ---------------------------------------------------------------------------

/**
 * Create a retry middleware with sensible defaults for the MCP network.
 */
export function createRetryMiddleware(
  overrides: Partial<RetryMiddlewareConfig> = {},
): RetryMiddleware {
  return new RetryMiddleware(overrides);
}

/**
 * Create a retry middleware tuned for high-throughput robot agent workloads.
 */
export function createRobotAgentRetry(): RetryMiddleware {
  return new RetryMiddleware({
    maxRetries: 5,
    baseDelayMs: 500,
    maxDelayMs: 15000,
    backoffMultiplier: 1.5,
    jitterFactor: 0.2,
    policies: {
      ...DEFAULT_POLICIES,
      [McpErrorCode.RATE_LIMITED]: { retry: true, maxRetries: 8 },
      [McpErrorCode.SERVER_ERROR]: { retry: true, maxRetries: 5 },
    },
  });
}

/**
 * Create a retry middleware with no retries (for testing or one-shot operations).
 */
export function createNoRetry(): RetryMiddleware {
  return new RetryMiddleware({ maxRetries: 0, policies: {} });
}
