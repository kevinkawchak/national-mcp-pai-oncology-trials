/**
 * DICOM client for the National MCP-PAI Oncology Trials network.
 *
 * Wraps the trialmcp-dicom MCP server tools:
 *   - dicom_query: Query DICOM studies by patient, modality, date, etc.
 *   - dicom_retrieve: Retrieve DICOM study/series pointers (WADO-RS URIs)
 *
 * All patient references use pseudonyms. Actual DICOM pixel data is
 * accessed via WADO-RS URIs returned by retrieve; the MCP server
 * never transmits raw imaging data over the MCP protocol.
 */

import { TrialMcpClient } from './client';
import { InvalidInputError } from './errors';
import type {
  DicomQueryParams,
  DicomQueryResult,
  DicomStudy,
  DicomRetrieveParams,
  DicomRetrieveResult,
} from './models';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER: 'trialmcp-dicom' = 'trialmcp-dicom';

/** Supported DICOM modalities for oncology imaging */
const ONCOLOGY_MODALITIES = [
  'CT',    // Computed Tomography
  'MR',    // Magnetic Resonance
  'PT',    // Positron Emission Tomography
  'NM',    // Nuclear Medicine
  'US',    // Ultrasound
  'DX',    // Digital Radiography
  'CR',    // Computed Radiography
  'MG',    // Mammography
  'XA',    // X-Ray Angiography
  'RTDOSE', // Radiation Therapy Dose
  'RTPLAN', // Radiation Therapy Plan
  'RTSTRUCT', // Radiation Therapy Structure Set
  'RTIMAGE', // Radiation Therapy Image
  'SEG',   // Segmentation
  'SR',    // Structured Report
] as const;

type OncologyModality = typeof ONCOLOGY_MODALITIES[number];

/** DICOM UID pattern (dotted numeric) */
const UID_PATTERN = /^[0-9]+(\.[0-9]+)*$/;

/** DICOM date format (YYYYMMDD or range) */
const DATE_PATTERN = /^\d{8}(-\d{8})?$/;

/** Maximum query results */
const MAX_QUERY_RESULTS = 200;

// ---------------------------------------------------------------------------
// DICOM Client
// ---------------------------------------------------------------------------

export class DicomClient {
  private readonly client: TrialMcpClient;

  constructor(client: TrialMcpClient) {
    this.client = client;
  }

  /**
   * Query DICOM studies matching the given criteria.
   *
   * Supports filtering by patient pseudonym, modality, date range,
   * study UID, and accession number. Results are paginated.
   *
   * @param params - Query parameters for filtering studies
   * @returns Matching studies with pagination metadata
   */
  async query(params: DicomQueryParams = {}): Promise<DicomQueryResult> {
    this.validateQueryParams(params);

    const toolParams: Record<string, unknown> = {};

    if (params.study_instance_uid) {
      toolParams.study_instance_uid = params.study_instance_uid;
    }
    if (params.patient_pseudonym) {
      toolParams.patient_pseudonym = params.patient_pseudonym;
    }
    if (params.modality) {
      toolParams.modality = params.modality;
    }
    if (params.study_date) {
      toolParams.study_date = params.study_date;
    }
    if (params.accession_number) {
      toolParams.accession_number = params.accession_number;
    }
    if (params.series_instance_uid) {
      toolParams.series_instance_uid = params.series_instance_uid;
    }
    if (params.limit !== undefined) {
      toolParams.limit = Math.min(params.limit, MAX_QUERY_RESULTS);
    }

    const result = await this.client.callTool<DicomQueryResult>(
      SERVER,
      'dicom_query',
      toolParams,
    );

    return result.data;
  }

  /**
   * Query studies for a specific patient pseudonym.
   * Convenience method for patient-scoped queries.
   */
  async queryByPatient(
    patientPseudonym: string,
    modality?: string,
  ): Promise<DicomStudy[]> {
    const result = await this.query({
      patient_pseudonym: patientPseudonym,
      modality,
    });
    return result.studies;
  }

  /**
   * Query studies by modality (e.g. CT, MR, PT for PET).
   */
  async queryByModality(
    modality: string,
    dateRange?: string,
  ): Promise<DicomStudy[]> {
    const result = await this.query({
      modality,
      study_date: dateRange,
    });
    return result.studies;
  }

  /**
   * Query radiation therapy plans and structures.
   * Common in oncology for treatment planning verification.
   */
  async queryRadiationTherapy(patientPseudonym: string): Promise<DicomStudy[]> {
    const rtModalities = ['RTPLAN', 'RTSTRUCT', 'RTDOSE', 'RTIMAGE'];
    const results: DicomStudy[] = [];

    for (const modality of rtModalities) {
      const queryResult = await this.query({
        patient_pseudonym: patientPseudonym,
        modality,
      });
      results.push(...queryResult.studies);
    }

    return results;
  }

