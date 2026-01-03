import requests
import time
import os

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")
CAMUNDA_API = "http://camunda:8080/engine-rest"

def test_flow():
    print("1. Starting process...")
    payload = {"contractTitle": "SingleTable Test", "requestedBy": "Tester"}
    
    try:
        r = requests.post(f"{BASE_URL}/start-process", json=payload, timeout=10)
        r.raise_for_status()
        resp = r.json()
        print(f"Started: {resp}")
        proc_inst_id = resp.get("camunda_response", {}).get("id")
    except Exception as e:
        print(f"Start failed: {e}")
        return

    if not proc_inst_id:
        print("No Process ID returned.")
        return

    print("2. completing User Task...")
    time.sleep(2)
    task_id = None
    for _ in range(5):
        try:
            r = requests.get(f"{CAMUNDA_API}/task?processInstanceId={proc_inst_id}")
            tasks = r.json()
            if tasks:
                task_id = tasks[0]["id"]
                break
        except: pass
        time.sleep(1)
    
    if task_id:
        requests.post(f"{CAMUNDA_API}/task/{task_id}/complete", json={}, timeout=10)
        print("User Task completed.")
    else:
        print("User Task not found.")
        return

    print("Waiting for worker...")
    time.sleep(10)

    print("3. Checking API...")
    try:
        r = requests.get(f"{BASE_URL}/api/providers/contracts", timeout=10)
        contracts = r.json()
        target = next((c for c in contracts if c.get("ContractTitle") == "SingleTable Test"), None)
        
        if target:
            print(f"Found Contract. Status: {target.get('ContractStatus')}")
            if target.get("ContractStatus") in ["Submitted", "Running"]:
                print("SUCCESS: Contract in DB.")
            else:
                print(f"FAILURE: Unexpected status {target.get('ContractStatus')}")
        else:
            print("FAILURE: Contract not found in API.")
            print(f"Contracts: {contracts}")

    except Exception as e:
        print(f"API failed: {e}")

if __name__ == "__main__":
    test_flow()
