/**
 * Client configuration for the National MCP-PAI Oncology Trials SDK.
 *
 * Provides typed configuration for connecting to the 5 MCP servers
 * (AuthZ, FHIR, DICOM, Ledger, Provenance) with support for
 * multi-site deployments, mTLS, and retry policies.
 */

import type { McpServerName } from './errors';

// ---------------------------------------------------------------------------
// Actor roles from spec/actor-model.md
// ---------------------------------------------------------------------------

export type ActorRole =
  | 'robot_agent'
  | 'trial_coordinator'
  | 'data_monitor'
  | 'auditor'
  | 'sponsor'
  | 'cro';

export const ACTOR_ROLES: readonly ActorRole[] = [
  'robot_agent',
  'trial_coordinator',
  'data_monitor',
  'auditor',
  'sponsor',
  'cro',
] as const;

// ---------------------------------------------------------------------------
// Server endpoint configuration
// ---------------------------------------------------------------------------

export interface ServerEndpoint {
  /** Base URL for the MCP server (e.g. https://authz.trialmcp.example.org) */
  url: string;
  /** Optional API key or bearer token for the server */
  apiKey?: string;
  /** Connection timeout in milliseconds */
  timeoutMs?: number;
  /** Whether to verify TLS certificates (default: true) */
  tlsVerify?: boolean;
  /** Path to client certificate for mTLS */
  clientCertPath?: string;
  /** Path to client key for mTLS */
  clientKeyPath?: string;
  /** Path to CA bundle for custom certificate authorities */
  caBundlePath?: string;
}

// ---------------------------------------------------------------------------
// Retry configuration
// ---------------------------------------------------------------------------

export interface RetryConfig {
  /** Maximum number of retry attempts (default: 3) */
  maxRetries: number;
  /** Initial delay in milliseconds between retries (default: 1000) */
  baseDelayMs: number;
  /** Maximum delay in milliseconds (default: 30000) */
  maxDelayMs: number;
  /** Exponential backoff multiplier (default: 2.0) */
  backoffMultiplier: number;
  /** Jitter factor 0.0-1.0 to add randomness (default: 0.1) */
  jitterFactor: number;
}

// ---------------------------------------------------------------------------
// Circuit breaker configuration
// ---------------------------------------------------------------------------

export interface CircuitBreakerConfig {
  /** Number of failures before opening the circuit (default: 5) */
  failureThreshold: number;
  /** Time in ms the circuit stays open before half-open probe (default: 60000) */
  resetTimeoutMs: number;
  /** Number of successful probes to close the circuit (default: 2) */
  successThreshold: number;
}

// ---------------------------------------------------------------------------
// Audit configuration
// ---------------------------------------------------------------------------

export interface AuditConfig {
  /** Whether to log all MCP tool calls to the Ledger (default: true) */
  enabled: boolean;
  /** Whether to include tool parameters in audit records (default: false for PHI safety) */
  includeParameters: boolean;
  /** Fields to redact from parameters when includeParameters is true */
  redactFields: string[];
}

// ---------------------------------------------------------------------------
// Main SDK configuration
// ---------------------------------------------------------------------------

export interface TrialMcpConfig {
  /** Actor role for RBAC policy evaluation */
  role: ActorRole;

  /** Caller identity string (e.g. robot ID, user principal) */
  callerId: string;

  /** Trial identifier for scoping operations */
  trialId?: string;

  /** Site identifier for multi-site deployments */
  siteId?: string;

  /** Per-server endpoint configuration */
  servers: Partial<Record<McpServerName, ServerEndpoint>>;

  /** Global default timeout in milliseconds (default: 30000) */
  defaultTimeoutMs?: number;

  /** Retry configuration for transient failures */
  retry?: Partial<RetryConfig>;

  /** Circuit breaker configuration */
  circuitBreaker?: Partial<CircuitBreakerConfig>;

  /** Audit logging configuration */
  audit?: Partial<AuditConfig>;

  /** Optional bearer token for pre-authenticated sessions */
  bearerToken?: string;

  /** Whether to enable debug logging (default: false) */
  debug?: boolean;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  backoffMultiplier: 2.0,
  jitterFactor: 0.1,
};

export const DEFAULT_CIRCUIT_BREAKER_CONFIG: CircuitBreakerConfig = {
  failureThreshold: 5,
  resetTimeoutMs: 60000,
  successThreshold: 2,
};

export const DEFAULT_AUDIT_CONFIG: AuditConfig = {
  enabled: true,
  includeParameters: false,
  redactFields: [
    'patient_id',
    'patient_pseudonym',
    'mrn',
    'ssn',
    'date_of_birth',
    'address',
    'phone',
    'email',
  ],
};

export const DEFAULT_TIMEOUT_MS = 30000;

// ---------------------------------------------------------------------------
// Configuration resolver
// ---------------------------------------------------------------------------

export function resolveRetryConfig(partial?: Partial<RetryConfig>): RetryConfig {
  return { ...DEFAULT_RETRY_CONFIG, ...partial };
}

export function resolveCircuitBreakerConfig(
  partial?: Partial<CircuitBreakerConfig>,
): CircuitBreakerConfig {
  return { ...DEFAULT_CIRCUIT_BREAKER_CONFIG, ...partial };
}

export function resolveAuditConfig(partial?: Partial<AuditConfig>): AuditConfig {
  return { ...DEFAULT_AUDIT_CONFIG, ...partial };
}

export function resolveConfig(config: TrialMcpConfig): Required<
  Pick<TrialMcpConfig, 'role' | 'callerId' | 'defaultTimeoutMs' | 'debug'>
> & {
  retry: RetryConfig;
  circuitBreaker: CircuitBreakerConfig;
  audit: AuditConfig;
  servers: Partial<Record<McpServerName, ServerEndpoint>>;
  trialId?: string;
  siteId?: string;
  bearerToken?: string;
} {
  return {
    role: config.role,
    callerId: config.callerId,
    trialId: config.trialId,
    siteId: config.siteId,
    servers: config.servers,
    defaultTimeoutMs: config.defaultTimeoutMs ?? DEFAULT_TIMEOUT_MS,
    retry: resolveRetryConfig(config.retry),
    circuitBreaker: resolveCircuitBreakerConfig(config.circuitBreaker),
    audit: resolveAuditConfig(config.audit),
    bearerToken: config.bearerToken,
    debug: config.debug ?? false,
  };
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

export function validateConfig(config: TrialMcpConfig): string[] {
  const errors: string[] = [];

  if (!ACTOR_ROLES.includes(config.role)) {
    errors.push(`Invalid role '${config.role}'. Must be one of: ${ACTOR_ROLES.join(', ')}`);
  }

  if (!config.callerId || config.callerId.trim().length === 0) {
    errors.push('callerId is required and must be non-empty');
  }

  if (!config.servers || Object.keys(config.servers).length === 0) {
    errors.push('At least one server endpoint must be configured');
  }

  for (const [name, endpoint] of Object.entries(config.servers)) {
    if (!endpoint?.url) {
      errors.push(`Server '${name}' must have a url`);
    } else {
      try {
        new URL(endpoint.url);
      } catch {
        errors.push(`Server '${name}' has invalid url: ${endpoint.url}`);
      }
    }
  }

  if (config.retry?.maxRetries !== undefined && config.retry.maxRetries < 0) {
    errors.push('retry.maxRetries must be >= 0');
  }

  if (config.retry?.baseDelayMs !== undefined && config.retry.baseDelayMs < 0) {
    errors.push('retry.baseDelayMs must be >= 0');
  }

  return errors;
}