  /**
   * Retrieve a DICOM study/series pointer (WADO-RS URI).
   *
   * Returns a URI that can be used to access the actual DICOM data
   * through a WADO-RS compliant server. The MCP server performs
   * authorization checks before returning the pointer.
   *
   * @param params - Retrieve parameters specifying the target study/series
   * @returns WADO-RS URI and metadata for accessing the DICOM data
   */
  async retrieve(params: DicomRetrieveParams): Promise<DicomRetrieveResult> {
    this.validateRetrieveParams(params);

    const result = await this.client.callTool<DicomRetrieveResult>(
      SERVER,
      'dicom_retrieve_pointer',
      {
        study_instance_uid: params.study_instance_uid,
        series_instance_uid: params.series_instance_uid,
        sop_instance_uid: params.sop_instance_uid,
        transfer_syntax: params.transfer_syntax,
      },
    );

    return result.data;
  }

  /**
   * Retrieve pointers for all series within a study.
   */
  async retrieveStudySeries(studyUid: string): Promise<DicomRetrieveResult> {
    return this.retrieve({ study_instance_uid: studyUid });
  }

  /**
   * Retrieve a specific series within a study.
   */
  async retrieveSeries(
    studyUid: string,
    seriesUid: string,
  ): Promise<DicomRetrieveResult> {
    return this.retrieve({
      study_instance_uid: studyUid,
      series_instance_uid: seriesUid,
    });
  }

  /**
   * Check if a study exists by querying for its UID.
   */
  async studyExists(studyUid: string): Promise<boolean> {
    try {
      const result = await this.query({ study_instance_uid: studyUid, limit: 1 });
      return result.total_count > 0;
    } catch {
      return false;
    }
  }

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------

  private validateQueryParams(params: DicomQueryParams): void {
    if (params.study_instance_uid && !UID_PATTERN.test(params.study_instance_uid)) {
      throw new InvalidInputError(
        `Invalid DICOM Study Instance UID format: '${params.study_instance_uid}'`,
        {
          server: SERVER,
          tool: 'dicom_query',
          details: { field: 'study_instance_uid', expectedPattern: 'Dotted numeric UID' },
        },
      );
    }

    if (params.series_instance_uid && !UID_PATTERN.test(params.series_instance_uid)) {
      throw new InvalidInputError(
        `Invalid DICOM Series Instance UID format: '${params.series_instance_uid}'`,
        {
          server: SERVER,
          tool: 'dicom_query',
          details: { field: 'series_instance_uid', expectedPattern: 'Dotted numeric UID' },
        },
      );
    }

    if (params.study_date && !DATE_PATTERN.test(params.study_date)) {
      throw new InvalidInputError(
        `Invalid DICOM date format: '${params.study_date}'. Use YYYYMMDD or YYYYMMDD-YYYYMMDD`,
        {
          server: SERVER,
          tool: 'dicom_query',
          details: { field: 'study_date', expectedPattern: 'YYYYMMDD or YYYYMMDD-YYYYMMDD' },
        },
      );
    }

    if (params.limit !== undefined && (params.limit < 1 || params.limit > MAX_QUERY_RESULTS)) {
      throw new InvalidInputError(
        `Query limit must be between 1 and ${MAX_QUERY_RESULTS}, got ${params.limit}`,
        { server: SERVER, tool: 'dicom_query', details: { field: 'limit' } },
      );
    }
  }

  private validateRetrieveParams(params: DicomRetrieveParams): void {
    if (!params.study_instance_uid) {
      throw new InvalidInputError(
        'study_instance_uid is required for DICOM retrieve',
        { server: SERVER, tool: 'dicom_retrieve_pointer', details: { field: 'study_instance_uid' } },
      );
    }

    if (!UID_PATTERN.test(params.study_instance_uid)) {
      throw new InvalidInputError(
        `Invalid Study Instance UID: '${params.study_instance_uid}'`,
        {
          server: SERVER,
          tool: 'dicom_retrieve_pointer',
          details: { field: 'study_instance_uid', expectedPattern: 'Dotted numeric UID' },
        },
      );
    }

    if (params.series_instance_uid && !UID_PATTERN.test(params.series_instance_uid)) {
      throw new InvalidInputError(
        `Invalid Series Instance UID: '${params.series_instance_uid}'`,
        {
          server: SERVER,
          tool: 'dicom_retrieve_pointer',
          details: { field: 'series_instance_uid', expectedPattern: 'Dotted numeric UID' },
        },
      );
    }
  }
}
