/**
 * OmniGate ERP OS — Enterprise & Investor Showcase Client-Side Engine
 * 100% Self-Contained Interactive Logic (Zero External Dependencies)
 * Includes: Autonomous Saga Procure-to-Pay, Audit Anomalous Orders, SHA-256 Ledger & Reverify
 */

// ==========================================
// 1. BUSINESS SCENARIOS DATA & SIMULATOR WORKFLOWS
// ==========================================
export const WORKFLOWS = {
  invoice_reconciliation: {
    id: "audit_invoice",
    name: "Audit Anomalous Orders & Reconciliation",
    badge: "Saved $45,000",
    terminalLines: [
      { tag: "system", text: "Autonomous Agent initialized on Ledger Cluster #4 (Audit Subsystem)" },
      { tag: "thought", text: "Thought: Scanning incoming vendor batch for Invoice #INV-2026-8849 ($450,000.00)..." },
      { tag: "action", text: "Action: db.query('SELECT * FROM purchase_orders WHERE vendor_id = 481 AND status = "FULFILLED"')" },
      { tag: "observe", text: "Observation: Found PO-9921 matching line items: 400x Server Racks @ $1,012.50/unit ($405,000.00)." },
      { tag: "thought", text: "Thought: Anomaly identified: Vendor invoiced 400 units but billed $450,000 instead of $405,000 (11.1% discrepancy = $45,000 duplicate surcharge)." },
      { tag: "action", text: "Action: ledger.rebalance({ invoice: 'INV-2026-8849', credit_adjustment: 45000.00, auth_mode: 'ZERO_UI' })" },
      { tag: "observe", text: "Observation: Ledger corrected. Ephemeral executive resolution card compiled in 11.4ms." }
    ],
    ephemeralUI: `
      <div class="ephemeral-card">
        <div class="ephemeral-card-header">
          <span class="ephemeral-card-title">💰 Invoice Discrepancy Resolved</span>
          <span class="badge-legacy card-badge">Audit Anomaly Detected</span>
        </div>
        <table class="ephemeral-diff-table font-mono">
          <thead>
            <tr><th>Field</th><th>Vendor Claimed</th><th>OmniGate Verified</th><th>Variance</th></tr>
          </thead>
          <tbody>
            <tr><td>Billed Total</td><td>$450,000.00</td><td class="text-emerald">$405,000.00</td><td class="text-emerald">-$45,000.00 (Recouped)</td></tr>
            <tr><td>Unit Price</td><td>$1,125.00</td><td class="text-cyan">$1,012.50</td><td>Contract Price Matched</td></tr>
            <tr><td>Tax & Freight</td><td>$0.00 (Included)</td><td>$0.00 (Included)</td><td>Validated</td></tr>
          </tbody>
        </table>
        <div class="ephemeral-actions">
          <button class="btn btn-primary btn-sm" onclick="alert('Transaction Approved & Dispatched to Settlement Network!')">✓ Execute $405,000 Settlement</button>
          <button class="btn btn-outline btn-sm" onclick="alert('Audit Memo Exported with SHA-256 Seal.')">📄 Export Audit Memo</button>
        </div>
      </div>
    `
  },
  inventory_stockout: {
    id: "saga_procure",
    name: "Run Saga Procure-to-Pay Logistics",
    badge: "Prevented $1.2M Stockout",
    terminalLines: [
      { tag: "system", text: "Logistics Agent active across 14 Global Fulfillment Nodes (Saga Orchestration)" },
      { tag: "thought", text: "Thought: Telemetry alert: Port of Rotterdam congestion delay (+14 days) threatens EU-Central Q3 fulfillment." },
      { tag: "action", text: "Action: supply_chain.simulate_reroute({ units: 5000, target: 'Frankfurt_HUB_01', alt_nodes: ['Lyon_FR', 'Antwerp_BE'] })" },
      { tag: "observe", text: "Observation: Route evaluated: 3,200 units redirected via Antwerp bonded rail, 1,800 units via Lyon air corridor." },
      { tag: "thought", text: "Thought: Inventory buffer replenished from 2.1 days to 18.5 days. Zero customer stockouts predicted." },
      { tag: "action", text: "Action: carrier_api.dispatch_manifests({ cost_variance: '+$4,200', saved_revenue: '$1,200,000' })" },
      { tag: "observe", text: "Observation: Manifests confirmed. Automated Purchase Order & Carrier tracking dispatched." }
    ],
    ephemeralUI: `
      <div class="ephemeral-card">
        <div class="ephemeral-card-header">
          <span class="ephemeral-card-title">📦 Autonomous Shipment Rerouting (Saga Workflow)</span>
          <span class="badge-omnigate card-badge">100% Buffer Secured</span>
        </div>
        <table class="ephemeral-diff-table font-mono">
          <thead>
            <tr><th>Corridor</th><th>Original Delay</th><th>Steered ETA</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>Rotterdam ➔ Frankfurt</td><td class="text-rose">+14 Days (Critical)</td><td>Bypassed</td><td>Rerouted</td></tr>
            <tr><td>Antwerp Rail (3,200 Units)</td><td>-</td><td class="text-emerald">Aug 26, 08:00 CEST</td><td>In Transit</td></tr>
            <tr><td>Lyon Air (1,800 Units)</td><td>-</td><td class="text-cyan">Aug 25, 14:30 CEST</td><td>Cleared</td></tr>
          </tbody>
        </table>
        <div class="ephemeral-actions">
          <button class="btn btn-primary btn-sm" onclick="alert('Carrier Webhooks Synchronized across SAP/NetSuite Connectors!')">⚡ Sync Logistics Webhooks</button>
        </div>
      </div>
    `
  },
  executive_report: {
    id: "executive_report",
    name: "Dynamic Executive P&L Synthesis",
    badge: "Synthesized in 8.2ms",
    terminalLines: [
      { tag: "system", text: "Executive Intelligence Kernel processing CEO natural language prompt" },
      { tag: "thought", text: "Thought: User query: 'Synthesize Q3 EBITDA impact under 5% EUR/USD currency fluctuation.'" },
      { tag: "action", text: "Action: analytics.vector_query('EBITDA sensitivity FX hedges 2026', top_k=50)" },
      { tag: "observe", text: "Observation: Extracted $142M EU sales volume, 65% hedged at 1.0850 strike." },
      { tag: "thought", text: "Thought: Computing cross-elasticity and unhedged balance sensitivity model..." },
      { tag: "action", text: "Action: ui_compiler.generate_chart({ type: 'SENSITIVITY_CURVE', ebitda_delta: '-$1.45M to +$1.82M' })" },
      { tag: "observe", text: "Observation: Dynamic executive sensitivity chart rendered into client sandbox." }
    ],
    ephemeralUI: `
      <div class="ephemeral-card">
        <div class="ephemeral-card-header">
          <span class="ephemeral-card-title">📊 Q3 EBITDA Sensitivity Matrix (EUR/USD &plusmn;5%)</span>
          <span class="badge-omnigate card-badge">Real-Time Synthesis</span>
        </div>
        <table class="ephemeral-diff-table font-mono">
          <thead>
            <tr><th>FX Shift</th><th>Hedged Volume</th><th>Unhedged Risk</th><th>Projected EBITDA</th></tr>
          </thead>
          <tbody>
            <tr><td>EUR/USD +5% (1.1390)</td><td>$92.3M (Protected)</td><td>$49.7M (Gain)</td><td class="text-emerald">$44.12M (+$1.82M)</td></tr>
            <tr><td>Baseline (1.0850)</td><td>$92.3M (Protected)</td><td>$49.7M (Par)</td><td>$42.30M ($0.00)</td></tr>
            <tr><td>EUR/USD -5% (1.0307)</td><td>$92.3M (Protected)</td><td>$49.7M (Drag)</td><td class="text-amber">$40.85M (-$1.45M)</td></tr>
          </tbody>
        </table>
        <div class="ephemeral-actions">
          <button class="btn btn-primary btn-sm" onclick="alert('Executive Memo Dispatched to Board Portal!')">📤 Send to Board Portal</button>
        </div>
      </div>
    `
  },
  security_quarantine: {
    id: "security_quarantine",
    name: "Zero-Trust Isolation",
    badge: "Threat Neutralized in 4ms",
    terminalLines: [
      { tag: "system", text: "Security Sentinel monitoring API Gateway and Auth Tokens" },
      { tag: "thought", text: "Thought: Security alert: Token #usr_8812 attempted admin escalation on /api/payroll/salaries from unrecognized IP (185.220.101.5)." },
      { tag: "action", text: "Action: auth_guard.isolate_session({ token: 'usr_8812', reason: 'UNAUTHORIZED_PRIVILEGE_ESCALATION' })" },
      { tag: "observe", text: "Observation: Session quarantined. All pending write operations aborted immediately." },
      { tag: "thought", text: "Thought: Generating immutable audit block with attacker fingerprint and cryptographic timestamp..." },
      { tag: "action", text: "Action: crypto_ledger.seal_incident_block({ actor: 'usr_8812', risk_level: 'CRITICAL', hash_algo: 'SHA-256' })" },
      { tag: "observe", text: "Observation: Block #14802 sealed. Incident report generated for SOC2 compliance." }
    ],
    ephemeralUI: `
      <div class="ephemeral-card">
        <div class="ephemeral-card-header">
          <span class="ephemeral-card-title">🛡️ Security Incident Quarantined</span>
          <span class="badge-legacy card-badge">Zero Data Leaked</span>
        </div>
        <table class="ephemeral-diff-table font-mono">
          <thead>
            <tr><th>Parameter</th><th>Detail</th><th>Action Taken</th></tr>
          </thead>
          <tbody>
            <tr><td>Target Endpoint</td><td>/api/payroll/salaries</td><td>Write Blocked</td></tr>
            <tr><td>Actor Token</td><td>usr_8812 (Suspicious)</td><td>Revoked &amp; Isolated</td></tr>
            <tr><td>Audit Proof</td><td class="text-cyan">SHA-256: 8f92a1c...e41</td><td>Sealed in Ledger</td></tr>
          </tbody>
        </table>
        <div class="ephemeral-actions">
          <button class="btn btn-primary btn-sm" onclick="alert('Incident Logged to SIEM (Splunk/Datadog)!')">🛡️ Sync with Enterprise SIEM</button>
        </div>
      </div>
    `
  }
};

