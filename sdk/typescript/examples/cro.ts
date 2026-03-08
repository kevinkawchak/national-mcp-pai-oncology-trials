/**
 * Contract Research Organization (CRO) workflow example for the
 * National MCP-PAI Oncology Trials SDK.
 *
 * Demonstrates a CRO monitoring trial operations across multiple sites:
 * 1. Review authorization policies for cross-site access
 * 2. Check study status and enrollment metrics
 * 3. Verify consistent policy enforcement across sites
 * 4. Generate multi-site operational report
 *
 * CROs have access to: authz_list_policies, fhir_study_status
 */

import {
  TrialMcpClient,
  AuthzClient,
  FhirClient,
  AuthMiddleware,
  isMcpError,
  type AuthzDecision,
  type StudyStatusResult,
  type ActorRole,
} from '../src';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const CRO_ID = 'cro-globaltrials-ops';
const TRIAL_ID = 'NCT-2026-ONCO-4521';

/** Multi-site deployment endpoints */
const SITES = [
  { siteId: 'site-mayo-roch-01', name: 'Mayo Clinic Rochester', region: 'midwest' },
  { siteId: 'site-mdanderson-01', name: 'MD Anderson', region: 'south' },
  { siteId: 'site-mskcc-01', name: 'Memorial Sloan Kettering', region: 'northeast' },
  { siteId: 'site-ucsf-01', name: 'UCSF Medical Center', region: 'west' },
  { siteId: 'site-dana-farber-01', name: 'Dana-Farber Cancer Institute', region: 'northeast' },
];

function createSiteClient(siteId: string): TrialMcpClient {
  return new TrialMcpClient({
    role: 'cro',
    callerId: CRO_ID,
    trialId: TRIAL_ID,
    siteId,
    servers: {
      'trialmcp-authz': { url: `https://authz.trialmcp.national.org`, timeoutMs: 10000 },
      'trialmcp-fhir': { url: `https://fhir.trialmcp.national.org`, timeoutMs: 15000 },
    },
    retry: { maxRetries: 2 },
  });
}

// ---------------------------------------------------------------------------
// Report types
// ---------------------------------------------------------------------------

interface SiteReport {
  siteId: string;
  siteName: string;
  region: string;
  studyStatus: StudyStatusResult | null;
  policyCompliant: boolean;
  policyIssues: string[];
}

interface MultiSiteReport {
  trialId: string;
  reportDate: string;
  totalSites: number;
  sitesReviewed: number;
  totalEnrollment: number;
  policyCompliance: number;
  siteReports: SiteReport[];
}

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

