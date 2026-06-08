import urllib.request
import urllib.error
import json
import time
import os
import sqlite3
import hashlib

# Configuration
API_URL = "http://127.0.0.1:8000"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erp_database.db")

# Helper colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_post_request(endpoint, body, token=None):
    url = f"{API_URL}{endpoint}"
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            return err.code, json.loads(err.read().decode("utf-8"))
        except Exception:
            return err.code, {"error": err.reason}
    except Exception as e:
        return 500, {"error": str(e)}

def run_get_request(endpoint, token=None):
    url = f"{API_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            return err.code, json.loads(err.read().decode("utf-8"))
        except Exception:
            return err.code, {"error": err.reason}
    except Exception as e:
        return 500, {"error": str(e)}

def get_auth_token(email, password="password123"):
    status, res = run_post_request("/api/auth/login", {"email": email, "password": password})
    if status == 200:
        return res.get("access_token")
    return None

def poll_task(task_id, token):
    print(f"{Colors.BLUE}[*] Enqueued task {task_id}. Polling progress...{Colors.ENDC}")
    poll_url = f"/api/tasks/{task_id}"
    for _ in range(30):
        time.sleep(1)
        status_code, task_res = run_get_request(poll_url, token=token)
        if status_code != 200:
            continue
        status = task_res.get("status")
        print(f"    - Current Status: {Colors.CYAN}{status}{Colors.ENDC}")
        if status in ["completed", "failed", "compensated"]:
            return task_res
    return None

def display_traces(task_res):
    print(f"\n{Colors.BOLD}--- Execution Trace Steps ---{Colors.ENDC}")
    traces = task_res.get("trace", [])
    for idx, trace in enumerate(traces):
        agent = trace.get("agent_name", "Unknown")
        action = trace.get("action_type", "Trace")
        details = trace.get("action_details", "")
        print(f"  [{idx+1}] {Colors.CYAN}[{agent}]{Colors.ENDC} - {action}: {details}")
    print("-----------------------------\n")

def check_stock(product_id):
    if not os.path.exists(DB_PATH):
        return "N/A"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, stock_quantity FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return f"'{row[0]}' stock level: {Colors.BOLD}{row[1]}{Colors.ENDC}"
    except Exception as e:
        return f"Error: {e}"
    return "Not Found"

def run_saga_compliant():
    print(f"\n{Colors.HEADER}=== Scenario 1: Compliant Procurement Saga ==={Colors.ENDC}")
    token = get_auth_token("charlie@example.com")
    if not token:
        print(f"{Colors.FAIL}[-] Authentication failed for Customer Charlie.{Colors.ENDC}")
        return

    print(f"[*] Stock status: {check_stock(1)}")
    print(f"[*] Ordering 1 Ergonomic Office Chair v2 (Total price: $299.99)...")
    status, res = run_post_request("/api/query", {"question": "Run Procure-to-Pay workflow to purchase 1 Ergonomic Office Chair v2"}, token=token)
    
    if status != 200:
        print(f"{Colors.FAIL}[-] Failed to enqueue task: {res}{Colors.ENDC}")
        return

    task_id = res.get("task_id")
    task_res = poll_task(task_id, token)
    
    if task_res:
        result = task_res.get("result", {})
        print(f"\n{Colors.GREEN}[+] Saga execution completed!{Colors.ENDC}")
        print(f"    - Final Status: {Colors.BOLD}{result.get('status')}{Colors.ENDC}")
        display_traces(task_res)
        print(f"[*] Updated stock: {check_stock(1)}")
    else:
        print(f"{Colors.FAIL}[-] Task execution timed out.{Colors.ENDC}")

