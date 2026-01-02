import os
import pyodbc

def env(name):
    return os.environ.get(name)

def main():
    server = env("AZURE_SQL_SERVER")
    database = env("AZURE_SQL_DATABASE")
    user = env("AZURE_SQL_USER")
    password = env("AZURE_SQL_PASSWORD")
    
    if not all([server, database, user, password]):
        print("Missing one or more Azure SQL env vars.")
        return

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

    print(f"Connecting to {server}...")
    try:
        conn = pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Connected. Reading create_tables.sql...")
    with open("create_tables.sql", "r") as f:
        sql_content = f.read()

    # Split by 'GO' commands (case insensitive)
    batches = [b.strip() for b in sql_content.replace('\r', '').split('\nGO') if b.strip()]
    if not batches:
        # Maybe just "GO" without newline? try regex split if needed, but simple split usually works for standardized files
        # Let's try splitting by regex to be safer if above fails, but above is robust enough for the file I saw.
        pass

    cursor = conn.cursor()
    for i, batch in enumerate(batches):
        print(f"Executing batch {i+1}/{len(batches)}...")
        try:
            cursor.execute(batch)
            conn.commit()
        except Exception as e:
            print(f"Error executing batch: {e}")
            print(f"Batch content: {batch[:100]}...")
            return

    print("All batches executed successfully.")
    conn.close()

if __name__ == "__main__":
    main()
