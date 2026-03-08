/**
 * Ledger client for the National MCP-PAI Oncology Trials network.
 *
 * Wraps the trialmcp-ledger MCP server tools:
 *   - ledger_append: Append a hash-chained audit record
 *   - ledger_verify: Verify the integrity of the audit chain
 *   - ledger_query: Query audit records with filters
 *   - ledger_export: Export the full audit chain for regulatory review
 *
 * The ledger maintains an immutable, hash-chained sequence of audit
 * records. Each record's hash depends on the previous record's hash,
 * forming a tamper-evident chain per spec/audit.md.
 */

import { TrialMcpClient } from './client';
import { InvalidInputError, ChainBrokenError } from './errors';
import type {
  AuditRecord,
  LedgerAppendParams,
  LedgerVerifyResult,
  LedgerQueryParams,
  LedgerExportResult,
} from './models';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER: 'trialmcp-ledger' = 'trialmcp-ledger';

/** Genesis hash: the previous_hash of the first record in any chain */
const GENESIS_HASH = '0'.repeat(64);

/** SHA-256 hash pattern */
const HASH_PATTERN = /^[0-9a-f]{64}$/;

/** Maximum records per query */
const MAX_QUERY_LIMIT = 1000;

/** MCP servers that produce auditable tool calls */
const AUDITABLE_SERVERS = [
  'trialmcp-authz',
  'trialmcp-fhir',
  'trialmcp-dicom',
  'trialmcp-ledger',
  'trialmcp-provenance',
] as const;

// ---------------------------------------------------------------------------
// Ledger Client
// ---------------------------------------------------------------------------

export class LedgerClient {
  private readonly client: TrialMcpClient;

  constructor(client: TrialMcpClient) {
    this.client = client;
  }

  /**
   * Append a new hash-chained audit record to the ledger.
   *
   * The server computes the SHA-256 hash of the record concatenated
   * with the previous record's hash. The caller provides the operation
   * metadata; the server handles hash chaining.
   *
   * @param params - Audit record fields
   * @returns The appended audit record including its computed hash
   */
  async append(params: LedgerAppendParams): Promise<AuditRecord> {
    this.validateAppendParams(params);

    const result = await this.client.callTool<AuditRecord>(SERVER, 'ledger_append', {
      server: params.server,
      tool: params.tool,
      caller: params.caller,
      result_summary: params.result_summary,
      parameters: params.parameters ?? {},
    });

    return result.data;
  }

  /**
   * Append an audit record for an MCP tool call.
   * Convenience method that constructs the record from tool call metadata.
   */
  async auditToolCall(
    server: string,
    tool: string,
    caller: string,
    resultSummary: string,
    parameters?: Record<string, unknown>,
  ): Promise<AuditRecord> {
    return this.append({
      server,
      tool,
      caller,
      result_summary: resultSummary,
      parameters,
    });
  }

  /**
   * Verify the integrity of the audit chain.
   *
   * Checks that every record's hash correctly chains from the
   * previous record. Detects tampering, insertion, deletion,
   * or reordering of audit records.
   *
   * @returns Verification result with chain length and any issues
   * @throws ChainBrokenError if verification reveals tampering
   */
  async verify(options: { throwOnBroken?: boolean } = {}): Promise<LedgerVerifyResult> {
    const result = await this.client.callTool<LedgerVerifyResult>(
      SERVER,
      'ledger_verify',
      {},
    );

    const verification = result.data;

    if (!verification.valid && options.throwOnBroken) {
      throw new ChainBrokenError(
        `Audit chain integrity verification failed: ${verification.reason ?? 'unknown reason'}`,
        {
          server: SERVER,
          tool: 'ledger_verify',
          details: {
            chain_length: verification.length,
            broken_at_index: verification.broken_at_index,
          } as Record<string, unknown>,
        },
      );
    }

    return verification;
  }

  /**
   * Assert that the audit chain is valid. Throws on broken chain.
   */
  async assertValid(): Promise<LedgerVerifyResult> {
    return this.verify({ throwOnBroken: true });
  }

