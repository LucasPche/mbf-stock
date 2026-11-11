"""Testes de integração: servidor HTTP real com banco temporário isolado."""
import http.client
import json
import os
import tempfile
import threading
import unittest
from contextlib import closing
from pathlib import Path
from http.server import ThreadingHTTPServer
import server

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.original_db = server.DB
        cls.original_admin = os.environ.get('MBF_ADMIN_PASSWORD')
        cls.original_operator = os.environ.get('MBF_OPERADOR_PASSWORD')
        server.DB = Path(cls.tmp.name) / 'test.db'
        os.environ['MBF_ADMIN_PASSWORD'] = 'AdminTeste123!'
        os.environ['MBF_OPERADOR_PASSWORD'] = 'OperadorTeste123!'
        server.init_db()
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=3)
        server.DB = cls.original_db
        server.SESSIONS.clear()
        for key, value in [('MBF_ADMIN_PASSWORD', cls.original_admin), ('MBF_OPERADOR_PASSWORD', cls.original_operator)]:
            if value is None: os.environ.pop(key, None)
            else: os.environ[key] = value
        cls.tmp.cleanup()

    def request(self, method, path, payload=None, token=None):
        con = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port, timeout=5)
        headers = {}
        if token: headers['X-Session-Token'] = token
        if payload is not None: headers['Content-Type'] = 'application/json'
        body = json.dumps(payload) if payload is not None else None
        try:
            con.request(method, path, body=body, headers=headers)
            response = con.getresponse()
            return response.status, json.loads(response.read().decode())
        finally:
            con.close()

    def login(self, username, password):
        status, body = self.request('POST', '/api/login', {'username': username, 'password': password})
        self.assertEqual(status, 200)
        return body['token']

    def test_consulta_sessao_fecha_conexao(self):
        """Cada consulta autenticada deve fechar a conexão SQLite utilizada."""
        from unittest.mock import patch
        token = self.login('operador', 'OperadorTeste123!')
        real_connect = server.connect
        opened = []

        class ConnectionProxy:
            def __init__(self, conn):
                self.conn = conn
                self.closed = False

            def __getattr__(self, name):
                return getattr(self.conn, name)

            def close(self):
                self.closed = True
                self.conn.close()

        def tracked_connect():
            conn = ConnectionProxy(real_connect())
            opened.append(conn)
            return conn

        with patch.object(server, 'connect', side_effect=tracked_connect):
            status, _ = self.request('GET', '/api/me', token=token)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(opened), 1)
        # A resposta HTTP pode chegar antes do finally do handler terminar.
        import time
        for _ in range(100):
            if all(c.closed for c in opened):
                break
            time.sleep(0.01)
        self.assertTrue(all(c.closed for c in opened))

    def test_login_e_senha_incorreta(self):
        self.assertEqual(self.request('POST', '/api/login', {'username':'admin','password':'errada'})[0], 401)
        self.assertEqual(self.request('GET', '/api/parts')[0], 401)

    def test_permissoes_de_operador(self):
        token = self.login('operador','OperadorTeste123!')
        self.assertEqual(self.request('GET','/api/users', token=token)[0],403)
        self.assertEqual(self.request('POST','/api/parts', {},token)[0],403)
        self.assertEqual(self.request('GET','/api/parts',token=token)[0],200)

    def test_ids_invalidos_nao_quebram_servidor(self):
        token = self.login('admin','AdminTeste123!')
        for path in ['/api/users/abc','/api/requests/abc','/api/signup-requests/abc']:
            with self.subTest(path=path):
                self.assertEqual(self.request('PUT',path,{},token)[0],400)
        self.assertEqual(self.request('DELETE','/api/users/abc',token=token)[0],400)

    def test_criacao_edicao_peca_e_historico(self):
        token = self.login('admin','AdminTeste123!')
        payload={'code':'TESTE-999','name':'Peca teste','category':'Teste','location':'Sala 1','quantity':10,'min_quantity':2,'unit':'un'}
        self.assertEqual(self.request('POST','/api/parts',payload,token)[0],200)
        status,body=self.request('GET','/api/parts',token=token)
        part=next(x for x in body['parts'] if x['code']=='TESTE-999')
        payload['quantity']=15
        self.assertEqual(self.request('PUT',f"/api/parts/{part['id']}",payload,token)[0],200)
        status,body=self.request('GET','/api/movements',token=token)
        self.assertTrue(any(x['part_id']==part['id'] and x['quantity']==5 and x['type']=='entrada' for x in body['movements']))
        self.assertEqual(self.request('DELETE',f"/api/parts/{part['id']}",token=token)[0],200)
        status, body = self.request('GET', '/api/parts', token=token)
        self.assertEqual(status, 200)
        self.assertFalse(any(p['id'] == part['id'] for p in body['parts']))
        status, body = self.request('GET', '/api/movements', token=token)
        self.assertTrue(any(m['part_id'] == part['id'] and m['type'] == 'exclusao' for m in body['movements']))

    def test_solicitacao_aprovacao_e_baixa(self):
        operator=self.login('operador','OperadorTeste123!')
        admin=self.login('admin','AdminTeste123!')
        status,body=self.request('GET','/api/parts',token=operator)
        part=next(x for x in body['parts'] if x['code']=='MBF-001')
        old=part['quantity']
        self.assertEqual(self.request('POST','/api/requests',{'part_id':part['id'],'quantity':3},operator)[0],200)
        status,body=self.request('GET','/api/requests',token=admin)
        req=next(x for x in body['requests'] if x['part_id']==part['id'] and x['status']=='pendente')
        self.assertEqual(self.request('PUT',f"/api/requests/{req['id']}",{'status':'aprovado'},admin)[0],200)
        status,body=self.request('GET','/api/parts',token=admin)
        self.assertEqual(next(x for x in body['parts'] if x['id']==part['id'])['quantity'],old-3)
        self.assertEqual(self.request('PUT',f"/api/requests/{req['id']}",{'status':'aprovado'},admin)[0],400)

    def test_solicitacao_invalida(self):
        operator=self.login('operador','OperadorTeste123!')
        for payload in [{'part_id':'abc','quantity':1},{'part_id':1,'quantity':'x'},{'part_id':1,'quantity':-1}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.request('POST','/api/requests',payload,operator)[0],400)

    def test_logout(self):
        token=self.login('operador','OperadorTeste123!')
        self.assertEqual(self.request('POST','/api/logout',{},token)[0],200)
        self.assertEqual(self.request('GET','/api/me',token=token)[0],401)

    def test_json_malformado_retorna_400(self):
        con = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port, timeout=5)
        try:
            con.request('POST', '/api/login', body='{', headers={'Content-Type': 'application/json'})
            response = con.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            con.close()

    def test_corpo_json_lista_retorna_400(self):
        con = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port, timeout=5)
        try:
            con.request('POST', '/api/login', body='[]', headers={'Content-Type': 'application/json'})
            response = con.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            con.close()

    def test_aprovacao_sem_saldo_nao_baixa_estoque(self):
        operator = self.login('operador', 'OperadorTeste123!')
        admin = self.login('admin', 'AdminTeste123!')
        status, body = self.request('GET', '/api/parts', token=operator)
        part = next(x for x in body['parts'] if x['code'] == 'MBF-002')
        initial = part['quantity']
        self.assertEqual(self.request('POST', '/api/requests', {'part_id':part['id'], 'quantity':initial+9999}, operator)[0], 200)
        _, body = self.request('GET', '/api/requests', token=admin)
        req = next(x for x in body['requests'] if x['part_id'] == part['id'] and x['status'] == 'pendente' and x['quantity'] == initial+9999)
        self.assertEqual(self.request('PUT', f"/api/requests/{req['id']}", {'status':'aprovado'}, admin)[0], 400)
        _, body = self.request('GET', '/api/parts', token=admin)
        self.assertEqual(next(x for x in body['parts'] if x['id'] == part['id'])['quantity'], initial)

    def test_sessao_bloqueada_e_revogada(self):
        operator = self.login('operador', 'OperadorTeste123!')
        with closing(server.connect()) as con:
            con.execute("UPDATE users SET active = 0 WHERE username = 'operador'")
            con.commit()

        try:
            self.assertEqual(self.request('GET', '/api/parts', token=operator)[0], 401)
        finally:
            with closing(server.connect()) as con:
                con.execute("UPDATE users SET active = 1 WHERE username = 'operador'")
                con.commit()

    def test_arquivo_privado_nao_e_servido(self):
        con = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port, timeout=5)
        try:
            con.request('GET', '/%2e%2e/server.py')
            response = con.getresponse()
            self.assertEqual(response.status, 404)
            response.read()
        finally:
            con.close()

    def test_rejeicao_nao_altera_saldo(self):
        operador = self.login('operador', 'OperadorTeste123!')
        admin = self.login('admin', 'AdminTeste123!')
        _, dados = self.request('GET', '/api/parts', token=operador)
        peca = next(p for p in dados['parts'] if p['code'] == 'MBF-003')
        saldo = peca['quantity']
        self.assertEqual(self.request('POST', '/api/requests', {'part_id': peca['id'], 'quantity': 2}, operador)[0], 200)
        _, dados = self.request('GET', '/api/requests', token=admin)
        pedido = next(r for r in dados['requests'] if r['part_id'] == peca['id'] and r['status'] == 'pendente' and r['quantity'] == 2)
        self.assertEqual(self.request('PUT', f"/api/requests/{pedido['id']}", {'status': 'rejeitado', 'admin_note': 'Teste automatizado'}, admin)[0], 200)
        _, dados = self.request('GET', '/api/parts', token=admin)
        self.assertEqual(next(p for p in dados['parts'] if p['id'] == peca['id'])['quantity'], saldo)
        _, dados = self.request('GET', '/api/requests', token=admin)
        self.assertEqual(next(r for r in dados['requests'] if r['id'] == pedido['id'])['status'], 'rejeitado')

    def test_integridade_referencial_banco(self):
        with closing(server.connect()) as con:
            self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_rotas_inexistentes_retornam_404(self):
        admin = self.login('admin', 'AdminTeste123!')
        self.assertEqual(self.request('GET', '/api/rota-inexistente', token=admin)[0], 404)
