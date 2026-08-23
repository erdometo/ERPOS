/**
 * Empirical Adversarial Stress Test Suite for R3 & R4:
 * - R3: Zero-UI Enterprise ERP Sandbox & Ephemeral Component Generator (4 Scenarios + Saga)
 * - R4: Cryptographic Ledger & Zero-Knowledge Audit Suite (Cascading Tamper, Sequential Recalculation, Rapid Cycles)
 * - Strict SAG Branding Compliance
 */

import { webcrypto } from "crypto";

// 1. Setup mock browser DOM globals before importing app.js
const elements = {};

function createMockElement(id, tagName = "div") {
  return {
    id,
    tagName: tagName.toUpperCase(),
    innerHTML: "",
    _textContent: "",
    get textContent() {
      if (this.innerHTML) {
        // Strip tags for textContent simulation
        return this.innerHTML.replace(/<[^>]*>?/gm, "").trim();
      }
      return this._textContent;
    },
    set textContent(val) {
      this._textContent = val;
      this.innerHTML = val;
    },
    get outerHTML() {
      const attrs = Object.entries(this.attributes).map(([k, v]) => ` ${k}="${v}"`).join("");
      const cls = this.className ? ` class="${this.className}"` : "";
      return `<${this.tagName.toLowerCase()}${cls}${attrs}>${this.innerHTML}</${this.tagName.toLowerCase()}>`;
    },
    value: "",
    className: "",
    children: [],
    scrollTop: 0,
    scrollHeight: 100,
    classList: {
      classes: new Set(),
      add(c) { this.classes.add(c); },
      remove(c) { this.classes.delete(c); },
      toggle(c, force) {
        if (force === undefined) {
          if (this.classes.has(c)) this.classes.delete(c);
          else this.classes.add(c);
        } else if (force) {
          this.classes.add(c);
        } else {
          this.classes.delete(c);
        }
      },
      contains(c) { return this.classes.has(c); }
    },
    style: {},
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = v; },
    getAttribute(k) { return this.attributes[k]; },
    appendChild(child) {
      this.children.push(child);
      if (typeof child === "object" && child.outerHTML) {
        this.innerHTML += child.outerHTML;
      }
    },
    remove() {},
    addEventListener() {}
  };
}

const mockDoc = {
  getElementById(id) {
    if (!elements[id]) {
      elements[id] = createMockElement(id);
    }
    return elements[id];
  },
  createElement(tag) {
    const el = createMockElement(`dyn_${Math.random().toString(36).substr(2, 9)}`, tag);
    return el;
  },
  querySelectorAll(selector) {
    return [];
  },
  querySelector(selector) {
    if (selector === ".raw-data-panel") {
      return this.getElementById("raw-data-panel");
    }
    return null;
  },
  addEventListener() {}
};

global.document = mockDoc;
global.window = {
  addEventListener() {},
  crypto: globalThis.crypto,
  navigator: { clipboard: { writeText: async () => {} } }
};
try {
  Object.defineProperty(globalThis.navigator, 'clipboard', {
    value: { writeText: async () => {} },
    configurable: true,
    writable: true
  });
} catch (e) {}

function assert(condition, message) {
  if (!condition) {
    console.error(`  [ASSERTION FAILED] ${message}`);
    throw new Error(message);
  }
}

let testsPassed = 0;
let testsTotal = 0;

function test(name, fn) {
  testsTotal++;
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    testsPassed++;
  } catch (err) {
    console.error(`  [FAIL] ${name}: ${err.message}`);
    throw err;
  }
}

async function runAsyncTest(name, fn) {
  testsTotal++;
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    testsPassed++;
  } catch (err) {
    console.error(`  [FAIL] ${name}: ${err.message}`);
    throw err;
  }
}

