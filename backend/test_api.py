import urllib.request
import urllib.error
import json
import time
import setup_db
import sqlite3

def run_test(name, question):
    print(f"\n=================== Running Test: {name} ===================")
    url = "http://127.0.0.1:8000/api/query"
    data = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f"Status Code: {response.status}")
            print(f"Number of Trace Steps: {len(res_data.get('trace', []))}")
            for step in res_data.get('trace', []):
                print(f"  [{step['agent']}] -> {step['action']}")
            print(f"UI Code Generated: {res_data.get('ui_code')[:150].strip()}...")
            return res_data
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

def run_post_request(url, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
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

def run_get_request(url):
    req = urllib.request.Request(url, method="GET")
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
    
    # 1. Test Safe Update
    print("Testing Safe Update action...")
    status, res = run_post_request(action_url, {
        "query": "UPDATE products SET stock_quantity = stock_quantity + 10 WHERE name = :name",
        "params": {"name": "Ergonomic Chair"}
    })
    print(f"Safe Update Status: {status}, Response: {res}")
    assert status == 200, "Safe update should succeed"
    assert res.get("status") == "success", "Response should report success"
    
    # 2. Test Blocked Destructive Query (DELETE)
    print("Testing Blocked Destructive Query (DELETE)...")
    status, res = run_post_request(action_url, {
        "query": "DELETE FROM users WHERE id = 1"
    })
    print(f"DELETE Action Status: {status}, Response: {res}")
    assert status == 400 or "error" in res or "detail" in res, "DELETE should be blocked"
    
    # 3. Test Blocked System Table modification
    print("Testing Blocked System Table modification...")
    status, res = run_post_request(action_url, {
        "query": "UPDATE audit_ledger SET row_hash = 'tampered' WHERE id = 1"
    })
    print(f"System Table Update Status: {status}, Response: {res}")
    assert status == 400 or "error" in res or "detail" in res, "System table modification should be blocked"
    
    # 4. Test Ledger Verification
    print("Testing Ledger Integrity verification...")
    status, res = run_get_request(ledger_url)
    print(f"Ledger Status: {status}, Verified: {res.get('is_verified')}, Tampered: {res.get('tampered_indices')}")
    assert status == 200
    assert res.get("is_verified") is True, "Ledger should be cryptographically verified"
    assert len(res.get("tampered_indices", [])) == 0, "No tampered records should exist"
    
    # 5. Test Tamper Detection
    print("Testing Cryptographic Tamper Detection...")
    db_file = "erp_database.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE audit_ledger SET action_details = 'tampered details' WHERE id = 2")
    conn.commit()
    conn.close()
    
    status, res = run_get_request(ledger_url)
    print(f"After Tampering: Status: {status}, Verified: {res.get('is_verified')}, Tampered Indices: {res.get('tampered_indices')}")
    assert res.get("is_verified") is False, "Ledger should fail verification after tampering"
    assert 2 in res.get("tampered_indices", []), "Index 2 should be flagged as tampered"
    print("Ledger Security Tests Passed successfully!")

if __name__ == "__main__":
    # Seed the database fresh before testing
    print("Re-seeding database for deterministic integration testing...")
    db_engine = setup_db.init_db()
    setup_db.seed_data(db_engine)
    
    # Wait for server to boot
    time.sleep(1)
    
    # Run the new security and ledger compliance tests
    test_generalized_actions()
    
    # Re-seed after tampering to restore clean state for other tests
    print("Re-seeding database after tampering test...")
    db_engine = setup_db.init_db()
    setup_db.seed_data(db_engine)
    
    # 1. Test Anomalous Operations
    run_test("Audit Anomalous Transactions", "Show me today's anomalous transactions")
    
    # 2. Test Evolutionary SQL Schema Mutation
    run_test("SQL Schema Evolution", "Add courier shipping details to orders table")
    
    # 3. Test Evolutionary Graph Mutation
    run_test("Graph Workflow Evolution", "Evolve Graph: Add an Express Freight Delivery workflow to govern freight orders")
    
    # 4. Test Evolutionary Vector Mapped Partition
    run_test("Vector Partition Evolution", "Vectorize Document: Map CEO freight regulations memo to Node 3")
    
    # 5. Test Circuit Breaker Protection
    run_test("FinOps Circuit Breaker Safety Limit", "Trigger an infinite query loop test")
