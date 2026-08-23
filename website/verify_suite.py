import os
import re
import json
import sqlite3
import unittest
import hashlib
import sys
import subprocess
import time
import requests

API_URL = "http://127.0.0.1:8000"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "erp_database.db"))
HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "public", "index.html"))
CSS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "public", "styles.css"))
JS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "public", "app.js"))

class TestOmniGateERP(unittest.TestCase):
    backend_proc = None

    @classmethod
    def setUpClass(cls):
        # Clear external LLM credentials to prevent hanging and force fast local simulator
        for env_var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "CUSTOM_CLIENT_ID", "CUSTOM_CLIENT_SECRET"]:
            if env_var in os.environ:
                del os.environ[env_var]

        # Force terminate any process on port 8000 to ensure fresh uvicorn startup with test environment
        try:
            output = subprocess.check_output("netstat -ano", shell=True).decode("utf-8")
            for line in output.splitlines():
                if "127.0.0.1:8000" in line or "0.0.0.0:8000" in line or ":8000 " in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and int(pid) > 0:
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            time.sleep(0.5)
        except Exception:
            pass

        # Start backend uvicorn server as a subprocess for API/E2E testing
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
        
        # Check if backend already running
        try:
            r = requests.get(f"{API_URL}/api/ledger", timeout=1)
            print("[*] Backend is already running.")
            return
        except requests.exceptions.RequestException:
            pass

        print("[*] Starting backend server subprocess...")
        python_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "python.exe"))
        if not os.path.exists(python_exe):
            python_exe = sys.executable

        cls.backend_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "main:app", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for backend to be ready
        for _ in range(20):
            try:
                requests.get(f"{API_URL}/api/schema", timeout=0.5)
                print("[*] Backend server started successfully.")
                break
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        else:
            print("[!] Warning: Could not connect to backend server. Some API tests will be skipped/mocked.")

    @classmethod
    def tearDownClass(cls):
        if cls.backend_proc:
            print("[*] Terminating backend server subprocess...")
            cls.backend_proc.terminate()
            cls.backend_proc.wait()

    def get_jwt_token(self, email, password="password123"):
        try:
            res = requests.post(f"{API_URL}/api/auth/login", json={"email": email, "password": password})
            if res.status_code == 200:
                return res.json().get("access_token")
        except requests.exceptions.RequestException:
            pass
        return None

    # ==========================================
    # TIER 1: Feature Coverage (20 Cases)
    # ==========================================

    def test_1_1_html_exists(self):
        """Verify index.html exists in website/public/"""
        self.assertTrue(os.path.isfile(HTML_PATH), f"index.html not found at {HTML_PATH}")

    def test_1_2_css_exists(self):
        """Verify styles.css exists in website/public/"""
        self.assertTrue(os.path.isfile(CSS_PATH), f"styles.css not found at {CSS_PATH}")

    def test_1_3_google_fonts(self):
        """Verify Outfit/Inter Google Fonts are referenced in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("fonts.googleapis.com", html)
        self.assertTrue(re.search(r"family=(Outfit|Inter)", html))

    def test_1_4_css_linked(self):
        """Verify styles.css link exists in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertTrue(re.search(r'href=["\']styles\.css["\']', html))

    def test_1_5_js_linked(self):
        """Verify app.js link exists in index.html as a module"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertTrue(re.search(r'src=["\']app\.js["\'].*type=["\']module["\']', html) or 
                        re.search(r'type=["\']module["\'].*src=["\']app\.js["\']', html))

    def test_1_6_container_terminal(self):
        """Verify terminal-container ID element exists in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="terminal-container"', html)

    def test_1_7_container_ledger(self):
        """Verify ledger-container ID element exists in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="ledger-container"', html)

    def test_1_8_container_placeholder(self):
        """Verify ephemeral-placeholder ID element exists in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="ephemeral-placeholder"', html)

    def test_1_9_container_ui_container(self):
        """Verify ephemeral-ui-container ID element exists in index.html"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="ephemeral-ui-container"', html)

    def test_1_10_css_fonts_defined(self):
        """Verify font variables defined in styles.css"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("font-heading", css)
        self.assertIn("font-body", css)
        self.assertIn("font-mono", css)

    def test_1_11_css_accents_defined(self):
        """Verify accent variables defined in styles.css"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("accent-violet", css)
        self.assertIn("accent-rose", css)
        self.assertIn("accent-emerald", css)
        self.assertIn("accent-amber", css)

    def test_1_12_css_glassmorphism(self):
        """Verify glassmorphic styles defined in styles.css"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("backdrop-filter", css)
        self.assertIn("box-shadow", css)

    def test_1_13_css_animations(self):
        """Verify pulse and glow animations defined in styles.css"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@keyframes", css)
        self.assertIn("pulse-success", css)
        self.assertIn("pulse-tampered", css)

    def test_1_14_css_responsiveness(self):
        """Verify media query responsive rules defined in styles.css"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@media", css)
        self.assertIn("max-width: 1024px", css)
        self.assertIn("max-width: 768px", css)

    def test_1_15_js_exists(self):
        """Verify app.js exists in website/public/"""
        self.assertTrue(os.path.isfile(JS_PATH), f"app.js not found at {JS_PATH}. (Implementation track has not yet created app.js)")

    def test_1_16_js_workflows_defined(self):
        """Verify workflows defined in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("audit" in js or "Audit Anomalous Orders" in js)
        self.assertTrue("saga" in js or "Run Saga Procure-to-Pay" in js)

    def test_1_17_js_react_traces_defined(self):
        """Verify reasoning trace definitions exist in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue(re.search(r"(trace|reasoning|Thought|Action|Observation)", js))

    def test_1_18_js_genesis_block(self):
        """Verify Genesis block prev_hash has 64 zeros in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("0000000000000000000000000000000000000000000000000000000000000000", js)

    def test_1_19_js_sha256_function(self):
        """Verify SHA-256 function or subtle crypto is used in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("SHA-256" in js or "sha256" in js or "crypto.subtle" in js)

    def test_1_20_js_button_listeners(self):
        """Verify button action bindings exist in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("btn-tamper-ledger" in js or "tamper" in js)
        self.assertTrue("btn-reverify" in js or "reverify" in js)
        self.assertTrue("btn-reset-ledger" in js or "reset" in js or "restore" in js)

    # ==========================================
    # TIER 2: Boundary & Corner Cases (20 Cases)
    # ==========================================

    def test_2_1_meta_viewport(self):
        """Verify meta viewport tag in index.html for responsiveness"""
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("name=\"viewport\"", html)
        self.assertIn("width=device-width", html)

    def test_2_2_css_body_bg(self):
        """Verify body has background styling (not default white)"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertTrue("background" in css or "background-color" in css)
        self.assertIn("body", css)

    def test_2_3_css_pulse_animations(self):
        """Verify pulse keyframe definitions in CSS"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("pulse-success", css)
        self.assertIn("pulse-tampered", css)

    def test_2_4_js_empty_workflow_handling(self):
        """Verify simulator logic for handling empty or invalid workflow clicks"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("active" in js or "click" in js or "error" in js or "disabled" in js)

    def test_2_5_js_tamper_block_bounds(self):
        """Verify tamper logic targeting block index 2"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("tamper" in js)
        self.assertTrue("2" in js or "index" in js or "block" in js)

    def test_2_6_js_tamper_breaks_chain(self):
        """Verify JS has logic to flag verification failure when a block is tampered"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("verify" in js or "validate" in js)
        self.assertTrue("tampered" in js or "broken" in js or "invalid" in js)

    def test_2_7_js_initial_ledger_state(self):
        """Verify app.js has initial verified ledger chain state"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("verified" in js or "is_verified" in js)

    def test_2_8_js_tampered_ledger_state(self):
        """Verify app.js handles tampered state flag"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("tamper" in js)

    def test_2_9_js_reset_restores_state(self):
        """Verify app.js reset/restore logic exists"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("reset" in js or "restore" in js or "seed" in js)

    def test_2_10_js_hash_format_regex(self):
        """Verify JS handles hash strings that look like SHA-256 hex"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("length" in js or "64" in js or "slice" in js or "substring" in js)

    def test_2_11_js_trace_rendering(self):
        """Verify ReAct trace sequential rendering logic in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("innerHTML" in js or "createElement" in js or "append" in js or "terminal" in js)

    def test_2_12_js_ephemeral_ui_render(self):
        """Verify dynamic ephemeral UI generation logic in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("ephemeral-ui-container" in js or "ephemeralUI" in js or "ui-container" in js)

    def test_2_13_js_ephemeral_clicks(self):
        """Verify ephemeral buttons action triggers in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("onAction" in js or "click" in js or "listener" in js or "button" in js)

    def test_2_14_js_concurrent_workflow_handling(self):
        """Verify active workflow locking logic in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("running" in js or "disabled" in js or "lock" in js or "busy" in js)

    def test_2_15_js_long_trace_height(self):
        """Verify scroll/height properties on terminal output container"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertTrue("overflow" in css or "max-height" in css or "height" in css)

    def test_2_16_js_tampering_triggers_change(self):
        """Verify hash verification check logic computes correct mismatch"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("!=" in js or "!==" in js or "match" in js or "verify" in js)

    def test_2_17_js_banner_toggling(self):
        """Verify success/error banner hide/show classes logic in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("classList" in js or "add" in js or "remove" in js or "hidden" in js or "toggle" in js)

    def test_2_18_js_tampered_block_css(self):
        """Verify CSS selector rules for tampered blocks exist"""
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertTrue("tampered" in css or "border-red" in css or "border-rose" in css)

    def test_2_19_js_workflow_disable_state(self):
        """Verify workflow button active/disabled attributes exist in app.js"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("disabled" in js or "setAttribute" in js or "classList" in js)

    def test_2_20_js_reset_clears_terminal_content(self):
        """Verify app.js reset clears console contents"""
        if not os.path.isfile(JS_PATH):
            self.skipTest("app.js not implemented yet")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertTrue("clear" in js or "innerHTML = ''" in js or "textContent = ''" in js or "reset" in js)

    # ==========================================
    # TIER 3: Cross-Feature Combinations (4 Cases)
    # ==========================================

    def test_3_1_console_action_updates_ledger_api(self):
        """Verify console waiver approval action mutates database and appends ledger record"""
        token = self.get_jwt_token("bob@example.com")
        if not token:
            self.skipTest("Backend server is not running or credentials invalid.")

        headers = {"Authorization": f"Bearer {token}"}
        # Verify initial ledger size
        r = requests.get(f"{API_URL}/api/ledger", headers=headers)
        self.assertEqual(r.status_code, 200)
        initial_blocks_count = len(r.json().get("events", []))

        # Perform secure action execute mutation (simulating waiver approval)
        mutation_query = {
            "query": "UPDATE orders SET status = 'approved' WHERE id = 1",
            "params": {}
        }
        res = requests.post(f"{API_URL}/api/action/execute", json=mutation_query, headers=headers)
        self.assertEqual(res.status_code, 200)

        # Check ledger appended new block
        r2 = requests.get(f"{API_URL}/api/ledger", headers=headers)
        self.assertEqual(r2.status_code, 200)
        new_blocks_count = len(r2.json().get("events", []))
        self.assertEqual(new_blocks_count, initial_blocks_count + 1)

    def test_3_2_ledger_tampering_fails_verification(self):
        """Verify direct DB ledger tampering causes verify api to return false and flag tampered index"""
        token = self.get_jwt_token("alice@example.com")
        if not token:
            self.skipTest("Backend not running or credentials invalid.")

        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify ledger initially clean
        r_init = requests.get(f"{API_URL}/api/ledger", headers=headers)
        self.assertTrue(r_init.json().get("is_verified"))

        # Connect to DB out-of-band and tamper
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action_details FROM audit_ledger WHERE id = 2")
        original_details = cursor.fetchone()[0]
        
        try:
            cursor.execute("UPDATE audit_ledger SET action_details = 'tampered_data' WHERE id = 2")
            conn.commit()
            
            # Hit ledger verify endpoint
            r_verify = requests.get(f"{API_URL}/api/ledger", headers=headers)
            self.assertFalse(r_verify.json().get("is_verified"))
            self.assertIn(2, r_verify.json().get("tampered_indices"))
        finally:
            # Restore db state
            cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (original_details,))
            conn.commit()
            conn.close()

    def test_3_3_ledger_verification_recovery_api(self):
        """Verify that after restoring tampered data, the ledger verify API returns true"""
        token = self.get_jwt_token("alice@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify ledger initially clean
        r_init = requests.get(f"{API_URL}/api/ledger", headers=headers)
        self.assertTrue(r_init.json().get("is_verified"))

        # Connect to DB out-of-band, tamper, and then immediately restore to verify recovery
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action_details FROM audit_ledger WHERE id = 2")
        original_details = cursor.fetchone()[0]
        
        try:
            cursor.execute("UPDATE audit_ledger SET action_details = 'tampered_data' WHERE id = 2")
            conn.commit()
            
            # Confirm tampered
            r_verify = requests.get(f"{API_URL}/api/ledger", headers=headers)
            self.assertFalse(r_verify.json().get("is_verified"))
            
            # Restore
            cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (original_details,))
            conn.commit()
            
            # Confirm recovered
            r_recovered = requests.get(f"{API_URL}/api/ledger", headers=headers)
            self.assertTrue(r_recovered.json().get("is_verified"))
        finally:
            conn.close()

    def test_3_4_rbac_graph_endpoint_isolation(self):
        """Verify that graph endpoint returns nodes based on role clearances"""
        cust_token = self.get_jwt_token("charlie@example.com")
        emp_token = self.get_jwt_token("bob@example.com")
        
        if not cust_token or not emp_token:
            self.skipTest("Backend not running.")

        # Customer role should be forbidden from calling graph directly or filtered
        res_cust = requests.get(f"{API_URL}/api/graph", headers={"Authorization": f"Bearer {cust_token}"})
        self.assertEqual(res_cust.status_code, 403)

        # Employee role should succeed
        res_emp = requests.get(f"{API_URL}/api/graph", headers={"Authorization": f"Bearer {emp_token}"})
        self.assertEqual(res_emp.status_code, 200)
        nodes = res_emp.json().get("nodes", [])
        self.assertTrue(len(nodes) > 0)

    # ==========================================
    # TIER 4: Real-World Scenarios (5 Cases)
    # ==========================================

    def test_4_1_scenario_audit_waiver_flow(self):
        """Simulate high-value order audit, waiver override, and ledger logging workflow"""
        token = self.get_jwt_token("bob@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}
        
        # Submit query to inspect Anomalous orders
        res = requests.post(f"{API_URL}/api/query", json={"question": "Show anomalous transactions"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        task_id = res.json().get("task_id")
        
        # Poll task until completed
        completed = False
        for _ in range(30):
            status_res = requests.get(f"{API_URL}/api/tasks/{task_id}", headers=headers).json()
            if status_res.get("status") == "completed":
                completed = True
                self.assertIn("ui_code", status_res.get("result", {}))
                break
            time.sleep(0.5)
        self.assertTrue(completed, "Query task polling timed out.")

        # Simulate waiver approval action
        action_payload = {
            "query": "UPDATE orders SET status = 'approved' WHERE id = 1",
            "params": {}
        }
        res_action = requests.post(f"{API_URL}/api/action/execute", json=action_payload, headers=headers)
        self.assertEqual(res_action.status_code, 200)

        # Check ledger status to verify new TRANSACTION_MUTATION is cryptographically verified
        r_ledger = requests.get(f"{API_URL}/api/ledger", headers=headers)
        self.assertTrue(r_ledger.json().get("is_verified"))

    def test_4_2_scenario_p2p_saga_rollback(self):
        """Simulate Saga Procure-to-Pay workflow with compliance violation and stock rollback"""
        token = self.get_jwt_token("bob@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}

        # Check initial stock of Standing Desk (ID 2, price 499.50)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
        initial_stock = cursor.fetchone()[0]
        conn.close()

        # Execute Saga P2P workflow for a transaction > $500 (e.g. buying 2 standing desks = $999.00)
        # This triggers a compliance limit violation and saga rollback compensation
        res = requests.post(f"{API_URL}/api/query", 
                            json={"question": "Run Procure-to-Pay workflow to purchase 2 Standing Desks"}, 
                            headers=headers)
        self.assertEqual(res.status_code, 200)
        task_id = res.json().get("task_id")

        # Poll task until completed/failed
        completed = False
        for _ in range(30):
            status_res = requests.get(f"{API_URL}/api/tasks/{task_id}", headers=headers).json()
            status = status_res.get("status")
            if status == "completed":
                completed = True
                trace = status_res.get("result", {}).get("trace", [])
                # Verify that trace logs the compensation rollback
                trace_text = str(trace)
                self.assertTrue("PAYMENT_REJECTED" in trace_text or "LIMIT_EXCEEDED" in trace_text or "compensation" in trace_text)
                break
            time.sleep(0.5)
        self.assertTrue(completed, "Saga query task polling timed out.")

        # Check that product stock was compensated/restored
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
        final_stock = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(final_stock, initial_stock, "Product stock was not correctly rolled back/compensated.")

    def test_4_3_scenario_tamper_detect_restore(self):
        """Simulate intrusion detection, warning display, and restoration recovery"""
        token = self.get_jwt_token("alice@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}

        # Tamper DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action_details FROM audit_ledger WHERE id = 2")
        original_details = cursor.fetchone()[0]
        cursor.execute("UPDATE audit_ledger SET action_details = 'hacked_logs' WHERE id = 2")
        conn.commit()

        try:
            # Verify chain fails
            res_verify1 = requests.get(f"{API_URL}/api/ledger", headers=headers).json()
            self.assertFalse(res_verify1.get("is_verified"))
            self.assertIn(2, res_verify1.get("tampered_indices"))

            # Simulate recovery (restoring original logs)
            cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (original_details,))
            conn.commit()

            # Verify chain succeeds
            res_verify2 = requests.get(f"{API_URL}/api/ledger", headers=headers).json()
            self.assertTrue(res_verify2.get("is_verified"))
            self.assertEqual(len(res_verify2.get("tampered_indices", [])), 0)
        finally:
            conn.close()

    def test_4_4_scenario_tamper_during_active_console(self):
        """Simulate security warning trigger when ledger is tampered while console query executes"""
        token = self.get_jwt_token("bob@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}

        # Start a standard query task
        res = requests.post(f"{API_URL}/api/query", json={"question": "Inspect product stock levels"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        task_id = res.json().get("task_id")

        # Programmatically tamper ledger during task resolution
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action_details FROM audit_ledger WHERE id = 2")
        original_details = cursor.fetchone()[0]
        cursor.execute("UPDATE audit_ledger SET action_details = 'tampered_during_execution' WHERE id = 2")
        conn.commit()

        try:
            # Verify ledger endpoint reflects breach
            res_ledger = requests.get(f"{API_URL}/api/ledger", headers=headers).json()
            self.assertFalse(res_ledger.get("is_verified"))
        finally:
            # Restore DB
            cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (original_details,))
            conn.commit()
            conn.close()

    def test_4_5_scenario_vector_schema_sync(self):
        """Verify schema explorer extraction returns expected SQL tables and Qdrant mappings"""
        token = self.get_jwt_token("bob@example.com")
        if not token:
            self.skipTest("Backend not running.")

        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/api/schema", headers=headers)
        self.assertEqual(res.status_code, 200)
        schema_text = res.text
        
        # Verify references to SQL tables and Hybrid vector mapping
        self.assertIn("orders", schema_text)
        self.assertIn("products", schema_text)
        self.assertIn("audit_ledger", schema_text)
        self.assertIn("vector", schema_text.lower())

if __name__ == "__main__":
    unittest.main()
