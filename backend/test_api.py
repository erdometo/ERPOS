import urllib.request
import urllib.error
import json
import time
import setup_db

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

if __name__ == "__main__":
    # Seed the database fresh before testing
    print("Re-seeding database for deterministic integration testing...")
    db_engine = setup_db.init_db()
    setup_db.seed_data(db_engine)
    
    # Wait for server to boot
    time.sleep(1)
    
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