// ==========================================
// 2. SIMULATOR RUNNER ENGINE
// ==========================================
let currentScenario = "invoice_reconciliation";
let isStreaming = false;

export function streamScenario(scenarioKey) {
  if (!scenarioKey || !WORKFLOWS[scenarioKey]) return;
  if (isStreaming) return;
  isStreaming = true;
  currentScenario = scenarioKey;

  const scenario = WORKFLOWS[scenarioKey];
  const term = document.getElementById("terminal-container");
  const placeholder = document.getElementById("ephemeral-placeholder");
  const uiContainer = document.getElementById("ephemeral-ui-container");

  if (!term || !placeholder || !uiContainer) {
    isStreaming = false;
    return;
  }

  term.innerHTML = "";
  placeholder.classList.remove("hidden");
  uiContainer.classList.add("hidden");
  uiContainer.innerHTML = "";

  let lineIdx = 0;
  function printNextLine() {
    if (lineIdx < scenario.terminalLines.length) {
      const item = scenario.terminalLines[lineIdx];
      const div = document.createElement("div");
      div.className = "terminal-line";
      div.innerHTML = `<span class="term-tag tag-${item.tag}">[${item.tag.toUpperCase()}]</span> ${item.text}`;
      term.appendChild(div);
      term.scrollTop = term.scrollHeight;
      lineIdx++;
      setTimeout(printNextLine, 280);
    } else {
      placeholder.classList.add("hidden");
      uiContainer.classList.remove("hidden");
      uiContainer.innerHTML = scenario.ephemeralUI;
      isStreaming = false;
    }
  }

  printNextLine();
}

