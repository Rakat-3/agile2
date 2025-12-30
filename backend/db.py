import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        database=os.getenv("DB_NAME", "camundaDB"),
        user=os.getenv("DB_USER", "camunda"),
        password=os.getenv("DB_PASSWORD", "camunda"),
        host=os.getenv("DB_HOST", "postgres"),  # IMPORTANT: docker hostname
        port=os.getenv("DB_PORT", "5432")
    )
