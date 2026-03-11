/**
 * conformance.js - Conformance level explorer
 * Interactive 5-level hierarchy
 * National MCP-PAI Oncology Trials v1.2.0
 */

(function () {
  "use strict";

  var levels = [
    {
      level: 1,
      name: "Core",
      servers: ["trialmcp-authz", "trialmcp-ledger"],
      tools: 10,
      useCase: "Basic authorization and tamper-evident audit logging",
      profiles: ["core.md"],
      description: "Every conforming implementation must satisfy Level 1. It provides deny-by-default RBAC through the authorization server and hash-chained audit trails through the ledger server. Together, these 10 tools establish the security and compliance foundation that all higher levels build upon.",
      requirements: [
        "Deny-by-default RBAC policy evaluation",
        "SHA-256 token lifecycle management",
        "Hash-chained audit record creation",
        "Chain integrity verification",
        "Audit record query and export"
      ]
    },
    {
      level: 2,
      name: "Clinical Read",
      servers: ["trialmcp-authz", "trialmcp-ledger", "trialmcp-fhir"],
      tools: 14,
      useCase: "FHIR R4 clinical data access with mandatory HIPAA Safe Harbor de-identification",
      profiles: ["core.md", "clinical-read.md"],
      description: "Level 2 adds the FHIR clinical data server, enabling read access to patient records, study status queries, and patient lookups. All clinical data is automatically de-identified using HIPAA Safe Harbor rules before leaving the server boundary.",
      requirements: [
        "All Level 1 requirements",
        "FHIR R4 resource read and search",
        "HIPAA Safe Harbor de-identification pipeline",
        "HMAC-SHA256 pseudonymization",
        "Patient lookup by pseudonymized identifier"
      ]
    },
    {
      level: 3,
      name: "Imaging",
      servers: ["trialmcp-authz", "trialmcp-ledger", "trialmcp-fhir", "trialmcp-dicom"],
      tools: 18,
      useCase: "DICOM imaging queries and RECIST 1.1 tumor measurements for treatment response evaluation",
      profiles: ["core.md", "clinical-read.md", "imaging.md"],
      description: "Level 3 adds the DICOM imaging server, providing access to imaging studies, secure image pointers (without pixel data transfer), study-level metadata, and RECIST 1.1 tumor measurement data critical to oncology trial response assessment.",
      requirements: [
        "All Level 2 requirements",
        "DICOM study query by patient or accession",
        "Secure image pointer retrieval",
        "Study-level metadata access",
        "RECIST 1.1 measurement queries"
      ]
    },
    {
      level: 4,
      name: "Federated Site",
      servers: ["trialmcp-authz", "trialmcp-ledger", "trialmcp-fhir", "trialmcp-dicom", "trialmcp-provenance"],
      tools: 23,
      useCase: "Multi-site data lineage tracking and federated learning participation",
      profiles: ["core.md", "clinical-read.md", "imaging.md", "federated-site.md"],
      description: "Level 4 adds the provenance server, enabling DAG-based data lineage tracking with forward and backward queries. Sites at this level can participate in federated learning rounds and cross-site provenance verification.",
      requirements: [
        "All Level 3 requirements",
        "DAG-based provenance recording",
        "Forward and backward lineage queries",
        "SHA-256 data fingerprinting",
        "Cross-site provenance chain verification"
      ]
    },
    {
      level: 5,
      name: "Robot Procedure",
      servers: ["trialmcp-authz", "trialmcp-ledger", "trialmcp-fhir", "trialmcp-dicom", "trialmcp-provenance"],
      tools: 23,
      useCase: "Full autonomous clinical workflow with safety modules and procedure state machines",
      profiles: ["core.md", "clinical-read.md", "imaging.md", "federated-site.md", "robot-procedure.md"],
      description: "Level 5 requires all five servers plus the complete safety module suite: emergency stop controller, procedure state machine, robot registry, task validator, gate service, approval checkpoint, and site verifier. This level enables autonomous robotic procedures under full safety governance.",
      requirements: [
        "All Level 4 requirements",
        "Emergency stop controller integration",
        "Procedure state machine enforcement",
        "5-gate safety evaluation pipeline",
        "Multi-party approval checkpoints",
        "Robot capability registration and validation"
      ]
    }
  ];

  function renderConformanceLevels(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var html = "";
    levels.forEach(function (l) {
      html += '<div class="conformance-level" data-level="' + l.level + '">';
      html += '<div class="level-num">' + l.level + '</div>';
      html += '<div class="level-body">';
      html += '<h4>Level ' + l.level + ': ' + l.name + ' <span style="font-size:0.8rem;color:#5d6d7e;font-weight:400">(' + l.tools + ' tools)</span></h4>';
      html += '<p>' + l.useCase + '</p>';
      html += '<div class="level-detail">';
      html += '<p style="margin-bottom:0.4rem"><strong>Required servers:</strong> ' + l.servers.map(function (s) { return '<code>' + s + '</code>'; }).join(", ") + '</p>';
      html += '<p style="margin-bottom:0.4rem">' + l.description + '</p>';
      html += '<p style="margin-bottom:0.3rem"><strong>Key requirements:</strong></p>';
      html += '<ul class="content-list">';
      l.requirements.forEach(function (r) {
        html += '<li>' + r + '</li>';
      });
      html += '</ul>';
      html += '<p class="text-muted" style="font-size:0.78rem">Profiles: ' + l.profiles.map(function (p) { return '<code>profiles/' + p + '</code>'; }).join(", ") + '</p>';
      html += '</div>';
      html += '</div>';
      html += '</div>';
    });

    container.innerHTML = html;
  }

  window.ConformanceExplorer = {
    render: renderConformanceLevels,
    levels: levels
  };

  document.addEventListener("DOMContentLoaded", function () {
    renderConformanceLevels("conformance-levels-container");
  });
})();
