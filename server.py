from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import json
import secrets
import sqlite3
import urllib.parse
import os
import logging


ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
DB = ROOT / "mbf_estoque.db"
SESSIONS = {}

logging.basicConfig(
    filename=ROOT / "mbf_auditoria.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def registrar_log(acao, usuario="sistema", detalhes=""):
    logging.info(
        "Usuario: %s | Acao: %s | Detalhes: %s",
        usuario,
        acao,
        detalhes
    )

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return f"{salt}${digest}"


def check_password(password, stored):
    salt, digest = stored.split("$", 1)
    return password_hash(password, salt).split("$", 1)[1] == digest


def ensure_column(cur, table, column, definition):
    columns = [row["name"] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    con = connect()
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
            sector TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            min_quantity INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'un',
            supplier TEXT DEFAULT '',
            unit_price REAL NOT NULL DEFAULT 0,
            sector TEXT DEFAULT '',
            entry_date TEXT DEFAULT '',
            description TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            comment TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pendente',
            admin_note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(part_id) REFERENCES parts(id)
        );

        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER,
            user_id INTEGER,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(part_id) REFERENCES parts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS signup_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            sector TEXT DEFAULT '',
            reason TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pendente',
            admin_note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    ensure_column(cur, "users", "sector", "TEXT DEFAULT ''")
    ensure_column(cur, "users", "active", "INTEGER NOT NULL DEFAULT 1")
    ensure_column(cur, "parts", "supplier", "TEXT DEFAULT ''")
    ensure_column(cur, "parts", "unit_price", "REAL NOT NULL DEFAULT 0")
    ensure_column(cur, "parts", "sector", "TEXT DEFAULT ''")
    ensure_column(cur, "parts", "entry_date", "TEXT DEFAULT ''")

    cur.execute("SELECT COUNT(*) AS total FROM users")
    if cur.fetchone()["total"] == 0:
        admin_password = os.environ.get("MBF_ADMIN_PASSWORD")
        operador_password = os.environ.get("MBF_OPERADOR_PASSWORD")

        if not admin_password or not operador_password:
            raise RuntimeError(
                "Configure MBF_ADMIN_PASSWORD e MBF_OPERADOR_PASSWORD "
                "antes de inicializar os usuários."
            )

        cur.executemany(
            "INSERT INTO users (name, username, password, role, sector, active) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("Administrador MBF", "admin", password_hash(admin_password), "admin", "Administracao", 1),
                ("Operador MBF", "operador", password_hash(operador_password), "user", "Producao", 1),
            ],
        )

    cur.execute("SELECT COUNT(*) AS total FROM parts")
    if cur.fetchone()["total"] == 0:
        cur.executemany(
            """
            INSERT INTO parts (code, name, category, location, quantity, min_quantity, unit, supplier, unit_price, sector, entry_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("MBF-001", "Chapa A36 3/16", "Acao", "Rua A / Box 02", 84, 40, "chapa", "Fornecedor A", 248.90, "Corte", "2026-07-01", "Chapa para corte e dobra"),
                ("MBF-002", "Barra redonda 1045 1 pol", "Acao", "Rua A / Rack 05", 18, 25, "barra", "Fornecedor B", 96.40, "Usinagem", "2026-07-02", "Uso em usinagem"),
                ("MBF-003", "Eletrodo E7018 3,25 mm", "Consumivel", "Almoxarifado solda", 12, 20, "kg", "Fornecedor C", 22.70, "Solda", "2026-07-03", "Consumivel de solda"),
                ("MBF-004", "Disco de corte 7 pol", "Consumivel", "Almoxarifado corte", 73, 35, "un", "Fornecedor C", 7.80, "Corte", "2026-07-04", "Disco para esmerilhadeira"),
                ("MBF-005", "Rolamento 6205 ZZ", "Peca", "Gaveta 12", 9, 10, "un", "Fornecedor D", 18.10, "Manutencao", "2026-07-05", "Reposicao mecanica"),
            ],
        )
    con.commit()
    con.close()


def row_dict(row):
    return dict(row) if row else None


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = urllib.parse.urlparse(path).path
        if path == "/":
            path = "/index.html"
        return str(PUBLIC / path.lstrip("/"))

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def current_user(self):
        token = self.headers.get("X-Session-Token")
        return SESSIONS.get(token)

    def require_user(self):
        user = self.current_user()
        if not user:
            self.send_json({"error": "Login necessario"}, 401)
            return None
        return user

    def require_admin(self):
        user = self.require_user()
        if not user:
            return None
        if user["role"] != "admin":
            self.send_json({"error": "Acesso restrito ao administrador"}, 403)
            return None
        return user

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/api/"):
            self.handle_api_get(path)
        else:
            super().do_GET()

    def do_POST(self):
        self.handle_api_post(urllib.parse.urlparse(self.path).path)

    def do_PUT(self):
        self.handle_api_put(urllib.parse.urlparse(self.path).path)

    def do_DELETE(self):
        self.handle_api_delete(urllib.parse.urlparse(self.path).path)

    def handle_api_get(self, path):
        user = self.require_user()
        if not user:
            return
        con = connect()
        cur = con.cursor()

        if path == "/api/me":
            self.send_json({"user": user})
        elif path == "/api/parts":
            rows = cur.execute("SELECT * FROM parts ORDER BY name").fetchall()
            self.send_json({"parts": [row_dict(row) for row in rows]})
        elif path == "/api/requests":
            if user["role"] == "admin":
                rows = cur.execute(
                    """
                    SELECT r.*, u.name AS user_name, p.name AS part_name, p.code AS part_code, p.unit AS unit
                    FROM requests r
                    JOIN users u ON u.id = r.user_id
                    JOIN parts p ON p.id = r.part_id
                    ORDER BY r.id DESC
                    """
                ).fetchall()
            else:
                rows = cur.execute(
                    """
                    SELECT r.*, u.name AS user_name, p.name AS part_name, p.code AS part_code, p.unit AS unit
                    FROM requests r
                    JOIN users u ON u.id = r.user_id
                    JOIN parts p ON p.id = r.part_id
                    WHERE r.user_id = ?
                    ORDER BY r.id DESC
                    """,
                    (user["id"],),
                ).fetchall()
            self.send_json({"requests": [row_dict(row) for row in rows]})
        elif path == "/api/movements":
            rows = cur.execute(
                """
                SELECT m.*, p.name AS part_name, u.name AS user_name
                FROM movements m
                LEFT JOIN parts p ON p.id = m.part_id
                LEFT JOIN users u ON u.id = m.user_id
                ORDER BY m.id DESC
                LIMIT 20
                """
            ).fetchall()
            self.send_json({"movements": [row_dict(row) for row in rows]})
        elif path == "/api/users":
            if user["role"] != "admin":
                self.send_json({"error": "Acesso restrito ao administrador"}, 403)
            else:
                rows = cur.execute("SELECT id, name, username, role, sector, active FROM users ORDER BY name").fetchall()
                self.send_json({"users": [row_dict(row) for row in rows]})
        elif path == "/api/signup-requests":
            if user["role"] != "admin":
                self.send_json({"error": "Acesso restrito ao administrador"}, 403)
            else:
                rows = cur.execute(
                    """
                    SELECT id, name, username, sector, reason, status, admin_note, created_at
                    FROM signup_requests
                    ORDER BY id DESC
                    """
                ).fetchall()
                self.send_json({"signup_requests": [row_dict(row) for row in rows]})
        else:
            self.send_json({"error": "Rota nao encontrada"}, 404)
        con.close()

    def handle_api_post(self, path):
        data = self.read_json()
        if path == "/api/signup":
            required = ["name", "username", "password"]
            if any(str(data.get(field, "")).strip() == "" for field in required):
                self.send_json({"error": "Preencha nome, usuario e senha"}, 400)
                return
            if len(data.get("password", "")) < 6:
                self.send_json({"error": "A senha precisa ter pelo menos 6 caracteres"}, 400)
                return
            con = connect()
            try:
                existing = con.execute(
                    """
                    SELECT username FROM users WHERE username = ?
                    UNION
                    SELECT username FROM signup_requests WHERE username = ? AND status = 'pendente'
                    """,
                    (data["username"].strip(), data["username"].strip()),
                ).fetchone()
                if existing:
                    self.send_json({"error": "Esse usuario ja existe ou ja esta aguardando liberacao"}, 409)
                    return
                con.execute(
                    """
                    INSERT INTO signup_requests (name, username, password, sector, reason)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        data["name"].strip(),
                        data["username"].strip(),
                        password_hash(data["password"]),
                        data.get("sector", "").strip(),
                        data.get("reason", "").strip(),
                    ),
                )
                con.commit()
                self.send_json({"ok": True})
            finally:
                con.close()
            return

        if path == "/api/login":
            con = connect()
            user = con.execute("SELECT * FROM users WHERE username = ?", (data.get("username"),)).fetchone()
            con.close()
            if not user or not check_password(data.get("password", ""), user["password"]):
                registrar_log("LOGIN_FALHOU", "desconhecido", "Credenciais invalidas")
                self.send_json({"error": "Usuario ou senha invalido"}, 401)
                return
            if not user["active"]:
                registrar_log("LOGIN_BLOQUEADO", user["username"], "Conta desativada")
                self.send_json({"error": "Usuario bloqueado. Procure o administrador"}, 403)
                return
            registrar_log("LOGIN_SUCESSO", user["username"], "Autenticacao realizada")
            token = secrets.token_hex(24)
            session_user = {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "role": user["role"],
                "sector": user["sector"],
                "active": user["active"],
            }
            SESSIONS[token] = session_user
            self.send_json({"token": token, "user": session_user})
            return

        if path == "/api/parts":
            user = self.require_admin()
            if not user:
                return
            required = ["code", "name", "category", "location", "quantity", "min_quantity", "unit"]
            if any(str(data.get(field, "")).strip() == "" for field in required):
                self.send_json({"error": "Preencha todos os campos obrigatorios"}, 400)
                return
            con = connect()
            try:
                cur = con.cursor()
                cur.execute(
                    """
                    INSERT INTO parts (code, name, category, location, quantity, min_quantity, unit, supplier, unit_price, sector, entry_date, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["code"].strip(),
                        data["name"].strip(),
                        data["category"].strip(),
                        data["location"].strip(),
                        int(data["quantity"]),
                        int(data["min_quantity"]),
                        data["unit"].strip(),
                        data.get("supplier", "").strip(),
                        float(data.get("unit_price") or 0),
                        data.get("sector", "").strip(),
                        data.get("entry_date", "").strip(),
                        data.get("description", "").strip(),
                    ),
                )
                part_id = cur.lastrowid
                cur.execute(
                    "INSERT INTO movements (part_id, user_id, type, quantity, note) VALUES (?, ?, ?, ?, ?)",
                    (part_id, user["id"], "cadastro", int(data["quantity"]), "Peca cadastrada pelo administrador"),
                )
                con.commit()
                self.send_json({"ok": True})
            except sqlite3.IntegrityError:
                self.send_json({"error": "Codigo ja cadastrado"}, 409)
            finally:
                con.close()
            return

        if path == "/api/requests":
            user = self.require_user()
            if not user:
                return
            con = connect()
            part = con.execute("SELECT * FROM parts WHERE id = ?", (data.get("part_id"),)).fetchone()
            if not part:
                con.close()
                self.send_json({"error": "Peca nao encontrada"}, 404)
                return
            quantity = int(data.get("quantity", 0))
            if quantity <= 0:
                con.close()
                self.send_json({"error": "Quantidade invalida"}, 400)
                return
            con.execute(
                "INSERT INTO requests (user_id, part_id, quantity, comment) VALUES (?, ?, ?, ?)",
                (user["id"], part["id"], quantity, data.get("comment", "").strip()),
            )
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return

        self.send_json({"error": "Rota nao encontrada"}, 404)

    def handle_api_put(self, path):
        user = self.require_admin()
        if not user:
            return
        data = self.read_json()
        con = connect()
        cur = con.cursor()

        if path.startswith("/api/parts/"):
            part_id = int(path.rsplit("/", 1)[1])
            cur.execute(
                """
                UPDATE parts
                SET code = ?, name = ?, category = ?, location = ?, quantity = ?, min_quantity = ?, unit = ?,
                    supplier = ?, unit_price = ?, sector = ?, entry_date = ?, description = ?
                WHERE id = ?
                """,
                (
                    data["code"].strip(),
                    data["name"].strip(),
                    data["category"].strip(),
                    data["location"].strip(),
                    int(data["quantity"]),
                    int(data["min_quantity"]),
                    data["unit"].strip(),
                    data.get("supplier", "").strip(),
                    float(data.get("unit_price") or 0),
                    data.get("sector", "").strip(),
                    data.get("entry_date", "").strip(),
                    data.get("description", "").strip(),
                    part_id,
                ),
            )
            cur.execute(
                "INSERT INTO movements (part_id, user_id, type, quantity, note) VALUES (?, ?, ?, ?, ?)",
                (part_id, user["id"], "edicao", int(data["quantity"]), "Cadastro da peca atualizado"),
            )
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return

        if path.startswith("/api/users/"):
            target_id = int(path.rsplit("/", 1)[1])
            target = cur.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
            if not target:
                con.close()
                self.send_json({"error": "Usuario nao encontrado"}, 404)
                return
            if target["id"] == user["id"] and int(data.get("active", 1)) == 0:
                con.close()
                self.send_json({"error": "Voce nao pode bloquear seu proprio usuario"}, 400)
                return
            password = target["password"]
            if data.get("password"):
                if len(data["password"]) < 6:
                    con.close()
                    self.send_json({"error": "A senha precisa ter pelo menos 6 caracteres"}, 400)
                    return
                password = password_hash(data["password"])
            cur.execute(
                """
                UPDATE users
                SET name = ?, username = ?, password = ?, role = ?, sector = ?, active = ?
                WHERE id = ?
                """,
                (
                    data["name"].strip(),
                    data["username"].strip(),
                    password,
                    data.get("role", "user"),
                    data.get("sector", "").strip(),
                    int(data.get("active", 1)),
                    target_id,
                ),
            )
            cur.execute(
                "INSERT INTO movements (user_id, type, quantity, note) VALUES (?, ?, ?, ?)",
                (user["id"], "usuario", 1, f"Usuario {data['username'].strip()} atualizado"),
            )
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return

        if path.startswith("/api/requests/"):
            request_id = int(path.rsplit("/", 1)[1])
            status = data.get("status")
            if status not in ("aprovado", "rejeitado"):
                con.close()
                self.send_json({"error": "Status invalido"}, 400)
                return
            req = cur.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
            if not req:
                con.close()
                self.send_json({"error": "Solicitacao nao encontrada"}, 404)
                return
            if req["status"] != "pendente":
                con.close()
                self.send_json({"error": "Solicitacao ja foi analisada"}, 400)
                return
            if status == "aprovado":
                part = cur.execute("SELECT * FROM parts WHERE id = ?", (req["part_id"],)).fetchone()
                if part["quantity"] < req["quantity"]:
                    con.close()
                    self.send_json({"error": "Estoque insuficiente"}, 400)
                    return
                cur.execute("UPDATE parts SET quantity = quantity - ? WHERE id = ?", (req["quantity"], req["part_id"]))
                cur.execute(
                    "INSERT INTO movements (part_id, user_id, type, quantity, note) VALUES (?, ?, ?, ?, ?)",
                    (req["part_id"], user["id"], "saida", req["quantity"], f"Solicitacao #{request_id} aprovada"),
                )
            cur.execute(
                "UPDATE requests SET status = ?, admin_note = ? WHERE id = ?",
                (status, data.get("admin_note", "").strip(), request_id),
            )
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return

        if path.startswith("/api/signup-requests/"):
            signup_id = int(path.rsplit("/", 1)[1])
            status = data.get("status")
            if status not in ("aprovado", "rejeitado"):
                con.close()
                self.send_json({"error": "Status invalido"}, 400)
                return
            signup = cur.execute("SELECT * FROM signup_requests WHERE id = ?", (signup_id,)).fetchone()
            if not signup:
                con.close()
                self.send_json({"error": "Pedido de cadastro nao encontrado"}, 404)
                return
            if signup["status"] != "pendente":
                con.close()
                self.send_json({"error": "Pedido de cadastro ja foi analisado"}, 400)
                return
            if status == "aprovado":
                existing = cur.execute("SELECT id FROM users WHERE username = ?", (signup["username"],)).fetchone()
                if existing:
                    con.close()
                    self.send_json({"error": "Ja existe usuario com esse login"}, 409)
                    return
                cur.execute(
                    "INSERT INTO users (name, username, password, role, sector, active) VALUES (?, ?, ?, ?, ?, ?)",
                    (signup["name"], signup["username"], signup["password"], "user", signup["sector"], 1),
                )
                cur.execute(
                    "INSERT INTO movements (user_id, type, quantity, note) VALUES (?, ?, ?, ?)",
                    (user["id"], "usuario", 1, f"Cadastro liberado para {signup['name']}"),
                )
            cur.execute(
                "UPDATE signup_requests SET status = ?, admin_note = ? WHERE id = ?",
                (status, data.get("admin_note", "").strip(), signup_id),
            )
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return

        con.close()
        self.send_json({"error": "Rota nao encontrada"}, 404)

    def handle_api_delete(self, path):
        user = self.require_admin()
        if not user:
            return
        if path.startswith("/api/parts/"):
            part_id = int(path.rsplit("/", 1)[1])
            con = connect()
            con.execute("DELETE FROM parts WHERE id = ?", (part_id,))
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return
        if path.startswith("/api/users/"):
            target_id = int(path.rsplit("/", 1)[1])
            if target_id == user["id"]:
                self.send_json({"error": "Voce nao pode excluir seu proprio usuario"}, 400)
                return
            con = connect()
            target = con.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
            if not target:
                con.close()
                self.send_json({"error": "Usuario nao encontrado"}, 404)
                return
            if target["role"] == "admin":
                admin_count = con.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'admin' AND active = 1").fetchone()["total"]
                if admin_count <= 1:
                    con.close()
                    self.send_json({"error": "Mantenha pelo menos um administrador ativo"}, 400)
                    return
            con.execute("DELETE FROM users WHERE id = ?", (target_id,))
            con.commit()
            con.close()
            self.send_json({"ok": True})
            return
        self.send_json({"error": "Rota nao encontrada"}, 404)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("localhost", 8000), Handler)
    print("MBF Estoque rodando em http://localhost:8000")
    server.serve_forever()
