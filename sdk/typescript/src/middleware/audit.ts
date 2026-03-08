/**
 * Audit middleware for the National MCP-PAI Oncology Trials SDK.
 *
 * Automatically records MCP tool calls to the Ledger server,
 * creating a hash-chained audit trail per spec/audit.md.
 * Supports PHI-safe parameter redaction and configurable
 * audit scoping.
 */

import type { TrialMcpClient, ClientEvent, ClientEventHandler } from '../client';
import { LedgerClient } from '../ledger';
import type { AuditRecord, AuditConfig } from '../config';
import { DEFAULT_AUDIT_CONFIG, resolveAuditConfig } from '../config';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AuditMiddlewareConfig {
  /** Whether audit logging is enabled (default: true) */
  enabled: boolean;
  /** Whether to include parameters in audit records (default: false for PHI safety) */
  includeParameters: boolean;
  /** Field names to redact from parameters */
  redactFields: string[];
  /** Servers to exclude from audit logging */
  excludeServers: string[];
  /** Tools to exclude from audit logging */
  excludeTools: string[];
  /** Whether to fail the tool call if audit logging fails (default: false) */
  failOnAuditError: boolean;
  /** Maximum number of audit records to buffer before flushing (default: 1) */
  bufferSize: number;
  /** Maximum time in ms to hold buffered records before flushing (default: 5000) */
  flushIntervalMs: number;
}

interface BufferedAuditEntry {
  server: string;
  tool: string;
  caller: string;
  resultSummary: string;
  parameters: Record<string, unknown>;
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Audit Middleware
// ---------------------------------------------------------------------------

export class AuditMiddleware {
  private readonly ledgerClient: LedgerClient;
  private readonly config: AuditMiddlewareConfig;
  private readonly buffer: BufferedAuditEntry[] = [];
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private unsubscribe: (() => void) | null = null;
  private auditCount: number = 0;
  private auditErrors: number = 0;

  constructor(
    client: TrialMcpClient,
    config: Partial<AuditMiddlewareConfig> = {},
  ) {
    this.ledgerClient = new LedgerClient(client);
    this.config = {
      enabled: config.enabled ?? true,
      includeParameters: config.includeParameters ?? false,
      redactFields: config.redactFields ?? DEFAULT_AUDIT_CONFIG.redactFields,
      excludeServers: config.excludeServers ?? [],
      excludeTools: config.excludeTools ?? [],
      failOnAuditError: config.failOnAuditError ?? false,
      bufferSize: config.bufferSize ?? 1,
      flushIntervalMs: config.flushIntervalMs ?? 5000,
    };
  }

  /**
   * Attach the audit middleware to a client by subscribing to events.
   */
  attach(client: TrialMcpClient): void {
    if (this.unsubscribe) {
      this.unsubscribe();
    }

    this.unsubscribe = client.on((event: ClientEvent, data: Record<string, unknown>) => {
      if (!this.config.enabled) return;

      if (event === 'toolResult') {
        this.handleToolResult(data).catch((err) => {
          this.auditErrors++;
          if (this.config.failOnAuditError) {
            throw err;
          }
        });
      }

      if (event === 'toolError') {
        this.handleToolError(data).catch((err) => {
          this.auditErrors++;
        });
      }
    });

    // Start flush timer if buffering
    if (this.config.bufferSize > 1) {
      this.startFlushTimer();
    }
  }

  /**
   * Detach the audit middleware from the client.
   */
  detach(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
    }
    this.stopFlushTimer();
  }

  /**
   * Manually record an audit entry.
   */
  async recordAudit(
    server: string,
    tool: string,
    caller: string,
    resultSummary: string,
    parameters: Record<string, unknown> = {},
  ): Promise<AuditRecord | null> {
    if (!this.config.enabled) return null;
    if (this.isExcluded(server, tool)) return null;

    const sanitizedParams = this.config.includeParameters
      ? this.redactParameters(parameters)
      : {};

    try {
      const record = await this.ledgerClient.append({
        server,
        tool,
        caller,
        result_summary: resultSummary,
        parameters: sanitizedParams,
      });

      this.auditCount++;
      return record;
    } catch (error) {
      this.auditErrors++;
      if (this.config.failOnAuditError) throw error;
      return null;
    }
  }