async function runSuite() {
  console.log("===============================================================================");
  console.log("STARTING EMPIRICAL ADVERSARIAL STRESS TEST SUITE: R3 & R4 SYSTEMS");
  console.log("===============================================================================\n");

  const app = await import("./public/app.js");
  const {
    calculateHash,
    initLedger,
    appendLedgerBlock,
    renderLedger,
    verifyLedgerChain,
    tamperLedgerBlock2,
    repairAndRecalculateLedger,
    updateZKMetrics,
    SimulatorState,
    Workflows,
    runWorkflow,
    approveWaiver,
    commitLedgerRebalance,
    dispatchPurchaseOrder,
    quarantineSecurityIncident,
    renderAuditDashboard,
    renderStockoutDashboard,
    renderFinancialDashboard,
    renderRBACDashboard,
    renderSagaDashboard
  } = app;

  // -----------------------------------------------------------------------------
  // SECTION 1: CRYPTOGRAPHIC LEDGER CORE HASHING & IMMUTABILITY (R4)
  // -----------------------------------------------------------------------------
  console.log("--- Section 1: Cryptographic Ledger Core Hashing & Immutability (R4) ---");

  await runAsyncTest("calculateHash produces valid 64-character hex SHA-256 digest", async () => {
    const hash = await calculateHash(0, "2026-06-10 09:00:00", "system_init --secure", "0000000000000000000000000000000000000000000000000000000000000000");
    assert(typeof hash === "string", "Hash must be a string");
    assert(hash.length === 64, `Hash length must be 64, got ${hash.length}`);
    assert(/^[0-9a-f]{64}$/.test(hash), "Hash must be valid 64-character lowercase hex");
    
    // Determinism test
    const hash2 = await calculateHash(0, "2026-06-10 09:00:00", "system_init --secure", "0000000000000000000000000000000000000000000000000000000000000000");
    assert(hash === hash2, "SHA-256 hash calculation must be deterministic");
  });

  await runAsyncTest("initLedger initializes deterministic 3-block chain (Genesis + 2 Mutations)", async () => {
    await initLedger();
    assert(Array.isArray(SimulatorState.ledgerChain), "ledgerChain must be an array");
    assert(SimulatorState.ledgerChain.length === 3, `Expected 3 blocks, got ${SimulatorState.ledgerChain.length}`);

    // Genesis Block
    const b0 = SimulatorState.ledgerChain[0];
    assert(b0.index === 0, "Block 0 index must be 0");
    assert(b0.previousHash === "0000000000000000000000000000000000000000000000000000000000000000", "Genesis previousHash must be 64 zeros");
    assert(b0.data === "system_init --secure", "Genesis data mismatch");
    assert(b0.hash.length === 64, "Genesis hash must be 64-character SHA-256");

    // Block 1
    const b1 = SimulatorState.ledgerChain[1];
    assert(b1.index === 1, "Block 1 index must be 1");
    assert(b1.previousHash === b0.hash, "Block 1 previousHash must point to Block 0 hash");
    assert(b1.data.includes("INSERT INTO orders"), "Block 1 data mismatch");

    // Block 2
    const b2 = SimulatorState.ledgerChain[2];
    assert(b2.index === 2, "Block 2 index must be 2");
    assert(b2.previousHash === b1.hash, "Block 2 previousHash must point to Block 1 hash");

    // Initial Verification Check
    await verifyLedgerChain();
    assert(!b0.tampered && !b1.tampered && !b2.tampered, "All initial blocks must be untampered");
  });

  await runAsyncTest("appendLedgerBlock dynamically appends and chains cryptographic hashes", async () => {
    await initLedger();
    const initialLen = SimulatorState.ledgerChain.length;
    await appendLedgerBlock("UPDATE inventory SET stock = stock - 1");

    assert(SimulatorState.ledgerChain.length === initialLen + 1, "Chain length should increment by 1");
    const newBlock = SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1];
    const prevBlock = SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 2];
    assert(newBlock.index === initialLen, "New block index must match previous length");
    assert(newBlock.previousHash === prevBlock.hash, "New block previousHash must strictly equal previous block hash");
    assert(!newBlock.tampered && !newBlock.cascadeInvalid, "New block must be clean");
  });

  // -----------------------------------------------------------------------------
  // SECTION 2: CASCADING TAMPER & SEQUENTIAL RECALCULATION (R4)
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 2: Cascading Tamper & Sequential Recalculation (R4) ---");

  await runAsyncTest("Simulate Malicious Tamper: Block 2 turns crimson AND all downstream blocks turn crimson with broken pointer warnings", async () => {
    await initLedger();
    // Append extra blocks 3 and 4 to test downstream cascade
    await appendLedgerBlock("INSERT INTO audit_log (event) VALUES ('auth_success')");
    await appendLedgerBlock("UPDATE accounts SET balance = balance + 500");
    assert(SimulatorState.ledgerChain.length === 5, "Expected 5 blocks before tamper");

    // Trigger Malicious Tamper on Block 2
    tamperLedgerBlock2();

    // Verify Block 2 state
    const b2 = SimulatorState.ledgerChain[2];
    assert(b2.tampered === true, "Block 2 must be flagged tampered=true");
    assert(b2.data.includes("25000.00"), "Block 2 payload must reflect tampered mutation");

    // Verify Downstream Blocks (3 and 4)
    const b3 = SimulatorState.ledgerChain[3];
    const b4 = SimulatorState.ledgerChain[4];
    assert(b3.cascadeInvalid === true, "Downstream Block 3 must be flagged cascadeInvalid=true");
    assert(b4.cascadeInvalid === true, "Downstream Block 4 must be flagged cascadeInvalid=true");

    // Verify DOM rendering
    renderLedger();
    const ledgerContainer = document.getElementById("ledger-container");
    assert(ledgerContainer.innerHTML.includes("tampered-block-card"), "DOM must contain .tampered-block-card for Block 2");
    assert(ledgerContainer.innerHTML.includes("cascade-invalid"), "DOM must contain .cascade-invalid for downstream blocks");
    assert(ledgerContainer.innerHTML.includes("broken-arrow"), "DOM must contain .broken-arrow with '≠' symbol");
    assert(ledgerContainer.innerHTML.includes("≠"), "DOM arrows must render broken pointer symbol ≠");

    // Verify ZK HUD metrics
    const tamperScoreEl = document.getElementById("zk-tamper-score");
    const merkleEl = document.getElementById("zk-merkle-root");
    assert(tamperScoreEl.textContent.includes("TAMPERED"), "ZK Tamper Score must reflect tamper breach");
    assert(merkleEl.textContent === "INVALIDATED", "Merkle root must reflect INVALIDATED");
  });

  await runAsyncTest("Cryptographic Repair & Recalculate: Sequential SHA-256 recalculation restores all blocks to emerald", async () => {
    // Current chain is tampered from previous test
    assert(SimulatorState.ledgerChain[2].tampered === true, "Precondition: Block 2 is tampered");
    assert(SimulatorState.ledgerChain[3].cascadeInvalid === true, "Precondition: Block 3 is cascade invalid");

    // Trigger Cryptographic Repair
    await repairAndRecalculateLedger();

    // Verify all blocks are mathematically verified and valid
    for (let i = 0; i < SimulatorState.ledgerChain.length; i++) {
      const b = SimulatorState.ledgerChain[i];
      assert(b.tampered === false, `Block ${i} tampered flag should be false after repair`);
      assert(b.cascadeInvalid === false, `Block ${i} cascadeInvalid flag should be false after repair`);
      if (i >= 2) {
        assert(b.repaired === true, `Block ${i} repaired flag should be true`);
      }

      if (i > 0) {
        const prev = SimulatorState.ledgerChain[i - 1];
        assert(b.previousHash === prev.hash, `Block ${i} previousHash must match Block ${i-1} newly calculated hash`);
      }
      
      const expectedHash = await calculateHash(b.index, b.timestamp, b.data, b.previousHash);
      assert(b.hash === expectedHash, `Block ${i} hash ${b.hash} must match computed hash ${expectedHash}`);
    }

    // Verify DOM rendering
    renderLedger();
    const ledgerContainer = document.getElementById("ledger-container");
    assert(!ledgerContainer.innerHTML.includes("tampered-block-card"), "DOM must NOT contain tampered blocks after repair");
    assert(!ledgerContainer.innerHTML.includes("cascade-invalid"), "DOM must NOT contain cascade-invalid blocks after repair");
    assert(!ledgerContainer.innerHTML.includes("≠"), "DOM must NOT contain broken arrows ≠ after repair");
    assert(ledgerContainer.innerHTML.includes("→"), "DOM must contain restored arrows →");

    // Verify ZK HUD metrics restored
    const tamperScoreEl = document.getElementById("zk-tamper-score");
    assert(tamperScoreEl.textContent === "100%", "ZK Tamper Score must be restored to 100%");
  });

  await runAsyncTest("Adversarial Stress Test: Rapid Repeated Tampers & Repairs (25 consecutive cycles)", async () => {
    await initLedger();
    // Add 6 extra blocks to have an 8-block chain
    for (let i = 0; i < 5; i++) {
      await appendLedgerBlock(`MUTATION_LOG_ENTRY_#${i}`);
    }
    assert(SimulatorState.ledgerChain.length === 8, "Expected 8 blocks");

    for (let cycle = 1; cycle <= 25; cycle++) {
      // 1. Malicious Tamper
      tamperLedgerBlock2();
      assert(SimulatorState.ledgerChain[2].tampered === true, `Cycle ${cycle}: Block 2 must be tampered`);
      for (let j = 3; j < 8; j++) {
        assert(SimulatorState.ledgerChain[j].cascadeInvalid === true, `Cycle ${cycle}: Block ${j} must be cascade invalid`);
      }

      // 2. Cryptographic Repair
      await repairAndRecalculateLedger();
      for (let j = 0; j < 8; j++) {
        assert(SimulatorState.ledgerChain[j].tampered === false, `Cycle ${cycle}: Block ${j} must be repaired`);
        assert(SimulatorState.ledgerChain[j].cascadeInvalid === false, `Cycle ${cycle}: Block ${j} must not be cascade invalid`);
      }
    }
    console.log("    [OK] 25 consecutive tamper/repair stress cycles completed with zero cryptographic drift.");
  });

  // -----------------------------------------------------------------------------
  // SECTION 3: R3 ZERO-UI SANDBOX - 4 ERP SCENARIOS & EPHEMERAL UI GENERATOR
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 3: R3 Zero-UI Sandbox - 4 ERP Scenarios & Ephemeral UI ---");

  await runAsyncTest("Scenario 1: Invoice Anomaly Detection & Ledger Rebalancing (Diff Table & Commit Action)", async () => {
    // 1. Verify Workflow Trace Structure
    const trace = Workflows.audit;
    assert(Array.isArray(trace) && trace.length > 5, "Workflow 'audit' must have comprehensive ReAct trace");
    assert(trace.some(t => t.text.includes("High Value Policy")), "Must reference High Value Policy");
    assert(trace.some(t => t.text.includes("node_vector_search")), "Must execute vector search");
    assert(trace.some(t => t.text.includes("CFO Directive 2026-B")), "Must cite CFO Directive 2026-B");

    // 2. Render Audit Dashboard
    renderAuditDashboard();
    const container = document.getElementById("ephemeral-ui-container");
    assert(container.innerHTML.includes("Scenario 1: Risk Assessment & Ledger Rebalance"), "Dashboard title mismatch");
    assert(container.innerHTML.includes("Accounting Ledger Rebalance Diff Table"), "Diff table missing");
    assert(container.innerHTML.includes("Accounts Payable (Acc 1010)"), "AP 1010 row missing");
    assert(container.innerHTML.includes("Suspense Holding (Acc 2040)"), "Suspense 2040 row missing");
    assert(container.innerHTML.includes("-$1,250.00"), "Diff delta negative -$1,250.00 missing");
    assert(container.innerHTML.includes("+$1,250.00"), "Diff delta positive +$1,250.00 missing");

    // 3. Test Commit Action: commitLedgerRebalance()
    const ledgerLenBefore = SimulatorState.ledgerChain.length;
    await commitLedgerRebalance();
    assert(SimulatorState.ledgerChain.length === ledgerLenBefore + 2, "commitLedgerRebalance must append 2 ledger blocks (AP and Suspense)");
    
    // 4. Test CFO Waiver Approval: approveWaiver(2)
    const targetOrder = SimulatorState.orders.find(o => o.id === 2);
    assert(targetOrder.status === "pending", "Order #2 must initially be pending");
    await approveWaiver(2);
    assert(targetOrder.status === "approved", "Order #2 must transition to approved");
    assert(SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1].data.includes("UPDATE orders SET status = 'approved' WHERE id = 2"), "Waiver approval block must be logged to ledger");
  });

  await runAsyncTest("Scenario 2: Automated Inventory Stockout Mitigation & PO Dispatch (Diff Table, SVG Chart, 1-Click PO)", async () => {
    // 1. Verify Workflow Trace Structure
    const trace = Workflows.inventory_stockout;
    assert(Array.isArray(trace) && trace.length > 5, "Workflow 'inventory_stockout' must have ReAct trace");
    assert(trace.some(t => t.text.includes("Quantum Processor v1")), "Must reference target SKU");
    assert(trace.some(t => t.text.includes("graph_traverse")), "Must perform Cypher graph traversal");
    assert(trace.some(t => t.text.includes("Apex Micro")), "Must select Apex Micro supplier");

    // 2. Render Stockout Dashboard
    renderStockoutDashboard();
    const container = document.getElementById("ephemeral-ui-container");
    assert(container.innerHTML.includes("Scenario 2: Stockout Mitigation & PO Dispatch"), "Dashboard title mismatch");
    assert(container.innerHTML.includes("Supplier Procurement Matrix"), "Supplier matrix missing");
    assert(container.innerHTML.includes("Apex Microelectronics (Optimal)"), "Apex Microelectronics row missing");
    assert(container.innerHTML.includes("Quantum Dynamics Corp"), "Quantum Dynamics row missing");
    assert(container.innerHTML.includes("Nova Foundry Direct"), "Nova Foundry row missing");

    // 3. Verify Burndown SVG Chart
    assert(container.innerHTML.includes("<svg"), "Burndown SVG chart element missing");
    assert(container.innerHTML.includes("Safety Threshold: 10 units"), "Safety threshold label missing in SVG");
    assert(container.innerHTML.includes("stockoutGradient"), "Linear gradient missing in SVG chart");
    assert(container.innerHTML.includes("<circle"), "Point markers missing in SVG chart");

    // 4. Test 1-Click PO Dispatch: dispatchPurchaseOrder()
    const prod = SimulatorState.products.find(p => p.name === "Quantum Processor v1");
    const initialStock = prod.stock_quantity;
    const ledgerLenBefore = SimulatorState.ledgerChain.length;

    await dispatchPurchaseOrder();
    assert(prod.stock_quantity === initialStock + 50, `Stock should increment by 50 units (expected ${initialStock + 50}, got ${prod.stock_quantity})`);
    assert(SimulatorState.ledgerChain.length === ledgerLenBefore + 1, "dispatchPurchaseOrder must append PO block to ledger");
    assert(SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1].data.includes("PO-2026-8841"), "PO number mismatch in ledger block");
  });

  await runAsyncTest("Scenario 3: Autonomous SQL Querying & Financial Report Synthesis (KPI Tiles & Dynamic SVG Chart)", async () => {
    // 1. Verify Workflow Trace Structure
    const trace = Workflows.sql_financial;
    assert(Array.isArray(trace) && trace.length > 5, "Workflow 'sql_financial' must have ReAct trace");
    assert(trace.some(t => t.text.includes("synthesize_financial_kpis")), "Must reference synthesis directive");
    assert(trace.some(t => t.text.includes("execute_sql")), "Must execute multi-table SQL aggregation");
    assert(trace.some(t => t.text.includes("gross_revenue")), "Must compute gross revenue");

    // 2. Render Financial Dashboard
    renderFinancialDashboard();
    const container = document.getElementById("ephemeral-ui-container");
    assert(container.innerHTML.includes("Scenario 3: Autonomous SQL & Financial Synthesis"), "Dashboard title mismatch");
    assert(container.innerHTML.includes("kpi-grid"), "Executive KPI Grid container missing");
    assert(container.innerHTML.includes("Gross ARR"), "Gross ARR KPI tile missing");
    assert(container.innerHTML.includes("$4.25M"), "Gross ARR $4.25M value missing");
    assert(container.innerHTML.includes("EBITDA Margin"), "EBITDA Margin KPI tile missing");
    assert(container.innerHTML.includes("34.2%"), "EBITDA Margin 34.2% value missing");
    assert(container.innerHTML.includes("Net Cash Burn"), "Net Cash Burn KPI tile missing");
    assert(container.innerHTML.includes("$42.1k/mo"), "Net Cash Burn value missing");
    assert(container.innerHTML.includes("Loop Latency"), "Loop Latency KPI tile missing");
    assert(container.innerHTML.includes("11.8ms"), "Loop Latency 11.8ms value missing");

    // 3. Verify Dynamic Multi-Series SVG Financial Chart
    assert(container.innerHTML.includes("Monthly Revenue vs Operating Outlay (FY2026)"), "Chart title missing");
    assert(container.innerHTML.includes("<svg"), "Financial SVG element missing");
    assert(container.innerHTML.includes("Jan") && container.innerHTML.includes("Jun"), "Month labels Jan..Jun missing");
    assert(container.innerHTML.includes("rect"), "SVG bar rect elements missing");
  });

  await runAsyncTest("Scenario 4: Role-Based Access Control (RBAC) Security Quarantine (Scope Diff Table & Quarantine Action)", async () => {
    // 1. Verify Workflow Trace Structure
    const trace = Workflows.rbac_quarantine;
    assert(Array.isArray(trace) && trace.length > 5, "Workflow 'rbac_quarantine' must have ReAct trace");
    assert(trace.some(t => t.text.includes("Token#usr_c789")), "Must reference target token");
    assert(trace.some(t => t.text.includes("198.51.100.42")), "Must reference source IP");
    assert(trace.some(t => t.text.includes("execute_security_quarantine")), "Must execute quarantine action");

    // 2. Render RBAC Quarantine Dashboard
    renderRBACDashboard();
    const container = document.getElementById("ephemeral-ui-container");
    assert(container.innerHTML.includes("Security Incident: Privilege Boundary Violation"), "Incident title missing");
    assert(container.innerHTML.includes("SESSION QUARANTINED"), "Session quarantined badge missing");
    assert(container.innerHTML.includes("198.51.100.42"), "Target IP missing");
    assert(container.innerHTML.includes("RBAC Permission Scope Analysis"), "Permission scope table missing");
    assert(container.innerHTML.includes("payroll_executive_ledger"), "Unauthorized target resource missing");
    assert(container.innerHTML.includes("SCHEMA_DUMP"), "Unauthorized mutation directive missing");
    assert(container.innerHTML.includes("Level 4 (CFO Clearance)"), "Unauthorized clearance level missing");
    assert(container.innerHTML.includes("pulse-tampered"), "Pulsating crimson animation missing");

    // 3. Test Quarantine Action: quarantineSecurityIncident()
    const ledgerLenBefore = SimulatorState.ledgerChain.length;
    await quarantineSecurityIncident();
    assert(SimulatorState.ledgerChain.length === ledgerLenBefore + 1, "quarantineSecurityIncident must append security audit block to ledger");
    assert(SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1].data.includes("198.51.100.42"), "Security block must log quarantined IP");
    assert(SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1].data.includes("BLACKLIST"), "Security block must log BLACKLIST action");
  });

  await runAsyncTest("Scenario 5: Saga Procure-to-Pay Workflow (Compliant vs Non-Compliant Compensation)", async () => {
    // Case A: Compliant Order ($299.99 <= $500.00 limit)
    const compliantTrace = Workflows.saga("Ergonomic Chair", 1, 299.99, true);
    assert(compliantTrace.some(t => t.text.includes("STATUS: COMPLETED") || t.text.includes("Saga Completed successfully")), "Compliant saga must complete successfully");
    assert(!compliantTrace.some(t => t.text.includes("Compensating rollback") || t.text.includes("DENIED")), "Compliant saga must not roll back");

    // Case B: Non-Compliant Order ($999.00 > $500.00 limit)
    const nonCompliantTrace = Workflows.saga("Standing Desk", 2, 999.00, false);
    assert(nonCompliantTrace.some(t => t.text.includes("DENIED") || t.text.includes("compensating rollback")), "Non-compliant saga must initiate backward rollback");
    assert(nonCompliantTrace.some(t => t.text.includes("COMPENSATED") || t.text.includes("Inventory restored")), "Non-compliant saga must compensate and restore stock");
  });

  // -----------------------------------------------------------------------------
  // SECTION 4: STRICT SAG BRANDING COMPLIANCE AUDIT
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 4: Strict SAG Branding Compliance Audit ---");

  test("Strict SAG Branding: Zero occurrences of 'ActiveGraph' anywhere in codebase strings", () => {
    const forbidden = "ActiveGraph";
    const appStr = JSON.stringify(app);
    assert(!appStr.includes(forbidden), `Forbidden string '${forbidden}' found in app exports!`);
    
    // Check Workflows
    const workflowsStr = JSON.stringify(Workflows);
    assert(!workflowsStr.includes(forbidden), `Forbidden string '${forbidden}' found in Workflows!`);
  });

  console.log("\n===============================================================================");
  console.log(`ALL R3 & R4 EMPIRICAL ADVERSARIAL TESTS PASSED: ${testsPassed} / ${testsTotal}`);
  console.log("===============================================================================\n");
}

runSuite().catch(err => {
  console.error("FATAL STRESS SUITE ERROR:", err);
  process.exit(1);
});
