"""Conexões SQLite locais ou PostgreSQL remoto (Supabase).

A seleção do backend é feita exclusivamente por DATABASE_URL.
Nunca registre a URL, pois ela contém credenciais.
"""
import os
import sqlite3
from pathlib import Path

def using_postgres():
    return bool(os.environ.get("DATABASE_URL"))

def _sql(sql):
    # As consultas do projeto usam placeholders SQLite ('?').
    # Não há placeholders dentro de literais SQL nas consultas atuais.
    return sql.replace("?", "%s")

class PostgresCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def execute(self, sql, params=None):
        sql = _sql(sql)
        self.lastrowid = None
        if sql.lstrip().upper().startswith("INSERT INTO PARTS "):
            self._cursor.execute(sql + " RETURNING id", params)
            self.lastrowid = self._cursor.fetchone()["id"]
        else:
            self._cursor.execute(sql, params)
        return self

    def executemany(self, sql, values):
        self._cursor.executemany(_sql(sql), values)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def executescript(self, sql):
        # O esquema SQLite original não é válido no PostgreSQL.
        schema = Path(__file__).parent / "supabase" / "schema.sql"
        self._cursor.execute(schema.read_text(encoding="utf-8"))
        return self

    def close(self):
        self._cursor.close()

class PostgresConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

def open_connection(database_path):
    url = os.environ.get("DATABASE_URL")
    if url:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("Instale as dependências: pip install -r requirements.txt") from exc
        connection = psycopg.connect(url, row_factory=dict_row, connect_timeout=10, sslmode="require")
        return PostgresConnection(connection)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.row_factory = sqlite3.Row
    return connection

def ensure_column(cursor, table, column, definition):
    if using_postgres():
        if (table, column) not in {
            ("users", "sector"), ("users", "active"), ("users", "terms_accepted_at"),
            ("signup_requests", "terms_accepted_at"),
            ("parts", "supplier"), ("parts", "unit_price"), ("parts", "entry_date"),
            ("parts", "deleted_at"), ("parts", "deleted_by")
        }:
            raise ValueError("Identificador de esquema não permitido")
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = ?",
            (table,),
        )
        existing = {row["column_name"] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        return
    columns = [row["name"] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

def database_errors():
    errors = [sqlite3.Error]
    if using_postgres():
        import psycopg
        errors.append(psycopg.Error)
    return tuple(errors)
