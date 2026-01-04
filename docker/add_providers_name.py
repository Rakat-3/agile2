
import pyodbc
import os

def env(name):
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def main():
    try:
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

        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Adding ProvidersName column to Contracts table...")
        try:
            cursor.execute("ALTER TABLE Contracts ADD ProvidersName NVARCHAR(255) NULL")
            print("Successfully added ProvidersName column.")
        except Exception as e:
            if "already exists" in str(e) or "42S21" in str(e):
                print("Column ProvidersName already exists.")
            else:
                raise e

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
