/**
 * TypeScript interfaces for all domain models in the
 * National MCP-PAI Oncology Trials network.
 *
 * These interfaces align with the JSON Schemas in /schemas/ and the
 * generated models in /models/typescript/generated_models.ts.
 */

// ---------------------------------------------------------------------------
// Authorization models
// ---------------------------------------------------------------------------

export type PolicyEffect = 'ALLOW' | 'DENY';

export type ActorRole =
  | 'robot_agent'
  | 'trial_coordinator'
  | 'data_monitor'
  | 'auditor'
  | 'sponsor'
  | 'cro';

export interface MatchingRule {
  role: string;
  server: string;
  tool: string;
  effect: PolicyEffect;
}

export interface AuthzDecision {
  allowed: boolean;
  effect: PolicyEffect;
  role: string;
  server: string;
  tool: string;
  evaluated_at: string;
  matching_rules?: MatchingRule[];
  deny_reason?: string;
  token_info?: Record<string, unknown>;
}

export interface TokenIssuance {
  token_hash: string;
  role: string;
  issued_at: string;
  expires_at: string;
}

export interface TokenValidation {
  valid: boolean;
  role?: string;
  reason?: string;
}

export interface TokenRevocation {
  revoked: boolean;
  token_hash?: string;
  reason?: string;
}

// ---------------------------------------------------------------------------
// FHIR models
// ---------------------------------------------------------------------------

export interface FhirResource {
  resourceType: string;
  id: string;
  meta?: FhirMeta;
  [key: string]: unknown;
}

export interface FhirMeta {
  versionId?: string;
  lastUpdated?: string;
  source?: string;
  profile?: string[];
  security?: FhirCoding[];
  tag?: FhirCoding[];
}

export interface FhirCoding {
  system?: string;
  code?: string;
  display?: string;
}

export interface FhirBundle {
  resourceType: 'Bundle';
  type: 'searchset' | 'batch' | 'transaction' | 'collection';
  total?: number;
  entry?: FhirBundleEntry[];
  link?: FhirBundleLink[];
}

export interface FhirBundleEntry {
  resource: FhirResource;
  fullUrl?: string;
  search?: { mode?: string; score?: number };
}

export interface FhirBundleLink {
  relation: string;
  url: string;
}

export interface FhirReadResult {
  resource: FhirResource;
  validation?: { valid: boolean; errors?: string[] };
}

export interface FhirSearchParams {
  resourceType: string;
  params: Record<string, string>;
  maxResults?: number;
}

export interface PatientLookupResult {
  patient_pseudonym: string;
  trial_id: string;
  enrollment_status: string;
  consent_status?: string;
  site_id?: string;
}

export interface StudyStatusResult {
  study_id: string;
  title: string;
  status: string;
  phase: string;
  enrollment_count: number;
  site_count: number;
  start_date?: string;
  end_date?: string;
  principal_investigator?: string;
}

// ---------------------------------------------------------------------------
// DICOM models
// ---------------------------------------------------------------------------

export interface DicomQueryParams {
  study_instance_uid?: string;
  patient_pseudonym?: string;
  modality?: string;
  study_date?: string;
  accession_number?: string;
  series_instance_uid?: string;
  limit?: number;
}

export interface DicomStudy {
  study_instance_uid: string;
  patient_pseudonym: string;
  study_date: string;
  modality: string;
  study_description?: string;
  accession_number?: string;
  number_of_series?: number;
  number_of_instances?: number;
  referring_physician?: string;
}

export interface DicomRetrieveParams {
  study_instance_uid: string;
  series_instance_uid?: string;
  sop_instance_uid?: string;
  transfer_syntax?: string;
}

export interface DicomRetrieveResult {
  wado_uri: string;
  study_instance_uid: string;
  series_instance_uid?: string;
  content_type: string;
  transfer_syntax: string;
  size_bytes?: number;
  checksum?: string;
}

export interface DicomQueryResult {
  studies: DicomStudy[];
  total_count: number;
  has_more: boolean;
}

// ---------------------------------------------------------------------------
// Ledger / Audit models
// ---------------------------------------------------------------------------

