/**
 * FHIR client for the National MCP-PAI Oncology Trials network.
 *
 * Wraps the trialmcp-fhir MCP server tools:
 *   - fhir_read: Read a FHIR resource by type and ID
 *   - fhir_search: Search FHIR resources with parameters
 *   - fhir_patient_lookup: Look up patient enrollment by pseudonym
 *   - fhir_study_status: Get clinical study status and enrollment metrics
 *
 * All patient identifiers use pseudonyms; real PHI never leaves the server.
 */

import { TrialMcpClient } from './client';
import { InvalidInputError, NotFoundError } from './errors';
import type {
  FhirResource,
  FhirBundle,
  FhirReadResult,
  FhirSearchParams,
  PatientLookupResult,
  StudyStatusResult,
} from './models';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER: 'trialmcp-fhir' = 'trialmcp-fhir';

/** FHIR resource types relevant to oncology trials */
const ONCOLOGY_RESOURCE_TYPES = [
  'Patient',
  'ResearchStudy',
  'ResearchSubject',
  'Observation',
  'Condition',
  'MedicationAdministration',
  'MedicationRequest',
  'Procedure',
  'DiagnosticReport',
  'ImagingStudy',
  'Consent',
  'Encounter',
  'CarePlan',
  'AdverseEvent',
  'ClinicalImpression',
] as const;

/** Maximum search results per query */
const MAX_SEARCH_RESULTS = 500;

/** Pattern for valid FHIR resource IDs */
const RESOURCE_ID_PATTERN = /^[A-Za-z0-9\-._]+$/;

// ---------------------------------------------------------------------------
// FHIR Client
// ---------------------------------------------------------------------------

export class FhirClient {
  private readonly client: TrialMcpClient;

  constructor(client: TrialMcpClient) {
    this.client = client;
  }

  /**
   * Read a single FHIR resource by type and ID.
   *
   * @param resourceType - FHIR resource type (e.g. 'Patient', 'ResearchStudy')
   * @param resourceId - Logical resource ID
   * @returns The FHIR resource with optional validation metadata
   * @throws NotFoundError if the resource does not exist
   * @throws InvalidInputError if resource type or ID is invalid
   */
  async read(resourceType: string, resourceId: string): Promise<FhirReadResult> {
    this.validateResourceType(resourceType);
    this.validateResourceId(resourceId);

    const result = await this.client.callTool<FhirReadResult>(SERVER, 'fhir_read', {
      resource_type: resourceType,
      resource_id: resourceId,
    });

    return result.data;
  }

  /**
   * Read a FHIR resource and return just the resource object.
   * Convenience wrapper around read() that unwraps the result.
   */
  async readResource(resourceType: string, resourceId: string): Promise<FhirResource> {
    const result = await this.read(resourceType, resourceId);
    return result.resource;
  }

  /**
   * Search FHIR resources with query parameters.
   *
   * Supports standard FHIR search parameters including modifiers.
   * Results are returned as a FHIR Bundle (searchset).
   *
   * @param resourceType - FHIR resource type to search
   * @param params - Search parameters as key-value pairs
   * @param maxResults - Maximum results to return (default: 100, max: 500)
   * @returns FHIR Bundle containing matching resources
   */
  async search(
    resourceType: string,
    params: Record<string, string> = {},
    maxResults: number = 100,
  ): Promise<FhirBundle> {
    this.validateResourceType(resourceType);

    if (maxResults <= 0 || maxResults > MAX_SEARCH_RESULTS) {
      throw new InvalidInputError(
        `maxResults must be between 1 and ${MAX_SEARCH_RESULTS}, got ${maxResults}`,
        { server: SERVER, tool: 'fhir_search', details: { field: 'maxResults' } },
      );
    }

    const result = await this.client.callTool<FhirBundle>(SERVER, 'fhir_search', {
      resource_type: resourceType,
      params,
      max_results: maxResults,
    });

    return result.data;
  }

