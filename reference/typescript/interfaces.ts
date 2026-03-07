/**
 * Generated TypeScript interfaces from /schemas/*.schema.json.
 *
 * These interfaces correspond to the auto-generated Python dataclasses
 * in models/python/generated_models.py and the TypeScript interfaces
 * in models/typescript/generated_models.ts.
 */

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

export interface AuthzDecision {
  allowed: boolean;
  effect: "ALLOW" | "DENY";
  role: string;
  server: string;
  tool: string;
  evaluated_at: string;
  matching_rules?: MatchingRule[];
  deny_reason?: string;
  token_info?: Record<string, unknown>;
}

export interface MatchingRule {
  role: string;
  server: string;
  tool: string;
  effect: "ALLOW" | "DENY";
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

export interface DicomQuery {
  request?: Record<string, unknown>;
  response?: Record<string, unknown>;
  permissions?: Record<string, unknown>;
  errors?: string[];
}

export interface ErrorResponse {
  error: boolean;
  code: string;
  message: string;
  server?: string;
  tool?: string;
  timestamp?: string;
  request_id?: string;
  details?: Record<string, unknown>;
}

export interface FhirRead {
  request?: Record<string, unknown>;
  response?: Record<string, unknown>;
  validation?: Record<string, unknown>;
  errors?: string[];
}

export interface FhirSearch {
  request?: Record<string, unknown>;
  response?: Record<string, unknown>;
  errors?: string[];
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

export interface DependencyStatus {
  name: string;
  status: string;
  latency_ms?: number;
}

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

export interface RobotCapabilityProfile {
  robot_id: string;
  platform: string;
  robot_type: string;
  usl_score: number;
  safety_prerequisites: Record<string, unknown>[];
  mcp_tools_required: string[];
  simulation_frameworks?: string[];
  site_id?: string;
  firmware_version?: string;
  last_calibration?: string;
}

export interface SiteCapabilityProfile {
  site_id: string;
  site_name: string;
  jurisdiction: Record<string, unknown>;
  servers: unknown[];
  conformance_level: number;
  data_residency: Record<string, unknown>;
  site_type?: string;
  robots?: unknown[];
  irb_approval?: Record<string, unknown>;
  contact?: Record<string, unknown>;
}

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
