import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    conn = psycopg2.connect(
        dbname="capstone",
        host="localhost",
        user="rudra",
        password="hello",
        port="5432"
    )
    
    return conn

