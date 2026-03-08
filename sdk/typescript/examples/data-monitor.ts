/**
 * Data Monitor workflow example for the National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a data safety monitoring board (DSMB) member reviewing
 * trial data for safety signals:
 * 1. Search for adverse events across all sites
 * 2. Review patient conditions and lab results
 * 3. Analyze imaging study completeness
 * 4. Generate safety metric summaries
 *
 * Data monitors have access to: fhir_read, fhir_search, dicom_query,
 * dicom_study_metadata
 */

import {
  TrialMcpClient,
  FhirClient,
  DicomClient,
  AuthMiddleware,
  isMcpError,
  type FhirBundle,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const MONITOR_ID = 'dsmb-member-dr-patel';
const TRIAL_ID = 'NCT-2026-ONCO-4521';

function createClient(): TrialMcpClient {
  return new TrialMcpClient({
    role: 'data_monitor',
    callerId: MONITOR_ID,
    trialId: TRIAL_ID,
    servers: {
      'trialmcp-authz': { url: 'https://authz.trialmcp.national.org' },
      'trialmcp-fhir': { url: 'https://fhir.trialmcp.national.org', timeoutMs: 15000 },
      'trialmcp-dicom': { url: 'https://dicom.trialmcp.national.org', timeoutMs: 15000 },
    },
    retry: { maxRetries: 2, baseDelayMs: 2000 },
  });
}

// ---------------------------------------------------------------------------
// Safety analysis helpers
// ---------------------------------------------------------------------------

interface SafetyMetrics {
  totalAdverseEvents: number;
  seriousAdverseEvents: number;
  gradeThreePlus: number;
  imagingCompleteness: number;
  dataQualityScore: number;
}

function analyzeSafetyBundle(bundle: FhirBundle): Partial<SafetyMetrics> {
  const entries = bundle.entry ?? [];
  let serious = 0;
  let gradeThreePlus = 0;

  for (const entry of entries) {
    const resource = entry.resource;
    if (resource.seriousness === 'serious') serious++;
    const grade = resource.severity as string | undefined;
    if (grade && ['grade-3', 'grade-4', 'grade-5'].includes(grade)) {
      gradeThreePlus++;
    }
  }

  return {
    totalAdverseEvents: entries.length,
    seriousAdverseEvents: serious,
    gradeThreePlus,
  };
}

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function dataMonitorWorkflow(): Promise<void> {
  const client = createClient();
  const fhir = new FhirClient(client);
  const dicom = new DicomClient(client);
  const auth = new AuthMiddleware(client);

  try {
    // Authenticate as data monitor
    console.log('[Monitor] Initializing DSMB review session...');
    await auth.initializeToken('data_monitor');

    // Step 1: Retrieve all adverse events for the trial
    console.log('[Monitor] Querying adverse events across all sites...');
    const adverseEvents = await fhir.search('AdverseEvent', {
      study: TRIAL_ID,
      _sort: '-date',
    }, 200);

    const safetyMetrics = analyzeSafetyBundle(adverseEvents);
    console.log(`[Monitor] Total AEs: ${safetyMetrics.totalAdverseEvents}`);
    console.log(`[Monitor] Serious AEs: ${safetyMetrics.seriousAdverseEvents}`);
    console.log(`[Monitor] Grade 3+: ${safetyMetrics.gradeThreePlus}`);

    // Step 2: Search for recent lab observations
    console.log('[Monitor] Reviewing laboratory results...');
    const labResults = await fhir.search('Observation', {
      category: 'laboratory',
      status: 'final',
      _sort: '-date',
    }, 100);
    console.log(`[Monitor] Lab results reviewed: ${labResults.total ?? 0}`);

    // Step 3: Check hematology parameters (critical for oncology)
    console.log('[Monitor] Checking hematology parameters...');
    const hemaObs = await fhir.search('Observation', {
      code: '58410-2', // CBC panel LOINC
      status: 'final',
    }, 50);
    console.log(`[Monitor] CBC panels: ${hemaObs.total ?? 0}`);

    // Step 4: Review conditions for dose-limiting toxicities
    console.log('[Monitor] Scanning for dose-limiting toxicities...');
    const toxicities = await fhir.search('Condition', {
      category: 'problem-list-item',
      clinical_status: 'active',
    }, 100);
    console.log(`[Monitor] Active conditions: ${toxicities.total ?? 0}`);

    // Step 5: Check imaging study completeness
    console.log('[Monitor] Auditing imaging protocol compliance...');
    const ctStudies = await dicom.queryByModality('CT');
    const petStudies = await dicom.queryByModality('PT');
    const mriStudies = await dicom.queryByModality('MR');

    console.log(`[Monitor] CT studies: ${ctStudies.length}`);
    console.log(`[Monitor] PET studies: ${petStudies.length}`);
    console.log(`[Monitor] MRI studies: ${mriStudies.length}`);

    // Step 6: Search for diagnostic reports
    console.log('[Monitor] Reviewing diagnostic reports...');
    const diagReports = await fhir.search('DiagnosticReport', {
      status: 'final',
      category: 'LAB',
    }, 50);
    console.log(`[Monitor] Final diagnostic reports: ${diagReports.total ?? 0}`);

    // Summary
    console.log('\n[Monitor] === DSMB Review Summary ===');
    console.log(`[Monitor] Trial: ${TRIAL_ID}`);
    console.log(`[Monitor] Adverse Events: ${safetyMetrics.totalAdverseEvents} total, ${safetyMetrics.seriousAdverseEvents} serious`);
    console.log(`[Monitor] Imaging: CT=${ctStudies.length}, PET=${petStudies.length}, MRI=${mriStudies.length}`);
    console.log(`[Monitor] Lab Reports: ${labResults.total ?? 0}`);
    console.log('[Monitor] Review session complete.');

  } catch (error) {
    if (isMcpError(error)) {
      console.error(`[Monitor] MCP Error: ${error.code} - ${error.message}`);
    } else {
      console.error('[Monitor] Error:', error);
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
  dataMonitorWorkflow().catch((err) => {
    console.error('Data monitor workflow failed:', err);
    process.exit(1);
  });
}

export { dataMonitorWorkflow };