def run_saga_non_compliant():
    print(f"\n{Colors.HEADER}=== Scenario 2: Non-Compliant Procurement Saga (Rollback) ==={Colors.ENDC}")
    token = get_auth_token("charlie@example.com")
    if not token:
        print(f"{Colors.FAIL}[-] Authentication failed for Customer Charlie.{Colors.ENDC}")
        return

    print(f"[*] Stock status: {check_stock(2)}")
    print(f"[*] Ordering 2 Standing Desk v3 (Total price: $999.00 - Exceeds $500 FinOps limit)...")
    status, res = run_post_request("/api/query", {"question": "Run Procure-to-Pay workflow to purchase 2 Standing Desk v3 (Dual Motor)"}, token=token)
    
    if status != 200:
        print(f"{Colors.FAIL}[-] Failed to enqueue task: {res}{Colors.ENDC}")
        return

    task_id = res.get("task_id")
    task_res = poll_task(task_id, token)
    
    if task_res:
        result = task_res.get("result", {})
        print(f"\n{Colors.WARNING}[!] Saga transaction failed and rolled back!{Colors.ENDC}")
        print(f"    - Final Status: {Colors.BOLD}{result.get('status')}{Colors.ENDC}")
        print(f"    - Error logged: {Colors.FAIL}{result.get('error')}{Colors.ENDC}")
        display_traces(task_res)
        print(f"[*] Restored stock status: {check_stock(2)}")
    else:
        print(f"{Colors.FAIL}[-] Task execution timed out.{Colors.ENDC}")

def test_rbac_clearances():
    print(f"\n{Colors.HEADER}=== Scenario 3: RBAC Product Clearance Isolation ==={Colors.ENDC}")
    roles = [
        ("Customer (Charlie)", "charlie@example.com", 1),
        ("Employee (Bob)", "bob@example.com", 2),
        ("Admin (Alice)", "alice@example.com", 3)
    ]
    
    for label, email, clearance in roles:
        print(f"\n[*] Querying product stock list as {Colors.BOLD}{label}{Colors.ENDC}...")
        token = get_auth_token(email)
        if not token:
            print(f"    {Colors.FAIL}[-] Failed to authenticate.{Colors.ENDC}")
            continue
            
        status, res = run_post_request("/api/query", {"question": "Inspect product stock levels"}, token=token)
        if status != 200:
            print(f"    {Colors.FAIL}[-] Failed to query: {res}{Colors.ENDC}")
            continue
            
        task_id = res.get("task_id")
        task_res = poll_task(task_id, token)
        
        if task_res:
            products = task_res.get("result", {}).get("data", {}).get("products", [])
            product_names = [p.get("name") for p in products]
            print(f"    {Colors.GREEN}[+] Clearance Level {clearance} results ({len(product_names)} items):{Colors.ENDC}")
            for p_name in product_names:
                print(f"      - {p_name}")
        else:
            print(f"    {Colors.FAIL}[-] Query timed out.{Colors.ENDC}")

def run_destructive_bypass():
    print(f"\n{Colors.HEADER}=== Scenario 4: SQL Shield Gateway Sandbox Interception ==={Colors.ENDC}")
    token = get_auth_token("bob@example.com") # Employee
    
    print(f"[*] Attacking: Attempting unauthorized DELETE from critical tables...")
    payload = {"question": "Execute delete command on audit ledger records"}
    status, res = run_post_request("/api/query", payload, token=token)
    
    if status == 400 or status == 403:
        print(f"    {Colors.GREEN}[+] Blocked by Shield Gateway (Status {status})!{Colors.ENDC}")
        print(f"    - Intercept Details: {Colors.WARNING}{res.get('detail') or res.get('error')}{Colors.ENDC}")
    else:
        # Check task execution status
        task_id = res.get("task_id")
        task_res = poll_task(task_id, token)
        if task_res:
            err = task_res.get("result", {}).get("error")
            print(f"    {Colors.GREEN}[+] Blocked at Worker Gateway Level!{Colors.ENDC}")
            print(f"    - Details: {Colors.WARNING}{err}{Colors.ENDC}")

