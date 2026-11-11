import unittest
from server import validar_id, password_hash, check_password


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

class TestSenhas(unittest.TestCase):

    def test_senha_correta(self):
        senha = "SenhaSegura123"
        hash_gerado = password_hash(senha)

        self.assertTrue(check_password(senha, hash_gerado))

    def test_senha_incorreta(self):
        hash_gerado = password_hash("SenhaCorreta123")

        self.assertFalse(check_password("SenhaErrada123", hash_gerado))

    def test_senha_nao_armazenada_em_texto(self):
        senha = "MinhaSenha123"
        hash_gerado = password_hash(senha)

        self.assertNotEqual(hash_gerado, senha)

    def test_salts_diferentes(self):
        senha = "Senha123"

        hash1 = password_hash(senha)
        hash2 = password_hash(senha)

        self.assertNotEqual(hash1, hash2)
class TestBancoDados(unittest.TestCase):

    def test_conexao_banco(self):
        from server import connect
        con = connect()
        self.assertIsNotNone(con)
        con.close()

    def test_chaves_estrangeiras(self):
        from server import connect
        con = connect()
        resultado = con.execute("PRAGMA foreign_keys").fetchone()[0]
        self.assertEqual(resultado, 1)
        con.close()
if __name__ == "__main__":
    unittest.main()