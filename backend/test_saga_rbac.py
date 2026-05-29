import urllib.request
import urllib.error
import json
import time
import sqlite3

def run_post_request(url, body, token=None):
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

def run_get_request(url, token=None):
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
    login_url = "http://127.0.0.1:8000/api/auth/login"
    status, res = run_post_request(login_url, {"email": email, "password": password})
    if status == 200:
        return res.get("access_token")
    return None

def poll_task(task_id, token):
    poll_url = f"http://127.0.0.1:8000/api/tasks/{task_id}"
    for _ in range(60):
        time.sleep(1)
        status_code, task_res = run_get_request(poll_url, token=token)
        if status_code != 200:
            continue
        status = task_res.get("status")
        if status in ["completed", "failed"]:
            return task_res
    return None

def test_rbac_clearance():
    print("\n=================== Running RBAC Dynamic Clearance Tests ===================")
    admin_token = get_auth_token("alice@example.com")
    employee_token = get_auth_token("bob@example.com")
    customer_token = get_auth_token("charlie@example.com")

    # 1. Test Customer (Charlie, clearance 1) Product Query
    print("[Test 1] Customer Product Check (Should filter out clearance 2 & 3 items)...")
    status, res = run_post_request("http://127.0.0.1:8000/api/query", {"question": "Inspect product stock levels"}, token=customer_token)
    task_id = res.get("task_id")
    task_res = poll_task(task_id, customer_token)
    result_data = task_res.get("result", {})
    products = result_data.get("data", {}).get("products", [])
    product_names = [p["name"] for p in products]
    print(f"Customer sees {len(products)} products: {product_names}")
    
    assert "Quantum Processor v1" not in product_names, "Customer should NOT see Employee-only items"
    assert "Mainframe Core Server Cluster" not in product_names, "Customer should NOT see Admin-only items"
    assert len(products) == 5, f"Customer should see exactly 5 public products, got {len(products)}"

    # 2. Test Employee (Bob, clearance 2) Product Query
    print("[Test 2] Employee Product Check (Should see Employee items but NOT Admin items)...")
    status, res = run_post_request("http://127.0.0.1:8000/api/query", {"question": "Inspect product stock levels"}, token=employee_token)
    task_id = res.get("task_id")
    task_res = poll_task(task_id, employee_token)
    result_data = task_res.get("result", {})
    products = result_data.get("data", {}).get("products", [])
    product_names = [p["name"] for p in products]
    print(f"Employee sees {len(products)} products: {product_names}")
    
    assert "Quantum Processor v1" in product_names, "Employee should see Employee items"
    assert "Mainframe Core Server Cluster" not in product_names, "Employee should NOT see Admin items"
    assert len(products) == 6, f"Employee should see exactly 6 products, got {len(products)}"

    # 3. Test Admin (Alice, clearance 3) Product Query via SQL tool simulation
    print("[Test 3] Admin Product Check (Should see ALL products)...")
    status, res = run_post_request("http://127.0.0.1:8000/api/query", {"question": "Inspect product stock levels"}, token=admin_token)
    task_id = res.get("task_id")
    task_res = poll_task(task_id, admin_token)
    result_data = task_res.get("result", {})
    products = result_data.get("data", {}).get("products", [])
    product_names = [p["name"] for p in products]
    print(f"Admin sees {len(products)} products: {product_names}")
    
    assert "Quantum Processor v1" in product_names
    assert "Mainframe Core Server Cluster" in product_names, "Admin should see Admin items"
    assert len(products) == 7, f"Admin should see all 7 products, got {len(products)}"

    print("RBAC Dynamic Clearance checks passed successfully!")

def test_saga_workflow():
    print("\n=================== Running Agentic Saga Transaction Tests ===================")
    customer_token = get_auth_token("charlie@example.com")
    
    # Get current stock of Ergonomic Chair
    db_file = "erp_database.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM products WHERE id = 1")
    initial_chair_stock = cursor.fetchone()[0]
    conn.close()
    print(f"Initial Ergonomic Chair stock: {initial_chair_stock}")

    # 1. Compliant Saga Run
    print("[Saga Test 1] Executing Compliant Purchase (Total: 1 * 299.99 = $299.99 <= $500 limit)...")
    status, res = run_post_request("http://127.0.0.1:8000/api/query", {
        "question": "Run Procure-to-Pay workflow to purchase 1 Ergonomic Chair"
    }, token=customer_token)
    task_id = res.get("task_id")
    task_res = poll_task(task_id, customer_token)
    result_data = task_res.get("result", {})
    
    saga_status = result_data.get("status") or result_data.get("data", {}).get("status")
    print(f"Compliant Saga status: {saga_status}")
    assert saga_status == "completed", f"Saga should complete successfully, got status: {saga_status}"

    # Verify stock deducted
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM products WHERE id = 1")
    updated_chair_stock = cursor.fetchone()[0]
    conn.close()
    print(f"Updated Ergonomic Chair stock: {updated_chair_stock}")
    assert updated_chair_stock == initial_chair_stock - 1, f"Stock should be reduced by 1. Expected: {initial_chair_stock - 1}, Got: {updated_chair_stock}"

    # 2. Rollback/Compensated Saga Run
    # Get current stock of Standing Desk
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
    initial_desk_stock = cursor.fetchone()[0]
    conn.close()
    print(f"\nInitial Standing Desk stock: {initial_desk_stock}")

    print("[Saga Test 2] Executing Non-Compliant Purchase (Total: 2 * 499.50 = $999.00 > $500 limit)...")
    status, res = run_post_request("http://127.0.0.1:8000/api/query", {
        "question": "Run Procure-to-Pay workflow to purchase 2 Standing Desks"
    }, token=customer_token)
    task_id = res.get("task_id")
    task_res = poll_task(task_id, customer_token)
    result_data = task_res.get("result", {})
    
    saga_status = result_data.get("status") or result_data.get("data", {}).get("status")
    saga_error = result_data.get("error") or result_data.get("data", {}).get("error")
    print(f"Rollback Saga status: {saga_status}, Expected Error: {saga_error}")
    
    assert saga_status == "compensated", f"Saga should rollback and report status 'compensated', got: {saga_status}"
    assert "exceeds compliance limit" in saga_error or "Payment Authorization Denied" in saga_error, f"Saga error should mention limit error, got: {saga_error}"

    # Verify stock restored
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM products WHERE id = 2")
    updated_desk_stock = cursor.fetchone()[0]
    conn.close()
    print(f"Updated Standing Desk stock after Saga Rollback: {updated_desk_stock}")
    assert updated_desk_stock == initial_desk_stock, f"Standing Desk stock should be restored. Expected: {initial_desk_stock}, Got: {updated_desk_stock}"

    print("Agentic Saga Pattern transaction checks passed successfully!")

if __name__ == "__main__":
    # Run the checks against our running backend
    test_rbac_clearance()
    test_saga_workflow()
