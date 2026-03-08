/**
 * Robot Agent workflow example for the National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a Physical AI robot agent performing an oncology procedure:
 * 1. Authenticate and obtain a session token
 * 2. Verify authorization for required tools
 * 3. Read patient data (pseudonymized) from FHIR
 * 4. Query DICOM imaging studies for treatment planning
 * 5. Record provenance for all data access
 * 6. Append audit trail entries to the ledger
 *
 * Robot agents have access to: fhir_read, dicom_query, dicom_retrieve_pointer,
 * ledger_append, provenance_record_access
 */

import {
  TrialMcpClient,
  AuthzClient,
  FhirClient,
  DicomClient,
  LedgerClient,
  ProvenanceClient,
  AuthMiddleware,
  AuditMiddleware,
  isMcpError,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const ROBOT_ID = 'robot-onc-arm-007';
const TRIAL_ID = 'NCT-2026-ONCO-4521';
const SITE_ID = 'site-mayo-roch-01';

function createClient(): TrialMcpClient {
  return new TrialMcpClient({
    role: 'robot_agent',
    callerId: ROBOT_ID,
    trialId: TRIAL_ID,
    siteId: SITE_ID,
    servers: {
      'trialmcp-authz': { url: 'https://authz.trialmcp.mayo.org', timeoutMs: 5000 },
      'trialmcp-fhir': { url: 'https://fhir.trialmcp.mayo.org', timeoutMs: 10000 },
      'trialmcp-dicom': { url: 'https://dicom.trialmcp.mayo.org', timeoutMs: 30000 },
      'trialmcp-ledger': { url: 'https://ledger.trialmcp.mayo.org', timeoutMs: 5000 },
      'trialmcp-provenance': { url: 'https://prov.trialmcp.mayo.org', timeoutMs: 5000 },
    },
    retry: { maxRetries: 3, baseDelayMs: 500 },
    debug: true,
  });
}

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function robotAgentWorkflow(): Promise<void> {
  const client = createClient();
  const authz = new AuthzClient(client);
  const fhir = new FhirClient(client);
  const dicom = new DicomClient(client);
  const ledger = new LedgerClient(client);
  const provenance = new ProvenanceClient(client);

  // Attach audit middleware for automatic logging
  const audit = new AuditMiddleware(client, {
    includeParameters: false, // Never log PHI
    excludeServers: ['trialmcp-ledger'], // Avoid recursive audit
  });
  audit.attach(client);

  try {
    // Step 1: Obtain session token
    console.log('[Robot] Obtaining session token...');
    const token = await authz.issueToken('robot_agent', 3600);
    console.log(`[Robot] Token issued, expires: ${token.expires_at}`);

    // Step 2: Verify authorization for required tools
    console.log('[Robot] Verifying tool authorizations...');
    const requiredTools = ['fhir_read', 'dicom_query', 'dicom_retrieve_pointer'];
    for (const tool of requiredTools) {
      const decision = await authz.evaluate('robot_agent', tool, 'trialmcp-fhir');
      console.log(`[Robot] ${tool}: ${decision.effect}`);
      if (!decision.allowed) {
        throw new Error(`Required tool '${tool}' not authorized for robot_agent`);
      }
    }

    // Step 3: Read patient data (pseudonym only)
    const patientPseudonym = 'PSEUDO-PAT-9823';
    console.log(`[Robot] Reading patient data: ${patientPseudonym}`);
    const patientData = await fhir.read('Patient', patientPseudonym);
    console.log(`[Robot] Patient resource loaded: ${patientData.resource.id}`);

    // Record provenance for patient data access
    await provenance.recordRead(
      `Patient/${patientPseudonym}`,
      ROBOT_ID,
      'robot_agent',
      'fhir_read',
      'Robot agent read patient demographics for procedure preparation',
    );

    // Step 4: Query DICOM imaging for treatment planning
    console.log('[Robot] Querying CT imaging studies...');
    const ctStudies = await dicom.queryByPatient(patientPseudonym, 'CT');
    console.log(`[Robot] Found ${ctStudies.length} CT studies`);

    if (ctStudies.length > 0) {
      const latestStudy = ctStudies[0];
      console.log(`[Robot] Retrieving latest CT: ${latestStudy.study_instance_uid}`);
      const pointer = await dicom.retrieveStudySeries(latestStudy.study_instance_uid);
      console.log(`[Robot] WADO-RS URI: ${pointer.wado_uri}`);

      // Record provenance for imaging access
      await provenance.recordRead(
        `DicomStudy/${latestStudy.study_instance_uid}`,
        ROBOT_ID,
        'robot_agent',
        'dicom_retrieve_pointer',
        'Robot agent retrieved CT study for robotic procedure guidance',
      );
    }

    // Step 5: Query radiation therapy plans
    console.log('[Robot] Querying radiation therapy data...');
    const rtData = await dicom.queryRadiationTherapy(patientPseudonym);
    console.log(`[Robot] Found ${rtData.length} RT objects`);

    // Step 6: Append audit trail
    console.log('[Robot] Recording procedure preparation audit...');
    await ledger.auditToolCall(
      'trialmcp-fhir',
      'fhir_read',
      ROBOT_ID,
      `Robot ${ROBOT_ID} read patient ${patientPseudonym} for procedure preparation`,
    );

    // Step 7: Cleanup - revoke token
    console.log('[Robot] Revoking session token...');
    await authz.revokeToken(token.token_hash);
    console.log('[Robot] Workflow complete.');

  } catch (error) {
    if (isMcpError(error)) {
      console.error(`[Robot] MCP Error: ${error.code} - ${error.message}`);
      console.error(`[Robot] Server: ${error.server}, Tool: ${error.tool}`);
    } else {
      console.error('[Robot] Unexpected error:', error);
    }
    throw error;
  } finally {
    audit.dispose();
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

if (require.main === module) {
  robotAgentWorkflow().catch((err) => {
    console.error('Robot agent workflow failed:', err);
    process.exit(1);
  });
}

export { robotAgentWorkflow };
