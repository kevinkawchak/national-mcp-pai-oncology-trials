/**
 * diagrams.js - Interactive diagram rendering engine
 * Converts the 7 process diagrams into interactive web visuals
 * National MCP-PAI Oncology Trials v1.2.0
 */

(function () {
  "use strict";

  /* ---------- State machine animation ---------- */
  function animateStateMachine(containerId, states, intervalMs) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var nodes = container.querySelectorAll(".state-node");
    if (nodes.length === 0) return;
    var idx = 0;

    function step() {
      nodes.forEach(function (n) { n.classList.remove("active-state"); });
      if (idx < nodes.length) {
        nodes[idx].classList.add("active-state");
      }
      idx = (idx + 1) % (nodes.length + 1);
    }

    step();
    setInterval(step, intervalMs || 2000);
  }

  /* ---------- Hash chain demo ---------- */
  function renderHashChain(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var genesisHash = "0000000000000000";
    var blocks = [
      { idx: 0, label: "Genesis", data: "CHAIN_INIT" },
      { idx: 1, label: "AuthZ Eval", data: "authz_evaluate(robot_agent, fhir_read)" },
      { idx: 2, label: "FHIR Read", data: "fhir_read(Patient, P-001)" },
      { idx: 3, label: "DICOM Query", data: "dicom_query(P-001, CT)" },
      { idx: 4, label: "Ledger Rec", data: "ledger_append(trialmcp-dicom, dicom_query)" }
    ];

    var html = '<div class="hash-chain">';
    blocks.forEach(function (b, i) {
      var hash = simpleHash(b.data + (i === 0 ? genesisHash : blocks[i-1].data));
      html += '<div class="hash-block">';
      html += '<div class="block-index">Block ' + b.idx + '</div>';
      html += '<div style="font-size:0.75rem;font-weight:600;margin-bottom:0.2rem">' + b.label + '</div>';
      html += '<div class="block-hash">' + hash + '</div>';
      html += '</div>';
      if (i < blocks.length - 1) {
        html += '<div class="hash-link">&rarr;</div>';
      }
    });
    html += '</div>';
    html += '<p class="text-muted" style="font-size:0.78rem;margin-top:0.5rem">Demonstrative hash chain using simplified hashing. Production uses SHA-256 with canonical JSON serialization.</p>';
    container.innerHTML = html;
  }

  function simpleHash(str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      var ch = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + ch;
      hash |= 0;
    }
    var hex = Math.abs(hash).toString(16).padStart(8, "0");
    return hex + hex.split("").reverse().join("");
  }

  /* ---------- Gate evaluation demo ---------- */
  function animateGates(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var gates = container.querySelectorAll(".gate-item");
    var statuses = container.querySelectorAll(".gate-status");
    var idx = 0;

    function evaluateNext() {
      if (idx >= gates.length) {
        setTimeout(function () {
          statuses.forEach(function (s) {
            s.textContent = "PENDING";
            s.className = "gate-status pending";
          });
          idx = 0;
          setTimeout(evaluateNext, 1000);
        }, 3000);
        return;
      }

      var status = statuses[idx];
      status.textContent = "EVALUATING...";
      status.className = "gate-status pending";

      setTimeout(function () {
        status.textContent = "PASS";
        status.className = "gate-status pass";
        idx++;
        setTimeout(evaluateNext, 500);
      }, 800);
    }

    setTimeout(evaluateNext, 1500);
  }

  /* ---------- Public init ---------- */
  window.DiagramEngine = {
    animateStateMachine: animateStateMachine,
    renderHashChain: renderHashChain,
    animateGates: animateGates
  };

  /* Auto-init on DOMContentLoaded */
  document.addEventListener("DOMContentLoaded", function () {
    animateStateMachine("robot-lifecycle-states", null, 2200);
    animateStateMachine("estop-lifecycle-states", null, 1800);
    renderHashChain("hash-chain-demo");
    animateGates("gate-evaluation-demo");
  });
})();