  /**
   * Search for ResearchStudy resources by trial phase.
   * Convenience method for common oncology trial queries.
   */
  async searchStudiesByPhase(phase: string, status?: string): Promise<FhirBundle> {
    const params: Record<string, string> = { phase };
    if (status) params.status = status;
    return this.search('ResearchStudy', params);
  }

  /**
   * Search for adverse events associated with a study.
   */
  async searchAdverseEvents(studyId: string): Promise<FhirBundle> {
    return this.search('AdverseEvent', { study: studyId });
  }

  /**
   * Look up a patient's enrollment status using their pseudonym.
   *
   * This tool uses pseudonymous identifiers only; real patient
   * identifiers are never transmitted over the MCP network.
   *
   * @param pseudonym - Patient pseudonym assigned at enrollment
   * @param trialId - Clinical trial identifier
   * @returns Patient enrollment and consent status
   */
  async patientLookup(pseudonym: string, trialId: string): Promise<PatientLookupResult> {
    if (!pseudonym || pseudonym.trim().length === 0) {
      throw new InvalidInputError('Patient pseudonym is required', {
        server: SERVER,
        tool: 'fhir_patient_lookup',
        details: { field: 'pseudonym' },
      });
    }

    if (!trialId || trialId.trim().length === 0) {
      throw new InvalidInputError('Trial ID is required', {
        server: SERVER,
        tool: 'fhir_patient_lookup',
        details: { field: 'trial_id' },
      });
    }

    const result = await this.client.callTool<PatientLookupResult>(
      SERVER,
      'fhir_patient_lookup',
      { pseudonym, trial_id: trialId },
    );

    return result.data;
  }

  /**
   * Get the status and enrollment metrics for a clinical study.
   *
   * Returns aggregate study-level data including enrollment counts,
   * site counts, and study phase information.
   *
   * @param studyId - Clinical study identifier
   * @returns Study status with enrollment metrics
   */
  async studyStatus(studyId: string): Promise<StudyStatusResult> {
    if (!studyId || studyId.trim().length === 0) {
      throw new InvalidInputError('Study ID is required', {
        server: SERVER,
        tool: 'fhir_study_status',
        details: { field: 'study_id' },
      });
    }

    const result = await this.client.callTool<StudyStatusResult>(
      SERVER,
      'fhir_study_status',
      { study_id: studyId },
    );

    return result.data;
  }

  /**
   * Retrieve multiple resources by type and IDs in parallel.
   *
   * @param resourceType - FHIR resource type
   * @param resourceIds - Array of resource IDs to fetch
   * @returns Array of resources (nulls for not-found)
   */
  async readMany(
    resourceType: string,
    resourceIds: string[],
  ): Promise<(FhirResource | null)[]> {
    const results = await Promise.allSettled(
      resourceIds.map((id) => this.readResource(resourceType, id)),
    );

    return results.map((r) =>
      r.status === 'fulfilled' ? r.value : null,
    );
  }

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------

  private validateResourceType(resourceType: string): void {
    if (!resourceType || !/^[A-Z][a-zA-Z]+$/.test(resourceType)) {
      throw new InvalidInputError(
        `Invalid FHIR resource type '${resourceType}'. Must be PascalCase (e.g. 'Patient')`,
        {
          server: SERVER,
          details: { field: 'resource_type', expectedPattern: '^[A-Z][a-zA-Z]+$' },
        },
      );
    }
  }

  private validateResourceId(resourceId: string): void {
    if (!resourceId || !RESOURCE_ID_PATTERN.test(resourceId)) {
      throw new InvalidInputError(
        `Invalid resource ID '${resourceId}'. Contains prohibited characters`,
        {
          server: SERVER,
          details: { field: 'resource_id', expectedPattern: '^[A-Za-z0-9\\-._]+$' },
        },
      );
    }
  }
}
