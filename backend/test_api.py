import urllib.request
import urllib.error
import json
import time
import setup_db
import sqlite3

def get_auth_token(email, password="password123"):
    login_url = "http://127.0.0.1:8000/api/auth/login"
    status, res = run_post_request(login_url, {"email": email, "password": password})
    print(f"DEBUG: Login for {email} status: {status}, response: {res}")
    if status == 200:
        return res.get("access_token")
    return None

def run_test(name, question, token=None):
    print(f"\n=================== Running Test: {name} ===================")
    url = "http://127.0.0.1:8000/api/query"
    data = json.dumps({"question": question}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url, 
        data=data, 
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            query_res = json.loads(response.read().decode("utf-8"))
            task_id = query_res.get("task_id")
            print(f"Query Status Code: {response.status}, Task ID: {task_id}")
            
            if not task_id:
                print("Error: No task ID returned.")
                return None
                
            # Poll status
            poll_url = f"http://127.0.0.1:8000/api/tasks/{task_id}"
            max_retries = 150
            for i in range(max_retries):
                time.sleep(1)
                status_code, task_res = run_get_request(poll_url, token=token)
                if status_code != 200:
                    print(f"Error polling task status: {status_code}, {task_res}")
                    return None
                    
                status = task_res.get("status")
                if status == "completed":
                    result = task_res.get("result", {})
                    print(f"Task completed successfully after {i+1} seconds.")
                    print(f"Number of Trace Steps: {len(result.get('trace', []))}")
                    for step in result.get('trace', []):
                        print(f"  [{step['agent']}] -> {step['action']}")
                    print(f"UI Code Generated: {result.get('ui_code', '')[:150].strip()}...")
                    return result
                elif status == "failed":
                    print(f"Task failed: {task_res.get('error')}")
                    return None
                else:
                    # Print status periodically
                    if (i + 1) % 5 == 0:
                        print(f"Task status: {status} (polling {i+1}/{max_retries})...")
            
            print("Error: Task timed out.")
            return None
    except urllib.error.HTTPError as http_err:
        print(f"HTTP Error: {http_err.code} {http_err.reason}")
        try:
            error_body = http_err.read().decode("utf-8")
            print(f"Response Body: {error_body}")
        except Exception:
            pass
    except Exception as e:
        print(f"Error executing test: {e}")
        return None

def run_post_request(url, body, token=None):
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST"
    )
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


