
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from auditar_banco import audit_database


class TestAuditoriaBanco(unittest.TestCase):

    def test_detecta_restricoes_ausentes(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "old.db"

            with closing(sqlite3.connect(db)) as con:
                con.execute(
                    "CREATE TABLE parts (id INTEGER PRIMARY KEY, quantity INTEGER)"
                )
                con.execute(
                    "CREATE TABLE requests (id INTEGER PRIMARY KEY, quantity INTEGER)"
                )
                con.execute(
                    "CREATE TABLE movements (id INTEGER PRIMARY KEY, quantity INTEGER)"
                )
                con.commit()

            result = audit_database(db)
            self.assertTrue(result["migration_required"])
            self.assertFalse(
                result["constraints"]["parts"]["CHECK(quantity >= 0)"]
            )

    def test_detecta_dados_invalidos_em_banco_legado(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "legacy.db"

            with closing(sqlite3.connect(db)) as con:
                con.execute(
                    "CREATE TABLE parts (id INTEGER PRIMARY KEY, "
                    "quantity INTEGER, min_quantity INTEGER, unit_price REAL)"
                )
                con.execute(
                    "CREATE TABLE requests (id INTEGER PRIMARY KEY, quantity INTEGER)"
                )
                con.execute(
                    "CREATE TABLE movements (id INTEGER PRIMARY KEY, quantity INTEGER)"
                )
                con.execute(
                    "INSERT INTO parts(quantity, min_quantity, unit_price) "
                    "VALUES (-3, 1, -5)"
                )
                con.execute(
                    "INSERT INTO requests(quantity) VALUES (0)"
                )
                con.execute(
                    "INSERT INTO movements(quantity) VALUES (-1)"
                )
                con.commit()

            result = audit_database(db)
            self.assertEqual(result["integrity_check"], "ok")
            self.assertEqual(
                result["invalid_value_counts"]["parts.quantity"], 1
            )
            self.assertEqual(
                result["invalid_value_counts"]["parts.unit_price"], 1
            )
            self.assertEqual(
                result["invalid_value_counts"]["requests.quantity"], 1
            )
            self.assertEqual(
                result["invalid_value_counts"]["movements.quantity"], 1
            )
            self.assertTrue(result["migration_required"])

    def test_nao_cria_banco_ausente(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "missing.db"

            with self.assertRaises(FileNotFoundError):
                audit_database(db)

            self.assertFalse(db.exists())

    def test_detecta_violacao_de_chave_estrangeira(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "broken.db"

            with closing(sqlite3.connect(db)) as con:
                con.execute(
                    "CREATE TABLE parts ("
                    "id INTEGER PRIMARY KEY, "
                    "quantity INTEGER CHECK(quantity >= 0), "
                    "min_quantity INTEGER CHECK(min_quantity >= 0), "
                    "unit_price REAL CHECK(unit_price >= 0))"
                )
                con.execute(
                    "CREATE TABLE requests ("
                    "id INTEGER PRIMARY KEY, "
                    "part_id INTEGER REFERENCES parts(id), "
                    "quantity INTEGER CHECK(quantity > 0))"
                )
                con.execute(
                    "CREATE TABLE movements ("
                    "id INTEGER PRIMARY KEY, "
                    "quantity INTEGER CHECK(quantity > 0))"
                )
                con.execute(
                    "INSERT INTO requests(id, part_id, quantity) "
                    "VALUES (1, 999, 1)"
                )
                con.commit()

            result = audit_database(db)
            self.assertEqual(result["foreign_key_violations"], 1)
            self.assertTrue(result["migration_required"])


if __name__ == "__main__":
    unittest.main()
