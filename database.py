import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os



def conectar():
    try:
        conn = psycopg2.connect(
            user="postgres.qsqajbcsbuezstvnaofj",
            password=os.environ["SENHA"],
            host="aws-0-sa-east-1.pooler.supabase.com",
            port="6543",
            dbname="postgres",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        raise
