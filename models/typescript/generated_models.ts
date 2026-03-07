/**
 * Auto-generated typed interfaces from /schemas/*.schema.json.
 *
 * DO NOT EDIT — regenerate with: python scripts/generate_models.py
 */

/** Audit Record */
export interface AuditRecord {
  /** Unique identifier for this audit record (UUID v4). */
  audit_id: string;
  /** ISO 8601 UTC timestamp of the audited event. */
  timestamp: string;
  /** MCP server that generated the event. */
  server: string;
  /** MCP tool that was invoked. */
  tool: string;
  /** Actor identifier. MUST be pseudonymized for patient-related calls. */
  caller: string;
  /** Tool call parameters. MUST be de-identified where applicable (no raw patient IDs, no PHI). */
  parameters: Record<string, unknown>;
  /** Brief outcome description of the tool invocation. */
  result_summary: string;
  /** SHA-256 hex digest (64 characters) of this record's canonical JSON serialization (alphabetical key order, excluding the hash field itself). */
  hash: string;
  /** SHA-256 hex digest of the preceding audit record. Genesis record uses '0' repeated 64 times. */
  previous_hash: string;
}

/** Authorization Decision */
export interface AuthzDecision {
  /** Whether the access request is authorized. */
  allowed: boolean;
  /** The policy evaluation outcome. */
  effect: string;
  /** Actor role that was evaluated. */
  role: string;
  /** Target MCP server for the request. */
  server: string;
  /** Target MCP tool for the request. */
  tool: string;
  /** Policy rules that matched this access request. */
  matching_rules?: Record<string, unknown>[];
  /** ISO 8601 UTC timestamp of the evaluation. */
  evaluated_at: string;
  /** Human-readable explanation when access is denied. */
  deny_reason?: string;
  /** Session token details if token-based authentication was used. */
  token_info?: Record<string, unknown>;
}

/** MCP Server Capability Descriptor */
export interface CapabilityDescriptor {
  /** Unique identifier for the MCP server (e.g., trialmcp-authz, trialmcp-fhir). */
  server_name: string;
  /** SemVer version of the server implementation. */
  version: string;
  /** The conformance level this server satisfies (1–5). */
  conformance_level: number;
  /** List of MCP tool names exposed by this server. */
  tools: string[];
  /** Optional vendor extension tool names (must use x-{vendor} prefix). */
  vendor_extensions?: string[];
  /** Regulatory standards the server claims compliance with. */
  regulatory_certifications?: string[];
  /** Contact information for the server operator. */
  contact?: Record<string, unknown>;
}

/** Consent Status */
export interface ConsentStatus {
  /** Unique identifier for this consent record (UUID v4). */
  consent_id: string;
  /** HMAC-SHA256 pseudonymized patient identifier. MUST NOT contain the real patient ID. */
  patient_pseudonym: string;
  /** Clinical trial identifier (e.g., NCT number). */
  trial_id: string;
  /** Current state in the consent state machine. */
  consent_state: string;
  /** Granular consent categories with individual status. */
  consent_categories: Record<string, unknown>[];
  /** ISO 8601 UTC timestamp of when this consent status was recorded. */
  recorded_at: string;
  /** Identifier of the actor who recorded the consent (typically trial_coordinator). */
  recorded_by?: string;
  /** Clinical site where consent was obtained. */
  site_id?: string;
  /** Version of the IRB-approved consent protocol used. */
  irb_protocol_version?: string;
  /** 21 CFR Part 11 compliant electronic signature. */
  electronic_signature?: Record<string, unknown>;
  /** Chronological history of consent state transitions. */
  state_history?: Record<string, unknown>[];
}

/** DICOM Query */
export interface DicomQuery {
  /** DICOM query input parameters. */
  request?: Record<string, unknown>;
  /** DICOM query output. */
  response?: Record<string, unknown>;
  /** Role-based query level permissions. */
  permissions?: Record<string, unknown>;
  /** Possible error codes. */
  errors?: string[];
}

/** Error Response */
export interface ErrorResponse {
  /** Always true for error responses. */
  error: boolean;
  /** Machine-readable error code from the standard taxonomy. */
  code: string;
  /** Human-readable error description. MUST NOT contain PHI, patient identifiers, or internal system details. */
  message: string;
  /** MCP server that generated the error. */
  server?: string;
  /** MCP tool that was invoked when the error occurred. */
  tool?: string;
  /** ISO 8601 UTC timestamp of the error. */
  timestamp?: string;
  /** Correlation ID for tracing this request across the system. */
  request_id?: string;
  /** Additional error context. MUST NOT contain PHI. */
  details?: Record<string, unknown>;
}

/** FHIR Read */
export interface FhirRead {
  /** FHIR read input parameters. */
  request?: Record<string, unknown>;
  /** FHIR read output. */
  response?: Record<string, unknown>;
  /** Input validation rules. */
  validation?: Record<string, unknown>;
  /** Possible error codes. */
  errors?: string[];
}

