import urllib.request
import urllib.error
import json
import time
import sys
import os

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

def run_delete_request(url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="DELETE")
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

def main():
    print("=================== Running Evaluation Framework Integration Tests ===================")
    
    # 1. Authenticate as Admin
    admin_token = get_auth_token("alice@example.com")
    if not admin_token:
        print("Error: Failed to authenticate as admin (Alice). Make sure uvicorn is running on port 8000.")
        sys.exit(1)
    print("[Success] Authenticated successfully as Admin (Alice)")
    
    # 2. Trigger Evaluation Run
    print("Triggering new evaluation run...")
    status, run_res = run_post_request("http://127.0.0.1:8000/api/eval/run", {}, token=admin_token)
    print(f"Trigger Status: {status}, Response: {run_res}")
    assert status == 200, "Evaluation trigger should return 200"
    run_id = run_res.get("run_id")
    assert run_id is not None, "Run ID should be generated"
    
    # 3. Poll Evaluation Run
    poll_url = f"http://127.0.0.1:8000/api/eval/runs/{run_id}"
    completed = False
    for i in range(45):
        time.sleep(1)
        s, details = run_get_request(poll_url, token=admin_token)
        run_status = details.get("run", {}).get("status")
        print(f"Polling Run #{run_id} ({i+1}/45) - Status: {run_status}")
        if run_status == "completed":
            completed = True
            print(f"[Success] Evaluation completed! Metrics:")
            print(f"  Total: {details['run']['total_count']}")
            print(f"  Pass:  {details['run']['pass_count']}")
            print(f"  Fail:  {details['run']['fail_count']}")
            break
        elif run_status == "failed":
            print("Error: Evaluation poller reported failure.")
            sys.exit(1)
            
    if not completed:
        print("Error: Evaluation run timed out.")
        sys.exit(1)
        
    # Verify scenarios list
    s, details = run_get_request(poll_url, token=admin_token)
    results = details.get("results", [])
    assert len(results) == 10, f"Expected 10 scenario results, got {len(results)}"
    print("[Success] 10 evaluation scenarios verified in run details")
    
    # 4. Save Human Judge Feedback
    target_result = results[0]
    result_id = target_result["id"]
    print(f"Submitting human judge feedback on scenario result #{result_id}...")
    judge_body = {
        "human_pass": 1,
        "human_score": 4,
        "human_feedback": "Verified compliant purchase, agent followed ReAct trace correctly."
    }
    s, judge_res = run_post_request(f"http://127.0.0.1:8000/api/eval/scenario-results/{result_id}/human-judge", judge_body, token=admin_token)
    print(f"Human Judge Save Status: {s}, Response: {judge_res}")
    assert s == 200, "Saving human judge should return 200"
    
    # Re-fetch and check if saved
    s, details = run_get_request(poll_url, token=admin_token)
    updated_result = next(r for r in details["results"] if r["id"] == result_id)
    assert updated_result["human_pass"] == 1
    assert updated_result["human_score"] == 4
    assert updated_result["human_feedback"] == "Verified compliant purchase, agent followed ReAct trace correctly."
    print("[Success] Human judge score and feedback successfully saved and verified")
    
    # 5. Optimize Graph Knowledge Node
    print("Fetching graph nodes for optimization...")
    s, nodes = run_get_request("http://127.0.0.1:8000/api/eval/nodes", token=admin_token)
    print(f"Fetched {len(nodes)} graph nodes.")
    assert len(nodes) > 0
    target_node = nodes[0]
    node_id = target_node["id"]
    
    original_markdown = target_node["skill_markdown"]
    new_markdown = original_markdown + "\n\n# Optimized comment added by Evaluation Optimizer."
    
    update_body = {
        "label": target_node["label"],
        "name": target_node["name"],
        "description": target_node["description"],
        "skill_markdown": new_markdown,
        "properties": target_node["properties"],
        "clearance_level": target_node["clearance_level"]
    }
    print(f"Updating skill markdown of graph node #{node_id} ({target_node['name']})...")
    s, update_res = run_post_request(f"http://127.0.0.1:8000/api/eval/nodes/{node_id}", update_body, token=admin_token)
    print(f"Update node status: {s}, Response: {update_res}")
    assert s == 200
    
    # Verify update persisted
    s, nodes_after = run_get_request("http://127.0.0.1:8000/api/eval/nodes", token=admin_token)
    updated_node = next(n for n in nodes_after if n["id"] == node_id)
    assert "Optimized comment" in updated_node["skill_markdown"]
    print("[Success] Graph node optimized successfully in both SQLite and Neo4j")
    
    # Restore original markdown to keep seed clean
    update_body["skill_markdown"] = original_markdown
    run_post_request(f"http://127.0.0.1:8000/api/eval/nodes/{node_id}", update_body, token=admin_token)
    
    # 6. Optimize Vector Partition Documents
    print("Upserting new vector partition document...")
    vector_body = {
        "node_id": node_id,
        "source_type": "policy",
        "text_content": "Optimized compliance directive: Any purchase must follow strict double audit validation.",
        "clearance_level": 2
    }
    s, upsert_res = run_post_request("http://127.0.0.1:8000/api/eval/vectors/upsert", vector_body, token=admin_token)
    print(f"Vector upsert status: {s}, Response: {upsert_res}")
    assert s == 200
    
    # Fetch vector partition list
    s, vectors = run_get_request("http://127.0.0.1:8000/api/eval/vectors", token=admin_token)
    print(f"Fetched {len(vectors)} vector partitions.")
    new_vector = next(v for v in vectors if "Optimized compliance directive" in v["text_content"])
    new_vector_id = new_vector["id"]
    print(f"[Success] Found newly upserted vector partition ID: {new_vector_id}")
    
    # Delete the vector partition to restore seed clean state
    print(f"Deleting vector partition ID {new_vector_id}...")
    s, delete_res = run_delete_request(f"http://127.0.0.1:8000/api/eval/vectors/{new_vector_id}", token=admin_token)
    print(f"Vector delete status: {s}, Response: {delete_res}")
    assert s == 200
    
    # Verify deletion
    s, vectors_after = run_get_request("http://127.0.0.1:8000/api/eval/vectors", token=admin_token)
    deleted_matches = [v for v in vectors_after if v["id"] == new_vector_id]
    assert len(deleted_matches) == 0, "Vector partition should be deleted"
    print("[Success] Vector partition successfully deleted and synced to Qdrant")
    
    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    main()
