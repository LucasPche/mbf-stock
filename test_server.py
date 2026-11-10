import unittest
from server import validar_id


class TestValidarID(unittest.TestCase):

    def test_id_valido(self):
        self.assertEqual(validar_id(1), 1)

    def test_id_com_texto_numerico(self):
        self.assertEqual(validar_id("10"), 10)

    def test_id_com_letras(self):
        self.assertIsNone(validar_id("abc"))

    def test_id_negativo(self):
        self.assertIsNone(validar_id(-5))

    def test_id_zero(self):
        self.assertIsNone(validar_id(0))

    def test_id_vazio(self):
        self.assertIsNone(validar_id(None))


if __name__ == "__main__":
    unittest.main()