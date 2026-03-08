/**
 * @trialmcp/sdk - TypeScript SDK for the National MCP-PAI Oncology Trials network.
 *
 * Provides typed clients for all 5 MCP servers (AuthZ, FHIR, DICOM, Ledger,
 * Provenance) with connection management, retry logic, circuit breaking,
 * and audit logging. Implements deny-by-default RBAC for 6 actor roles.
 *
 * @example
 * ```typescript
 * import { TrialMcpClient, AuthzClient, FhirClient } from '@trialmcp/sdk';
 *
 * const client = new TrialMcpClient({
 *   role: 'robot_agent',
 *   callerId: 'robot-001',
 *   servers: {
 *     'trialmcp-authz': { url: 'https://authz.trialmcp.example.org' },
 *     'trialmcp-fhir': { url: 'https://fhir.trialmcp.example.org' },
 *   },
 * });
 *
 * const fhir = new FhirClient(client);
 * const patient = await fhir.read('Patient', 'pseudo-12345');
 * ```
 *
 * References:
 * 1. Kawchak, K. (2026). TrialMCP. DOI: 10.5281/zenodo.18869776
 * 2. Kawchak, K. (2026). Physical AI Oncology Trials. DOI: 10.5281/zenodo.18445179
 * 3. Kawchak, K. (2026). PAI Oncology Trial FL. DOI: 10.5281/zenodo.18840880
 */

// Client
export { TrialMcpClient, HttpTransport } from './client';
export type { McpTransport, ClientEvent, ClientEventHandler } from './client';

// Server-specific clients
export { AuthzClient } from './authz';
export { FhirClient } from './fhir';
export { DicomClient } from './dicom';
export { LedgerClient } from './ledger';
export { ProvenanceClient } from './provenance';

// Configuration
export {
  type TrialMcpConfig,
  type ServerEndpoint,
  type RetryConfig,
  type CircuitBreakerConfig,
  type AuditConfig,
  type ActorRole,
  ACTOR_ROLES,
  DEFAULT_RETRY_CONFIG,
  DEFAULT_CIRCUIT_BREAKER_CONFIG,
  DEFAULT_AUDIT_CONFIG,
  DEFAULT_TIMEOUT_MS,
  resolveConfig,
  validateConfig,
} from './config';

// Errors
export {
  McpError,
  McpErrorCode,
  AuthzDeniedError,
  AuthzExpiredError,
  InvalidInputError,
  NotFoundError,
  ChainBrokenError,
  PhiLeakError,
  RateLimitedError,
  ServerError,
  UnavailableError,
  createMcpError,
  isMcpError,
  isRetryable,
} from './errors';
export type { McpErrorDetails, McpErrorOptions, McpServerName } from './errors';

// Models
export type {
  AuthzDecision,
  MatchingRule,
  TokenIssuance,
  TokenValidation,
  TokenRevocation,
  PolicyEffect,
  FhirResource,
  FhirMeta,
  FhirCoding,
  FhirBundle,
  FhirBundleEntry,
  FhirBundleLink,
  FhirReadResult,
  FhirSearchParams,
  PatientLookupResult,
  StudyStatusResult,
  DicomQueryParams,
  DicomStudy,
  DicomRetrieveParams,
  DicomRetrieveResult,
  DicomQueryResult,
  AuditRecord,
  LedgerAppendParams,
  LedgerVerifyResult,
  LedgerQueryParams,
  LedgerExportResult,
  ProvenanceRecord,
  ProvenanceRecordParams,
  ProvenanceQueryResult,
  ProvenanceVerifyResult,
  HealthStatus,
  DependencyStatus,
  CapabilityDescriptor,
  TaskOrder,
  ConsentStatus,
  ErrorResponse,
  McpToolCall,
  McpToolResult,
} from './models';

// Middleware
export {
  AuthMiddleware,
  AuditMiddleware,
  RetryMiddleware,
  CircuitBreakerMiddleware,
  CircuitState,
  createRetryMiddleware,
  createRobotAgentRetry,
  createNoRetry,
  createCircuitBreaker,
} from './middleware';
export type {
  AuthMiddlewareConfig,
  AuditMiddlewareConfig,
  RetryPolicy,
  RetryMiddlewareConfig,
  RetryResult,
  CircuitBreakerStats,
  CircuitBreakerEvent,
  CircuitBreakerListener,
  CircuitBreakerMiddlewareConfig,
} from './middleware';
