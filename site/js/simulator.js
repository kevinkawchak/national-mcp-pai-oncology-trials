/**
 * simulator.js - National deployment topology simulator
 * Deterministic simulation, not a live system
 * National MCP-PAI Oncology Trials v1.2.0
 */

(function () {
  "use strict";

  var regions = [
    { name: "East", sites: 210, latencyBase: 12 },
    { name: "Central", sites: 305, latencyBase: 18 },
    { name: "West", sites: 248, latencyBase: 15 }
  ];

  var servers = [
    "trialmcp-authz",
    "trialmcp-fhir",
    "trialmcp-dicom",
    "trialmcp-ledger",
    "trialmcp-provenance"
  ];

  var simRunning = false;
  var simInterval = null;

  function getOutput() {
    return document.getElementById("sim-output");
  }

  function log(msg) {
    var out = getOutput();
    if (!out) return;
    out.textContent += msg + "\n";
    out.scrollTop = out.scrollHeight;
  }

  function clearLog() {
    var out = getOutput();
    if (out) out.textContent = "";
  }

  function rng(seed) {
    return ((seed * 9301 + 49297) % 233280) / 233280;
  }

  function simulateDeployment() {
    clearLog();
    log("=== National MCP-PAI Deployment Simulation ===");
    log("Version: 1.2.0 | Mode: Deterministic Simulation");
    log("Note: All values are modeled approximations.\n");

    var totalSites = 0;
    var totalServers = 0;

    regions.forEach(function (r) {
      log("--- Region: " + r.name + " ---");
      log("  Sites: " + r.sites);
      log("  Servers per site: 5");
      log("  Total servers: " + (r.sites * 5));
      log("  Base latency: " + r.latencyBase + "ms (modeled)");

      servers.forEach(function (s, i) {
        var lat = r.latencyBase + (i * 2.3);
        log("    " + s + ": ~" + lat.toFixed(1) + "ms avg response");
      });

      totalSites += r.sites;
      totalServers += r.sites * 5;
      log("");
    });

    log("=== National Totals ===");
    log("  Total sites: " + totalSites);
    log("  Total MCP servers: " + totalServers);
    log("  Total tools exposed: " + (totalSites * 23));
    log("  Federated aggregation nodes: 3");
    log("");
    log("=== Simulation Complete ===");
  }

  function simulateWorkflow() {
    clearLog();
    log("=== Robot Procedure Workflow Simulation ===");
    log("Version: 1.2.0 | Site: Demo-East-001\n");

    var steps = [
      { phase: "1. Authorization", server: "trialmcp-authz", tool: "authz_evaluate", result: "ALLOW", latency: 8 },
      { phase: "1. Token Issue", server: "trialmcp-authz", tool: "authz_issue_token", result: "token_abc123", latency: 12 },
      { phase: "2. Patient Query", server: "trialmcp-fhir", tool: "fhir_read", result: "Patient/P-001 (de-identified)", latency: 45 },
      { phase: "2. Study Status", server: "trialmcp-fhir", tool: "fhir_study_status", result: "ACTIVE", latency: 22 },
      { phase: "3. Imaging Query", server: "trialmcp-dicom", tool: "dicom_query", result: "3 CT studies found", latency: 65 },
      { phase: "3. RECIST Data", server: "trialmcp-dicom", tool: "dicom_recist_measurements", result: "target_lesion: 2.4cm", latency: 38 },
      { phase: "4. Safety Gates", server: "safety/gate_service", tool: "evaluate_all_gates", result: "5/5 PASS", latency: 150 },
      { phase: "4. Approval", server: "safety/approval_checkpoint", tool: "request_approval", result: "APPROVED (clinician + system)", latency: 200 },
      { phase: "5. Procedure", server: "safety/procedure_state", tool: "transition(ACTIVE)", result: "state=ACTIVE", latency: 5 },
      { phase: "5. Audit Record", server: "trialmcp-ledger", tool: "ledger_append", result: "hash=a3f2...9d01", latency: 15 },
      { phase: "6. Provenance", server: "trialmcp-provenance", tool: "provenance_record", result: "node_id=prov-7721", latency: 18 },
      { phase: "6. Complete", server: "safety/procedure_state", tool: "transition(COMPLETING)", result: "state=COMPLETING", latency: 5 }
    ];

    var idx = 0;
    simRunning = true;

    function nextStep() {
      if (!simRunning || idx >= steps.length) {
        if (idx >= steps.length) {
          log("\n=== Workflow Complete ===");
          log("Total simulated latency: ~583ms");
          log("Audit records created: 12");
          log("Provenance nodes: 1 (with edges)");
        }
        simRunning = false;
        return;
      }

      var s = steps[idx];
      log("[" + s.phase + "]");
      log("  Server: " + s.server);
      log("  Tool:   " + s.tool);
      log("  Result: " + s.result);
      log("  Latency: ~" + s.latency + "ms (modeled)\n");

      idx++;
      simInterval = setTimeout(nextStep, 300);
    }

    nextStep();
  }

  function simulateAuditChain() {
    clearLog();
    log("=== Audit Chain Verification Simulation ===");
    log("Version: 1.2.0 | Algorithm: SHA-256\n");

    var chain = [
      { idx: 0, server: "GENESIS", tool: "CHAIN_INIT", prev: "0".repeat(16), hash: "a1b2c3d4e5f67890" },
      { idx: 1, server: "trialmcp-authz", tool: "authz_evaluate", prev: "a1b2c3d4e5f67890", hash: "f8e7d6c5b4a39201" },
      { idx: 2, server: "trialmcp-fhir", tool: "fhir_read", prev: "f8e7d6c5b4a39201", hash: "1122334455667788" },
      { idx: 3, server: "trialmcp-dicom", tool: "dicom_query", prev: "1122334455667788", hash: "aabbccddee001122" },
      { idx: 4, server: "trialmcp-ledger", tool: "ledger_append", prev: "aabbccddee001122", hash: "9988776655443322" },
      { idx: 5, server: "trialmcp-provenance", tool: "provenance_record", prev: "9988776655443322", hash: "deadbeef12345678" }
    ];

    log("Chain length: " + chain.length + " records\n");

    chain.forEach(function (r) {
      log("Record #" + r.idx + ":");
      log("  Server:    " + r.server);
      log("  Tool:      " + r.tool);
      log("  Prev hash: " + r.prev + "...");
      log("  Hash:      " + r.hash + "...");

      if (r.idx > 0 && r.prev === chain[r.idx - 1].hash) {
        log("  Verify:    PASS (prev_hash matches prior record)");
      } else if (r.idx === 0) {
        log("  Verify:    GENESIS (chain root)");
      }
      log("");
    });

    log("=== Chain Integrity: VALID ===");
    log("All " + chain.length + " records verified successfully.");
    log("\nNote: Hashes shown are demonstrative. Production");
    log("uses full 64-character SHA-256 digests.");
  }

  function stopSimulation() {
    simRunning = false;
    if (simInterval) {
      clearTimeout(simInterval);
      simInterval = null;
    }
    log("\n[Simulation stopped by user]");
  }

  /* ---------- Public API ---------- */
  window.Simulator = {
    deployment: simulateDeployment,
    workflow: simulateWorkflow,
    auditChain: simulateAuditChain,
    stop: stopSimulation
  };
})();
