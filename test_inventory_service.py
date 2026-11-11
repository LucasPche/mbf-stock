"""Testes das regras de estoque, isolados do HTTP."""
import sqlite3
import unittest
from inventory_service import stock_adjustment, reserve_withdrawal


class InventoryServiceTests(unittest.TestCase):
    def test_entrada(self):
        self.assertEqual(stock_adjustment(10, 15), ("entrada", 5))

    def test_saida(self):
        self.assertEqual(stock_adjustment(15, 12), ("saida", 3))

    def test_sem_movimento(self):
        self.assertIsNone(stock_adjustment(12, 12))

    def test_baixa_atomica_e_saldo_insuficiente(self):
        with sqlite3.connect(":memory:") as con:
            con.execute("CREATE TABLE parts (id INTEGER PRIMARY KEY, quantity INTEGER NOT NULL)")
            con.execute("INSERT INTO parts VALUES (1, 3)")
            cur = con.cursor()
            self.assertTrue(reserve_withdrawal(cur, 1, 2))
            self.assertFalse(reserve_withdrawal(cur, 1, 2))
            self.assertFalse(reserve_withdrawal(cur, 999, 1))
            self.assertEqual(con.execute("SELECT quantity FROM parts WHERE id=1").fetchone()[0], 1)

    def test_quantidade_invalida(self):
        with sqlite3.connect(":memory:") as con:
            for value in (0, -1, True, "3"):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    reserve_withdrawal(con.cursor(), 1, value)