export interface AuditRecord {
  audit_id: string;
  timestamp: string;
  server: string;
  tool: string;
  caller: string;
  parameters: Record<string, unknown>;
  result_summary: string;
  hash: string;
  previous_hash: string;
}

export interface LedgerAppendParams {
  server: string;
  tool: string;
  caller: string;
  result_summary: string;
  parameters?: Record<string, unknown>;
}

export interface LedgerVerifyResult {
  valid: boolean;
  length: number;
  reason?: string;
  broken_at_index?: number;
}

export interface LedgerQueryParams {
  server?: string;
  tool?: string;
  caller?: string;
  from_timestamp?: string;
  to_timestamp?: string;
  limit?: number;
}

export interface LedgerExportResult {
  records: AuditRecord[];
  chain_length: number;
  export_timestamp: string;
  checksum: string;
}

// ---------------------------------------------------------------------------
// Provenance models
// ---------------------------------------------------------------------------

export interface ProvenanceRecord {
  record_id: string;
  source_id: string;
  action: string;
  actor_id: string;
  actor_role: string;
  tool_call: string;
  timestamp: string;
  source_type?: string;
  input_hash?: string;
  output_hash?: string;
  origin_server?: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface ProvenanceRecordParams {
  source_id: string;
  action: string;
  actor_id: string;
  actor_role: ActorRole;
  tool_call: string;
  source_type?: string;
  input_hash?: string;
  output_hash?: string;
  origin_server?: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface ProvenanceQueryResult {
  records: ProvenanceRecord[];
  total_count: number;
  query_direction: 'forward' | 'backward';
}

export interface ProvenanceVerifyResult {
  valid: boolean;
  source_id: string;
  chain_length: number;
  first_recorded: string;
  last_recorded: string;
  actors_involved: string[];
  issues?: string[];
}

// ---------------------------------------------------------------------------
// Health and capability models
// ---------------------------------------------------------------------------

export interface DependencyStatus {
  name: string;
  status: string;
  latency_ms?: number;
}

export interface HealthStatus {
  server_name: string;
  status: string;
  version: string;
  uptime_seconds: number;
  checked_at: string;
  conformance_level?: number;
  dependencies?: DependencyStatus[];
  metrics?: Record<string, unknown>;
  site_id?: string;
}

export interface CapabilityDescriptor {
  server_name: string;
  version: string;
  conformance_level: number;
  tools: string[];
  vendor_extensions?: string[];
  regulatory_certifications?: string[];
  contact?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Task and consent models
// ---------------------------------------------------------------------------

export interface TaskOrder {
  task_id: string;
  trial_id: string;
  site_id: string;
  procedure_type: string;
  robot_id: string;
  status: string;
  scheduled_at: string;
  patient_pseudonym?: string;
  started_at?: string;
  completed_at?: string;
  safety_prerequisites?: Record<string, unknown>[];
  usl_score_minimum?: number;
  mcp_tools_used?: string[];
  audit_record_ids?: string[];
  notes?: string;
}

export interface ConsentStatus {
  consent_id: string;
  patient_pseudonym: string;
  trial_id: string;
  consent_state: string;
  consent_categories: Record<string, unknown>[];
  recorded_at: string;
  recorded_by?: string;
  site_id?: string;
  irb_protocol_version?: string;
  electronic_signature?: Record<string, unknown>;
  state_history?: Record<string, unknown>[];
}

// ---------------------------------------------------------------------------
// Error response model
// ---------------------------------------------------------------------------

export interface ErrorResponse {
  error: true;
  code: string;
  message: string;
  server?: string;
  tool?: string;
  timestamp?: string;
  request_id?: string;
  details?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Generic MCP tool call/result
// ---------------------------------------------------------------------------

export interface McpToolCall {
  server: string;
  tool: string;
  parameters: Record<string, unknown>;
  caller: string;
  role: ActorRole;
  requestId: string;
  timestamp: string;
}

export interface McpToolResult<T = unknown> {
  data: T;
  requestId: string;
  server: string;
  tool: string;
  durationMs: number;
  timestamp: string;
}
