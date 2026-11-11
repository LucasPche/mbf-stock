"""Restrições de integridade verificadas em um banco novo e isolado."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import server


class DatabaseConstraintsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "isolado.db"
        self.db_patch = patch.object(server, "DB", self.db)
        self.db_patch.start()
        with patch.dict(os.environ, {"MBF_ADMIN_PASSWORD": "AdminForte123!", "MBF_OPERADOR_PASSWORD": "OperadorForte123!"}):
            server.init_db()
        self.con = server.connect()

    def tearDown(self):
        self.con.close()
        self.db_patch.stop()
        self.temp.cleanup()

    def test_peca_nao_aceita_estoque_negativo(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("UPDATE parts SET quantity = -1 WHERE id = 1")

    def test_peca_nao_aceita_minimo_negativo(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("UPDATE parts SET min_quantity = -1 WHERE id = 1")

    def test_peca_nao_aceita_preco_negativo(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("UPDATE parts SET unit_price = -1 WHERE id = 1")

    def test_solicitacao_nao_aceita_quantidade_zero(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO requests (user_id,part_id,quantity) VALUES (1,1,0)")

    def test_movimentacao_nao_aceita_quantidade_negativa(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO movements (part_id,user_id,type,quantity) VALUES (1,1,'saida',-2)")

    def test_solicitacao_nao_aceita_peca_inexistente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO requests (user_id,part_id,quantity) VALUES (1,999999,1)")


if __name__ == "__main__":
    unittest.main()
