/**
 * Provenance client for the National MCP-PAI Oncology Trials network.
 *
 * Wraps the trialmcp-provenance MCP server tools:
 *   - provenance_record_access: Record a provenance event for data access
 *   - provenance_query_forward: Trace data lineage forward from a source
 *   - provenance_query_backward: Trace data lineage backward to origins
 *   - provenance_verify: Verify provenance chain integrity for a source
 *
 * Provenance tracking enables full data lineage across the oncology
 * trial network, supporting regulatory audit requirements (21 CFR Part 11,
 * GDPR Article 30) and W3C PROV-DM compliance.
 */

import { TrialMcpClient } from './client';
import { InvalidInputError } from './errors';
import type {
  ProvenanceRecord,
  ProvenanceRecordParams,
  ProvenanceQueryResult,
  ProvenanceVerifyResult,
  ActorRole,
} from './models';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER: 'trialmcp-provenance' = 'trialmcp-provenance';

/** Standard provenance actions aligned with W3C PROV-DM */
const PROVENANCE_ACTIONS = [
  'CREATE',
  'READ',
  'UPDATE',
  'DELETE',
  'TRANSFORM',
  'DERIVE',
  'TRANSFER',
  'VALIDATE',
  'APPROVE',
  'SIGN',
  'ANONYMIZE',
  'PSEUDONYMIZE',
] as const;

type ProvenanceAction = typeof PROVENANCE_ACTIONS[number];

/** Valid actor roles */
const VALID_ROLES: ActorRole[] = [
  'robot_agent',
  'trial_coordinator',
  'data_monitor',
  'auditor',
  'sponsor',
  'cro',
];

// ---------------------------------------------------------------------------
// Provenance Client
// ---------------------------------------------------------------------------

export class ProvenanceClient {
  private readonly client: TrialMcpClient;

  constructor(client: TrialMcpClient) {
    this.client = client;
  }

  /**
   * Record a provenance event for a data access or transformation.
   *
   * Creates an immutable provenance record linking an actor, action,
   * and data source. Supports input/output hashes for data integrity
   * tracking across transformations.
   *
   * @param params - Provenance record parameters
   * @returns The created provenance record with server-assigned ID
   */
  async record(params: ProvenanceRecordParams): Promise<ProvenanceRecord> {
    this.validateRecordParams(params);

    const toolParams: Record<string, unknown> = {
      source_id: params.source_id,
      action: params.action,
      actor_id: params.actor_id,
      actor_role: params.actor_role,
      tool_call: params.tool_call,
    };

    if (params.source_type) toolParams.source_type = params.source_type;
    if (params.input_hash) toolParams.input_hash = params.input_hash;
    if (params.output_hash) toolParams.output_hash = params.output_hash;
    if (params.origin_server) toolParams.origin_server = params.origin_server;
    if (params.description) toolParams.description = params.description;
    if (params.metadata) toolParams.metadata = params.metadata;

    const result = await this.client.callTool<ProvenanceRecord>(
      SERVER,
      'provenance_record_access',
      toolParams,
    );

    return result.data;
  }

  /**
   * Record a data read provenance event.
   * Convenience method for the most common provenance action.
   */
  async recordRead(
    sourceId: string,
    actorId: string,
    actorRole: ActorRole,
    toolCall: string,
    description?: string,
  ): Promise<ProvenanceRecord> {
    return this.record({
      source_id: sourceId,
      action: 'READ',
      actor_id: actorId,
      actor_role: actorRole,
      tool_call: toolCall,
      description,
    });
  }

  /**
   * Record a data transformation provenance event.
   * Captures input and output hashes for integrity verification.
   */
  async recordTransform(
    sourceId: string,
    actorId: string,
    actorRole: ActorRole,
    toolCall: string,
    inputHash: string,
    outputHash: string,
    description?: string,
  ): Promise<ProvenanceRecord> {
    return this.record({
      source_id: sourceId,
      action: 'TRANSFORM',
      actor_id: actorId,
      actor_role: actorRole,
      tool_call: toolCall,
      input_hash: inputHash,
      output_hash: outputHash,
      description,
    });
  }

