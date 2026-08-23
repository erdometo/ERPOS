"""
Challenger 2: Headless Chrome CDP Live Browser Stress Suite
Deep verification of Cryptographic Ledger, ROI Calculator Sliders, and ReAct Concurrency in live Chrome.
"""

import os
import sys
import json
import time
import subprocess
import threading
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import asyncio
import websockets

PORT = 8097
CHROME_PORT = 9230
PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "public"))
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

class Challenger2CDPTest(unittest.TestCase):
    httpd = None
    server_thread = None
    chrome_proc = None
    ws_url = None

    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", PORT), QuietHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        print(f"[*] Challenger 2 HTTP Server started on http://127.0.0.1:{PORT}")

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

        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--remote-debugging-port={CHROME_PORT}",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--user-data-dir=" + os.path.join(os.environ.get("TEMP", "C:/Temp"), f"chrome_chal2_profile_{int(time.time())}"),
            f"http://127.0.0.1:{PORT}/index.html"
        ]
        cls.chrome_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[*] Headless Chrome launched (PID: {cls.chrome_proc.pid})")

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

    def test_01_genesis_block_64_zeros_and_chain_structure(self):
        """Test Genesis block 64-zero format invariant in live WebCrypto browser environment"""
        res = self.eval_js("""
            (async () => {
                await window.initLedger();
                const b0 = window.SimulatorState.ledgerChain[0];
                const prev = b0.previousHash;
                const isAllZeros = /^0{64}$/.test(prev);
                const hashLen = b0.hash.length;
                const isHashHex = /^[0-9a-f]{64}$/.test(b0.hash);
                return {
                    prevLen: prev.length,
                    isAllZeros,
                    hashLen,
                    isHashHex,
                    chainLen: window.SimulatorState.ledgerChain.length
                };
            })()
        """)
        self.assertEqual(res["prevLen"], 64, "Genesis previousHash must have length 64")
        self.assertTrue(res["isAllZeros"], "Genesis previousHash must be all zeros")
        self.assertEqual(res["hashLen"], 64, "Genesis hash must be 64-char SHA-256")
        self.assertTrue(res["isHashHex"], "Genesis hash must be lowercase hex")
        self.assertEqual(res["chainLen"], 3, "Initial chain length must be 3")
        print("[PASS] Genesis block 64-zero format verified in live Chrome WebCrypto")

    def test_02_ledger_block2_tamper_cascade_and_repair_live(self):
        """Test Block 2 tamper cascade, DOM crimson classes, and sequential repair in live browser"""
        res = self.eval_js("""
            (async () => {
                // Add 2 extra blocks to make 5 blocks
                await window.appendLedgerBlock("TRANSACTION_AUDIT_LOG_ENTRY_A");
                await window.appendLedgerBlock("TRANSACTION_AUDIT_LOG_ENTRY_B");

                // Tamper Block 2
                window.tamperLedgerBlock2();

                const container = document.getElementById("ledger-container");
                const html = container.innerHTML;

                const tamperedCards = container.querySelectorAll(".tampered-block-card").length;
                const cascadeCards = container.querySelectorAll(".cascade-invalid").length;
                const brokenArrows = container.querySelectorAll(".broken-arrow").length;
                const tamperScore = document.getElementById("zk-tamper-score").textContent;
                const merkleRoot = document.getElementById("zk-merkle-root").textContent;

                // Repair
                await window.repairAndRecalculateLedger();
                const repairedCards = container.querySelectorAll(".repaired-block-card").length;
                const remainingTampered = container.querySelectorAll(".tampered-block-card").length;
                const repairedScore = document.getElementById("zk-tamper-score").textContent;

                return {
                    tamperedCards,
                    cascadeCards,
                    brokenArrows,
                    tamperScore,
                    merkleRoot,
                    repairedCards,
                    remainingTampered,
                    repairedScore
                };
            })()
        """)
        self.assertEqual(res["tamperedCards"], 1, "Expected 1 .tampered-block-card")
        self.assertEqual(res["cascadeCards"], 2, "Expected 2 .cascade-invalid blocks downstream")
        self.assertGreaterEqual(res["brokenArrows"], 1, "Expected at least 1 .broken-arrow")
        self.assertIn("TAMPERED", res["tamperScore"], "Tamper score must indicate breach")
        self.assertEqual(res["merkleRoot"], "INVALIDATED", "Merkle root must be INVALIDATED")
        self.assertEqual(res["repairedCards"], 3, "Expected 3 repaired blocks (index 2, 3, 4)")
        self.assertEqual(res["remainingTampered"], 0, "Expected 0 tampered cards after repair")
        self.assertEqual(res["repairedScore"], "100%", "Tamper score must be 100% after repair")
        print("[PASS] Block 2 tamper cascade and sequential repair verified in live Chrome")

    def test_03_roi_sliders_live_boundary_and_math_interaction(self):
        """Test ROI sliders boundary dragging, live input events, and calculated outputs in DOM"""
        res = self.eval_js("""
            (() => {
                const hcSlider = document.getElementById("slider-headcount") || document.getElementById("headcount-slider");
                const revSlider = document.getElementById("slider-revenue") || document.getElementById("revenue-slider");
                const opsSlider = document.getElementById("slider-ops") || document.getElementById("ops-slider");

                // 1. Set to max values
                hcSlider.value = "10000";
                revSlider.value = "1000";
                opsSlider.value = "500";
                hcSlider.dispatchEvent(new Event("input"));
                revSlider.dispatchEvent(new Event("input"));
                opsSlider.dispatchEvent(new Event("input"));

                const maxSav = document.getElementById("calc-savings").textContent;
                const maxHrs = document.getElementById("calc-hours").textContent;
                const maxPay = document.getElementById("calc-payback").textContent;
                const maxRoi = document.getElementById("calc-roi").textContent;

                // 2. Set to min values
                hcSlider.value = "250";
                revSlider.value = "10";
                opsSlider.value = "10";
                hcSlider.dispatchEvent(new Event("input"));
                revSlider.dispatchEvent(new Event("input"));
                opsSlider.dispatchEvent(new Event("input"));

                const minSav = document.getElementById("calc-savings").textContent;
                const minHrs = document.getElementById("calc-hours").textContent;
                const minPay = document.getElementById("calc-payback").textContent;
                const minRoi = document.getElementById("calc-roi").textContent;

                return {
                    maxSav, maxHrs, maxPay, maxRoi,
                    minSav, minHrs, minPay, minRoi
                };
            })()
        """)
        # At max (500 ops, 1000 rev): directLabor=500*42000=21M, errorSavings=1000*6500=6.5M, consulting=450k -> total=27.95M
        # paybackDays = Math.max(18, Math.round(45 - (500 / 30))) = Math.max(18, 28) = 28
        self.assertNotIn("NaN", res["maxSav"], "Max savings must not contain NaN")
        self.assertIn("120,000 hrs", res["maxHrs"].replace(".", ","), "Max hours reclaimed should be 120,000 hrs")
        self.assertIn("28 Days", res["maxPay"], "Payback days for 500 ops staff should be 28 Days")
        self.assertIn("770%", res["maxRoi"], "Max net ROI should be 770%")

        self.assertNotIn("NaN", res["minSav"], "Min savings must not contain NaN")
        self.assertIn("2,400 hrs", res["minHrs"].replace(".", ","), "Min hours reclaimed should be 2,400 hrs")
        self.assertIn("45 Days", res["minPay"], "Min payback days should be 45 Days")
        self.assertIn("325%", res["minRoi"], "Min net ROI should be 325%")
        print("[PASS] ROI Sliders live boundary and math interaction verified in live Chrome")

    def test_04_react_rapid_concurrency_stress_in_dom(self):
        """Stress-test rapid scenario clicking and verify no DOM clobbering or uncaught exceptions"""
        res = self.eval_js("""
            (async () => {
                const scenarios = ["audit", "inventory_stockout", "sql_financial", "rbac_quarantine"];
                
                // Rapidly trigger all 4 scenario buttons in 20ms intervals
                for (let i = 0; i < 4; i++) {
                    const btn = document.querySelector(`.btn-scenario[data-scenario='${scenarios[i]}']`);
                    if (btn) btn.click();
                    await new Promise(r => setTimeout(r, 20));
                }

                // Wait for the active processing scenario to complete
                while (window.SimulatorState.isProcessing) {
                    await new Promise(r => setTimeout(r, 100));
                }
                await new Promise(r => setTimeout(r, 200));

                const term = document.getElementById("terminal-container");
                const uiContainer = document.getElementById("ephemeral-ui-container");
                const lineCount = term ? term.querySelectorAll(".terminal-line").length : 0;
                const hasEphemeralCard = uiContainer ? uiContainer.innerHTML.includes("ephemeral-card") || uiContainer.innerHTML.includes("ephemeral-header") || uiContainer.innerHTML.includes("kpi-grid") : false;

                return {
                    lineCount,
                    hasEphemeralCard,
                    activeScenario: window.SimulatorState.activeScenario,
                    isProcessing: window.SimulatorState.isProcessing
                };
            })()
        """)
        self.assertGreater(res["lineCount"], 0, "Terminal lines must be rendered")
        self.assertTrue(res["hasEphemeralCard"], "Ephemeral UI dashboard must be rendered")
        self.assertFalse(res["isProcessing"], "SimulatorState.isProcessing must be false upon completion")
        print(f"[PASS] ReAct rapid concurrency stress (Active Scenario: {res['activeScenario']}, Terminal Lines: {res['lineCount']})")

if __name__ == "__main__":
    unittest.main()