// ==========================================
// 3. SAG TRAJECTORY STEERING VISUALIZER (THE MOAT)
// ==========================================
const TRAJECTORY_STEPS = [
  {
    step: 1,
    name: "Step 1: Initiation",
    risk: "8%",
    riskClass: "risk-low",
    thought: "Thought: Analyzing system state and mining semantic file entities from knowledge graph...",
    action: "Action: semantic_agent_graph.query(context='invoice_bound_widget')",
    entities: ["django/forms/boundfield.py", "pytest", "sqlite://ledger"]
  },
  {
    step: 2,
    name: "Step 2: t_safe Risk Checkpoint",
    risk: "42%",
    riskClass: "risk-med",
    thought: "Thought: Risk radar: Historical entity failure frequency indicates 42% risk of recursion trap in BoundWidget class.",
    action: "Action: sag_flight_controller.evaluate_branch_risk(checkpoint='t_safe')",
    entities: ["BoundWidget.render()", "RecursionError", "P(fail|E)=0.42"]
  },
  {
    step: 3,
    name: "Step 3: SAG Trajectory Intercept",
    risk: "15%",
    riskClass: "risk-low",
    thought: "Thought: SAG Intercept: Unguided LLM drifted into infinite recursion loop (83% failure risk). Steered agent branches onto safe green path.",
    action: "Action: sag.steer_branch(target='emerald_recovery_path', patch='clean_bound_field')",
    entities: ["safe_bound_widget.py", "memory_checkpoint", "branch_divergence"]
  },
  {
    step: 4,
    name: "Step 4: Targeted Execution",
    risk: "6%",
    riskClass: "risk-low",
    thought: "Thought: Executing isolated unit test suite across 15,318 Princeton test cases with zero regressions.",
    action: "Action: pytest tests/forms_tests/field_tests/test_boundfield.py",
    entities: ["test_boundfield.py", "PASS_100%", "assert_clean"]
  },
  {
    step: 5,
    name: "Step 5: Verified Task Completion",
    risk: "2%",
    riskClass: "risk-low",
    thought: "Thought: Task 100% verified. Zero human intervention required. Trajectory sealed into SAG memory graph.",
    action: "Action: agent.complete_task({ status: 'SUCCESS_100%', execution_time_ms: 11.8 })",
    entities: ["Task_Resolved", "Ledger_Sealed", "99.4%_Reliability"]
  }
];

