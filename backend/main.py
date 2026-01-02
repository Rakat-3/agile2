from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection, get_azure_connection
import sys

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
    Returns counts for Created, Approved, and Rejected contracts from Azure SQL.
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM CreatedContracts")
        created_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ApprovedContracts")
        approved_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM RejectedContracts")
        rejected_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "submitted": created_count,
            "approved": approved_count,
            "rejected": rejected_count
        }
    except Exception as e:
        print(f"Error in /stats: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contracts/{status}")
def get_contracts(status: str):
    """
    Returns list of contracts based on status: 'submitted', 'approved', 'rejected'.
    """
    status = status.lower()
    table_map = {
        "submitted": "CreatedContracts",
        "approved": "ApprovedContracts",
        "rejected": "RejectedContracts"
    }
    
    if status not in table_map:
        raise HTTPException(status_code=400, detail="Invalid status. Must be submitted, approved, or rejected.")
    
    table_name = table_map[status]
    
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        # Select relevant columns. This assumes standard columns available across tables or specific ones per table.
        # For simplicity, we'll fetch common ones + extras.
        if status == "submitted":
            query = "SELECT ContractId, ContractTitle, ContractType, RequestType, CreatedAt FROM CreatedContracts ORDER BY CreatedAt DESC"
        elif status == "approved":
            query = "SELECT ContractId, ContractTitle, ContractType, VersionNumber, SignedDate, ApprovedAt FROM ApprovedContracts ORDER BY ApprovedAt DESC"
        elif status == "rejected":
            query = "SELECT ContractId, ContractTitle, LegalComment, ApprovalDecision, RejectedAt FROM RejectedContracts ORDER BY RejectedAt DESC"
            
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

@app.post("/start-process")
def start_process(data: dict):
    """
    Starts the Camunda process and passes initial variables.
    """
    payload = {
        "variables": {
            "contractTitle": {"value": data.get("contractTitle"), "type": "String"},
            "requestedBy": {"value": data.get("requestedBy"), "type": "String"},
        }
    }
    # Note: Using localhost might fail if this runs in docker and hits host's 8080,
    # but the docker-compose defines 'camunda' service. 
    # The original code had localhost. I'll rely on the existing setup or update to 'camunda' if needed.
    # For now, keeping it robust: try env var or default to service name.
    
    try:
        res = requests.post(
            f"{CAMUNDA_URL}/process-definition/key/Contract_Management_Process/start",
            json=payload,
            timeout=10
        )
        return {"camunda_response": res.json()}
    except Exception as e:
        return {"error": str(e)}