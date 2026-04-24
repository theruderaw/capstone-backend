import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "capstone"),
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "rudra"),
        password=os.getenv("DB_PASS", "hello"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    return conn

