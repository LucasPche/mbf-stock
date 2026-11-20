"""Teste de conexão ao PostgreSQL sem alterar dados.

Uso: pip install 'psycopg[binary]'
     DATABASE_URL=... python supabase/check_connection.py
"""
import os
import sys
from urllib.parse import urlsplit

def main():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("ERRO: DATABASE_URL não configurada.")
        return 2
    parsed = urlsplit(url)
    if parsed.scheme not in ("postgresql", "postgres"):
        print("ERRO: DATABASE_URL não é uma URL PostgreSQL.")
        return 2
    try:
        import psycopg
    except ImportError:
        print("ERRO: instale psycopg[binary] antes de testar.")
        return 2
    try:
        with psycopg.connect(url, connect_timeout=10, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user")
                database, _ = cur.fetchone()
                cur.execute("""SELECT table_name FROM information_schema.tables
                               WHERE table_schema='public'
                                 AND table_name = ANY(%s)""",
                            (["users", "parts", "requests", "movements", "signup_requests"],))
                existing = {row[0] for row in cur.fetchall()}
                expected = {"users", "parts", "requests", "movements", "signup_requests"}
                print("Conexão TLS ao PostgreSQL OK. Banco:", database)
                print("Tabelas:", ", ".join(sorted(existing)) or "(nenhuma)")
                missing = expected - existing
                if missing:
                    print("FALTAM:", ", ".join(sorted(missing)))
                    return 1
                print("Esquema básico encontrado. Isto NÃO valida a migração do servidor.")
                return 0
    except Exception as exc:
        print("Falha na conexão:", type(exc).__name__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
