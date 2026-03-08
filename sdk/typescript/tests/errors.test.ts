/**
 * Tests for the MCP error taxonomy.
 *
 * Validates error construction, serialization, classification,
 * and factory functions for all 9 error codes.
 */

import {
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
} from '../src/errors';

// ---------------------------------------------------------------------------
// McpError base class
// ---------------------------------------------------------------------------

describe('McpError', () => {
  it('should construct with code and message', () => {
    const error = new McpError(McpErrorCode.SERVER_ERROR, 'Something went wrong');

    expect(error.code).toBe(McpErrorCode.SERVER_ERROR);
    expect(error.message).toBe('Something went wrong');
    expect(error.name).toBe('McpError');
    expect(error.timestamp).toBeDefined();
    expect(error instanceof Error).toBe(true);
    expect(error instanceof McpError).toBe(true);
  });

  it('should include optional metadata', () => {
    const error = new McpError(McpErrorCode.NOT_FOUND, 'Resource not found', {
      server: 'trialmcp-fhir',
      tool: 'fhir_read',
      requestId: 'req-12345',
      details: { field: 'resource_id' },
    });

    expect(error.server).toBe('trialmcp-fhir');
    expect(error.tool).toBe('fhir_read');
    expect(error.requestId).toBe('req-12345');
    expect(error.details?.field).toBe('resource_id');
  });

  it('should serialize to JSON matching error-response schema', () => {
    const error = new McpError(McpErrorCode.INVALID_INPUT, 'Bad input', {
      server: 'trialmcp-fhir',
      tool: 'fhir_read',
      requestId: 'req-001',
      details: { field: 'resource_type', expectedPattern: '^[A-Z][a-zA-Z]+$' },
    });

    const json = error.toJSON();

    expect(json.error).toBe(true);
    expect(json.code).toBe('INVALID_INPUT');
    expect(json.message).toBe('Bad input');
    expect(json.server).toBe('trialmcp-fhir');
    expect(json.tool).toBe('fhir_read');
    expect(json.request_id).toBe('req-001');
    expect(json.timestamp).toBeDefined();
    expect((json.details as Record<string, unknown>).field).toBe('resource_type');
  });

  it('should deserialize from response object', () => {
    const response = {
      error: true,
      code: 'AUTHZ_DENIED',
      message: 'Access denied',
      server: 'trialmcp-dicom',
      tool: 'dicom_query',
      request_id: 'req-999',
      timestamp: '2026-03-06T14:31:00Z',
    };

    const error = McpError.fromResponse(response);

    expect(error.code).toBe(McpErrorCode.AUTHZ_DENIED);
    expect(error.message).toBe('Access denied');
    expect(error.server).toBe('trialmcp-dicom');
    expect(error.tool).toBe('dicom_query');
    expect(error.requestId).toBe('req-999');
  });

  it('should store cause error', () => {
    const cause = new Error('underlying issue');
    const error = new McpError(McpErrorCode.SERVER_ERROR, 'Wrapped error', { cause });

    expect(error.cause).toBe(cause);
  });
});

// ---------------------------------------------------------------------------
// Retryability classification
// ---------------------------------------------------------------------------

