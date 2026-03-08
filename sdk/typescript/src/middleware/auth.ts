/**
 * Auth middleware for the National MCP-PAI Oncology Trials SDK.
 *
 * Provides pre-flight authorization checks before MCP tool calls,
 * automatic token management, and token refresh. Implements the
 * deny-by-default RBAC policy from spec/actor-model.md.
 */

import type { TrialMcpClient, ClientEvent } from '../client';
import { AuthzClient } from '../authz';
import { AuthzDeniedError, AuthzExpiredError } from '../errors';
import type { ActorRole, TokenIssuance, AuthzDecision } from '../models';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AuthMiddlewareConfig {
  /** Whether to perform pre-flight authorization checks (default: true) */
  preflightAuthz: boolean;
  /** Whether to automatically manage session tokens (default: true) */
  autoTokenManagement: boolean;
  /** Token TTL in seconds (default: 3600) */
  tokenTtlSeconds: number;
  /** Seconds before expiry to trigger proactive refresh (default: 300) */
  refreshBeforeExpiry: number;
  /** Cache authorization decisions for this many seconds (default: 60) */
  authzCacheTtl: number;
  /** Whether to cache DENY decisions (default: false for safety) */
  cacheDenyDecisions: boolean;
}

interface AuthzCacheEntry {
  decision: AuthzDecision;
  cachedAt: number;
}

// ---------------------------------------------------------------------------
// Auth Middleware
// ---------------------------------------------------------------------------

export class AuthMiddleware {
  private readonly authzClient: AuthzClient;
  private readonly config: AuthMiddlewareConfig;
  private readonly authzCache: Map<string, AuthzCacheEntry> = new Map();
  private currentToken: TokenIssuance | null = null;
  private refreshTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    client: TrialMcpClient,
    config: Partial<AuthMiddlewareConfig> = {},
  ) {
    this.authzClient = new AuthzClient(client);
    this.config = {
      preflightAuthz: config.preflightAuthz ?? true,
      autoTokenManagement: config.autoTokenManagement ?? true,
      tokenTtlSeconds: config.tokenTtlSeconds ?? 3600,
      refreshBeforeExpiry: config.refreshBeforeExpiry ?? 300,
      authzCacheTtl: config.authzCacheTtl ?? 60,
      cacheDenyDecisions: config.cacheDenyDecisions ?? false,
    };
  }

  /**
   * Perform pre-flight authorization check for a tool call.
   * Returns the decision, using cache when available.
   */
  async authorize(
    role: ActorRole,
    tool: string,
    server: string,
  ): Promise<AuthzDecision> {
    if (!this.config.preflightAuthz) {
      return {
        allowed: true,
        effect: 'ALLOW',
        role,
        server,
        tool,
        evaluated_at: new Date().toISOString(),
      };
    }

    // Check cache
    const cacheKey = `${role}:${server}:${tool}`;
    const cached = this.authzCache.get(cacheKey);

    if (cached) {
      const age = (Date.now() - cached.cachedAt) / 1000;
      if (age < this.config.authzCacheTtl) {
        return cached.decision;
      }
      this.authzCache.delete(cacheKey);
    }

    // Evaluate
    const decision = await this.authzClient.evaluate(role, tool, server);

    // Cache the result
    if (decision.allowed || this.config.cacheDenyDecisions) {
      this.authzCache.set(cacheKey, {
        decision,
        cachedAt: Date.now(),
      });
    }

    return decision;
  }

  /**
   * Authorize and throw if denied.
   */
  async assertAuthorized(
    role: ActorRole,
    tool: string,
    server: string,
  ): Promise<void> {
    const decision = await this.authorize(role, tool, server);

    if (!decision.allowed) {
      throw new AuthzDeniedError(
        decision.deny_reason ??
          `Role '${role}' is denied access to '${tool}' on '${server}'`,
        { server: server as 'trialmcp-authz', tool },
      );
    }
  }

  /**
   * Initialize token management. Obtains a session token and
   * schedules proactive refresh.
   */
  async initializeToken(role: ActorRole): Promise<TokenIssuance> {
    this.currentToken = await this.authzClient.issueToken(
      role,
      this.config.tokenTtlSeconds,
    );

    if (this.config.autoTokenManagement) {
      this.scheduleTokenRefresh(role);
    }

    return this.currentToken;
  }

  /**
   * Get the current valid token, refreshing if needed.
   */
  async getToken(role: ActorRole): Promise<TokenIssuance> {
    if (!this.currentToken) {
      return this.initializeToken(role);
    }

    // Check if token is about to expire
    const expiresAt = new Date(this.currentToken.expires_at);
    const refreshAt = new Date(
      expiresAt.getTime() - this.config.refreshBeforeExpiry * 1000,
    );

    if (new Date() >= refreshAt) {
      return this.initializeToken(role);
    }

    return this.currentToken;
  }

  /**
   * Validate the current token.
   */
  async validateCurrentToken(): Promise<boolean> {
    if (!this.currentToken) return false;

    try {
      const result = await this.authzClient.validateToken(
        this.currentToken.token_hash,
      );
      return result.valid;
    } catch (error) {
      if (error instanceof AuthzExpiredError) {
        this.currentToken = null;
        return false;
      }
      throw error;
    }
  }

  /**
   * Revoke the current token and clean up.
   */
  async revokeCurrentToken(): Promise<void> {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }

    if (this.currentToken) {
      await this.authzClient.revokeToken(this.currentToken.token_hash);
      this.currentToken = null;
    }
  }

  /**
   * Clear the authorization decision cache.
   */
  clearCache(): void {
    this.authzCache.clear();
  }

  /**
   * Dispose of all resources (timers, cache).
   */
  dispose(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
    this.authzCache.clear();
    this.currentToken = null;
  }

  // -------------------------------------------------------------------------
  // Private
  // -------------------------------------------------------------------------

  private scheduleTokenRefresh(role: ActorRole): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    if (!this.currentToken) return;

    const expiresAt = new Date(this.currentToken.expires_at);
    const refreshAt = new Date(
      expiresAt.getTime() - this.config.refreshBeforeExpiry * 1000,
    );
    const delayMs = Math.max(0, refreshAt.getTime() - Date.now());

    this.refreshTimer = setTimeout(async () => {
      try {
        await this.initializeToken(role);
      } catch {
        // Token refresh failure is non-fatal; next call will retry
      }
    }, delayMs);

    // Ensure the timer does not prevent process exit
    if (this.refreshTimer && typeof this.refreshTimer === 'object' && 'unref' in this.refreshTimer) {
      (this.refreshTimer as NodeJS.Timeout).unref();
    }
  }
}
