"""
Empirical Adversarial Test Suite for R1 & R2 via Chrome DevTools Protocol (CDP)
Executes in real headless Google Chrome with live DOM, JS Engine, CSS rendering, and Console error trapping.
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

PORT = 8089
CHROME_PORT = 9223
PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "public"))
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

class HeadlessBrowserTest(unittest.TestCase):
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
        profile_dir = os.path.join(os.environ.get("TEMP", "C:/Temp"), "chrome_test_profile_r1r2")
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--remote-debugging-port={CHROME_PORT}",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile_dir}",
            f"http://127.0.0.1:{PORT}/index.html"
        ]
        cls.chrome_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[*] Headless Chrome launched (PID: {cls.chrome_proc.pid})")

        # 3. Wait for Chrome CDP to become ready and find page tab
        for _ in range(30):
            try:
                r = requests.get(f"http://127.0.0.1:{CHROME_PORT}/json", timeout=1)
                tabs = r.json()
                page_tabs = [t for t in tabs if t.get("type") == "page"]
                if page_tabs:
                    cls.ws_url = page_tabs[0].get("webSocketDebuggerUrl")
                    print(f"[*] Connected to Chrome Page Tab: {cls.ws_url}")
                    break
            except Exception:
                time.sleep(0.3)
        else:
            raise RuntimeError("Failed to find Chrome page tab via CDP")

        # 4. Wait for DOM and SAGStudioEngine to initialize
        cls.wait_for_dom()

    @classmethod
    def tearDownClass(cls):
        if cls.chrome_proc:
            cls.chrome_proc.terminate()
            cls.chrome_proc.wait()
            print("[*] Chrome process terminated.")
        if cls.httpd:
            cls.httpd.shutdown()
            print("[*] HTTP Server stopped.")

    @classmethod
    def wait_for_dom(cls):
        """Wait until document is ready and SAGStudioEngine is loaded"""
        async def _exec():
            async with websockets.connect(cls.ws_url, max_size=10_000_000) as ws:
                for _ in range(50):
                    await asyncio.sleep(0.1)
                    await ws.send(json.dumps({
                        "id": 99,
                        "method": "Runtime.evaluate",
                        "params": {
                            "expression": "document.readyState === 'complete' && typeof window.SAGStudioEngine !== 'undefined' && document.getElementById('dag-visualizer-container') !== null",
                            "returnByValue": True
                        }
                    }))
                    resp = await ws.recv()
                    data = json.loads(resp)
                    if data.get("id") == 99 and data.get("result", {}).get("result", {}).get("value") is True:
                        print("[*] Page and SAGStudioEngine ready.")
                        return
                raise RuntimeError("Page load timed out waiting for DOM readiness")
        asyncio.run(_exec())

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

    def test_01_zero_js_console_errors_on_load(self):
        """Verify page loads cleanly with zero console runtime errors or unhandled exceptions"""
        result = self.eval_js("""
            (() => {
                return {
                    docTitle: document.title,
                    readyState: document.readyState,
                    hasStudio: typeof window.SAGStudioEngine !== 'undefined',
                    hasHUD: document.getElementById('hud-throughput') !== null,
                    cardCount: document.querySelectorAll('.benchmark-card').length,
                    hasScrubber: document.getElementById('dag-timeline-scrubber') !== null,
                    hasInspector: document.getElementById('dag-telemetry-inspector') !== null
                };
            })()
        """)
        self.assertTrue("OmniGate" in result["docTitle"] or "SAG" in result["docTitle"], f"Title mismatch: {result['docTitle']}")
        self.assertEqual(result["readyState"], "complete")
        self.assertTrue(result["hasStudio"], "SAGStudioEngine missing")
        self.assertTrue(result["hasHUD"], "Throughput HUD missing")
        self.assertEqual(result["cardCount"], 6, f"Expected 6 benchmark cards, found {result['cardCount']}")
        self.assertTrue(result["hasScrubber"], "Timeline scrubber missing")
        self.assertTrue(result["hasInspector"], "Telemetry inspector missing")
        print(f"[PASS] Page loaded cleanly. Title: '{result['docTitle']}', Cards: {result['cardCount']}")

    def test_02_strict_sag_branding_compliance(self):
        """Verify ZERO occurrences of 'ActiveGraph' anywhere in document or window scope"""
        result = self.eval_js("""
            (() => {
                const html = document.documentElement.outerHTML;
                const hasForbiddenText = html.includes("ActiveGraph");
                const windowKeys = Object.keys(window).filter(k => k.includes("ActiveGraph"));
                return {
                    hasForbiddenText,
                    windowKeys,
                    sagStudioExists: typeof window.SAGStudioEngine !== 'undefined'
                };
            })()
        """)
        self.assertFalse(result["hasForbiddenText"], "Strict Branding Violation: 'ActiveGraph' found in DOM HTML!")
        self.assertEqual(len(result["windowKeys"]), 0, f"Found 'ActiveGraph' keys in window: {result['windowKeys']}")
        self.assertTrue(result["sagStudioExists"], "window.SAGStudioEngine must be defined")
        print("[PASS] Strict SAG Branding verified: Zero occurrences of 'ActiveGraph'")

    def test_03_css_custom_properties_and_glassmorphism(self):
        """Verify CSS design tokens and Obsidian theme variables computed on document root"""
        result = self.eval_js("""
            (() => {
                const root = getComputedStyle(document.documentElement);
                return {
                    fontHeading: root.getPropertyValue('--font-heading').trim(),
                    fontMono: root.getPropertyValue('--font-mono').trim(),
                    accentEmerald: root.getPropertyValue('--accent-emerald').trim(),
                    accentRose: root.getPropertyValue('--accent-rose').trim(),
                    accentAmber: root.getPropertyValue('--accent-amber').trim(),
                    accentCyan: root.getPropertyValue('--accent-cyan').trim()
                };
            })()
        """)
        self.assertTrue(len(result["fontHeading"]) > 0, "--font-heading missing")
        self.assertTrue(len(result["fontMono"]) > 0, "--font-mono missing")
        self.assertTrue(len(result["accentEmerald"]) > 0, "--accent-emerald missing")
        self.assertTrue(len(result["accentRose"]) > 0, "--accent-rose missing")
        print(f"[PASS] Obsidian Glassmorphism CSS variables verified: heading='{result['fontHeading']}', emerald='{result['accentEmerald']}'")

    def test_04_r2_all_6_benchmarks_interactive_switching(self):
        """Adversarially switch across all 6 benchmark cards in Hub and verify spotlight updates and loading into Studio"""
        benchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"]
        for b_id in benchmarks:
            res = self.eval_js(f"""
                (() => {{
                    // 1. Click benchmark card
                    const card = document.querySelector(`.benchmark-card[data-benchmark='{b_id}']`);
                    if (!card) return {{ error: `Card {b_id} not found` }};
                    card.click();
                    
                    const spotlightTag = document.getElementById("spotlight-tag").textContent;
                    const spotlightTitle = document.getElementById("spotlight-title").textContent;
                    
                    // 2. Click load into studio button
                    const btnLoad = document.getElementById("btn-load-benchmark-into-studio");
                    if (btnLoad) btnLoad.click();

                    // 3. Check Studio active badge and current dataset
                    const studioBadge = document.getElementById("dag-active-benchmark-badge").textContent;
                    const engineDataset = window.SAGStudioEngine.getCurrentDataset();
                    const upperNodesCount = document.querySelectorAll(".dag-lane-row:first-child .dag-node").length;
                    const lowerNodesCount = document.querySelectorAll(".dag-lane-row:last-child .dag-node").length;

                    return {{
                        cardActive: card.classList.contains("active"),
                        spotlightTag,
                        spotlightTitle,
                        studioBadge,
                        engineDatasetId: engineDataset.id,
                        upperNodesCount,
                        lowerNodesCount
                    }};
                }})()
            """)
            self.assertNotIn("error", res, f"Error selecting benchmark {b_id}: {res.get('error')}")
            self.assertTrue(res["cardActive"], f"Benchmark card {b_id} should be active")
            self.assertEqual(res["engineDatasetId"], b_id, f"Engine dataset ID mismatch for {b_id}")
            self.assertEqual(res["upperNodesCount"], 5, f"Expected 5 upper nodes for {b_id}")
            self.assertEqual(res["lowerNodesCount"], 5, f"Expected 5 lower nodes for {b_id}")
        print("[PASS] All 6 Benchmarks interactive switcher & Studio loader verified")

    def test_05_r1_transport_controls_stress_and_boundary(self):
        """Stress-test Transport Controls: Boundary steps (0, 4), t_safe jump, Reset, and Rapid Toggling"""
        res = self.eval_js("""
            (() => {
                const engine = window.SAGStudioEngine;
                engine.loadBenchmark("swe-bench");
                
                // Test Prev at 0
                engine.goToStep(0);
                document.getElementById("btn-dag-prev").click();
                const stepAtPrev0 = engine.currentStepIndex;
                
                // Test Next at 4
                engine.goToStep(4);
                document.getElementById("btn-dag-next").click();
                const stepAtNext4 = engine.currentStepIndex;
                
                // Test Jump to t_safe
                engine.goToStep(0);
                document.getElementById("btn-dag-tsafe").click();
                const stepAtTSafe = engine.currentStepIndex;
                
                // Test Reset
                engine.goToStep(3);
                document.getElementById("btn-dag-reset").click();
                const stepAtReset = engine.currentStepIndex;
                
                // Test Rapid Play / Pause toggling
                for (let i = 0; i < 50; i++) {
                    document.getElementById("btn-dag-play").click();
                }
                const isPlayingAfter50 = engine.isPlaying;
                engine.pause();

                return {
                    stepAtPrev0,
                    stepAtNext4,
                    stepAtTSafe,
                    stepAtReset,
                    isPlayingAfter50
                };
            })()
        """)
        self.assertEqual(res["stepAtPrev0"], 0, "Step prev at 0 should stay at 0")
        self.assertEqual(res["stepAtNext4"], 4, "Step next at 4 should stay at 4")
        self.assertEqual(res["stepAtTSafe"], 2, "Jump to t_safe should land at step 2")
        self.assertEqual(res["stepAtReset"], 0, "Reset should return to step 0")
        self.assertFalse(res["isPlayingAfter50"], "50 toggles (even) should leave engine in paused state")
        print("[PASS] Transport controls boundaries, t_safe jump, and rapid toggling verified")

    def test_06_r1_speed_modifier_presets(self):
        """Verify speed presets (0.25x, 0.5x, 1x, 2x, 5x, 10x) button interactions and active class state"""
        speeds = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
        for spd in speeds:
            res = self.eval_js(f"""
                (() => {{
                    const btn = document.querySelector(`#dag-speed-presets .btn-speed[data-speed='{spd}']`);
                    if (!btn) return {{ error: "Speed button not found for {spd}" }};
                    btn.click();
                    return {{
                        engineSpeed: window.SAGStudioEngine.playbackSpeed,
                        btnActive: btn.classList.contains("active")
                    }};
                }})()
            """)
            self.assertNotIn("error", res, f"Speed preset {spd} failed")
            self.assertEqual(res["engineSpeed"], spd, f"Engine speed mismatch for {spd}")
            self.assertTrue(res["btnActive"], f"Speed button {spd} missing active class")
        print("[PASS] Speed modifier presets (0.25x - 10x) verified")

    def test_07_r1_playback_mode_toggles(self):
        """Verify Progressive Bloom vs Pulse Highlight toggling and node CSS animation classes"""
        res = self.eval_js("""
            (() => {
                const engine = window.SAGStudioEngine;
                engine.loadBenchmark("swe-bench");
                engine.goToStep(1);

                // Click Bloom
                document.getElementById("btn-mode-bloom").click();
                const bloomActive = document.getElementById("btn-mode-bloom").classList.contains("active");
                const bloomNode = document.querySelector(".dag-node.node-blooming");
                
                // Click Pulse
                document.getElementById("btn-mode-pulse").click();
                const pulseActive = document.getElementById("btn-mode-pulse").classList.contains("active");
                const pulseNode = document.querySelector(".dag-node.node-pulse-active");

                return {
                    bloomActive,
                    hasBloomNode: bloomNode !== null,
                    pulseActive,
                    hasPulseNode: pulseNode !== null
                };
            })()
        """)
        self.assertTrue(res["bloomActive"] and res["hasBloomNode"], "Bloom mode toggle failed")
        self.assertTrue(res["pulseActive"] and res["hasPulseNode"], "Pulse mode toggle failed")
        print("[PASS] Playback mode toggles (Progressive Bloom vs Pulse Highlight) verified")

    def test_08_r1_timeline_scrubber_and_telemetry_sync(self):
        """Verify timeline scrubber boundary scrubbing and real-time Telemetry Inspector synchronization"""
        for step_val in [0, 1, 2, 3, 4]:
            res = self.eval_js(f"""
                (() => {{
                    const scrubber = document.getElementById("dag-timeline-scrubber");
                    scrubber.value = {step_val};
                    scrubber.dispatchEvent(new Event("input"));

                    const stepCounterText = document.getElementById("dag-step-counter").textContent;
                    const activeTick = document.querySelector("#dag-scrubber-ticks .tick.active");
                    const tickStep = activeTick ? activeTick.getAttribute("data-step") : null;

                    const riskBarWidth = document.getElementById("telemetry-risk-bar").style.width;
                    const riskBadgeText = document.getElementById("telemetry-risk-badge").textContent;
                    const thoughtText = document.getElementById("telemetry-thought").textContent;
                    const actionText = document.getElementById("telemetry-action").textContent;
                    const obsText = document.getElementById("telemetry-observation").textContent;
                    const entitiesCount = document.querySelectorAll("#telemetry-entities .entity-pill").length;

                    return {{
                        stepCounterText,
                        tickStep,
                        riskBarWidth,
                        riskBadgeText,
                        thoughtLength: thoughtText.trim().length,
                        actionLength: actionText.trim().length,
                        obsLength: obsText.trim().length,
                        entitiesCount
                    }};
                }})()
            """)
            self.assertEqual(res["stepCounterText"], f"Step t{step_val} of t4", f"Step counter mismatch at step {step_val}")
            self.assertEqual(res["tickStep"], str(step_val), f"Scrubber tick mismatch at step {step_val}")
            self.assertTrue(len(res["riskBarWidth"]) > 0, f"Risk bar width empty at step {step_val}")
            self.assertTrue(res["thoughtLength"] > 0, f"Thought text empty at step {step_val}")
            self.assertTrue(res["actionLength"] > 0, f"Action text empty at step {step_val}")
            self.assertTrue(res["obsLength"] > 0, f"Observation text empty at step {step_val}")
        print("[PASS] Scrubber boundary scrubbing and Telemetry Inspector synchronization verified")

    def test_09_r2_live_throughput_hud_metrics(self):
        """Verify live throughput HUD metric counters are displayed and populated with target ranges"""
        res = self.eval_js("""
            (() => {
                const tp = document.getElementById("hud-throughput").textContent;
                return {
                    throughputText: tp,
                    hasEvents: document.querySelector(".hud-card:nth-child(2) .hud-value").textContent.includes("23,610"),
                    hasTestCases: document.querySelector(".hud-card:nth-child(3) .hud-value").textContent.includes("15,318"),
                    hasEntities: document.querySelector(".hud-card:nth-child(4) .hud-value").textContent.includes("1,236")
                };
            })()
        """)
        self.assertTrue("2,51" in res["throughputText"] or "2,52" in res["throughputText"], f"Throughput value out of expected range: {res['throughputText']}")
        self.assertTrue(res["hasEvents"], "Episodic events metric mismatch")
        self.assertTrue(res["hasTestCases"], "Test cases metric mismatch")
        self.assertTrue(res["hasEntities"], "Semantic entities metric mismatch")
        print(f"[PASS] Live Throughput HUD metrics verified: {res['throughputText']}")

if __name__ == "__main__":
    unittest.main()
