import requests
import time
import sys

import os

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")

# If I run from host, it is localhost.
# I'll rely on env var or arg, default to http://backend:8000 for docker exec.

def test_flow():
    print("1. Starting process to create contract...")
    # Start process
    payload = {
        "contractTitle": "Test Contract API",
        "requestedBy": "Automated Tester"
    }
    try:
        r = requests.post(f"{BASE_URL}/start-process", json=payload, timeout=10)
        r.raise_for_status()
        resp_json = r.json()
        print(f"Process started: {resp_json}")
        
        # Get Process Instance ID
        # Response structure depends on how main.py returns it.
        # main.py: return {"camunda_response": res.json()}
        # Camunda response: {"id": "...", ...}
        proc_inst_id = resp_json.get("camunda_response", {}).get("id")
        if not proc_inst_id:
             print(f"Could not get process instance ID. Full Response: {resp_json}")
             return

    except Exception as e:
        print(f"Failed to start process: {e}")
        return

    CAMUNDA_API = "http://camunda:8080/engine-rest"
    
    print("Fetching User Task for PM...")
    task_id = None
    for _ in range(10):
        try:
            r = requests.get(f"{CAMUNDA_API}/task?processInstanceId={proc_inst_id}")
            tasks = r.json()
            if tasks:
                task_id = tasks[0]["id"]
                print(f"Found User Task: {task_id}")
                break
        except Exception as e:
            print(f"Error fetching tasks: {e}")
        time.sleep(1)
        
    if not task_id:
        print("User task not found!")
        return

    print("Completing User Task...")
    try:
        # Complete with variables if needed, or just complete.
        # Worker reads variables from process scope.
        # We ensure variables are set (from start_process).
        r = requests.post(f"{CAMUNDA_API}/task/{task_id}/complete", json={}, timeout=10)
        r.raise_for_status()
        print("User Task Completed.")
    except Exception as e:
         print(f"Failed to complete task: {e}")
         return

    print("Waiting for worker to create contract (sleep 10s)...")

    time.sleep(10)

    print("2. Fetching contracts via GET /api/providers/contracts...")
    contract_id = None
    try:
        r = requests.get(f"{BASE_URL}/api/providers/contracts", timeout=10)
        r.raise_for_status()
        contracts = r.json()
        print(f"Found {len(contracts)} contracts.")
        
        target = None
        for c in contracts:
            if c.get("ContractTitle") == "Test Contract API":
                target = c
                break
        
        if not target:
            print("Target contract not found! Worker might be slow or failed.")
            print("Contracts found:", contracts)
            return

        print("Target validation:")
        print(f"  ContractStatus: {target.get('ContractStatus')} (Expected: Running)")
        print(f"  ProvidersBudget: {target.get('ProvidersBudget')} (Expected: None)")
        print(f"  ProvidersComment: {target.get('ProvidersComment')} (Expected: '')")

        contract_id = target.get("ContractId")
        if not contract_id:
            print("Error: ContractId is missing.")
            return

    except Exception as e:
        print(f"GET failed: {e}")
        return

    print(f"3. Patching contract {contract_id}...")
    patch_data = {
        "providersBudget": 9999,
        "providersComment": "Approved budget"
    }
    try:
        r = requests.patch(f"{BASE_URL}/api/providers/contracts/{contract_id}", json=patch_data, timeout=10)
        r.raise_for_status()
        print("Patch successful:", r.json())
    except Exception as e:
        print(f"PATCH failed: {e}")
        return

    print("4. Verifying update...")
    try:
        r = requests.get(f"{BASE_URL}/api/providers/contracts", timeout=10)
        r.raise_for_status()
        contracts = r.json()
        target = next((c for c in contracts if c["ContractId"] == contract_id), None)
        
        if target:
             print(f"  ProvidersBudget: {target.get('ProvidersBudget')} (Expected: 9999)")
             print(f"  ProvidersComment: {target.get('ProvidersComment')} (Expected: 'Approved budget')")
             
             if target.get('ProvidersBudget') == 9999 and target.get('ProvidersComment') == "Approved budget":
                 print("SUCCESS: Verification Passed.")
             else:
                 print("FAILURE: Values did not update correctly.")
        else:
            print("Error: Contract disappeared?")

    except Exception as e:
        print(f"Verification GET failed: {e}")

if __name__ == "__main__":
    test_flow()