let activeStep = 1;
let isPlaying = false;
let playInterval = null;

export function renderTrajectoryStep(stepNum) {
  activeStep = stepNum;
  const data = TRAJECTORY_STEPS[stepNum - 1];

  const stepInd = document.getElementById("step-indicator");
  const scrubber = document.getElementById("trajectory-scrubber");
  const badge = document.getElementById("active-node-badge");
  const riskVal = document.getElementById("risk-score-value");
  const bar = document.getElementById("risk-bar-fill");

  if (stepInd) stepInd.innerText = `${data.step} / 5`;
  if (scrubber) scrubber.value = data.step;
  if (badge) badge.innerText = data.name;
  if (riskVal) riskVal.innerText = data.risk;
  
  if (bar) {
    bar.style.width = data.risk;
    bar.className = `risk-bar-inner ${data.riskClass}`;
  }

  const thoughtEl = document.getElementById("telemetry-thought");
  const actionEl = document.getElementById("telemetry-action");
  if (thoughtEl) thoughtEl.innerText = data.thought;
  if (actionEl) actionEl.innerText = data.action;

  const entityContainer = document.getElementById("telemetry-entities");
  if (entityContainer) {
    entityContainer.innerHTML = "";
    data.entities.forEach(ent => {
      const span = document.createElement("span");
      span.className = "entity-badge entity-file";
      span.innerText = ent;
      entityContainer.appendChild(span);
    });
  }
}

export function togglePlayback() {
  const icon = document.getElementById("play-icon");

  if (isPlaying) {
    clearInterval(playInterval);
    isPlaying = false;
    if (icon) icon.innerText = "▶";
  } else {
    isPlaying = true;
    if (icon) icon.innerText = "⏸";
    const speedEl = document.getElementById("playback-speed");
    const speed = speedEl ? parseFloat(speedEl.value) || 1.0 : 1.0;
    const intervalMs = 2000 / speed;

    playInterval = setInterval(() => {
      let nextStep = activeStep + 1;
      if (nextStep > 5) nextStep = 1;
      renderTrajectoryStep(nextStep);
    }, intervalMs);
  }
}

// ==========================================
// 4. INTERACTIVE ENTERPRISE ROI CALCULATOR
// ==========================================
export function updateROI() {
  const hcEl = document.getElementById("slider-headcount");
  const revEl = document.getElementById("slider-revenue");
  const opsEl = document.getElementById("slider-ops");

  const headcount = hcEl ? parseInt(hcEl.value) || 2500 : 2500;
  const revenue = revEl ? parseInt(revEl.value) || 250 : 250;
  const opsStaff = opsEl ? parseInt(opsEl.value) || 120 : 120;

  const dispHc = document.getElementById("display-headcount");
  const dispRev = document.getElementById("display-revenue");
  const dispOps = document.getElementById("display-ops");

  if (dispHc) dispHc.innerText = `${headcount.toLocaleString()} employees`;
  if (dispRev) dispRev.innerText = `$${revenue}M`;
  if (dispOps) dispOps.innerText = `${opsStaff} staff`;

  // Financial Calculations
  const directLaborSavings = opsStaff * 42000;
  const errorSavings = revenue * 6500;
  const consultingSavings = 450000;
  const totalSavings = directLaborSavings + errorSavings + consultingSavings;

  const hoursReclaimed = opsStaff * 240;
  const paybackDays = Math.max(18, Math.round(45 - (opsStaff / 30)));
  const netROI = Math.round(320 + (revenue * 0.45));

  const calcSav = document.getElementById("calc-savings");
  const calcHrs = document.getElementById("calc-hours");
  const calcPay = document.getElementById("calc-payback");
  const calcRoi = document.getElementById("calc-roi");

  if (calcSav) calcSav.innerText = `$${totalSavings.toLocaleString()}`;
  if (calcHrs) calcHrs.innerText = `${hoursReclaimed.toLocaleString()} hrs`;
  if (calcPay) calcPay.innerText = `< ${paybackDays} Days`;
  if (calcRoi) calcRoi.innerText = `${netROI}%`;
}

