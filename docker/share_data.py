import os
import pyodbc

# Try to load .env manually since we don't have python-dotenv installed
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

def env(name: str) -> str:
    v = os.getenv(name)
    if v is None:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def sql_conn():
    server = env("AZURE_SQL_SERVER")
    database = env("AZURE_SQL_DATABASE")
    user = env("AZURE_SQL_USER")
    password = env("AZURE_SQL_PASSWORD")

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        f"Uid={user};"
        f"Pwd={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def print_table(cursor, table_name, query):
    print(f"\n--- {table_name} ---")
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("(No data)")
            return

        # Get column names
        columns = [column[0] for column in cursor.description]
        print(f"Columns: {', '.join(columns)}")
        print("-" * 50)
        
        for row in rows:
            print(row)
            
    except Exception as e:
        print(f"Error reading {table_name}: {e}")

def main():
    load_env_file()
    
    try:
        print("Connecting to Azure SQL...")
        with sql_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Created Contracts
            print_table(cursor, "CreatedContracts", 
                        "SELECT ContractId, ContractTitle, ContractType, Status = 'Submitted', CreatedAt FROM CreatedContracts")

            # 2. Approved Contracts
            print_table(cursor, "ApprovedContracts", 
                        "SELECT ContractId, ContractTitle, SignedDate, ApprovedAt FROM ApprovedContracts")

            # 3. Rejected Contracts
            print_table(cursor, "RejectedContracts", 
                        "SELECT ContractId, ContractTitle, LegalComment, RejectedAt FROM RejectedContracts")
                        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("Ensure you have set the .env variables correctly.")

if __name__ == "__main__":
    main()