async function croWorkflow(): Promise<void> {
  const siteReports: SiteReport[] = [];

  console.log('[CRO] Starting multi-site operational review...');
  console.log(`[CRO] Trial: ${TRIAL_ID}`);
  console.log(`[CRO] Sites to review: ${SITES.length}`);
  console.log('');

  for (const site of SITES) {
    console.log(`[CRO] --- Reviewing site: ${site.name} (${site.siteId}) ---`);

    const client = createSiteClient(site.siteId);
    const authz = new AuthzClient(client);
    const fhir = new FhirClient(client);
    const auth = new AuthMiddleware(client);

    const report: SiteReport = {
      siteId: site.siteId,
      siteName: site.name,
      region: site.region,
      studyStatus: null,
      policyCompliant: true,
      policyIssues: [],
    };

    try {
      // Authenticate
      await auth.initializeToken('cro');

      // Step 1: Verify CRO permissions are consistent
      console.log('[CRO]   Checking CRO permissions...');
      const allowedTools = ['authz_list_policies', 'fhir_study_status'];
      const deniedTools = ['fhir_read', 'fhir_patient_lookup', 'dicom_query', 'ledger_query'];

      for (const tool of allowedTools) {
        const decision = await authz.evaluate('cro', tool, 'trialmcp-authz');
        if (!decision.allowed) {
          report.policyCompliant = false;
          report.policyIssues.push(`Expected ALLOW for cro/${tool}, got DENY`);
        }
      }

      for (const tool of deniedTools) {
        const decision = await authz.evaluate('cro', tool, 'trialmcp-authz');
        if (decision.allowed) {
          report.policyCompliant = false;
          report.policyIssues.push(`Expected DENY for cro/${tool}, got ALLOW (PHI risk)`);
        }
      }

      console.log(`[CRO]   Policy compliance: ${report.policyCompliant ? 'PASS' : 'FAIL'}`);

      // Step 2: Check study status
      console.log('[CRO]   Querying study status...');
      try {
        report.studyStatus = await fhir.studyStatus(TRIAL_ID);
        console.log(`[CRO]   Status: ${report.studyStatus.status}`);
        console.log(`[CRO]   Phase: ${report.studyStatus.phase}`);
        console.log(`[CRO]   Enrollment: ${report.studyStatus.enrollment_count}`);
      } catch (error) {
        if (isMcpError(error)) {
          console.log(`[CRO]   Study status unavailable: ${error.code}`);
        }
      }

      // Step 3: Verify robot agent policy at this site
      console.log('[CRO]   Verifying robot agent policy...');
      const robotTools = ['fhir_read', 'dicom_query', 'ledger_append'];
      for (const tool of robotTools) {
        const decision = await authz.evaluate('robot_agent', tool, 'trialmcp-authz');
        if (!decision.allowed) {
          report.policyIssues.push(
            `Robot agent denied ${tool} at ${site.siteId} - may block procedures`,
          );
        }
      }

      siteReports.push(report);

    } catch (error) {
      if (isMcpError(error)) {
        console.error(`[CRO]   Site error: ${error.code} - ${error.message}`);
      }
      report.policyIssues.push(`Site unreachable or error: ${(error as Error).message}`);
      siteReports.push(report);
    } finally {
      auth.dispose();
    }

    console.log('');
  }

  // Generate multi-site report
  const totalEnrollment = siteReports.reduce(
    (sum, r) => sum + (r.studyStatus?.enrollment_count ?? 0),
    0,
  );
  const compliantSites = siteReports.filter((r) => r.policyCompliant).length;

  const multiSiteReport: MultiSiteReport = {
    trialId: TRIAL_ID,
    reportDate: new Date().toISOString(),
    totalSites: SITES.length,
    sitesReviewed: siteReports.length,
    totalEnrollment,
    policyCompliance: (compliantSites / siteReports.length) * 100,
    siteReports,
  };

  console.log('[CRO] === Multi-Site Operational Report ===');
  console.log(`[CRO] Trial: ${multiSiteReport.trialId}`);
  console.log(`[CRO] Date: ${multiSiteReport.reportDate}`);
  console.log(`[CRO] Sites Reviewed: ${multiSiteReport.sitesReviewed}/${multiSiteReport.totalSites}`);
  console.log(`[CRO] Total Enrollment: ${multiSiteReport.totalEnrollment}`);
  console.log(`[CRO] Policy Compliance: ${multiSiteReport.policyCompliance.toFixed(1)}%`);
  console.log('');
  console.log('[CRO] Site Details:');

  for (const report of siteReports) {
    const status = report.policyCompliant ? 'COMPLIANT' : 'NON-COMPLIANT';
    const enrollment = report.studyStatus?.enrollment_count ?? 'N/A';
    console.log(`[CRO]   ${report.siteName.padEnd(35)} ${status.padEnd(15)} Enrollment: ${enrollment}`);
    for (const issue of report.policyIssues) {
      console.log(`[CRO]     WARNING: ${issue}`);
    }
  }

  console.log('[CRO] Report complete.');
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

if (require.main === module) {
  croWorkflow().catch((err) => {
    console.error('CRO workflow failed:', err);
    process.exit(1);
  });
}

export { croWorkflow };
