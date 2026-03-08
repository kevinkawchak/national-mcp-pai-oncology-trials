/**
 * AuthZ client for the National MCP-PAI Oncology Trials network.
 *
 * Wraps the trialmcp-authz MCP server tools:
 *   - authz_evaluate: Evaluate RBAC policy for a role/tool/server tuple
 *   - authz_issue_token: Issue a scoped session token
 *   - authz_validate_token: Validate an existing session token
 *   - authz_revoke_token: Revoke a session token
 *
 * Implements deny-by-default RBAC with explicit DENY precedence.
 */

import { TrialMcpClient } from './client';
import { AuthzDeniedError, AuthzExpiredError, InvalidInputError } from './errors';
import type {
  AuthzDecision,
  TokenIssuance,
  TokenValidation,
  TokenRevocation,
  ActorRole,
} from './models';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER: 'trialmcp-authz' = 'trialmcp-authz';

/** Maximum token TTL enforced server-side (24 hours) */
const MAX_TOKEN_TTL_SECONDS = 86400;

/** Default token TTL (1 hour) */
const DEFAULT_TOKEN_TTL_SECONDS = 3600;

// ---------------------------------------------------------------------------
// AuthZ Client
// ---------------------------------------------------------------------------

export class AuthzClient {
  private readonly client: TrialMcpClient;
  private cachedToken: TokenIssuance | null = null;

  constructor(client: TrialMcpClient) {
    this.client = client;
  }

  /**
   * Evaluate whether a role is authorized to invoke a tool on a server.
   *
   * Uses the deny-by-default RBAC policy matrix defined in spec/actor-model.md.
   * An explicit DENY rule always takes precedence over ALLOW.
   *
   * @param role - Actor role to evaluate (e.g. 'robot_agent')
   * @param tool - MCP tool name (e.g. 'fhir_read')
   * @param server - Target MCP server (defaults to 'trialmcp-authz')
   * @returns Authorization decision with matching rules
   * @throws AuthzDeniedError if access is denied and throwOnDeny is true
   */
  async evaluate(
    role: ActorRole,
    tool: string,
    server: string = SERVER,
    options: { throwOnDeny?: boolean } = {},
  ): Promise<AuthzDecision> {
    this.validateRole(role);
    this.validateToolName(tool);

    const result = await this.client.callTool<AuthzDecision>(SERVER, 'authz_evaluate', {
      role,
      tool,
      server,
    });

    const decision = result.data;

    if (!decision.allowed && options.throwOnDeny) {
      throw new AuthzDeniedError(
        decision.deny_reason ?? `Role '${role}' denied access to '${tool}' on '${server}'`,
        { server: SERVER, tool: 'authz_evaluate' },
      );
    }

    return decision;
  }

  /**
   * Check authorization and throw if denied. Convenience wrapper around evaluate().
   */
  async assertAuthorized(
    role: ActorRole,
    tool: string,
    server: string = SERVER,
  ): Promise<AuthzDecision> {
    return this.evaluate(role, tool, server, { throwOnDeny: true });
  }

  /**
   * Issue a scoped session token for the given role.
   *
   * Tokens are SHA-256 hashed server-side; the raw token is never stored.
   * Maximum TTL is 24 hours per regulatory requirements.
   *
   * @param role - Actor role for the token
   * @param expiresInSeconds - Token lifetime (default: 3600, max: 86400)
   * @returns Token issuance details including the token hash
   */
  async issueToken(
    role: ActorRole,
    expiresInSeconds: number = DEFAULT_TOKEN_TTL_SECONDS,
  ): Promise<TokenIssuance> {
    this.validateRole(role);

    if (expiresInSeconds <= 0 || expiresInSeconds > MAX_TOKEN_TTL_SECONDS) {
      throw new InvalidInputError(
        `Token TTL must be between 1 and ${MAX_TOKEN_TTL_SECONDS} seconds, got ${expiresInSeconds}`,
        { server: SERVER, tool: 'authz_issue_token' },
      );
    }

    const result = await this.client.callTool<TokenIssuance>(SERVER, 'authz_issue_token', {
      role,
      expires_in: expiresInSeconds,
    });

    this.cachedToken = result.data;
    return result.data;
  }

  /**
   * Validate a session token.
   *
   * @param tokenHash - SHA-256 hash of the token to validate
   * @returns Validation result with role if valid
   * @throws AuthzExpiredError if the token is expired
   */
  async validateToken(tokenHash: string): Promise<TokenValidation> {
    this.validateTokenHash(tokenHash);

    const result = await this.client.callTool<TokenValidation>(
      SERVER,
      'authz_validate_token',
      { token_hash: tokenHash },
    );

    const validation = result.data;

    if (!validation.valid && validation.reason === 'TOKEN_EXPIRED') {
      throw new AuthzExpiredError('Session token has expired', {
        server: SERVER,
        tool: 'authz_validate_token',
      });
    }

    return validation;
  }

  /**
   * Revoke a session token immediately.
   *
   * Once revoked, the token cannot be used for any further authorization
   * checks. This action is irreversible.
   *
   * @param tokenHash - SHA-256 hash of the token to revoke
   * @returns Revocation result
   */
  async revokeToken(tokenHash: string): Promise<TokenRevocation> {
    this.validateTokenHash(tokenHash);

    const result = await this.client.callTool<TokenRevocation>(
      SERVER,
      'authz_revoke_token',
      { token_hash: tokenHash },
    );

    // Clear cached token if it matches
    if (this.cachedToken?.token_hash === tokenHash) {
      this.cachedToken = null;
    }

    return result.data;
  }

  /**
   * Get the currently cached token, if any.
   */
  getCachedToken(): TokenIssuance | null {
    if (!this.cachedToken) return null;

    // Check if cached token has expired
    const expiresAt = new Date(this.cachedToken.expires_at);
    if (expiresAt <= new Date()) {
      this.cachedToken = null;
      return null;
    }

    return this.cachedToken;
  }

  /**
   * Issue a token if no valid cached token exists.
   */
  async ensureToken(
    role: ActorRole,
    expiresInSeconds: number = DEFAULT_TOKEN_TTL_SECONDS,
  ): Promise<TokenIssuance> {
    const cached = this.getCachedToken();
    if (cached) return cached;
    return this.issueToken(role, expiresInSeconds);
  }

  // -------------------------------------------------------------------------
  // Validation helpers
  // -------------------------------------------------------------------------

  private validateRole(role: string): void {
    const validRoles: ActorRole[] = [
      'robot_agent', 'trial_coordinator', 'data_monitor',
      'auditor', 'sponsor', 'cro',
    ];
    if (!validRoles.includes(role as ActorRole)) {
      throw new InvalidInputError(
        `Invalid role '${role}'. Must be one of: ${validRoles.join(', ')}`,
        { server: SERVER, details: { field: 'role' } },
      );
    }
  }

  private validateToolName(tool: string): void {
    if (!tool || !/^[a-z][a-z0-9_]*$/.test(tool)) {
      throw new InvalidInputError(
        `Invalid tool name '${tool}'. Must match pattern ^[a-z][a-z0-9_]*$`,
        { server: SERVER, details: { field: 'tool', expectedPattern: '^[a-z][a-z0-9_]*$' } },
      );
    }
  }

  private validateTokenHash(tokenHash: string): void {
    if (!tokenHash || !/^[0-9a-f]{64}$/.test(tokenHash)) {
      throw new InvalidInputError(
        'Invalid token hash. Must be a 64-character hex string (SHA-256)',
        { server: SERVER, details: { field: 'token_hash', expectedPattern: '^[0-9a-f]{64}$' } },
      );
    }
  }
}
