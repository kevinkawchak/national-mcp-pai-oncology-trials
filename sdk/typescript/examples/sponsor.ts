/**
 * Sponsor workflow example for the National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a pharmaceutical sponsor reviewing trial-level data:
 * 1. Review authorization policies for the trial
 * 2. Verify that deny-by-default RBAC is properly configured
 * 3. Check cross-role access patterns
 * 4. Validate that PHI access is properly restricted
 *
 * Sponsors have limited access: authz_list_policies only.
 * They cannot access FHIR, DICOM, or Ledger data directly.
 */

import {
  TrialMcpClient,
  AuthzClient,
  AuthMiddleware,
  isMcpError,
  AuthzDeniedError,
  type AuthzDecision,
  type ActorRole,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const SPONSOR_ID = 'sponsor-novapharma-regulatory';
const TRIAL_ID = 'NCT-2026-ONCO-4521';

function createClient(): TrialMcpClient {
  return new TrialMcpClient({
    role: 'sponsor',
    callerId: SPONSOR_ID,
    trialId: TRIAL_ID,
    servers: {
      'trialmcp-authz': { url: 'https://authz.trialmcp.national.org', timeoutMs: 10000 },
    },
    retry: { maxRetries: 2 },
  });
}

// ---------------------------------------------------------------------------
// Policy review helpers
// ---------------------------------------------------------------------------

interface PolicyMatrix {
  role: ActorRole;
  tool: string;
  server: string;
  allowed: boolean;
  effect: string;
}

const ALL_TOOLS = [
  'fhir_read',
  'fhir_search',
  'fhir_patient_lookup',
  'fhir_study_status',
  'dicom_query',
  'dicom_retrieve_pointer',
  'dicom_study_metadata',
  'ledger_append',
  'ledger_query',
  'ledger_verify',
  'ledger_replay',
  'ledger_chain_status',
  'provenance_record_access',
  'authz_list_policies',
];

const ALL_ROLES: ActorRole[] = [
  'robot_agent',
  'trial_coordinator',
  'data_monitor',
  'auditor',
  'sponsor',
  'cro',
];

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function sponsorWorkflow(): Promise<void> {
  const client = createClient();
  const authz = new AuthzClient(client);
  const auth = new AuthMiddleware(client);

  try {
    // Authenticate as sponsor
    console.log('[Sponsor] Initializing sponsor review session...');
    await auth.initializeToken('sponsor');

    // Step 1: Verify own access is properly restricted
    console.log('[Sponsor] Verifying sponsor access restrictions...');
    const sponsorTools = ALL_TOOLS.slice(0, 5); // Sample of tools
    let deniedCount = 0;
    let allowedCount = 0;

    for (const tool of sponsorTools) {
      const decision = await authz.evaluate('sponsor', tool, 'trialmcp-authz');
      if (decision.allowed) {
        allowedCount++;
        console.log(`[Sponsor]   ALLOW: ${tool}`);
      } else {
        deniedCount++;
      }
    }
    console.log(`[Sponsor] Sponsor access: ${allowedCount} allowed, ${deniedCount} denied (expected mostly denied)`);

    // Step 2: Review cross-role access matrix
    console.log('\n[Sponsor] Building cross-role access matrix...');
    const matrix: PolicyMatrix[] = [];

    for (const role of ALL_ROLES) {
      const criticalTools = ['fhir_read', 'fhir_patient_lookup', 'dicom_query', 'ledger_query'];
      for (const tool of criticalTools) {
        const decision = await authz.evaluate(role, tool, 'trialmcp-authz');
        matrix.push({
          role,
          tool,
          server: 'trialmcp-authz',
          allowed: decision.allowed,
          effect: decision.effect,
        });
      }
    }

    // Display matrix
    console.log('\n[Sponsor] === Role-Tool Access Matrix ===');
    console.log('[Sponsor] ' + 'Role'.padEnd(22) + 'fhir_read  fhir_patient  dicom_query  ledger_query');
    console.log('[Sponsor] ' + '-'.repeat(80));

    for (const role of ALL_ROLES) {
      const row = matrix.filter((m) => m.role === role);
      const cells = row.map((m) => (m.allowed ? 'ALLOW' : 'DENY ').padEnd(13));
      console.log(`[Sponsor] ${role.padEnd(22)}${cells.join('')}`);
    }

    // Step 3: Verify PHI access controls
    console.log('\n[Sponsor] Verifying PHI access controls...');
    const phiTools = ['fhir_read', 'fhir_patient_lookup', 'fhir_search'];
    const restrictedRoles: ActorRole[] = ['sponsor', 'cro'];

    let phiControlsValid = true;
    for (const role of restrictedRoles) {
      for (const tool of phiTools) {
        const decision = await authz.evaluate(role, tool, 'trialmcp-fhir');
        if (decision.allowed) {
          console.log(`[Sponsor] WARNING: ${role} has access to PHI tool ${tool}`);
          phiControlsValid = false;
        }
      }
    }

    if (phiControlsValid) {
      console.log('[Sponsor] PHI access controls: COMPLIANT');
    } else {
      console.log('[Sponsor] PHI access controls: NON-COMPLIANT - review required');
    }

    // Step 4: Verify robot agent has appropriate access
    console.log('\n[Sponsor] Verifying robot agent permissions...');
    const robotTools = ['fhir_read', 'dicom_query', 'ledger_append', 'provenance_record_access'];
    for (const tool of robotTools) {
      const decision = await authz.evaluate('robot_agent', tool, 'trialmcp-fhir');
      const status = decision.allowed ? 'ALLOWED (expected)' : 'DENIED (unexpected)';
      console.log(`[Sponsor]   robot_agent -> ${tool}: ${status}`);
    }

    // Step 5: Summary
    console.log('\n[Sponsor] === Sponsor Policy Review Summary ===');
    console.log(`[Sponsor] Trial: ${TRIAL_ID}`);
    console.log(`[Sponsor] Roles reviewed: ${ALL_ROLES.length}`);
    console.log(`[Sponsor] Policy entries evaluated: ${matrix.length}`);
    console.log(`[Sponsor] PHI controls: ${phiControlsValid ? 'COMPLIANT' : 'NEEDS REVIEW'}`);
    console.log('[Sponsor] Review session complete.');

  } catch (error) {
    if (isMcpError(error)) {
      console.error(`[Sponsor] MCP Error: ${error.code} - ${error.message}`);
    } else {
      console.error('[Sponsor] Error:', error);
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
  sponsorWorkflow().catch((err) => {
    console.error('Sponsor workflow failed:', err);
    process.exit(1);
  });
}

export { sponsorWorkflow };
