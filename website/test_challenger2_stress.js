/**
 * Challenger 2: Deep Cryptographic Ledger, Math Stress & ReAct Concurrency Test Suite
 * 
 * Target Domains:
 * 1. SHA-256 Web Crypto API verification against Node.js native crypto oracle.
 * 2. Genesis Block 64-zero format invariant testing.
 * 3. Deep chain (20+ blocks) cascading tamper invalidation.
 * 4. Multi-cycle stress (100 rapid tamper/repair/reset loops).
 * 5. ROI math boundary testing & fuzzing (min, max, extreme, negative, NaN inputs).
 * 6. ReAct workflow concurrency and state machine re-entrancy.
 * 7. Ephemeral UI mutation consistency under ledger state changes.
 */

import { createHash } from "crypto";

// 1. DOM Mock for Node environment
const elements = {};

function createMockElement(id, tagName = "div") {
  return {
    id,
    tagName: tagName.toUpperCase(),
    innerHTML: "",
    _textContent: "",
    _innerText: "",
    get textContent() {
      if (this.innerHTML) {
        return this.innerHTML.replace(/<[^>]*>?/gm, "").trim();
      }
      return this._textContent;
    },
    set textContent(val) {
      this._textContent = val;
      this.innerHTML = val;
    },
    get innerText() {
      return this._innerText || this.textContent;
    },
    set innerText(val) {
      this._innerText = val;
      this.textContent = val;
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
    return createMockElement(`dyn_${Math.random().toString(36).substr(2, 9)}`, tag);
  },
  querySelectorAll(selector) {
    return [];
  },
  querySelector(selector) {
    return null;
  },
  addEventListener() {},
  body: createMockElement("body", "body")
};

global.document = mockDoc;
global.window = {
  addEventListener() {},
  crypto: globalThis.crypto,
  navigator: { clipboard: { writeText: async () => {} } }
};

function assert(condition, message) {
  if (!condition) {
    console.error(`  [ASSERTION FAILED] ${message}`);
    throw new Error(message);
  }
}

let testsPassed = 0;
let testsTotal = 0;

async function runTest(name, fn) {
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

async function runChallengerSuite() {
  console.log("===============================================================================");
  console.log("CHALLENGER 2: DEEP CRYPTOGRAPHIC LEDGER, MATH & CONCURRENCY STRESS SUITE");
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
    resetLedger,
    updateZKMetrics,
    updateROI,
    SimulatorState,
    Workflows,
    runWorkflow,
    approveWaiver,
    commitLedgerRebalance,
    dispatchPurchaseOrder,
    quarantineSecurityIncident
  } = app;

  // -----------------------------------------------------------------------------
  // TEST GROUP 1: CRYPTOGRAPHIC HASH ORACLE & INVARIANT VERIFICATION
  // -----------------------------------------------------------------------------
  console.log("--- Group 1: Cryptographic Hash Oracle & Invariant Verification ---");

  await runTest("calculateHash produces byte-for-byte identical output to Node crypto SHA-256 oracle", async () => {
    const testCases = [
      { idx: 0, ts: "2026-06-10 09:00:00", data: "system_init --secure", prev: "0000000000000000000000000000000000000000000000000000000000000000" },
      { idx: 1, ts: "2026-06-10 09:01:20", data: "INSERT INTO orders (id, item, amount) VALUES (1, 'Server Racks', 405000)", prev: "a".repeat(64) },
      { idx: 99, ts: "2026-12-31 23:59:59", data: "SPECIAL CHARS !@#$%^&*()_+-=[]{}|;':,.<>?/`~ \n\t", prev: "f".repeat(64) },
      { idx: 1000, ts: "", data: "", prev: "" }
    ];

    for (const tc of testCases) {
      const appHash = await calculateHash(tc.idx, tc.ts, tc.data, tc.prev);
      const payload = `${tc.idx}|${tc.ts}|${tc.data}|${tc.prev}`;
      const oracleHash = createHash("sha256").update(payload, "utf8").digest("hex");
      assert(appHash === oracleHash, `Hash mismatch for input [${payload}]: app=${appHash}, oracle=${oracleHash}`);
    }
  });

  await runTest("Genesis block strictly adheres to 64-zero previousHash format invariant", async () => {
    await initLedger();
    const genesis = SimulatorState.ledgerChain[0];
    assert(genesis.index === 0, "Genesis index must be 0");
    assert(genesis.previousHash.length === 64, `Genesis previousHash length must be 64, got ${genesis.previousHash.length}`);
    assert(/^0{64}$/.test(genesis.previousHash), `Genesis previousHash must consist strictly of 64 zeros, got ${genesis.previousHash}`);
    
    // Check verification function on Genesis block
    const isValid = await verifyLedgerChain();
    assert(isValid === true, "Freshly initialized ledger must verify 100% valid");
  });

  await runTest("Avalanche effect test: 1-character mutation completely alters SHA-256 digest", async () => {
    const data1 = "UPDATE accounts SET balance = 405000";
    const data2 = "UPDATE accounts SET balance = 405001";
    const h1 = await calculateHash(1, "2026-06-10 09:00:00", data1, "0".repeat(64));
    const h2 = await calculateHash(1, "2026-06-10 09:00:00", data2, "0".repeat(64));
    
    assert(h1 !== h2, "Hashes must not collide");
    
    // Count bit differences
    let diffBits = 0;
    for (let i = 0; i < 64; i++) {
      const v1 = parseInt(h1[i], 16);
      const v2 = parseInt(h2[i], 16);
      let xor = v1 ^ v2;
      while (xor > 0) {
        diffBits += (xor & 1);
        xor >>= 1;
      }
    }
    // Expected bit difference in SHA-256 avalanche is ~50% (128 out of 256 bits)
    assert(diffBits > 80, `Avalanche effect too weak: only ${diffBits}/256 bits changed`);
  });

  // -----------------------------------------------------------------------------
  // TEST GROUP 2: DEEP CHAIN CASCADING INVALIDATION & MULTI-CYCLE STRESS
  // -----------------------------------------------------------------------------
  console.log("\n--- Group 2: Deep Chain Cascading Invalidation & Multi-Cycle Stress ---");

  await runTest("Deep Chain Cascading: Tampering Block #2 on a 25-block chain invalidates blocks 3 through 24", async () => {
    await initLedger();
    // Add 22 extra blocks (total 25)
    for (let i = 3; i < 25; i++) {
      await appendLedgerBlock(`DATA_MUTATION_EVENT_SEQUENCE_${i}`);
    }
    assert(SimulatorState.ledgerChain.length === 25, `Expected 25 blocks, got ${SimulatorState.ledgerChain.length}`);

    // Pre-tamper verification
    let valid = await verifyLedgerChain();
    assert(valid === true, "Pre-tamper 25-block chain must be valid");

    // Tamper Block 2
    tamperLedgerBlock2();

    // Verify Block 0 and 1 remain untampered and clean
    assert(SimulatorState.ledgerChain[0].tampered === false, "Genesis block 0 must remain untampered");
    assert(SimulatorState.ledgerChain[1].tampered === false, "Block 1 must remain untampered");

    // Verify Block 2 is tampered
    assert(SimulatorState.ledgerChain[2].tampered === true, "Block 2 must be flagged tampered");

    // Verify all 22 downstream blocks (3 to 24) are cascade-invalidated
    for (let i = 3; i < 25; i++) {
      assert(SimulatorState.ledgerChain[i].cascadeInvalid === true, `Block ${i} must have cascadeInvalid=true`);
      assert(SimulatorState.ledgerChain[i].is_verified === false, `Block ${i} must have is_verified=false`);
    }

    // Verify repair on deep 25-block chain
    await repairAndRecalculateLedger();
    for (let i = 0; i < 25; i++) {
      const b = SimulatorState.ledgerChain[i];
      assert(b.tampered === false, `Block ${i} tampered must be false after repair`);
      assert(b.cascadeInvalid === false, `Block ${i} cascadeInvalid must be false after repair`);
      assert(b.is_verified === true, `Block ${i} is_verified must be true after repair`);
      if (i > 0) {
        assert(b.previousHash === SimulatorState.ledgerChain[i-1].hash, `Block ${i} previousHash must match Block ${i-1} hash`);
      }
    }

    valid = await verifyLedgerChain();
    assert(valid === true, "Repaired 25-block chain must verify 100% valid");
  });

  await runTest("Multi-Cycle Stress: 50 consecutive Tamper -> Repair -> Reset -> Append cycles", async () => {
    for (let cycle = 1; cycle <= 50; cycle++) {
      // 1. Reset
      await resetLedger();
      assert(SimulatorState.ledgerChain.length === 3, `Cycle ${cycle}: Chain length must be 3 after reset`);
      assert(SimulatorState.ledgerChain[0].previousHash === "0".repeat(64), `Cycle ${cycle}: Genesis prevHash must be 64 zeros`);

      // 2. Append 2 blocks
      await appendLedgerBlock(`CYCLE_${cycle}_BLOCK_3`);
      await appendLedgerBlock(`CYCLE_${cycle}_BLOCK_4`);
      assert(SimulatorState.ledgerChain.length === 5, `Cycle ${cycle}: Chain length must be 5`);

      // 3. Tamper
      tamperLedgerBlock2();
      assert(SimulatorState.ledgerChain[2].tampered === true, `Cycle ${cycle}: Block 2 tampered`);
      assert(SimulatorState.ledgerChain[3].cascadeInvalid === true, `Cycle ${cycle}: Block 3 cascade invalid`);
      assert(SimulatorState.ledgerChain[4].cascadeInvalid === true, `Cycle ${cycle}: Block 4 cascade invalid`);

      // 4. Repair
      await repairAndRecalculateLedger();
      assert(SimulatorState.ledgerChain.every(b => !b.tampered && !b.cascadeInvalid), `Cycle ${cycle}: All blocks clean after repair`);

      // 5. Verify cryptographic chain validity
      const valid = await verifyLedgerChain();
      assert(valid === true, `Cycle ${cycle}: verifyLedgerChain must return true`);
    }
  });

  // -----------------------------------------------------------------------------
  // TEST GROUP 3: ENTERPRISE ROI CALCULATOR EXTREME VALUES & BOUNDARY FUZZING
  // -----------------------------------------------------------------------------
  console.log("\n--- Group 3: Enterprise ROI Calculator Extreme Values & Boundary Fuzzing ---");

  await runTest("ROI Calculator math with default baseline values (2500 HC, $250M Rev, 120 Ops)", () => {
    document.getElementById("slider-headcount").value = "2500";
    document.getElementById("slider-revenue").value = "250";
    document.getElementById("slider-ops").value = "120";

    updateROI();

    const calcSav = document.getElementById("calc-savings").innerText;
    const calcHrs = document.getElementById("calc-hours").innerText;
    const calcPay = document.getElementById("calc-payback").innerText;
    const calcRoi = document.getElementById("calc-roi").innerText;

    // Normalize dots/commas for locale independence
    const normSav = calcSav.replace(/[.,]/g, "");
    const normHrs = calcHrs.replace(/[.,]/g, "");

    assert(normSav === "$7115000", `Expected $7,115,000, got ${calcSav}`);
    assert(normHrs === "28800 hrs", `Expected 28,800 hrs, got ${calcHrs}`);
    assert(calcPay === "< 41 Days", `Expected < 41 Days, got ${calcPay}`);
    assert(calcRoi === "433%", `Expected 433%, got ${calcRoi}`);
  });

  await runTest("ROI Calculator minimum boundary values (100 HC, $5M Rev, 5 Ops)", () => {
    document.getElementById("slider-headcount").value = "100";
    document.getElementById("slider-revenue").value = "5";
    document.getElementById("slider-ops").value = "5";

    updateROI();

    const calcSav = document.getElementById("calc-savings").innerText;
    const calcHrs = document.getElementById("calc-hours").innerText;
    const calcPay = document.getElementById("calc-payback").innerText;
    const calcRoi = document.getElementById("calc-roi").innerText;

    const normSav = calcSav.replace(/[.,]/g, "");
    const normHrs = calcHrs.replace(/[.,]/g, "");

    assert(normSav === "$692500", `Expected $692,500, got ${calcSav}`);
    assert(normHrs === "1200 hrs", `Expected 1,200 hrs, got ${calcHrs}`);
    assert(calcPay === "< 45 Days", `Expected < 45 Days, got ${calcPay}`);
    assert(calcRoi === "322%", `Expected 322%, got ${calcRoi}`);
  });

  await runTest("ROI Calculator maximum boundary values (50,000 HC, $5,000M Rev, 1,000 Ops)", () => {
    document.getElementById("slider-headcount").value = "50000";
    document.getElementById("slider-revenue").value = "5000";
    document.getElementById("slider-ops").value = "1000";

    updateROI();

    const calcSav = document.getElementById("calc-savings").innerText;
    const calcHrs = document.getElementById("calc-hours").innerText;
    const calcPay = document.getElementById("calc-payback").innerText;
    const calcRoi = document.getElementById("calc-roi").innerText;

    const normSav = calcSav.replace(/[.,]/g, "");
    const normHrs = calcHrs.replace(/[.,]/g, "");

    assert(normSav === "$74950000", `Expected $74,950,000, got ${calcSav}`);
    assert(normHrs === "240000 hrs", `Expected 240,000 hrs, got ${calcHrs}`);
    assert(calcPay === "< 18 Days", `Expected < 18 Days (clamped), got ${calcPay}`);
    assert(calcRoi === "2570%", `Expected 2570%, got ${calcRoi}`);
  });

  await runTest("ROI Calculator fuzz test with extreme, zero, and missing inputs", () => {
    const fuzzInputs = [
      { hc: "0", rev: "0", ops: "0" },
      { hc: "-500", rev: "-100", ops: "-50" },
      { hc: "invalid", rev: "undefined", ops: "null" },
      { hc: "999999999", rev: "999999", ops: "99999" }
    ];

    for (const inp of fuzzInputs) {
      document.getElementById("slider-headcount").value = inp.hc;
      document.getElementById("slider-revenue").value = inp.rev;
      document.getElementById("slider-ops").value = inp.ops;

      updateROI();

      const calcSav = document.getElementById("calc-savings").innerText;
      const calcHrs = document.getElementById("calc-hours").innerText;
      const calcPay = document.getElementById("calc-payback").innerText;
      const calcRoi = document.getElementById("calc-roi").innerText;

      assert(!calcSav.includes("NaN"), `NaN produced in savings for input ${JSON.stringify(inp)}`);
      assert(!calcHrs.includes("NaN"), `NaN produced in hours for input ${JSON.stringify(inp)}`);
      assert(!calcPay.includes("NaN"), `NaN produced in payback for input ${JSON.stringify(inp)}`);
      assert(!calcRoi.includes("NaN"), `NaN produced in ROI for input ${JSON.stringify(inp)}`);
    }
  });

  // -----------------------------------------------------------------------------
  // TEST GROUP 4: REACT WORKFLOW CONCURRENCY & RE-ENTRANCY LOCKS
  // -----------------------------------------------------------------------------
  console.log("\n--- Group 4: ReAct Workflow Concurrency & Re-Entrancy Locks ---");

  await runTest("runWorkflow rejects concurrent executions while isProcessing is true", async () => {
    SimulatorState.isProcessing = false;
    
    // Start scenario 1
    const p1 = runWorkflow("audit");
    assert(SimulatorState.isProcessing === true, "SimulatorState.isProcessing must be true during execution");

    // Attempt to start scenario 2 concurrently while p1 is running
    const p2 = runWorkflow("inventory_stockout");
    assert(SimulatorState.activeScenario === "audit", "Active scenario must remain 'audit' because concurrent call was rejected");

    await p1;
    assert(SimulatorState.isProcessing === false, "SimulatorState.isProcessing must be false after completion");
  });

  await runTest("Ephemeral actions properly mutate application state and append ledger blocks sequentially", async () => {
    await resetLedger();
    const startBlocks = SimulatorState.ledgerChain.length; // 3

    // 1. Commit Rebalance (adds 2 blocks)
    await commitLedgerRebalance();
    assert(SimulatorState.ledgerChain.length === startBlocks + 2, "commitLedgerRebalance must add 2 blocks");

    // 2. Approve Waiver (adds 1 block)
    await approveWaiver(2);
    assert(SimulatorState.ledgerChain.length === startBlocks + 3, "approveWaiver must add 1 block");

    // 3. Dispatch PO (adds 1 block)
    await dispatchPurchaseOrder();
    assert(SimulatorState.ledgerChain.length === startBlocks + 4, "dispatchPurchaseOrder must add 1 block");

    // 4. Quarantine Incident (adds 1 block)
    await quarantineSecurityIncident();
    assert(SimulatorState.ledgerChain.length === startBlocks + 5, "quarantineSecurityIncident must add 1 block");

    // Verify all 8 blocks in chain form a valid SHA-256 cryptographic sequence
    const isValid = await verifyLedgerChain();
    assert(isValid === true, "Ledger chain with all ephemeral mutations must verify 100% cryptographically valid");
  });

  console.log("\n===============================================================================");
  console.log(`ALL CHALLENGER 2 STRESS TESTS PASSED: ${testsPassed} / ${testsTotal}`);
  console.log("===============================================================================\n");
}

runChallengerSuite().catch(err => {
  console.error("FATAL CHALLENGER 2 SUITE ERROR:", err);
  process.exit(1);
});
