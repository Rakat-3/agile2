import socket
import sys

host = "rakat-sqlsrv-01.database.windows.net"
port = 1433

print(f"Testing connection to {host}:{port}...")
try:
    sock = socket.create_connection((host, port), timeout=10)
    print("SUCCESS: Connection established!")
    sock.close()
except socket.error as e:
    print(f"FAILURE: Could not connect. Error: {e}")
