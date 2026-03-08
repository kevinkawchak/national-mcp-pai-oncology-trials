/**
 * Trial Coordinator workflow example for the National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a trial coordinator managing an oncology clinical trial:
 * 1. Check study status and enrollment metrics
 * 2. Search for enrolled patients by criteria
 * 3. Review patient consent and eligibility
 * 4. Query DICOM studies for protocol compliance
 * 5. List active authorization policies
 *
 * Trial coordinators have access to: fhir_read, fhir_search, fhir_patient_lookup,
 * fhir_study_status, dicom_query, dicom_retrieve_pointer, dicom_study_metadata,
 * authz_list_policies
 */

import {
  TrialMcpClient,
  AuthzClient,
  FhirClient,
  DicomClient,
  AuthMiddleware,
  isMcpError,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const COORDINATOR_ID = 'coord-sarah-chen';
const TRIAL_ID = 'NCT-2026-ONCO-4521';
const SITE_ID = 'site-mdanderson-01';

function createClient(): TrialMcpClient {
  return new TrialMcpClient({
    role: 'trial_coordinator',
    callerId: COORDINATOR_ID,
    trialId: TRIAL_ID,
    siteId: SITE_ID,
    servers: {
      'trialmcp-authz': { url: 'https://authz.trialmcp.mdanderson.org' },
      'trialmcp-fhir': { url: 'https://fhir.trialmcp.mdanderson.org' },
      'trialmcp-dicom': { url: 'https://dicom.trialmcp.mdanderson.org' },
    },
    retry: { maxRetries: 2 },
  });
}

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function trialCoordinatorWorkflow(): Promise<void> {
  const client = createClient();
  const authz = new AuthzClient(client);
  const fhir = new FhirClient(client);
  const dicom = new DicomClient(client);
  const authMiddleware = new AuthMiddleware(client);

  try {
    // Step 1: Authenticate
    console.log('[Coordinator] Initializing session...');
    await authMiddleware.initializeToken('trial_coordinator');

    // Step 2: Check study status
    console.log('[Coordinator] Checking study status...');
    const studyStatus = await fhir.studyStatus(TRIAL_ID);
    console.log(`[Coordinator] Study: ${studyStatus.title}`);
    console.log(`[Coordinator] Phase: ${studyStatus.phase}, Status: ${studyStatus.status}`);
    console.log(`[Coordinator] Enrolled: ${studyStatus.enrollment_count} across ${studyStatus.site_count} sites`);

    // Step 3: Search for patients with specific conditions
    console.log('[Coordinator] Searching for lung cancer patients...');
    const conditions = await fhir.search('Condition', {
      code: 'C34', // ICD-10 lung cancer
      clinical_status: 'active',
    }, 50);

    const matchCount = conditions.total ?? 0;
    console.log(`[Coordinator] Found ${matchCount} active lung cancer conditions`);

    // Step 4: Look up specific patient enrollment
    console.log('[Coordinator] Looking up patient enrollment...');
    const enrollment = await fhir.patientLookup('PSEUDO-PAT-4471', TRIAL_ID);
    console.log(`[Coordinator] Patient status: ${enrollment.enrollment_status}`);
    console.log(`[Coordinator] Consent: ${enrollment.consent_status ?? 'unknown'}`);

    // Step 5: Search for adverse events
    console.log('[Coordinator] Reviewing adverse events...');
    const adverseEvents = await fhir.searchAdverseEvents(TRIAL_ID);
    console.log(`[Coordinator] Adverse events: ${adverseEvents.total ?? 0}`);

    // Step 6: Query imaging compliance
    console.log('[Coordinator] Checking imaging protocol compliance...');
    const requiredModalities = ['CT', 'PT']; // CT + PET required by protocol
    for (const modality of requiredModalities) {
      const studies = await dicom.queryByModality(modality);
      console.log(`[Coordinator] ${modality} studies on record: ${studies.length}`);
    }

    // Step 7: Search for research subjects
    console.log('[Coordinator] Querying research subjects...');
    const subjects = await fhir.search('ResearchSubject', {
      study: TRIAL_ID,
      status: 'on-study',
    }, 100);
    console.log(`[Coordinator] Active subjects: ${subjects.total ?? 0}`);

    // Step 8: Review medication administrations for protocol adherence
    console.log('[Coordinator] Checking medication administrations...');
    const meds = await fhir.search('MedicationAdministration', {
      status: 'completed',
    }, 20);
    console.log(`[Coordinator] Recent administrations: ${meds.entry?.length ?? 0}`);

    console.log('[Coordinator] Daily review complete.');

  } catch (error) {
    if (isMcpError(error)) {
      console.error(`[Coordinator] MCP Error: ${error.code} - ${error.message}`);
    } else {
      console.error('[Coordinator] Error:', error);
    }
    throw error;
  } finally {
    authMiddleware.dispose();
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

if (require.main === module) {
  trialCoordinatorWorkflow().catch((err) => {
    console.error('Trial coordinator workflow failed:', err);
    process.exit(1);
  });
}

export { trialCoordinatorWorkflow };