  /**
   * Query audit records with optional filters.
   *
   * Supports filtering by server, tool, caller, and time range.
   * Results are returned in chronological order.
   *
   * @param params - Query filters
   * @returns Matching audit records
   */
  async query(params: LedgerQueryParams = {}): Promise<AuditRecord[]> {
    this.validateQueryParams(params);

    const toolParams: Record<string, unknown> = {};

    if (params.server) toolParams.server = params.server;
    if (params.tool) toolParams.tool = params.tool;
    if (params.caller) toolParams.caller = params.caller;
    if (params.from_timestamp) toolParams.from_timestamp = params.from_timestamp;
    if (params.to_timestamp) toolParams.to_timestamp = params.to_timestamp;
    if (params.limit !== undefined) {
      toolParams.limit = Math.min(params.limit, MAX_QUERY_LIMIT);
    }

    const result = await this.client.callTool<AuditRecord[]>(
      SERVER,
      'ledger_query',
      toolParams,
    );

    return result.data;
  }

  /**
   * Query records for a specific server.
   */
  async queryByServer(server: string, limit?: number): Promise<AuditRecord[]> {
    return this.query({ server, limit });
  }

  /**
   * Query records for a specific tool.
   */
  async queryByTool(tool: string, limit?: number): Promise<AuditRecord[]> {
    return this.query({ tool, limit });
  }

  /**
   * Query records for a specific caller.
   */
  async queryByCaller(caller: string, limit?: number): Promise<AuditRecord[]> {
    return this.query({ caller, limit });
  }

  /**
   * Query records within a time range.
   */
  async queryByTimeRange(
    from: string,
    to: string,
    limit?: number,
  ): Promise<AuditRecord[]> {
    return this.query({ from_timestamp: from, to_timestamp: to, limit });
  }

  /**
   * Export the complete audit chain for regulatory review.
   *
   * Returns all audit records in chain order with a checksum
   * of the complete export for integrity verification.
   *
   * @returns Full audit chain export with metadata
   */
  async export(): Promise<LedgerExportResult> {
    const result = await this.client.callTool<LedgerExportResult>(
      SERVER,
      'ledger_export',
      {},
    );

    return result.data;
  }

  /**
   * Count audit records matching the given filters.
   */
  async count(params: LedgerQueryParams = {}): Promise<number> {
    const records = await this.query({ ...params, limit: MAX_QUERY_LIMIT });
    return records.length;
  }

  /**
   * Get the latest N audit records.
   */
  async latest(count: number = 10): Promise<AuditRecord[]> {
    const records = await this.query({ limit: count });
    return records.slice(-count);
  }

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------

  private validateAppendParams(params: LedgerAppendParams): void {
    if (!params.server || params.server.trim().length === 0) {
      throw new InvalidInputError('server is required for ledger append', {
        server: SERVER,
        tool: 'ledger_append',
        details: { field: 'server' },
      });
    }

    if (!params.tool || params.tool.trim().length === 0) {
      throw new InvalidInputError('tool is required for ledger append', {
        server: SERVER,
        tool: 'ledger_append',
        details: { field: 'tool' },
      });
    }

    if (!params.caller || params.caller.trim().length === 0) {
      throw new InvalidInputError('caller is required for ledger append', {
        server: SERVER,
        tool: 'ledger_append',
        details: { field: 'caller' },
      });
    }

    if (!params.result_summary || params.result_summary.trim().length === 0) {
      throw new InvalidInputError('result_summary is required for ledger append', {
        server: SERVER,
        tool: 'ledger_append',
        details: { field: 'result_summary' },
      });
    }
  }

  private validateQueryParams(params: LedgerQueryParams): void {
    if (params.limit !== undefined && (params.limit < 1 || params.limit > MAX_QUERY_LIMIT)) {
      throw new InvalidInputError(
        `Query limit must be between 1 and ${MAX_QUERY_LIMIT}, got ${params.limit}`,
        { server: SERVER, tool: 'ledger_query', details: { field: 'limit' } },
      );
    }

    if (params.from_timestamp) {
      const date = new Date(params.from_timestamp);
      if (isNaN(date.getTime())) {
        throw new InvalidInputError(
          `Invalid from_timestamp: '${params.from_timestamp}'. Must be ISO 8601`,
          { server: SERVER, tool: 'ledger_query', details: { field: 'from_timestamp' } },
        );
      }
    }

    if (params.to_timestamp) {
      const date = new Date(params.to_timestamp);
      if (isNaN(date.getTime())) {
        throw new InvalidInputError(
          `Invalid to_timestamp: '${params.to_timestamp}'. Must be ISO 8601`,
          { server: SERVER, tool: 'ledger_query', details: { field: 'to_timestamp' } },
        );
      }
    }
  }
}
