from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection, get_azure_connection
import sys
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is running!"}
    
@app.get("/test-db")
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "message": "Database connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stats")
def get_stats():
    """
    Returns counts for Submitted, Running, Approved, and Rejected contracts from Azure SQL.
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT ContractStatus, COUNT(*) FROM Contracts GROUP BY ContractStatus")
        rows = cursor.fetchall()
        
        stats = {row[0]: row[1] for row in rows} if rows else {}
        # Ensure base keys for safety
        for k in ["Submitted", "Running", "Approved", "Rejected"]:
            if k not in stats: stats[k] = 0
            
        return stats
    except Exception as e:
        print(f"Error in /stats: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/dashboard-stats")
def get_admin_dashboard_stats():
    """
    Detailed stats for the Cockpit Dashboard Plugin.
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT ContractStatus, COUNT(*) FROM Contracts GROUP BY ContractStatus")
        rows = cursor.fetchall()
        status_counts = {row[0]: row[1] for row in rows} if rows else {}
        
        for s in ["Submitted", "Running", "Approved", "Rejected"]:
            if s not in status_counts:
                status_counts[s] = 0
                
        return {
            "totalContracts": sum(status_counts.values()),
            "byStatus": status_counts,
            "systemHealth": "Healthy"
        }
    except Exception as e:
        print(f"Error in /api/admin/dashboard-stats: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contracts/{status}")
def get_contracts(status: str):
    """
    Returns list of contracts based on status: 'submitted', 'approved', 'rejected'.
    """
    status = status.lower()
    allowed = ["submitted", "approved", "rejected"]
    if status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status. Must be submitted, approved, or rejected.")
    
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        # Map frontend status to DB status
        # 'submitted' could match 'Submitted' or 'Running'
        # 'approved' matches 'Approved'
        # 'rejected' matches 'Rejected'
        
        if status == "submitted":
            query = "SELECT * FROM Contracts WHERE ContractStatus IN ('Submitted', 'Running') ORDER BY CreatedAt DESC"
        elif status == "approved":
             query = "SELECT * FROM Contracts WHERE ContractStatus = 'Approved' ORDER BY ApprovedAt DESC"
        else: # rejected
             query = "SELECT * FROM Contracts WHERE ContractStatus = 'Rejected' ORDER BY RejectedAt DESC"
            
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dicts
        columns = [column[0] for column in cursor.description]
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
            
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error in /contracts/{status}: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

        
import requests

CAMUNDA_URL = "http://camunda:8080/engine-rest" # Use docker service name if running in docker

class ProviderUpdate(BaseModel):
    providersBudget: Optional[int] = None
    providersComment: Optional[str] = None
    meetRequirement: Optional[str] = None
    providersName: Optional[str] = None

@app.get("/api/providers/contracts")
def get_provider_contracts():
    """
    Returns contracts for providers that are in 'Submitted' or 'Running' status.
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        # Select specific fields requested, filtering for 'Submitted' or 'Running' contracts
        query = """
            SELECT ContractId, ContractTitle, ContractType, Roles, Skills, RequestType, 
                   Budget, ContractStartDate, ContractEndDate, Description,
                   ContractStatus, ProvidersBudget, ProvidersComment, MeetRequirement, ProvidersName
            FROM Contracts
            WHERE ContractStatus IN ('Submitted', 'Running')
            ORDER BY CreatedAt DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
            
        conn.close()
        return results
    except Exception as e:
        print(f"Error in /api/providers/contracts: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/providers/contracts/{contract_id}")
