"""
Challenger 1: Deep Live Browser CDP Adversarial Stress Suite for UI & Transport Controls
Executes in real headless Google Chrome with live DOM, JS Engine, and CDP console event monitors.
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

class Challenger1CDPStressTest(unittest.TestCase):
    httpd = None
    server_thread = None
    chrome_proc = None
    ws_url = None
    console_errors = []

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
        profile_dir = os.path.join(os.environ.get("TEMP", "C:/Temp"), "chrome_test_profile_challenger1")
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

        # 3. Wait for Chrome CDP to become ready
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
            raise RuntimeError("Failed to connect to Chrome CDP")

        # 4. Wait for DOM ready
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
        async def _exec():
            async with websockets.connect(cls.ws_url, max_size=10_000_000) as ws:
                for _ in range(50):
                    await asyncio.sleep(0.1)
                    await ws.send(json.dumps({
                        "id": 1,
                        "method": "Runtime.evaluate",
                        "params": {
                            "expression": "document.readyState === 'complete' && typeof window.SAGStudioEngine !== 'undefined'",
                            "returnByValue": True
                        }
                    }))
                    resp = await ws.recv()
                    data = json.loads(resp)
                    if data.get("result", {}).get("result", {}).get("value") is True:
                        return
        asyncio.run(_exec())

    def cdp_eval(self, js_expression):
        async def _exec():
            async with websockets.connect(self.ws_url, max_size=10_000_000) as ws:
                # Enable Runtime console events
                await ws.send(json.dumps({"id": 100, "method": "Runtime.enable"}))
                await ws.recv()
                msg_id = int(time.time() * 1000) % 1000000
                await ws.send(json.dumps({
                    "id": msg_id,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": js_expression,
                        "returnByValue": True,
                        "awaitPromise": True
                    }
                }))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == msg_id:
                        res = data.get("result", {})
                        if "exceptionDetails" in res:
                            raise RuntimeError(f"JS Exception: {res['exceptionDetails']}")
                        return res.get("result", {}).get("value")
                    elif data.get("method") == "Runtime.consoleAPICalled":
                        c_type = data.get("params", {}).get("type")
                        if c_type == "error":
                            self.console_errors.append(data.get("params", {}).get("args", []))
        return asyncio.run(_exec())

    def test_1_rapid_play_pause_clicking_stress(self):
        """Stress test: Rapidly clicking Play/Pause button 60 times via live DOM dispatch"""
        script = """
        (() => {
          const btn = document.getElementById('btn-dag-play') || document.getElementById('btn-play-pause');
          if (!btn) throw new Error('Play button not found');
          
          let initialState = window.SAGStudioEngine.isPlaying;
          for (let i = 0; i < 60; i++) {
            btn.click();
          }
          return {
            initialState,
            finalState: window.SAGStudioEngine.isPlaying,
            buttonHasPlayingClass: btn.classList.contains('playing'),
            timerActive: window.SAGStudioEngine.playbackTimer !== null
          };
        })()
        """
        res = self.cdp_eval(script)
        self.assertEqual(res["initialState"], res["finalState"])
        if not res["finalState"]:
            self.assertFalse(res["buttonHasPlayingClass"])
            self.assertFalse(res["timerActive"])
        print("[PASS] Rapid Play/Pause live DOM click spam (60 clicks) passed.")

    def test_2_boundary_stepping_stress(self):
        """Stress test: Spamming Step Next and Step Prev buttons at the extreme boundaries"""
        script = """
        (() => {
          const btnNext = document.getElementById('btn-dag-next') || document.getElementById('btn-step-next');
          const btnPrev = document.getElementById('btn-dag-prev') || document.getElementById('btn-step-prev');
          const counter = document.getElementById('dag-step-counter');

          // Reset to 0
          window.SAGStudioEngine.goToStep(0);

          // Click Prev 50 times at min boundary (0)
          for (let i = 0; i < 50; i++) {
            btnPrev.click();
          }
          const minStep = window.SAGStudioEngine.currentStepIndex;
          const minText = counter.textContent;

          // Click Next 100 times to reach and exceed max boundary (4)
          for (let i = 0; i < 100; i++) {
            btnNext.click();
          }
          const maxStep = window.SAGStudioEngine.currentStepIndex;
          const maxText = counter.textContent;

          // Click Prev 50 times again to reach 0
          for (let i = 0; i < 50; i++) {
            btnPrev.click();
          }
          const finalMinStep = window.SAGStudioEngine.currentStepIndex;

          return { minStep, minText, maxStep, maxText, finalMinStep };
        })()
        """
        res = self.cdp_eval(script)
        self.assertEqual(res["minStep"], 0)
        self.assertIn("t0", res["minText"])
        self.assertEqual(res["maxStep"], 4)
        self.assertIn("t4", res["maxText"])
        self.assertEqual(res["finalMinStep"], 0)
        print("[PASS] Transport boundary stepping (50 underflow, 100 overflow clicks) verified.")

    def test_3_tsafe_jump_and_reset_stress(self):
        """Stress test: Alternating Jump to t_safe and Reset across multiple benchmarks"""
        script = """
        (() => {
          const btnSafe = document.getElementById('btn-dag-tsafe') || document.getElementById('btn-jump-safe');
          const btnReset = document.getElementById('btn-dag-reset') || document.getElementById('btn-reset');
          const results = [];

          const benchmarks = ['swe-bench', 'intercode', 'webarena', 'alfworld', 'toolbench', 'atif'];
          benchmarks.forEach(bId => {
            window.SAGStudioEngine.loadBenchmark(bId);
            
            // From step 0, jump to safe
            btnSafe.click();
            const safeStep = window.SAGStudioEngine.currentStepIndex;
            
            // Reset to step 0
            btnReset.click();
            const resetStep = window.SAGStudioEngine.currentStepIndex;
            
            // Step to 4, then jump to safe
            window.SAGStudioEngine.goToStep(4);
            btnSafe.click();
            const safeStepFrom4 = window.SAGStudioEngine.currentStepIndex;

            results.push({ bId, safeStep, resetStep, safeStepFrom4 });
          });

          return results;
        })()
        """
        results = self.cdp_eval(script)
        for r in results:
            self.assertEqual(r["safeStep"], 2, f"Failed for {r['bId']}")
            self.assertEqual(r["resetStep"], 0, f"Failed reset for {r['bId']}")
            self.assertEqual(r["safeStepFrom4"], 2, f"Failed safe from 4 for {r['bId']}")
        print("[PASS] Jump to t_safe and Reset stress across all 6 benchmarks verified.")

    def test_4_scrubber_rapid_scrub_stress(self):
        """Stress test: Timeline scrubber input dispatch with boundary, normal, and out-of-range values"""
        script = """
        (() => {
          const scrubber = document.getElementById('dag-timeline-scrubber') || document.getElementById('trajectory-scrubber');
          const valuesToTest = [-2, 0, 1, 2, 3, 4, 10, 2, 0, 4];
          const observedSteps = [];

          valuesToTest.forEach(v => {
            scrubber.value = String(v);
            scrubber.dispatchEvent(new Event('input', { bubbles: true }));
            observedSteps.push(window.SAGStudioEngine.currentStepIndex);
          });

          return observedSteps;
        })()
        """
        observed = self.cdp_eval(script)
        expected = [0, 0, 1, 2, 3, 4, 4, 2, 0, 4]
        self.assertEqual(observed, expected)
        print("[PASS] Scrubber rapid dispatch & boundary clamping verified.")

    def test_5_speed_presets_and_mode_switching_stress(self):
        """Stress test: Rapid clicking all speed buttons and bloom/pulse mode toggles"""
        script = """
        (() => {
          const speedBtns = document.querySelectorAll('#dag-speed-presets .btn-speed');
          const btnBloom = document.getElementById('btn-mode-bloom');
          const btnPulse = document.getElementById('btn-mode-pulse');

          const speedResults = [];
          speedBtns.forEach(btn => {
            btn.click();
            speedResults.push({
              targetSpeed: btn.getAttribute('data-speed'),
              engineSpeed: window.SAGStudioEngine.playbackSpeed,
              isActive: btn.classList.contains('active')
            });
          });

          // Test Mode Toggling 50 times
          let modeResults = [];
          for (let i = 0; i < 50; i++) {
            if (i % 2 === 0) {
              if (btnBloom) btnBloom.click();
            } else {
              if (btnPulse) btnPulse.click();
            }
          }
          modeResults.push({
            finalMode: window.SAGStudioEngine.playbackMode,
            bloomActive: btnBloom ? btnBloom.classList.contains('active') : null,
            pulseActive: btnPulse ? btnPulse.classList.contains('active') : null
          });

          return { speedResults, modeResults };
        })()
        """
        res = self.cdp_eval(script)
        for s in res["speedResults"]:
            self.assertAlmostEqual(float(s["targetSpeed"]), s["engineSpeed"])
            self.assertTrue(s["isActive"])
        self.assertEqual(res["modeResults"][0]["finalMode"], "pulse")
        self.assertTrue(res["modeResults"][0]["pulseActive"])
        self.assertFalse(res["modeResults"][0]["bloomActive"])
        print("[PASS] Speed presets and bloom/pulse live toggling verified.")

    def test_6_scenario_switcher_stress(self):
        """Stress test: Sequential scenario switching across all 4 sandboxes with mutex verification"""
        script = """
        (async () => {
          // Wait for any prior processing to settle
          while (window.SimulatorState.isProcessing) {
            await new Promise(r => setTimeout(r, 50));
          }

          const scKeys = ['audit', 'inventory_stockout', 'sql_financial', 'rbac_quarantine'];
          const history = [];

          for (const key of scKeys) {
            // Find button
            const btn = document.querySelector(`.scenario-btn[data-scenario='${key}']`) ||
                        document.querySelector(`.btn-scenario[data-scenario='${key}']`);
            if (!btn) continue;
            
            // Trigger click
            btn.click();
            
            // Wait for stream to complete
            while (window.SimulatorState.isProcessing) {
              await new Promise(r => setTimeout(r, 40));
            }

            history.push({
              key,
              isActive: btn.classList.contains('active'),
              activeScenario: window.SimulatorState.activeScenario,
              hasEphemeralCard: document.querySelector('.ephemeral-card') !== null
            });
          }

          return history;
        })()
        """
        history = self.cdp_eval(script)
        self.assertEqual(len(history), 4)
        for h in history:
            self.assertEqual(h["key"], h["activeScenario"])
            self.assertTrue(h["isActive"])
            self.assertTrue(h["hasEphemeralCard"])
        print("[PASS] Scenario switcher sequential streaming and ephemeral card compilation verified.")

    def test_7_modal_dialog_open_close_spam_stress(self):
        """Stress test: Spamming modal open buttons, close buttons, and backdrop clicks 40 times"""
        script = """
        (() => {
          const modal = document.getElementById('briefing-modal') || document.getElementById('investor-modal');
          const btnOpen = document.getElementById('btn-open-briefing');
          const btnClose = document.getElementById('modal-close-btn');
          const btnOpenCta = document.getElementById('btn-open-briefing-cta');

          if (!modal || !btnOpen || !btnClose) {
            throw new Error('Modal elements missing');
          }

          let transitions = 0;
          for (let i = 0; i < 40; i++) {
            // Open via nav or CTA button
            if (i % 2 === 0) {
              btnOpen.click();
            } else if (btnOpenCta) {
              btnOpenCta.click();
            } else {
              btnOpen.click();
            }
            if (!modal.classList.contains('hidden')) transitions++;

            // Close via close button or backdrop click
            if (i % 2 === 0) {
              btnClose.click();
            } else {
              modal.dispatchEvent(new MouseEvent('click', { bubbles: true, target: modal }));
            }
            if (modal.classList.contains('hidden')) transitions++;
          }

          return {
            transitions,
            isClosed: modal.classList.contains('hidden')
          };
        })()
        """
        res = self.cdp_eval(script)
        self.assertEqual(res["transitions"], 80)
        self.assertTrue(res["isClosed"])
        print("[PASS] Modal open/close/backdrop spamming (80 state transitions) verified.")

    def test_8_modal_form_submission_and_toast(self):
        """Stress test: Modal form submission, success box render, and toast feedback"""
        script = """
        (() => {
          const modal = document.getElementById('briefing-modal') || document.getElementById('investor-modal');
          const btnOpen = document.getElementById('btn-open-briefing');
          const form = document.getElementById('briefing-form');
          const successBox = document.getElementById('briefing-success');

          // Open modal
          btnOpen.click();
          const wasOpened = !modal.classList.contains('hidden');

          // Submit form
          form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
          const formHiddenAfterSubmit = form.classList.contains('hidden');
          const successShownAfterSubmit = successBox ? !successBox.classList.contains('hidden') : true;

          // Check toast container
          const toasts = document.querySelectorAll('.toast-item');
          const latestToast = toasts.length > 0 ? toasts[toasts.length - 1].textContent : '';

          return { wasOpened, formHiddenAfterSubmit, successShownAfterSubmit, latestToast };
        })()
        """
        res = self.cdp_eval(script)
        self.assertTrue(res["wasOpened"])
        self.assertTrue(res["formHiddenAfterSubmit"])
        self.assertTrue(res["successShownAfterSubmit"])
        self.assertIn("Briefing Request", res["latestToast"])
        print("[PASS] Modal form submission and toast feedback verified.")

    def test_9_contact_email_copy_button(self):
        """Stress test: Contact 1-click email copy button and toast dispatch"""
        script = """
        (async () => {
          const btnCopy = document.getElementById('btn-copy-email');
          if (!btnCopy) throw new Error('btn-copy-email not found');
          btnCopy.click();
          
          await new Promise(r => setTimeout(r, 150));
          
          const toasts = document.querySelectorAll('.toast-item');
          const latestToast = toasts.length > 0 ? toasts[toasts.length - 1].textContent : '';
          return {
            buttonFound: true,
            toastCount: toasts.length,
            toastText: latestToast
          };
        })()
        """
        res = self.cdp_eval(script)
        self.assertTrue(res["buttonFound"])
        self.assertGreater(res["toastCount"], 0)
        self.assertIn("info@omnigateos.com", res["toastText"])
        print("[PASS] Contact email 1-click copy and toast notification verified.")

if __name__ == "__main__":
    unittest.main()