// ==========================================
// 5. CRYPTOGRAPHIC LEDGER & TAMPER DEMO
// ==========================================
export const INITIAL_LEDGER_CHAIN = [
  {
    index: 0,
    timestamp: "2026-08-24T00:01:14Z",
    event: "Genesis Block (Cluster Init)",
    prevHash: "0000000000000000000000000000000000000000000000000000000000000000",
    hash: "a9f8b4c2098e1f574d320984ba10284759281a02938475620192847561029384",
    is_verified: true,
    tampered: false
  },
  {
    index: 1,
    timestamp: "2026-08-24T00:04:22Z",
    event: "Invoice Anomaly Recoup ($45,000)",
    prevHash: "a9f8b4c2098e1f574d320984ba10284759281a02938475620192847561029384",
    hash: "3b8c9d01247a56ef981023475891a02948576102938475610293847561029384",
    is_verified: true,
    tampered: false
  },
  {
    index: 2,
    timestamp: "2026-08-24T00:06:50Z",
    event: "Supply Chain Manifest Auto-Route (Antwerp)",
    prevHash: "3b8c9d01247a56ef981023475891a02948576102938475610293847561029384",
    hash: "f4e5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
    is_verified: true,
    tampered: false
  },
  {
    index: 3,
    timestamp: "2026-08-24T00:09:12Z",
    event: "Executive FX Sensitivity Synthesis Sealed",
    prevHash: "f4e5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
    hash: "c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2",
    is_verified: true,
    tampered: false
  }
];

export let ledgerBlocks = JSON.parse(JSON.stringify(INITIAL_LEDGER_CHAIN));

export async function calculateSHA256(text) {
  if (window.crypto && window.crypto.subtle) {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await window.crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
  }
  // Simple fallback
  return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
}

export function validateChain(blocks) {
  for (let i = 1; i < blocks.length; i++) {
    if (blocks[i].prevHash !== blocks[i - 1].hash || blocks[i].tampered) {
      return { verified: false, brokenIndex: i };
    }
  }
  return { verified: true, brokenIndex: -1 };
}

export function renderLedger() {
  const container = document.getElementById("ledger-container");
  if (!container) return;
  container.innerHTML = "";

  ledgerBlocks.forEach((block) => {
    const card = document.createElement("div");
    card.className = `glass-card block-card ${block.tampered ? "tampered" : ""}`;
    card.innerHTML = `
      <div class="block-header">
        <span>Block #${block.index}</span>
        <span class="${block.tampered ? "text-rose" : "text-emerald"}">${block.tampered ? "⚠️ INVALID" : "✓ SEALED"}</span>
      </div>
      <div class="block-field">
        <span class="block-label">Event Data</span>
        <span class="block-val">${block.event}</span>
      </div>
      <div class="block-field">
        <span class="block-label">Previous Hash</span>
        <span class="block-val">${block.prevHash.substring(0, 16)}...</span>
      </div>
      <div class="block-field">
        <span class="block-label">Block Hash (SHA-256)</span>
        <span class="block-val ${block.tampered ? "text-rose" : "text-cyan"}">${block.hash.substring(0, 16)}...</span>
      </div>
    `;
    container.appendChild(card);
  });
}

export function tamperBlock() {
  ledgerBlocks[2].event = "TAMPERED: Altered Supplier IBAN to Offshore Account";
  ledgerBlocks[2].hash = "9999999999999999999999999999999999999999999999999999999999999999";
  ledgerBlocks[2].tampered = true;
  ledgerBlocks[2].is_verified = false;
  ledgerBlocks[3].tampered = true;
  ledgerBlocks[3].is_verified = false;

  const badge = document.getElementById("chain-status-badge");
  if (badge) {
    badge.className = "chain-badge badge-tampered";
    badge.innerHTML = '<span class="status-dot pulse-tampered"></span> INTEGRITY_VIOLATION: Chain Broken at Block #2 (Failed verification)';
  }

  renderLedger();
}

