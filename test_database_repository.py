"""Testes da camada de persistência isolada."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from database_repository import open_connection, ensure_column


class DatabaseRepositoryTests(unittest.TestCase):
    def test_foreign_keys_and_busy_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            con = open_connection(Path(tmp) / 'repo.db')
            try:
                self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0], 1)
                self.assertEqual(con.execute('PRAGMA busy_timeout').fetchone()[0], 10000)
            finally:
                con.close()

    def test_ensure_column_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            con = open_connection(Path(tmp) / 'repo.db')
            try:
                cur = con.cursor()
                cur.execute('CREATE TABLE sample (id INTEGER PRIMARY KEY)')
                ensure_column(cur, 'sample', 'label', "TEXT DEFAULT ''")
                ensure_column(cur, 'sample', 'label', "TEXT DEFAULT ''")
                columns = [row['name'] for row in cur.execute('PRAGMA table_info(sample)')]
                self.assertEqual(columns.count('label'), 1)
            finally:
                con.close()
