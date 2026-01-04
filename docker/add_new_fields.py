import pyodbc
import os

def env(name):
    return os.environ[name]

def main():
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

    print(f"Connecting to {server}...")
    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # List of columns to add
        columns = [
            ("EmployeeName", "NVARCHAR(255) NULL"),
            ("OfficeAddress", "NVARCHAR(255) NULL"),
            ("FinalPrice", "FLOAT NULL"),
            ("MeetRequirement", "NVARCHAR(50) NULL")
        ]

        for col_name, col_type in columns:
            try:
                print(f"Adding column {col_name}...")
                cursor.execute(f"ALTER TABLE Contracts ADD {col_name} {col_type}")
                print(f"Successfully added {col_name}")
            except pyodbc.ProgrammingError as e:
                if "Column already exists" in str(e) or "42S21" in str(e): # 42S21 is SQLState for column already exists
                    print(f"Column {col_name} already exists. Skipping.")
                else:
                    print(f"Error adding {col_name}: {e}")

        conn.close()
        print("Schema update completed.")
    except Exception as e:
        print(f"Connection failed or error occurred: {e}")

if __name__ == "__main__":
    main()