def update_provider_contract(contract_id: str, update: ProviderUpdate):
    """
    Updates providersBudget, providersComment and meetRequirement for a contract.
    This endpoint is used by providers to submit their offers.
    It also attempts to sync the data back to Camunda process variables if an active instance is found.
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        # Check if contract exists
        cursor.execute("SELECT ContractId, ContractStatus FROM Contracts WHERE ContractId = ?", contract_id)
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Contract with ID {contract_id} not found")
            
        # Update fields in DB
        query = """
            UPDATE Contracts
            SET ContractStatus = 'Running', ProvidersBudget = ?, ProvidersComment = ?, MeetRequirement = ?, ProvidersName = ?
            WHERE ContractId = ?
        """
        cursor.execute(query, update.providersBudget, update.providersComment, update.meetRequirement, update.providersName, contract_id)
        conn.commit()
        conn.close()

        # Camunda Sync: Try to find and update process variables
        try:
            print(f"[Camunda Sync] Looking for ACTIVE instances with contractId={contract_id}...", flush=True)
            # Find all active process instances with this contractId
            search_url = f"{CAMUNDA_URL}/process-instance?variables=contractId_eq_{contract_id}&active=true"
            instances_res = requests.get(search_url)
            active_instances = instances_res.json()
            
            if not active_instances:
                 print(f"[Camunda Sync] No ACTIVE process instances found. Checking history for fallback...")
                 fallback_res = requests.get(f"{CAMUNDA_URL}/variable-instance?variableName=contractId&variableValue={contract_id}")
                 active_instances = [{"id": v["processInstanceId"]} for v in fallback_res.json()[:1]] # Use first one from history as fallback

            if active_instances:
                print(f"[Camunda Sync] Syncing to {len(active_instances)} instance(s)...", flush=True)
                
                # Prepare variables
                modifications = {}
                if update.providersName is not None:
                    modifications["providersName"] = {"value": str(update.providersName), "type": "String"}
                if update.providersBudget is not None:
                    modifications["providersBudget"] = {"value": int(update.providersBudget), "type": "Integer"}
                if update.providersComment is not None:
                    modifications["providersComment"] = {"value": str(update.providersComment), "type": "String"}
                if update.meetRequirement is not None:
                    modifications["meetRequirement"] = {"value": str(update.meetRequirement), "type": "String"}

                if modifications:
                    var_payload = {"modifications": modifications}
                    for inst in active_instances:
                        inst_id = inst.get("id") or inst.get("processInstanceId")
                        if not inst_id: continue
                        
                        resp = requests.post(f"{CAMUNDA_URL}/process-instance/{inst_id}/variables", json=var_payload)
                        if resp.status_code >= 400:
                            print(f"[Camunda Sync] ERROR for {inst_id}: {resp.status_code} - {resp.text}", flush=True)
                        else:
                            print(f"[Camunda Sync] SUCCESS: Pushed variables to {inst_id}", flush=True)
            else:
                print(f"[Camunda Sync] CRITICAL: No instance found at all for contractId={contract_id}", flush=True)
        except Exception as camunda_err:
            print(f"Warning: Failed to sync with Camunda: {camunda_err}", file=sys.stderr)

        return {
            "status": "success",
            "message": "Contract updated and synced successfully",
            "contractId": contract_id,
            "updatedFields": {
                "providersBudget": update.providersBudget,
                "providersComment": update.providersComment,
                "meetRequirement": update.meetRequirement,
                "providersName": update.providersName
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in PATCH /api/providers/contracts: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-process")
def start_process(data: dict):
    """
    Starts the Camunda process and passes initial variables.
    """
    # Note: contractId is NOT generated here, it's generated by the store-create-contract-worker
    payload = {
        "variables": {
            "contractTitle": {"value": data.get("contractTitle"), "type": "String"},
            "requestedBy": {"value": data.get("requestedBy"), "type": "String"},
        }
    }
    
    try:
        print(f"Starting process in Camunda: {data.get('contractTitle')}")
        res = requests.post(
            f"{CAMUNDA_URL}/process-definition/key/contractTool/start",
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        return {"camunda_response": res.json()}
    except Exception as e:
        print(f"Failed to start Camunda process: {e}", file=sys.stderr)
        return {"error": str(e)}
