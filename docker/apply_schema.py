import os
import pyodbc 

def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

def env(name: str) -> str:
    v = os.getenv(name)
    if v is None: raise RuntimeError(f"Missing env var: {name}")
    return v

def sql_conn():
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{env('AZURE_SQL_SERVER')},1433;"
        f"Database={env('AZURE_SQL_DATABASE')};"
        f"Uid={env('AZURE_SQL_USER')};"
        f"Pwd={env('AZURE_SQL_PASSWORD')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def main():
    load_env_file()
    sql_file = os.path.join(os.path.dirname(__file__), "create_tables.sql")
    with open(sql_file, "r") as f: batches = f.read().split("GO")
    
    print("Applying schema...")
    with sql_conn() as conn:
        cursor = conn.cursor()
        for i, batch in enumerate(batches):
            if batch.strip():
                print(f"Batch {i}: {batch[:50]}...")
                try:
                    cursor.execute(batch)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing batch {i}: {e}")
    print("Schema applied.")

if __name__ == "__main__":
    main()
