/**
 * Typed error classes for the National MCP-PAI Oncology Trials SDK.
 *
 * Implements the 9-code error taxonomy defined in schemas/error-response.schema.json.
 * All errors carry structured metadata (server, tool, requestId) for tracing
 * across the distributed MCP server network.
 *
 * IMPORTANT: Error messages MUST NOT contain PHI, patient identifiers, or
 * internal system details per regulatory requirements.
 */

// ---------------------------------------------------------------------------
// Error code enum
// ---------------------------------------------------------------------------

export enum McpErrorCode {
  AUTHZ_DENIED = 'AUTHZ_DENIED',
  AUTHZ_EXPIRED = 'TOKEN_EXPIRED',
  INVALID_INPUT = 'INVALID_INPUT',
  NOT_FOUND = 'NOT_FOUND',
  CHAIN_BROKEN = 'VALIDATION_FAILED',
  PHI_LEAK = 'PERMISSION_DENIED',
  RATE_LIMITED = 'RATE_LIMITED',
  SERVER_ERROR = 'INTERNAL_ERROR',
  UNAVAILABLE = 'TOKEN_REVOKED',
}

export type McpServerName =
  | 'trialmcp-authz'
  | 'trialmcp-fhir'
  | 'trialmcp-dicom'
  | 'trialmcp-ledger'
  | 'trialmcp-provenance';

// ---------------------------------------------------------------------------
// Error metadata
// ---------------------------------------------------------------------------

export interface McpErrorDetails {
  field?: string;
  expectedPattern?: string;
  retryAfterSeconds?: number;
  [key: string]: unknown;
}

export interface McpErrorOptions {
  server?: McpServerName;
  tool?: string;
  requestId?: string;
  timestamp?: string;
  details?: McpErrorDetails;
  cause?: Error;
}

// ---------------------------------------------------------------------------
// Base error
// ---------------------------------------------------------------------------

export class McpError extends Error {
  public readonly code: McpErrorCode;
  public readonly server?: McpServerName;
  public readonly tool?: string;
  public readonly requestId?: string;
  public readonly timestamp: string;
  public readonly details?: McpErrorDetails;
  public readonly isRetryable: boolean;

  constructor(code: McpErrorCode, message: string, options: McpErrorOptions = {}) {
    super(message);
    this.name = 'McpError';
    this.code = code;
    this.server = options.server;
    this.tool = options.tool;
    this.requestId = options.requestId;
    this.timestamp = options.timestamp ?? new Date().toISOString();
    this.details = options.details;
    this.isRetryable = McpError.isRetryableCode(code);

    if (options.cause) {
      this.cause = options.cause;
    }
    Object.setPrototypeOf(this, new.target.prototype);
  }

  static isRetryableCode(code: McpErrorCode): boolean {
    return [
      McpErrorCode.RATE_LIMITED,
      McpErrorCode.SERVER_ERROR,
      McpErrorCode.UNAVAILABLE,
    ].includes(code);
  }

  toJSON(): Record<string, unknown> {
    return {
      error: true,
      code: this.code,
      message: this.message,
      server: this.server,
      tool: this.tool,
      timestamp: this.timestamp,
      request_id: this.requestId,
      details: this.details,
    };
  }

  static fromResponse(response: Record<string, unknown>): McpError {
    const code = (response.code as McpErrorCode) ?? McpErrorCode.SERVER_ERROR;
    const message = (response.message as string) ?? 'Unknown MCP error';
    return new McpError(code, message, {
      server: response.server as McpServerName | undefined,
      tool: response.tool as string | undefined,
      requestId: response.request_id as string | undefined,
      timestamp: response.timestamp as string | undefined,
      details: response.details as McpErrorDetails | undefined,
    });
  }
}

// ---------------------------------------------------------------------------
// Specific error classes
// ---------------------------------------------------------------------------

export class AuthzDeniedError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.AUTHZ_DENIED, message, options);
    this.name = 'AuthzDeniedError';
  }
}

export class AuthzExpiredError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.AUTHZ_EXPIRED, message, options);
    this.name = 'AuthzExpiredError';
  }
}

export class InvalidInputError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.INVALID_INPUT, message, options);
    this.name = 'InvalidInputError';
  }
}

export class NotFoundError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.NOT_FOUND, message, options);
    this.name = 'NotFoundError';
  }
}

export class ChainBrokenError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.CHAIN_BROKEN, message, options);
    this.name = 'ChainBrokenError';
  }
}

export class PhiLeakError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.PHI_LEAK, message, options);
    this.name = 'PhiLeakError';
  }
}

export class RateLimitedError extends McpError {
  public readonly retryAfterSeconds: number;

  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.RATE_LIMITED, message, options);
    this.name = 'RateLimitedError';
    this.retryAfterSeconds = options.details?.retryAfterSeconds as number ?? 30;
  }
}

export class ServerError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.SERVER_ERROR, message, options);
    this.name = 'ServerError';
  }
}

export class UnavailableError extends McpError {
  constructor(message: string, options: McpErrorOptions = {}) {
    super(McpErrorCode.UNAVAILABLE, message, options);
    this.name = 'UnavailableError';
  }
}

// ---------------------------------------------------------------------------
// Error factory
// ---------------------------------------------------------------------------

const ERROR_CLASS_MAP: Record<string, new (msg: string, opts?: McpErrorOptions) => McpError> = {
  AUTHZ_DENIED: AuthzDeniedError,
  TOKEN_EXPIRED: AuthzExpiredError,
  INVALID_INPUT: InvalidInputError,
  NOT_FOUND: NotFoundError,
  VALIDATION_FAILED: ChainBrokenError,
  PERMISSION_DENIED: PhiLeakError,
  RATE_LIMITED: RateLimitedError,
  INTERNAL_ERROR: ServerError,
  TOKEN_REVOKED: UnavailableError,
};

export function createMcpError(
  code: string,
  message: string,
  options: McpErrorOptions = {},
): McpError {
  const ErrorClass = ERROR_CLASS_MAP[code] ?? McpError;
  return new ErrorClass(message, options);
}

export function isMcpError(error: unknown): error is McpError {
  return error instanceof McpError;
}

export function isRetryable(error: unknown): boolean {
  return isMcpError(error) && error.isRetryable;
}
