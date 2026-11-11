"""Camada de acesso SQLite do MBF Stock.

Centraliza abertura de conexões e inspeção de esquema; não contém rotas HTTP.
O caminho do banco é injetado para permitir testes com arquivos temporários.
"""
import sqlite3


def open_connection(database_path):
    connection = sqlite3.connect(database_path, timeout=10)
    connection.execute('PRAGMA foreign_keys = ON')
    connection.execute('PRAGMA busy_timeout = 10000')
    connection.row_factory = sqlite3.Row
    return connection


def ensure_column(cursor, table, column, definition):
    # Apenas identificadores internos e fixos devem ser passados pelo chamador.
    columns = [row['name'] for row in cursor.execute(f'PRAGMA table_info({table})').fetchall()]
    if column not in columns:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
