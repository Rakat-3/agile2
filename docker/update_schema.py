
import pyodbc
import os

def env(name):
    # Retrieve from OS (Docker env)
    return os.getenv(name)

def main():
    server = env("AZURE_SQL_SERVER")
    database = env("AZURE_SQL_DATABASE")
    user = env("AZURE_SQL_USER")
    password = env("AZURE_SQL_PASSWORD")

    if not all([server, database, user, password]):
        print("Missing DB credentials in env")
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

    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # Add ContractStatus
        try:
            print("Adding ContractStatus...")
            cursor.execute("ALTER TABLE CreatedContracts ADD ContractStatus NVARCHAR(50) DEFAULT 'Running' WITH VALUES")
            print("Done.")
        except Exception as e:
            print(f"ContractStatus error (maybe exists): {e}")

        # Add ProvidersBudget
        try:
            print("Adding ProvidersBudget...")
            cursor.execute("ALTER TABLE CreatedContracts ADD ProvidersBudget INT NULL")
            print("Done.")
        except Exception as e:
            print(f"ProvidersBudget error (maybe exists): {e}")

        # Add ProvidersComment
        try:
            print("Adding ProvidersComment...")
            cursor.execute("ALTER TABLE CreatedContracts ADD ProvidersComment NVARCHAR(MAX) NULL")
            print("Done.")
        except Exception as e:
            print(f"ProvidersComment error (maybe exists): {e}")

        conn.close()

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