  /**
   * Query provenance records forward from a source.
   *
   * Traces the lineage of data from a specific source forward in time,
   * showing how the data was used, transformed, or derived.
   *
   * @param sourceId - Source identifier to trace from
   * @param maxDepth - Maximum depth of forward traversal (default: 10)
   * @returns Forward provenance chain from the source
   */
  async queryForward(
    sourceId: string,
    maxDepth: number = 10,
  ): Promise<ProvenanceQueryResult> {
    this.validateSourceId(sourceId);
    this.validateDepth(maxDepth);

    const result = await this.client.callTool<ProvenanceQueryResult>(
      SERVER,
      'provenance_query_forward',
      { source_id: sourceId, max_depth: maxDepth },
    );

    return result.data;
  }

  /**
   * Query provenance records backward to find origins.
   *
   * Traces the lineage of data backward in time to discover
   * its original sources and the chain of transformations.
   *
   * @param sourceId - Source identifier to trace backward from
   * @param maxDepth - Maximum depth of backward traversal (default: 10)
   * @returns Backward provenance chain to origins
   */
  async queryBackward(
    sourceId: string,
    maxDepth: number = 10,
  ): Promise<ProvenanceQueryResult> {
    this.validateSourceId(sourceId);
    this.validateDepth(maxDepth);

    const result = await this.client.callTool<ProvenanceQueryResult>(
      SERVER,
      'provenance_query_backward',
      { source_id: sourceId, max_depth: maxDepth },
    );

    return result.data;
  }

  /**
   * Verify the provenance chain integrity for a source.
   *
   * Checks that the complete provenance chain for a data source
   * is consistent, with valid actor roles, timestamps, and
   * hash chains for transformed data.
   *
   * @param sourceId - Source identifier to verify
   * @returns Verification result with chain details
   */
  async verify(sourceId: string): Promise<ProvenanceVerifyResult> {
    this.validateSourceId(sourceId);

    const result = await this.client.callTool<ProvenanceVerifyResult>(
      SERVER,
      'provenance_verify',
      { source_id: sourceId },
    );

    return result.data;
  }

  /**
   * Get a complete lineage report for a source.
   * Combines forward and backward queries with verification.
   */
  async fullLineage(sourceId: string): Promise<{
    forward: ProvenanceQueryResult;
    backward: ProvenanceQueryResult;
    verification: ProvenanceVerifyResult;
  }> {
    const [forward, backward, verification] = await Promise.all([
      this.queryForward(sourceId),
      this.queryBackward(sourceId),
      this.verify(sourceId),
    ]);

    return { forward, backward, verification };
  }

  /**
   * Get all unique actors who have accessed a data source.
   */
  async getActors(sourceId: string): Promise<string[]> {
    const verification = await this.verify(sourceId);
    return verification.actors_involved;
  }

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------

  private validateRecordParams(params: ProvenanceRecordParams): void {
    if (!params.source_id || params.source_id.trim().length === 0) {
      throw new InvalidInputError('source_id is required', {
        server: SERVER,
        tool: 'provenance_record_access',
        details: { field: 'source_id' },
      });
    }

    if (!params.action || params.action.trim().length === 0) {
      throw new InvalidInputError('action is required', {
        server: SERVER,
        tool: 'provenance_record_access',
        details: { field: 'action' },
      });
    }

    if (!params.actor_id || params.actor_id.trim().length === 0) {
      throw new InvalidInputError('actor_id is required', {
        server: SERVER,
        tool: 'provenance_record_access',
        details: { field: 'actor_id' },
      });
    }

    if (!VALID_ROLES.includes(params.actor_role)) {
      throw new InvalidInputError(
        `Invalid actor_role '${params.actor_role}'. Must be one of: ${VALID_ROLES.join(', ')}`,
        {
          server: SERVER,
          tool: 'provenance_record_access',
          details: { field: 'actor_role' },
        },
      );
    }

    if (!params.tool_call || params.tool_call.trim().length === 0) {
      throw new InvalidInputError('tool_call is required', {
        server: SERVER,
        tool: 'provenance_record_access',
        details: { field: 'tool_call' },
      });
    }
  }

  private validateSourceId(sourceId: string): void {
    if (!sourceId || sourceId.trim().length === 0) {
      throw new InvalidInputError('source_id is required', {
        server: SERVER,
        details: { field: 'source_id' },
      });
    }
  }

  private validateDepth(maxDepth: number): void {
    if (maxDepth < 1 || maxDepth > 100) {
      throw new InvalidInputError(
        `max_depth must be between 1 and 100, got ${maxDepth}`,
        { server: SERVER, details: { field: 'max_depth' } },
      );
    }
  }
}