describe('retryability', () => {
  it('should mark RATE_LIMITED as retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.RATE_LIMITED)).toBe(true);
  });

  it('should mark SERVER_ERROR as retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.SERVER_ERROR)).toBe(true);
  });

  it('should mark UNAVAILABLE as retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.UNAVAILABLE)).toBe(true);
  });

  it('should mark AUTHZ_DENIED as not retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.AUTHZ_DENIED)).toBe(false);
  });

  it('should mark INVALID_INPUT as not retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.INVALID_INPUT)).toBe(false);
  });

  it('should mark NOT_FOUND as not retryable', () => {
    expect(McpError.isRetryableCode(McpErrorCode.NOT_FOUND)).toBe(false);
  });

  it('should set isRetryable on instance', () => {
    const retryable = new ServerError('temp');
    const nonRetryable = new AuthzDeniedError('denied');

    expect(retryable.isRetryable).toBe(true);
    expect(nonRetryable.isRetryable).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Specific error classes
// ---------------------------------------------------------------------------

describe('AuthzDeniedError', () => {
  it('should have correct code and name', () => {
    const error = new AuthzDeniedError('Access denied');
    expect(error.code).toBe(McpErrorCode.AUTHZ_DENIED);
    expect(error.name).toBe('AuthzDeniedError');
    expect(error instanceof McpError).toBe(true);
    expect(error instanceof AuthzDeniedError).toBe(true);
  });
});

describe('AuthzExpiredError', () => {
  it('should have correct code and name', () => {
    const error = new AuthzExpiredError('Token expired');
    expect(error.code).toBe(McpErrorCode.AUTHZ_EXPIRED);
    expect(error.name).toBe('AuthzExpiredError');
  });
});

describe('InvalidInputError', () => {
  it('should have correct code and include field details', () => {
    const error = new InvalidInputError('Bad resource type', {
      details: { field: 'resource_type', expectedPattern: '^[A-Z][a-zA-Z]+$' },
    });
    expect(error.code).toBe(McpErrorCode.INVALID_INPUT);
    expect(error.name).toBe('InvalidInputError');
    expect(error.details?.field).toBe('resource_type');
    expect(error.details?.expectedPattern).toBe('^[A-Z][a-zA-Z]+$');
  });
});

describe('NotFoundError', () => {
  it('should have correct code', () => {
    const error = new NotFoundError('Patient not found');
    expect(error.code).toBe(McpErrorCode.NOT_FOUND);
    expect(error.name).toBe('NotFoundError');
  });
});

describe('ChainBrokenError', () => {
  it('should have correct code', () => {
    const error = new ChainBrokenError('Hash mismatch at index 42');
    expect(error.code).toBe(McpErrorCode.CHAIN_BROKEN);
    expect(error.name).toBe('ChainBrokenError');
  });
});

describe('PhiLeakError', () => {
  it('should have correct code', () => {
    const error = new PhiLeakError('PHI detected in response');
    expect(error.code).toBe(McpErrorCode.PHI_LEAK);
    expect(error.name).toBe('PhiLeakError');
  });
});

describe('RateLimitedError', () => {
  it('should have correct code and retryAfterSeconds', () => {
    const error = new RateLimitedError('Too many requests', {
      details: { retryAfterSeconds: 60 },
    });
    expect(error.code).toBe(McpErrorCode.RATE_LIMITED);
    expect(error.name).toBe('RateLimitedError');
    expect(error.retryAfterSeconds).toBe(60);
    expect(error.isRetryable).toBe(true);
  });

  it('should default retryAfterSeconds to 30', () => {
    const error = new RateLimitedError('Too many requests');
    expect(error.retryAfterSeconds).toBe(30);
  });
});

describe('ServerError', () => {
  it('should have correct code', () => {
    const error = new ServerError('Internal server error');
    expect(error.code).toBe(McpErrorCode.SERVER_ERROR);
    expect(error.name).toBe('ServerError');
    expect(error.isRetryable).toBe(true);
  });
});

describe('UnavailableError', () => {
  it('should have correct code', () => {
    const error = new UnavailableError('Server unavailable');
    expect(error.code).toBe(McpErrorCode.UNAVAILABLE);
    expect(error.name).toBe('UnavailableError');
    expect(error.isRetryable).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Factory and utility functions
// ---------------------------------------------------------------------------

describe('createMcpError', () => {
  it('should create correct error class for each code', () => {
    expect(createMcpError('AUTHZ_DENIED', 'denied')).toBeInstanceOf(AuthzDeniedError);
    expect(createMcpError('TOKEN_EXPIRED', 'expired')).toBeInstanceOf(AuthzExpiredError);
    expect(createMcpError('INVALID_INPUT', 'bad')).toBeInstanceOf(InvalidInputError);
    expect(createMcpError('NOT_FOUND', 'gone')).toBeInstanceOf(NotFoundError);
    expect(createMcpError('VALIDATION_FAILED', 'broken')).toBeInstanceOf(ChainBrokenError);
    expect(createMcpError('PERMISSION_DENIED', 'phi')).toBeInstanceOf(PhiLeakError);
    expect(createMcpError('RATE_LIMITED', 'slow')).toBeInstanceOf(RateLimitedError);
    expect(createMcpError('INTERNAL_ERROR', 'boom')).toBeInstanceOf(ServerError);
    expect(createMcpError('TOKEN_REVOKED', 'revoked')).toBeInstanceOf(UnavailableError);
  });

  it('should fall back to McpError for unknown codes', () => {
    const error = createMcpError('UNKNOWN_CODE', 'mystery');
    expect(error).toBeInstanceOf(McpError);
  });
});

describe('isMcpError', () => {
  it('should return true for McpError instances', () => {
    expect(isMcpError(new McpError(McpErrorCode.SERVER_ERROR, 'test'))).toBe(true);
    expect(isMcpError(new AuthzDeniedError('test'))).toBe(true);
    expect(isMcpError(new RateLimitedError('test'))).toBe(true);
  });

  it('should return false for non-McpError values', () => {
    expect(isMcpError(new Error('regular'))).toBe(false);
    expect(isMcpError(null)).toBe(false);
    expect(isMcpError(undefined)).toBe(false);
    expect(isMcpError('string')).toBe(false);
    expect(isMcpError({ code: 'AUTHZ_DENIED' })).toBe(false);
  });
});

describe('isRetryable', () => {
  it('should return true for retryable MCP errors', () => {
    expect(isRetryable(new ServerError('temp'))).toBe(true);
    expect(isRetryable(new RateLimitedError('slow'))).toBe(true);
    expect(isRetryable(new UnavailableError('down'))).toBe(true);
  });

  it('should return false for non-retryable MCP errors', () => {
    expect(isRetryable(new AuthzDeniedError('denied'))).toBe(false);
    expect(isRetryable(new InvalidInputError('bad'))).toBe(false);
    expect(isRetryable(new NotFoundError('gone'))).toBe(false);
  });

  it('should return false for non-MCP errors', () => {
    expect(isRetryable(new Error('regular'))).toBe(false);
    expect(isRetryable(null)).toBe(false);
  });
});
