import psycopg2
from psycopg2 import OperationalError

def get_connection():
    try:
        conn = psycopg2.connect(
            host="aws-0-ap-south-1.pooler.supabase.com",      
            database="postgres",  
            port="6543",           
            user="postgres.qfrlbhpyohtyvwegzvbl",           
            password="Arulmozhi2007."
        )
        print("Connection successful")
        return conn
    except OperationalError as e:
        print("Error:", e)
        return None