def test_generalized_actions():
    print("\n=================== Running Action & Ledger Security Tests ===================")
    action_url = "http://127.0.0.1:8000/api/action/execute"
    ledger_url = "http://127.0.0.1:8000/api/ledger"
    
    # Authenticate and retrieve tokens for testing RBAC
    admin_token = get_auth_token("alice@example.com")
    employee_token = get_auth_token("bob@example.com")
    customer_token = get_auth_token("charlie@example.com")
    
    # 1. Test Safe Update (with Employee token)
    print("Testing Safe Update action...")
    status, res = run_post_request(action_url, {
        "query": "UPDATE products SET stock_quantity = stock_quantity + 10 WHERE name = :name",
        "params": {"name": "Ergonomic Chair"}
    }, token=employee_token)
    print(f"Safe Update Status: {status}, Response: {res}")
    assert status == 200, "Safe update should succeed"
    assert res.get("status") == "success", "Response should report success"
    
    # 2. Test Blocked Destructive Query (DELETE, with Employee token)
    print("Testing Blocked Destructive Query (DELETE)...")
    status, res = run_post_request(action_url, {
        "query": "DELETE FROM users WHERE id = 1"
    }, token=employee_token)
    print(f"DELETE Action Status: {status}, Response: {res}")
    assert status == 400 or "error" in res or "detail" in res, "DELETE should be blocked"
    
    # 3. Test Blocked System Table modification (with Employee token)
    print("Testing Blocked System Table modification...")
    status, res = run_post_request(action_url, {
        "query": "UPDATE audit_ledger SET row_hash = 'tampered' WHERE id = 1"
    }, token=employee_token)
    print(f"System Table Update Status: {status}, Response: {res}")
    assert status == 400 or "error" in res or "detail" in res, "System table modification should be blocked"
    
    # 4. Test Ledger Verification (with Employee token)
    print("Testing Ledger Integrity verification...")
    status, res = run_get_request(ledger_url, token=employee_token)
    print(f"Ledger Status: {status}, Verified: {res.get('is_verified')}, Tampered: {res.get('tampered_indices')}")
    assert status == 200
    assert res.get("is_verified") is True, "Ledger should be cryptographically verified"
    assert len(res.get("tampered_indices", [])) == 0, "No tampered records should exist"
    
    # 5. Test Tamper Detection (with Employee token)
    print("Testing Cryptographic Tamper Detection...")
    import os
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erp_database.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE audit_ledger SET action_details = 'tampered details' WHERE id = 2")
    conn.commit()
    conn.close()
    
    status, res = run_get_request(ledger_url, token=employee_token)
    print(f"After Tampering: Status: {status}, Verified: {res.get('is_verified')}, Tampered Indices: {res.get('tampered_indices')}")
    assert res.get("is_verified") is False, "Ledger should fail verification after tampering"
    assert 2 in res.get("tampered_indices", []), "Index 2 should be flagged as tampered"
    
    # 6. Test RBAC: Customer blocked from executing action mutations
    print("Testing RBAC: Customer Action block...")
    status, res = run_post_request(action_url, {
        "query": "UPDATE products SET stock_quantity = stock_quantity + 10 WHERE name = :name",
        "params": {"name": "Ergonomic Chair"}
    }, token=customer_token)
    print(f"Customer Action Status: {status}, Response: {res}")
    assert status == 403 or "Forbidden" in str(res) or "detail" in res, "Customer action execution should be forbidden (403)"
    
    # 7. Test RBAC: Employee blocked from DDL schema evolution (blocked at execute_ddl)
    print("Testing RBAC: Employee DDL evolution block...")
    # Employee tries to evolve schema via query route
    url = "http://127.0.0.1:8000/api/query"
    status, res = run_post_request(url, {"question": "Add courier shipping details to orders table"}, token=employee_token)
    print(f"Employee DDL query execution task enqueued: Status: {status}, Response: {res}")
    
    # Poll task to completion/failure
    task_id = res.get("task_id")
    if task_id:
        poll_url = f"http://127.0.0.1:8000/api/tasks/{task_id}"
        for _ in range(15):
            time.sleep(1)
            s_code, t_res = run_get_request(poll_url, token=employee_token)
            if t_res.get("status") in ["completed", "failed"]:
                print(f"Employee DDL task concluded with status: {t_res.get('status')}")
                break
                
    # Verify the schema did not evolve
    schema_status, schema_res_after = run_get_request("http://127.0.0.1:8000/api/schema", token=employee_token)
    assert "courier_name" not in schema_res_after.get("schema", ""), "Employee should not be able to evolve schema with new column"

    print("Ledger Security & RBAC Tests Passed successfully!")

if __name__ == "__main__":
    # Seed the database fresh before testing
    print("Re-seeding database for deterministic integration testing...")
    db_engine = setup_db.init_db()
    setup_db.seed_data(db_engine)
    
    # Wait for server to boot
    time.sleep(1)
    
    # Run the new security and ledger compliance tests
    test_generalized_actions()
    
    # Re-seed after tampering test to restore clean state for other tests
    print("Re-seeding database after tampering test...")
    db_engine = setup_db.init_db()
    setup_db.seed_data(db_engine)
    
    # Authenticate admin and employee for query test runs
    admin_token = get_auth_token("alice@example.com")
    employee_token = get_auth_token("bob@example.com")
    
    # 1. Test Anomalous Operations
    run_test("Audit Anomalous Transactions", "Show me today's anomalous transactions", token=employee_token)
    
    # 2. Test Evolutionary SQL Schema Mutation (Requires Admin)
    run_test("SQL Schema Evolution", "Add courier shipping details to orders table", token=admin_token)
    
    # 3. Test Evolutionary Graph Mutation (Requires Admin)
    run_test("Graph Workflow Evolution", "Evolve Graph: Add an Express Freight Delivery workflow to govern freight orders", token=admin_token)
    
    # 4. Test Evolutionary Vector Mapped Partition (Requires Admin)
    run_test("Vector Partition Evolution", "Vectorize Document: Map CEO freight regulations memo to Node 3", token=admin_token)
    
    # 5. Test Circuit Breaker Protection
    run_test("FinOps Circuit Breaker Safety Limit", "Trigger an infinite query loop test", token=admin_token)