  /**
   * Flush any buffered audit records.
   */
  async flush(): Promise<void> {
    const entries = this.buffer.splice(0, this.buffer.length);

    for (const entry of entries) {
      await this.recordAudit(
        entry.server,
        entry.tool,
        entry.caller,
        entry.resultSummary,
        entry.parameters,
      );
    }
  }

  /**
   * Get audit statistics.
   */
  getStats(): { totalRecorded: number; totalErrors: number; bufferSize: number } {
    return {
      totalRecorded: this.auditCount,
      totalErrors: this.auditErrors,
      bufferSize: this.buffer.length,
    };
  }

  /**
   * Dispose of all resources.
   */
  dispose(): void {
    this.detach();
    this.buffer.length = 0;
  }

  // -------------------------------------------------------------------------
  // Private: Event handlers
  // -------------------------------------------------------------------------

  private async handleToolResult(data: Record<string, unknown>): Promise<void> {
    const server = data.server as string;
    const tool = data.tool as string;

    if (this.isExcluded(server, tool)) return;

    // Avoid recursive audit logging (don't audit the audit)
    if (server === 'trialmcp-ledger' && tool.startsWith('ledger_')) return;

    const entry: BufferedAuditEntry = {
      server,
      tool,
      caller: (data as Record<string, unknown>).requestId as string ?? 'unknown',
      resultSummary: `Tool call succeeded: ${tool} (${data.durationMs}ms)`,
      parameters: (data as Record<string, unknown>).data as Record<string, unknown> ?? {},
      timestamp: new Date().toISOString(),
    };

    if (this.config.bufferSize <= 1) {
      await this.recordAudit(
        entry.server,
        entry.tool,
        entry.caller,
        entry.resultSummary,
        entry.parameters,
      );
    } else {
      this.buffer.push(entry);
      if (this.buffer.length >= this.config.bufferSize) {
        await this.flush();
      }
    }
  }

  private async handleToolError(data: Record<string, unknown>): Promise<void> {
    const server = data.server as string;
    const tool = data.tool as string;

    if (this.isExcluded(server, tool)) return;
    if (server === 'trialmcp-ledger' && tool.startsWith('ledger_')) return;

    const errorInfo = data.error as Record<string, unknown> ?? {};
    const resultSummary = `Tool call failed: ${tool} (${errorInfo.code ?? 'UNKNOWN'}: ${errorInfo.message ?? 'unknown error'})`;

    await this.recordAudit(server, tool, data.requestId as string ?? 'unknown', resultSummary);
  }

  // -------------------------------------------------------------------------
  // Private: Helpers
  // -------------------------------------------------------------------------

  private isExcluded(server: string, tool: string): boolean {
    return (
      this.config.excludeServers.includes(server) ||
      this.config.excludeTools.includes(tool)
    );
  }

  /**
   * Redact PHI-sensitive fields from parameters.
   * MUST NOT allow patient identifiers into audit records.
   */
  private redactParameters(params: Record<string, unknown>): Record<string, unknown> {
    const redacted: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(params)) {
      if (this.config.redactFields.some((field) => key.toLowerCase().includes(field.toLowerCase()))) {
        redacted[key] = '[REDACTED]';
      } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        redacted[key] = this.redactParameters(value as Record<string, unknown>);
      } else {
        redacted[key] = value;
      }
    }

    return redacted;
  }

  private startFlushTimer(): void {
    this.stopFlushTimer();
    this.flushTimer = setInterval(() => {
      if (this.buffer.length > 0) {
        this.flush().catch(() => {});
      }
    }, this.config.flushIntervalMs);

    if (this.flushTimer && typeof this.flushTimer === 'object' && 'unref' in this.flushTimer) {
      (this.flushTimer as NodeJS.Timeout).unref();
    }
  }

  private stopFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }
}