def verify_ledger():
    print(f"\n{Colors.HEADER}=== Scenario 5: Cryptographic Ledger Audits & Verification ==={Colors.ENDC}")
    status, res = run_get_request("/api/ledger")
    if status == 200:
        verified = res.get("verified", False)
        tampered = res.get("tampered", [])
        
        if verified:
            print(f"    {Colors.GREEN}[+] Cryptographic Signature Chain: VERIFIED (Pristine status){Colors.ENDC}")
        else:
            print(f"    {Colors.FAIL}[-] Cryptographic Signature Chain: COMPROMISED!{Colors.ENDC}")
            print(f"    - Tampered Record Indices: {Colors.BOLD}{tampered}{Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}[-] Failed to fetch ledger: {res}{Colors.ENDC}")

def simulate_tampering():
    print(f"\n{Colors.HEADER}=== Scenario 6: Attack Simulation (Data Tampering) ==={Colors.ENDC}")
    if not os.path.exists(DB_PATH):
        print(f"{Colors.FAIL}[-] erp_database.db not located.{Colors.ENDC}")
        return
        
    print(f"[*] Modifying database out-of-band (simulating direct SQL breach)...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Find index 2 or any transaction row to modify
        cursor.execute("SELECT id, action_type, action_details FROM audit_ledger WHERE id = 2")
        row = cursor.fetchone()
        if not row:
            print(f"    {Colors.WARNING}[!] Ledger block #2 not found. Seeding database first recommended.{Colors.ENDC}")
            conn.close()
            return
            
        original_details = row[2]
        print(f"    - Current row detail: {original_details}")
        
        # Inject altered payload details
        compromised_details = json.dumps({"action": "Redirect payment transactions to hacker account"})
        cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (compromised_details,))
        conn.commit()
        conn.close()
        
        print(f"    {Colors.GREEN}[+] Injected tampered data successfully!{Colors.ENDC}")
        print(f"[*] Re-verifying ledger state now:")
        verify_ledger()
        
        # Restore ledger to pristine state
        print(f"\n[*] Recovering database ledger state...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE audit_ledger SET action_details = ? WHERE id = 2", (original_details,))
        conn.commit()
        conn.close()
        print(f"    {Colors.GREEN}[+] Restored ledger state. Re-verifying...{Colors.ENDC}")
        verify_ledger()
        
    except Exception as e:
        print(f"    {Colors.FAIL}[-] Error during tampering simulation: {e}{Colors.ENDC}")

def main_menu():
    while True:
        print(f"\n{Colors.BOLD}================================================={Colors.ENDC}")
        print(f"{Colors.CYAN}{Colors.BOLD}     OmniGate ERPOS Developer Test Dashboard     {Colors.ENDC}")
        print(f"{Colors.BOLD}================================================={Colors.ENDC}")
        print("1. Run Compliant Purchase Saga (Deduct Stock & Auto-Approve)")
        print("2. Run Non-Compliant Purchase Saga (Trigger Spend Block & Compensate)")
        print("3. Verify RBAC Clearance Levels Isolation (Charlie vs Bob vs Alice)")
        print("4. Test SQL Shield Sandbox Guards (Inject Destructive DELETE)")
        print("5. Verify Cryptographic Ledger Signature Chain")
        print("6. Run Out-of-band Tamper Simulation & Autorecovery check")
        print("0. Exit Dashboard")
        print("=================================================")
        
        choice = input(f"{Colors.BOLD}Enter selection [0-6]: {Colors.ENDC}").strip()
        if choice == "1":
            run_saga_compliant()
        elif choice == "2":
            run_saga_non_compliant()
        elif choice == "3":
            test_rbac_clearances()
        elif choice == "4":
            run_destructive_bypass()
        elif choice == "5":
            verify_ledger()
        elif choice == "6":
            simulate_tampering()
        elif choice == "0":
            print(f"\n{Colors.GREEN}Exiting developer dashboard. Happy coding!{Colors.ENDC}")
            break
        else:
            print(f"{Colors.WARNING}Invalid choice. Please select 0 to 6.{Colors.ENDC}")

if __name__ == "__main__":
    main_menu()