export function reverifyChain() {
  ledgerBlocks[2].event = "Supply Chain Manifest Auto-Route (Antwerp)";
  ledgerBlocks[2].hash = "f4e5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5";
  ledgerBlocks[2].tampered = false;
  ledgerBlocks[2].is_verified = true;
  ledgerBlocks[3].tampered = false;
  ledgerBlocks[3].is_verified = true;

  const badge = document.getElementById("chain-status-badge");
  if (badge) {
    badge.className = "chain-badge badge-valid";
    badge.innerHTML = '<span class="status-dot green"></span> Chain Validated &amp; Verified (SHA-256)';
  }

  renderLedger();
}

export function resetLedger() {
  ledgerBlocks = JSON.parse(JSON.stringify(INITIAL_LEDGER_CHAIN));
  const badge = document.getElementById("chain-status-badge");
  if (badge) {
    badge.className = "chain-badge badge-valid";
    badge.innerHTML = '<span class="status-dot green"></span> Chain Validated &amp; Verified (SHA-256)';
  }
  renderLedger();
}

// ==========================================
// 6. INITIALIZATION & EVENT BINDINGS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  // Scenario Buttons
  const scenarioBtns = document.querySelectorAll(".scenario-btn");
  scenarioBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      scenarioBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const scKey = btn.getAttribute("data-scenario");
      streamScenario(scKey);
    });
  });

  // Initial Scenario Run
  streamScenario("invoice_reconciliation");

  // Trajectory Controls
  const btnPlay = document.getElementById("btn-play-pause");
  const btnPrev = document.getElementById("btn-step-prev");
  const btnNext = document.getElementById("btn-step-next");
  const btnSafe = document.getElementById("btn-jump-safe");
  const btnReset = document.getElementById("btn-reset");
  const scrubber = document.getElementById("trajectory-scrubber");

  if (btnPlay) btnPlay.addEventListener("click", togglePlayback);
  if (btnPrev) btnPrev.addEventListener("click", () => { if (activeStep > 1) renderTrajectoryStep(activeStep - 1); });
  if (btnNext) btnNext.addEventListener("click", () => { if (activeStep < 5) renderTrajectoryStep(activeStep + 1); });
  if (btnSafe) btnSafe.addEventListener("click", () => renderTrajectoryStep(2));
  if (btnReset) btnReset.addEventListener("click", () => renderTrajectoryStep(1));
  if (scrubber) scrubber.addEventListener("input", (e) => renderTrajectoryStep(parseInt(e.target.value)));

  // ROI Calculator Listeners
  const slHc = document.getElementById("slider-headcount");
  const slRev = document.getElementById("slider-revenue");
  const slOps = document.getElementById("slider-ops");

  if (slHc) slHc.addEventListener("input", updateROI);
  if (slRev) slRev.addEventListener("input", updateROI);
  if (slOps) slOps.addEventListener("input", updateROI);
  updateROI();

  // Ledger Buttons
  const btnTamper = document.getElementById("btn-tamper-ledger") || document.getElementById("btn-tamper");
  const btnReverify = document.getElementById("btn-reverify") || document.getElementById("btn-repair");
  const btnResetLedger = document.getElementById("btn-reset-ledger");

  if (btnTamper) btnTamper.addEventListener("click", tamperBlock);
  if (btnReverify) btnReverify.addEventListener("click", reverifyChain);
  if (btnResetLedger) btnResetLedger.addEventListener("click", resetLedger);
  renderLedger();

  // Modal Handlers
  const modal = document.getElementById("briefing-modal");
  const openBtns = [
    document.getElementById("btn-open-briefing"),
    document.getElementById("btn-open-briefing-cta"),
    document.getElementById("btn-calc-briefing")
  ];
  const closeBtn = document.getElementById("modal-close-btn");
  const form = document.getElementById("briefing-form");
  const successBox = document.getElementById("briefing-success");

  openBtns.forEach(b => {
    if (b) b.addEventListener("click", () => modal && modal.classList.remove("hidden"));
  });

  if (closeBtn && modal) {
    closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.classList.add("hidden");
    });
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      form.classList.add("hidden");
      if (successBox) successBox.classList.remove("hidden");
      setTimeout(() => {
        if (modal) modal.classList.add("hidden");
        form.classList.remove("hidden");
        if (successBox) successBox.classList.add("hidden");
        form.reset();
      }, 3500);
    });
  }
});