/** FHIR Search */
export interface FhirSearch {
  /** FHIR search input parameters. */
  request?: Record<string, unknown>;
  /** FHIR search output. */
  response?: Record<string, unknown>;
  /** Possible error codes. */
  errors?: string[];
}

/** Health Status */
export interface HealthStatus {
  /** MCP server identifier. */
  server_name: string;
  /** Current health status of the server. */
  status: string;
  /** Server implementation version (SemVer). */
  version: string;
  /** Server uptime in seconds since last restart. */
  uptime_seconds: number;
  /** ISO 8601 UTC timestamp of this health check. */
  checked_at: string;
  /** Conformance level this server satisfies. */
  conformance_level?: number;
  /** Status of downstream dependencies. */
  dependencies?: Record<string, unknown>[];
  /** Operational metrics for monitoring. */
  metrics?: Record<string, unknown>;
  /** Clinical site where this server is deployed. */
  site_id?: string;
}

/** Provenance Record */
export interface ProvenanceRecord {
  /** Unique identifier for this provenance record (UUID v4). */
  record_id: string;
  /** Reference to the DataSource being accessed. */
  source_id: string;
  /** Category of the data source. */
  source_type?: string;
  /** Operation performed on the data source. */
  action: string;
  /** Identifier of the actor performing the action. */
  actor_id: string;
  /** Role of the actor from the 6-actor model. */
  actor_role: string;
  /** MCP tool invocation that triggered this access event. */
  tool_call: string;
  /** SHA-256 hex digest fingerprint of the input data. */
  input_hash?: string;
  /** SHA-256 hex digest fingerprint of the output data. */
  output_hash?: string;
  /** ISO 8601 UTC timestamp of the access event. */
  timestamp: string;
  /** MCP server that owns the data source. */
  origin_server?: string;
  /** Human-readable description of the data access event. */
  description?: string;
  /** Additional properties specific to the source type. */
  metadata?: Record<string, unknown>;
}

/** Robot Capability Profile */
export interface RobotCapabilityProfile {
  /** Unique identifier for this robot instance (UUID v4). */
  robot_id: string;
  /** Robot hardware platform name. */
  platform: string;
  /** Category of robotic system. */
  robot_type: string;
  /** Unification Standard Level (USL) readiness score on a 1.0–10.0 scale, evaluating simulation, AI integration, cross-robot sharing, and multi-site collaboration. */
  usl_score: number;
  /** Safety checks that must pass before the robot is authorized for clinical procedures. */
  safety_prerequisites: Record<string, unknown>[];
  /** MCP tools this robot needs access to for its clinical workflow. */
  mcp_tools_required: string[];
  /** Simulation environments validated for this robot platform. */
  simulation_frameworks?: string[];
  /** Clinical site where this robot is deployed. */
  site_id?: string;
  /** Current firmware or software version of the robot. */
  firmware_version?: string;
  /** ISO 8601 UTC timestamp of last calibration. */
  last_calibration?: string;
}

/** Site Capability Profile */
export interface SiteCapabilityProfile {
  /** Unique identifier for this clinical site. */
  site_id: string;
  /** Human-readable name of the clinical site. */
  site_name: string;
  /** Category of clinical site. */
  site_type?: string;
  /** Regulatory jurisdiction of the site. */
  jurisdiction: Record<string, unknown>;
  /** MCP servers deployed at this site. */
  servers: any[];
  /** Highest conformance level achieved by this site (1–5). */
  conformance_level: number;
  /** Data residency and sovereignty constraints. */
  data_residency: Record<string, unknown>;
  /** Physical AI systems deployed at this site. */
  robots?: any[];
  /** IRB approval status for Physical AI trial operations. */
  irb_approval?: Record<string, unknown>;
  contact?: Record<string, unknown>;
}

/** Task Order */
export interface TaskOrder {
  /** Unique identifier for this task order (UUID v4). */
  task_id: string;
  /** Clinical trial identifier (e.g., NCT number). */
  trial_id: string;
  /** Clinical site where the task will be executed. */
  site_id: string;
  /** Type of clinical procedure. */
  procedure_type: string;
  /** Identifier of the assigned Physical AI robot. */
  robot_id: string;
  /** HMAC-SHA256 pseudonymized patient identifier. MUST NOT contain the real patient ID. */
  patient_pseudonym?: string;
  /** Current status of the task order. */
  status: string;
  /** ISO 8601 UTC timestamp of the scheduled execution. */
  scheduled_at: string;
  /** ISO 8601 UTC timestamp when execution began. */
  started_at?: string;
  /** ISO 8601 UTC timestamp when execution completed. */
  completed_at?: string;
  /** Safety checks that must pass before task execution. */
  safety_prerequisites?: Record<string, unknown>[];
  /** Minimum USL score required for the assigned robot to execute this task. */
  usl_score_minimum?: number;
  /** MCP tools invoked during this task. */
  mcp_tools_used?: string[];
  /** References to audit ledger records generated by this task. */
  audit_record_ids?: string[];
  /** Operator notes or clinical observations. */
  notes?: string;
}
