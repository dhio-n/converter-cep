import psycopg2
from psycopg2.extras import RealDictCursor
import os

def conectar():
    try:
        password = os.getenv("SENHA")
        if not password:
            raise ValueError("A variável de ambiente 'SENHA' não foi definida.")

        conn = psycopg2.connect(
            user="postgres.qsqajbcsbuezstvnaofj",
            password=password,
            host="aws-0-sa-east-1.pooler.supabase.com",
            port="6543",
            dbname="postgres",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        raise
