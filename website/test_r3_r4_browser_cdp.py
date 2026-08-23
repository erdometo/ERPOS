"""
Empirical Adversarial Test Suite for R3 & R4 via Headless Chrome DevTools Protocol (CDP)
Executes in real headless Google Chrome with live DOM, JS Engine, Web Crypto API, and SVG/CSS rendering.
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import asyncio
import websockets

PORT = 8095
CHROME_PORT = 9228
PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "public"))
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

class HeadlessBrowserTestR3R4(unittest.TestCase):
    httpd = None
    server_thread = None
    chrome_proc = None
    ws_url = None

    @classmethod
    def setUpClass(cls):
        # 1. Start HTTP Server
        cls.httpd = HTTPServer(("127.0.0.1", PORT), QuietHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        print(f"[*] Local HTTP Server started on http://127.0.0.1:{PORT}")

        # Kill any lingering chrome on CHROME_PORT
        try:
            output = subprocess.check_output("netstat -ano", shell=True).decode("utf-8")
            for line in output.splitlines():
                if f":{CHROME_PORT} " in line:
                    parts = line.split()
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) > 0:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        time.sleep(0.5)

        # 2. Start Headless Chrome
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--remote-debugging-port={CHROME_PORT}",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--user-data-dir=" + os.path.join(os.environ.get("TEMP", "C:/Temp"), f"chrome_r3r4_profile_{int(time.time())}"),
            f"http://127.0.0.1:{PORT}/index.html"
        ]
        cls.chrome_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[*] Headless Chrome launched (PID: {cls.chrome_proc.pid})")

        # 3. Wait for Chrome CDP to become ready
        for _ in range(30):
            try:
                r = requests.get(f"http://127.0.0.1:{CHROME_PORT}/json", timeout=1)
                all_tabs = r.json()
                tabs = [t for t in all_tabs if t.get("type") == "page" and "http" in t.get("url", "")]
                if not tabs:
                    tabs = [t for t in all_tabs if t.get("type") == "page"]
                if tabs and len(tabs) > 0:
                    cls.ws_url = tabs[0].get("webSocketDebuggerUrl")
                    print(f"[*] Connected to Chrome CDP: {cls.ws_url} (URL: {tabs[0].get('url')})")
                    break
            except Exception:
                time.sleep(0.3)
        else:
            raise RuntimeError("Failed to connect to Headless Chrome via CDP")

        # 4. Wait for page initialization
        time.sleep(1.5)

    @classmethod
    def tearDownClass(cls):
        if cls.chrome_proc:
            cls.chrome_proc.terminate()
            cls.chrome_proc.wait()
            print("[*] Chrome process terminated.")
        if cls.httpd:
            cls.httpd.shutdown()
            print("[*] HTTP Server stopped.")

    def eval_js(self, expression):
        """Evaluates JS in the browser context and returns value"""
        async def _exec():
            async with websockets.connect(self.ws_url, max_size=10_000_000) as ws:
                msg_id = int(time.time() * 1000) % 1000000
                payload = {
                    "id": msg_id,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": expression,
                        "returnByValue": True,
                        "awaitPromise": True
                    }
                }
                await ws.send(json.dumps(payload))
                while True:
                    resp = await ws.recv()
                    data = json.loads(resp)
                    if data.get("id") == msg_id:
                        res = data.get("result", {})
                        if "exceptionDetails" in res:
                            raise RuntimeError(f"JS Exception: {json.dumps(res['exceptionDetails'])}")
                        return res.get("result", {}).get("value")
        return asyncio.run(_exec())

    def test_01_strict_branding_compliance_in_live_dom(self):
        """Verify strict SAG branding and ZERO occurrences of 'ActiveGraph' in live DOM"""
        result = self.eval_js("""
            (() => {
                const html = document.documentElement.outerHTML;
                const hasForbiddenText = html.includes("ActiveGraph");
                return {
                    hasForbiddenText,
                    ledgerExists: typeof window.verifyLedgerChain === 'function',
                    simulatorExists: typeof window.SimulatorState !== 'undefined'
                };
            })()
        """)
        self.assertFalse(result["hasForbiddenText"], "Strict Branding Violation: 'ActiveGraph' found in DOM HTML!")
        self.assertTrue(result["ledgerExists"], "window.verifyLedgerChain must exist")
        self.assertTrue(result["simulatorExists"], "window.SimulatorState must exist")
        print("[PASS] Strict SAG Branding verified in live Chrome DOM")

    def test_02_scenario_1_audit_diff_table_and_commit(self):
        """Verify Scenario 1: Invoice Anomaly Detection, Diff Table rendering, and Commit/Waiver actions"""
        res = self.eval_js("""
            (async () => {
                // 1. Click Scenario 1 Preset Button
                const btnScenario1 = document.querySelector(".btn-scenario[data-scenario='audit']");
                if (btnScenario1) btnScenario1.click();
                
                // Poll until workflow completes
                await new Promise(r => setTimeout(r, 300));
                while (window.SimulatorState.isProcessing) {
                    await new Promise(r => setTimeout(r, 100));
                }
                await new Promise(r => setTimeout(r, 200));

                const container = document.getElementById("ephemeral-ui-container");
                const html = container ? container.innerHTML : "";
                const text = container ? container.textContent : "";
                
                const hasTitle = text.includes("Scenario 1: Risk Assessment & Ledger Rebalance") || html.includes("Scenario 1");
                const hasDiffTable = html.includes("Accounting Ledger Rebalance Diff Table");
                const hasAP = html.includes("Accounts Payable (Acc 1010)");
                const hasSuspense = html.includes("Suspense Holding (Acc 2040)");
                const hasNegativeDelta = html.includes("-$1,250.00");
                const hasPositiveDelta = html.includes("+$1,250.00");

                // 2. Commit Ledger Rebalance
                const initialLedgerLen = window.SimulatorState.ledgerChain.length;
                await window.commitLedgerRebalance();
                const postCommitLedgerLen = window.SimulatorState.ledgerChain.length;

                // 3. Authorize CFO Waiver
                await window.approveWaiver(2);
                const postWaiverLedgerLen = window.SimulatorState.ledgerChain.length;
                const order2 = window.SimulatorState.orders.find(o => o.id === 2);

                return {
                    hasTitle,
                    hasDiffTable,
                    hasAP,
                    hasSuspense,
                    hasNegativeDelta,
                    hasPositiveDelta,
                    initialLedgerLen,
                    postCommitLedgerLen,
                    postWaiverLedgerLen,
                    order2Status: order2 ? order2.status : null
                };
            })()
        """)
        self.assertTrue(res["hasTitle"], "Scenario 1 title missing")
        self.assertTrue(res["hasDiffTable"], "Scenario 1 diff table missing")
        self.assertTrue(res["hasAP"], "Accounts Payable row missing in diff table")
        self.assertTrue(res["hasSuspense"], "Suspense row missing in diff table")
        self.assertTrue(res["hasNegativeDelta"], "Negative delta -$1,250.00 missing")
        self.assertTrue(res["hasPositiveDelta"], "Positive delta +$1,250.00 missing")
        self.assertEqual(res["postCommitLedgerLen"], res["initialLedgerLen"] + 2, "commitLedgerRebalance must append 2 ledger blocks")
        self.assertEqual(res["postWaiverLedgerLen"], res["postCommitLedgerLen"] + 1, "approveWaiver must append 1 ledger block")
        self.assertEqual(res["order2Status"], "approved", "Order 2 status must be approved")
        print("[PASS] Scenario 1 (Invoice Anomaly & Ledger Rebalancing) verified in live browser")

    def test_03_scenario_2_stockout_mitigation_and_po_dispatch(self):
        """Verify Scenario 2: Stockout Mitigation, SVG Burndown Chart, and 1-Click PO Dispatch"""
        res = self.eval_js("""
            (async () => {
                // 1. Click Scenario 2 Button
                const btnScenario2 = document.querySelector(".btn-scenario[data-scenario='inventory_stockout']");
                if (btnScenario2) btnScenario2.click();

                await new Promise(r => setTimeout(r, 300));
                while (window.SimulatorState.isProcessing) {
                    await new Promise(r => setTimeout(r, 100));
                }
                await new Promise(r => setTimeout(r, 200));

                const container = document.getElementById("ephemeral-ui-container");
                const html = container ? container.innerHTML : "";
                const text = container ? container.textContent : "";

                const hasTitle = text.includes("Scenario 2: Stockout Mitigation & PO Dispatch") || html.includes("Scenario 2");
                const hasSupplierMatrix = html.includes("Supplier Procurement Matrix");
                const hasApex = html.includes("Apex Microelectronics (Optimal)");
                const hasQuantum = html.includes("Quantum Dynamics Corp");
                const hasSvg = html.includes("<svg") && html.includes("Safety Threshold: 10 units");
                const hasGradient = html.includes("stockoutGradient");

                // 2. Dispatch Purchase Order
                const prod = window.SimulatorState.products.find(p => p.name === "Quantum Processor v1");
                const stockBefore = prod ? prod.stock_quantity : 0;
                const ledgerBefore = window.SimulatorState.ledgerChain.length;

                await window.dispatchPurchaseOrder();

                const stockAfter = prod ? prod.stock_quantity : 0;
                const ledgerAfter = window.SimulatorState.ledgerChain.length;

                return {
                    hasTitle,
                    hasSupplierMatrix,
                    hasApex,
                    hasQuantum,
                    hasSvg,
                    hasGradient,
                    stockBefore,
                    stockAfter,
                    ledgerBefore,
                    ledgerAfter
                };
            })()
        """)
        self.assertTrue(res["hasTitle"], "Scenario 2 title missing")
        self.assertTrue(res["hasSupplierMatrix"], "Supplier procurement matrix missing")
        self.assertTrue(res["hasApex"], "Apex Microelectronics missing")
        self.assertTrue(res["hasQuantum"], "Quantum Dynamics Corp missing")
        self.assertTrue(res["hasSvg"], "Burndown SVG chart with threshold missing")
        self.assertTrue(res["hasGradient"], "SVG gradient missing")
        self.assertEqual(res["stockAfter"], res["stockBefore"] + 50, "PO dispatch must add +50 units to stock")
        self.assertEqual(res["ledgerAfter"], res["ledgerBefore"] + 1, "PO dispatch must append 1 ledger block")
        print("[PASS] Scenario 2 (Stockout Mitigation & PO Dispatch) verified in live browser")

    def test_04_scenario_3_sql_financial_synthesis_and_kpi_grid(self):
        """Verify Scenario 3: Autonomous SQL Querying, Executive KPI Tiles, and Dynamic SVG Chart"""
        res = self.eval_js("""
            (async () => {
                const btnScenario3 = document.querySelector(".btn-scenario[data-scenario='sql_financial']");
                if (btnScenario3) btnScenario3.click();

                await new Promise(r => setTimeout(r, 300));
                while (window.SimulatorState.isProcessing) {
                    await new Promise(r => setTimeout(r, 100));
                }
                await new Promise(r => setTimeout(r, 200));

                const container = document.getElementById("ephemeral-ui-container");
                const html = container ? container.innerHTML : "";
                const text = container ? container.textContent : "";

                const hasTitle = text.includes("Scenario 3: Autonomous SQL & Financial Synthesis") || html.includes("Scenario 3");
                const hasKpiGrid = html.includes("kpi-grid");
                const hasArr = html.includes("Gross ARR") && html.includes("$4.25M");
                const hasEbitda = html.includes("EBITDA Margin") && html.includes("34.2%");
                const hasBurn = html.includes("Net Cash Burn") && html.includes("$42.1k/mo");
                const hasLatency = html.includes("Loop Latency") && html.includes("11.8ms");
                const hasSvgChart = html.includes("<svg") && html.includes("Monthly Revenue vs Operating Outlay (FY2026)");
                const hasJan = html.includes("Jan") && html.includes("Jun");

                return {
                    hasTitle,
                    hasKpiGrid,
                    hasArr,
                    hasEbitda,
                    hasBurn,
                    hasLatency,
                    hasSvgChart,
                    hasJan
                };
            })()
        """)
        self.assertTrue(res["hasTitle"], "Scenario 3 title missing")
        self.assertTrue(res["hasKpiGrid"], "KPI grid missing")
        self.assertTrue(res["hasArr"], "Gross ARR KPI tile missing")
        self.assertTrue(res["hasEbitda"], "EBITDA Margin KPI tile missing")
        self.assertTrue(res["hasBurn"], "Net Cash Burn KPI tile missing")
        self.assertTrue(res["hasLatency"], "Loop Latency KPI tile missing")
        self.assertTrue(res["hasSvgChart"], "Dynamic multi-series SVG chart missing")
        self.assertTrue(res["hasJan"], "Monthly SVG labels missing")
        print("[PASS] Scenario 3 (Autonomous SQL & Financial Report Synthesis) verified in live browser")

    def test_05_scenario_4_rbac_security_quarantine(self):
        """Verify Scenario 4: RBAC Security Quarantine, Permission Diff Table, and Perimeter Blacklist Action"""
        res = self.eval_js("""
            (async () => {
                const btnScenario4 = document.querySelector(".btn-scenario[data-scenario='rbac_quarantine']");
                if (btnScenario4) btnScenario4.click();

                await new Promise(r => setTimeout(r, 300));
                while (window.SimulatorState.isProcessing) {
                    await new Promise(r => setTimeout(r, 100));
                }
                await new Promise(r => setTimeout(r, 200));

                const container = document.getElementById("ephemeral-ui-container");
                const html = container ? container.innerHTML : "";
                const text = container ? container.textContent : "";

                const hasTitle = text.includes("Security Incident: Privilege Boundary Violation") || html.includes("Security Incident");
                const hasQuarantinedBadge = html.includes("SESSION QUARANTINED");
                const hasIp = html.includes("198.51.100.42");
                const hasScopeTable = html.includes("RBAC Permission Scope Analysis");
                const hasPayroll = html.includes("payroll_executive_ledger");
                const hasDump = html.includes("SCHEMA_DUMP");
                const hasLevel4 = html.includes("Level 4 (CFO Clearance)");

                const ledgerBefore = window.SimulatorState.ledgerChain.length;
                await window.quarantineSecurityIncident();
                const ledgerAfter = window.SimulatorState.ledgerChain.length;
                const lastBlock = window.SimulatorState.ledgerChain[ledgerAfter - 1];

                return {
                    hasTitle,
                    hasQuarantinedBadge,
                    hasIp,
                    hasScopeTable,
                    hasPayroll,
                    hasDump,
                    hasLevel4,
                    ledgerBefore,
                    ledgerAfter,
                    lastBlockData: lastBlock ? lastBlock.data : ""
                };
            })()
        """)
        self.assertTrue(res["hasTitle"], "Scenario 4 title missing")
        self.assertTrue(res["hasQuarantinedBadge"], "Session quarantined badge missing")
        self.assertTrue(res["hasIp"], "Target IP missing")
        self.assertTrue(res["hasScopeTable"], "Scope analysis table missing")
        self.assertTrue(res["hasPayroll"], "payroll_executive_ledger target missing")
        self.assertTrue(res["hasDump"], "SCHEMA_DUMP mutation missing")
        self.assertTrue(res["hasLevel4"], "Level 4 clearance missing")
        self.assertEqual(res["ledgerAfter"], res["ledgerBefore"] + 1, "Quarantine action must append security audit block to ledger")
        self.assertIn("198.51.100.42", res["lastBlockData"], "Security audit block must contain IP")
        self.assertIn("BLACKLIST", res["lastBlockData"], "Security audit block must contain BLACKLIST")
        print("[PASS] Scenario 4 (RBAC Security Quarantine) verified in live browser")

    def test_06_r4_cryptographic_tamper_cascading_invalidation(self):
        """Stress-test R4: Simulate Malicious Tamper -> Block 2 turns crimson AND downstream blocks turn crimson with broken pointer warnings"""
        res = self.eval_js("""
            (() => {
                const btnTamper = document.getElementById("btn-tamper-ledger");
                if (btnTamper) btnTamper.click();

                const container = document.getElementById("ledger-container");
                const html = container ? container.innerHTML : "";

                const b2 = window.SimulatorState.ledgerChain[2];
                const b3 = window.SimulatorState.ledgerChain[3];

                const hasTamperedClass = html.includes("tampered-block-card");
                const hasCascadeClass = html.includes("cascade-invalid");
                const hasBrokenArrow = html.includes("broken-arrow");
                const hasBrokenSymbol = html.includes("≠");

                const errorBanner = document.getElementById("ledger-status-error");
                const successBanner = document.getElementById("ledger-status-success");
                const isErrorBannerVisible = errorBanner && !errorBanner.classList.contains("hidden");
                const isSuccessBannerHidden = successBanner && successBanner.classList.contains("hidden");

                const tamperScore = document.getElementById("zk-tamper-score").textContent;
                const merkleRoot = document.getElementById("zk-merkle-root").textContent;

                return {
                    b2Tampered: b2.tampered,
                    b3CascadeInvalid: b3 ? b3.cascadeInvalid : true,
                    hasTamperedClass,
                    hasCascadeClass,
                    hasBrokenArrow,
                    hasBrokenSymbol,
                    isErrorBannerVisible,
                    isSuccessBannerHidden,
                    tamperScore,
                    merkleRoot
                };
            })()
        """)
        self.assertTrue(res["b2Tampered"], "Block 2 must be tampered")
        self.assertTrue(res["b3CascadeInvalid"], "Block 3 must have cascadeInvalid=true")
        self.assertTrue(res["hasTamperedClass"], "DOM must render .tampered-block-card")
        self.assertTrue(res["hasCascadeClass"], "DOM must render .cascade-invalid")
        self.assertTrue(res["hasBrokenArrow"], "DOM must render .broken-arrow")
        self.assertTrue(res["hasBrokenSymbol"], "DOM must render broken pointer symbol ≠")
        self.assertTrue(res["isErrorBannerVisible"], "Error banner must be visible")
        self.assertTrue(res["isSuccessBannerHidden"], "Success banner must be hidden")
        self.assertIn("TAMPERED", res["tamperScore"], "ZK tamper score must reflect TAMPERED")
        self.assertEqual(res["merkleRoot"], "INVALIDATED", "Merkle root must be INVALIDATED")
        print("[PASS] Cryptographic Tamper & Cascading Downstream Invalidation verified in live browser")

    def test_07_r4_cryptographic_repair_and_sequential_recalculation(self):
        """Stress-test R4: Cryptographic Repair & Recalculate -> Sequential SHA-256 recalculation restores all blocks to emerald"""
        res = self.eval_js("""
            (async () => {
                await window.repairAndRecalculateLedger();

                const container = document.getElementById("ledger-container");
                const html = container ? container.innerHTML : "";

                const allBlocksClean = window.SimulatorState.ledgerChain.every(b => !b.tampered && !b.cascadeInvalid);
                const hasRepairedClass = html.includes("repaired-block-card");
                const hasNoTamperedClass = !html.includes("tampered-block-card");
                const hasNoCascadeClass = !html.includes("cascade-invalid");
                const hasRestoredArrow = html.includes("→") && !html.includes("≠");

                const errorBanner = document.getElementById("ledger-status-error");
                const successBanner = document.getElementById("ledger-status-success");
                const isSuccessBannerVisible = successBanner && !successBanner.classList.contains("hidden");
                const isErrorBannerHidden = errorBanner && errorBanner.classList.contains("hidden");

                const tamperScore = document.getElementById("zk-tamper-score").textContent;

                return {
                    allBlocksClean,
                    hasRepairedClass,
                    hasNoTamperedClass,
                    hasNoCascadeClass,
                    hasRestoredArrow,
                    isSuccessBannerVisible,
                    isErrorBannerHidden,
                    tamperScore
                };
            })()
        """)
        self.assertTrue(res["allBlocksClean"], "All blocks must be clean after repair")
        self.assertTrue(res["hasRepairedClass"], "DOM must render repaired-block-card")
        self.assertTrue(res["hasNoTamperedClass"], "DOM must NOT render tampered-block-card")
        self.assertTrue(res["hasNoCascadeClass"], "DOM must NOT render cascade-invalid")
        self.assertTrue(res["hasRestoredArrow"], "DOM arrows must be restored to →")
        self.assertTrue(res["isSuccessBannerVisible"], "Success banner must be visible")
        self.assertTrue(res["isErrorBannerHidden"], "Error banner must be hidden")
        self.assertEqual(res["tamperScore"], "100%", "ZK tamper score must be restored to 100%")
        print("[PASS] Cryptographic Repair & Sequential Recalculation verified in live browser")

    def test_08_r4_repeated_tampers_and_repairs_stress_cycles(self):
        """Stress-test R4: Rapid repeated tampers and repairs in browser execution loop"""
        res = self.eval_js("""
            (async () => {
                for (let i = 0; i < 4; i++) {
                    const btnTamper = document.getElementById("btn-tamper-ledger");
                    if (btnTamper) btnTamper.click();
                    
                    if (!window.SimulatorState.ledgerChain[2].tampered) {
                        return { error: `Tamper failed at iteration ${i}` };
                    }
                    
                    await window.repairAndRecalculateLedger();
                    if (window.SimulatorState.ledgerChain.some(b => b.tampered || b.cascadeInvalid)) {
                        return { error: `Repair failed at iteration ${i}` };
                    }
                }
                return { success: true, count: 4 };
            })()
        """)
        self.assertNotIn("error", res, f"Repeated tamper/repair stress cycle failed: {res.get('error')}")
        self.assertTrue(res.get("success"), "Expected stress cycles to complete successfully")
        print("[PASS] 4 consecutive rapid tamper/repair stress cycles in live browser verified")

    def test_09_r4_restore_system_baseline_reset_action(self):
        """Verify restore system baseline button resets state, restores initial 3 blocks, and clears errors"""
        res = self.eval_js("""
            (async () => {
                const btnReset = document.getElementById("btn-reset-ledger");
                if (btnReset) btnReset.click();

                await new Promise(r => setTimeout(r, 300));

                const chainLen = window.SimulatorState.ledgerChain.length;
                const b0 = window.SimulatorState.ledgerChain[0];
                const b1 = window.SimulatorState.ledgerChain[1];
                const b2 = window.SimulatorState.ledgerChain[2];

                const isB0Genesis = b0 && b0.index === 0 && b0.previousHash === "0000000000000000000000000000000000000000000000000000000000000000";
                const isB1Valid = b1 && b1.index === 1 && b1.previousHash === b0.hash;
                const isB2Valid = b2 && b2.index === 2 && b2.previousHash === b1.hash;

                const errorBanner = document.getElementById("ledger-status-error");
                const successBanner = document.getElementById("ledger-status-success");
                const isErrorHidden = errorBanner && errorBanner.classList.contains("hidden");
                const isSuccessVisible = successBanner && !successBanner.classList.contains("hidden");

                const placeholder = document.getElementById("ephemeral-placeholder");
                const isPlaceholderVisible = placeholder && !placeholder.classList.contains("hidden");

                return {
                    chainLen,
                    isB0Genesis,
                    isB1Valid,
                    isB2Valid,
                    isErrorHidden,
                    isSuccessVisible,
                    isPlaceholderVisible
                };
            })()
        """)
        self.assertEqual(res["chainLen"], 3, "Reset must restore chain length to 3")
        self.assertTrue(res["isB0Genesis"], "Block 0 must be Genesis block")
        self.assertTrue(res["isB1Valid"], "Block 1 must point to Block 0 hash")
        self.assertTrue(res["isB2Valid"], "Block 2 must point to Block 1 hash")
        self.assertTrue(res["isErrorHidden"], "Error banner must be hidden after reset")
        self.assertTrue(res["isSuccessVisible"], "Success banner must be visible after reset")
        self.assertTrue(res["isPlaceholderVisible"], "Ephemeral placeholder must be visible after reset")
        print("[PASS] System Baseline Reset action verified in live browser")

if __name__ == "__main__":
    unittest.main()
