/**
 * Auditor workflow example for the National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a regulatory auditor performing compliance verification:
 * 1. Verify the integrity of the audit chain (hash-chain validation)
 * 2. Query audit records by server, tool, and time range
 * 3. Export the complete audit chain for offline analysis
 * 4. Cross-reference audit records with provenance
 * 5. Generate compliance report metrics
 *
 * Auditors have access to: ledger_query, ledger_verify, ledger_replay,
 * ledger_chain_status
 */

import {
  TrialMcpClient,
  LedgerClient,
  AuthMiddleware,
  isMcpError,
  ChainBrokenError,
  type AuditRecord,
  type LedgerVerifyResult,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const AUDITOR_ID = 'auditor-fda-inspector-jones';
const TRIAL_ID = 'NCT-2026-ONCO-4521';

function createClient(): TrialMcpClient {
  return new TrialMcpClient({
    role: 'auditor',
    callerId: AUDITOR_ID,
    trialId: TRIAL_ID,
    servers: {
      'trialmcp-authz': { url: 'https://authz.trialmcp.national.org' },
      'trialmcp-ledger': { url: 'https://ledger.trialmcp.national.org', timeoutMs: 60000 },
    },
    retry: { maxRetries: 1 },
  });
}

// ---------------------------------------------------------------------------
// Compliance analysis helpers
// ---------------------------------------------------------------------------

interface ComplianceReport {
  chainIntegrity: 'VALID' | 'COMPROMISED' | 'UNKNOWN';
  totalRecords: number;
  recordsByServer: Record<string, number>;
  recordsByTool: Record<string, number>;
  uniqueCallers: string[];
  timeRange: { earliest: string; latest: string } | null;
  anomalies: string[];
}

function analyzeRecords(records: AuditRecord[]): Omit<ComplianceReport, 'chainIntegrity'> {
  const byServer: Record<string, number> = {};
  const byTool: Record<string, number> = {};
  const callerSet = new Set<string>();
  const anomalies: string[] = [];
  let earliest: string | null = null;
  let latest: string | null = null;

  for (const record of records) {
    byServer[record.server] = (byServer[record.server] ?? 0) + 1;
    byTool[record.tool] = (byTool[record.tool] ?? 0) + 1;
    callerSet.add(record.caller);

    if (!earliest || record.timestamp < earliest) earliest = record.timestamp;
    if (!latest || record.timestamp > latest) latest = record.timestamp;

    // Check for out-of-order timestamps
    if (earliest && record.timestamp < earliest) {
      anomalies.push(`Record ${record.audit_id} has timestamp before chain start`);
    }
  }

  return {
    totalRecords: records.length,
    recordsByServer: byServer,
    recordsByTool: byTool,
    uniqueCallers: Array.from(callerSet),
    timeRange: earliest && latest ? { earliest, latest } : null,
    anomalies,
  };
}

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function auditorWorkflow(): Promise<void> {
  const client = createClient();
  const ledger = new LedgerClient(client);
  const auth = new AuthMiddleware(client);

  try {
    // Authenticate as auditor
    console.log('[Auditor] Initializing audit session...');
    await auth.initializeToken('auditor');

    // Step 1: Verify chain integrity
    console.log('[Auditor] Verifying audit chain integrity...');
    let verification: LedgerVerifyResult;
    try {
      verification = await ledger.assertValid();
      console.log(`[Auditor] Chain integrity: VALID (${verification.length} records)`);
    } catch (error) {
      if (error instanceof ChainBrokenError) {
        console.error('[Auditor] CRITICAL: Audit chain integrity COMPROMISED');
        console.error(`[Auditor] Reason: ${error.message}`);
        // Continue audit to gather evidence
        verification = { valid: false, length: 0, reason: error.message };
      } else {
        throw error;
      }
    }

    // Step 2: Query all records
    console.log('[Auditor] Querying complete audit history...');
    const allRecords = await ledger.query({ limit: 1000 });
    console.log(`[Auditor] Retrieved ${allRecords.length} audit records`);

    // Step 3: Analyze by server
    console.log('[Auditor] Analyzing records by MCP server...');
    const servers = ['trialmcp-authz', 'trialmcp-fhir', 'trialmcp-dicom', 'trialmcp-ledger', 'trialmcp-provenance'];
    for (const server of servers) {
      const serverRecords = await ledger.queryByServer(server, 500);
      console.log(`[Auditor]   ${server}: ${serverRecords.length} records`);
    }

    // Step 4: Analyze by time range (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    console.log('[Auditor] Querying last 30 days...');
    const recentRecords = await ledger.queryByTimeRange(
      thirtyDaysAgo.toISOString(),
      new Date().toISOString(),
    );
    console.log(`[Auditor] Records in last 30 days: ${recentRecords.length}`);

    // Step 5: Check for robot agent activity
    console.log('[Auditor] Reviewing robot agent audit trail...');
    const robotRecords = await ledger.queryByCaller('robot-onc-arm-007', 100);
    console.log(`[Auditor] Robot agent records: ${robotRecords.length}`);

    // Step 6: Export full chain for offline analysis
    console.log('[Auditor] Exporting audit chain...');
    const exportResult = await ledger.export();
    console.log(`[Auditor] Exported ${exportResult.records.length} records`);
    console.log(`[Auditor] Export checksum: ${exportResult.checksum}`);

    // Step 7: Generate compliance report
    const analysis = analyzeRecords(allRecords);
    const report: ComplianceReport = {
      chainIntegrity: verification.valid ? 'VALID' : 'COMPROMISED',
      ...analysis,
    };

    console.log('\n[Auditor] === Compliance Audit Report ===');
    console.log(`[Auditor] Chain Integrity: ${report.chainIntegrity}`);
    console.log(`[Auditor] Total Records: ${report.totalRecords}`);
    console.log(`[Auditor] Unique Callers: ${report.uniqueCallers.length}`);
    if (report.timeRange) {
      console.log(`[Auditor] Time Range: ${report.timeRange.earliest} to ${report.timeRange.latest}`);
    }
    console.log('[Auditor] Records by server:');
    for (const [server, count] of Object.entries(report.recordsByServer)) {
      console.log(`[Auditor]   ${server}: ${count}`);
    }
    if (report.anomalies.length > 0) {
      console.log(`[Auditor] ANOMALIES DETECTED: ${report.anomalies.length}`);
      for (const anomaly of report.anomalies) {
        console.log(`[Auditor]   - ${anomaly}`);
      }
    }
    console.log('[Auditor] Audit session complete.');

  } catch (error) {
    if (isMcpError(error)) {
      console.error(`[Auditor] MCP Error: ${error.code} - ${error.message}`);
    } else {
      console.error('[Auditor] Error:', error);
    }
    throw error;
  } finally {
    auth.dispose();
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

if (require.main === module) {
  auditorWorkflow().catch((err) => {
    console.error('Auditor workflow failed:', err);
    process.exit(1);
  });
}

export { auditorWorkflow };
