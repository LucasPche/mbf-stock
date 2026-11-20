import unittest
from unittest.mock import Mock, patch
import database_repository as db

class TestPostgresAdapter(unittest.TestCase):
    def test_placeholder_conversion(self):
        self.assertEqual(db._sql("SELECT * FROM users WHERE id = ?"), "SELECT * FROM users WHERE id = %s")

    def test_cursor_chaining_and_mapping(self):
        raw = Mock()
        raw.fetchone.return_value = {"id": 7}
        cursor = db.PostgresCursor(raw)
        self.assertIs(cursor.execute("SELECT * FROM parts WHERE id = ?", (7,)), cursor)
        raw.execute.assert_called_with("SELECT * FROM parts WHERE id = %s", (7,))

    def test_insert_parts_returns_id(self):
        raw = Mock()
        raw.fetchone.return_value = {"id": 42}
        cursor = db.PostgresCursor(raw)
        cursor.execute("INSERT INTO parts (name) VALUES (?)", ("Peca",))
        raw.execute.assert_called_with("INSERT INTO parts (name) VALUES (%s) RETURNING id", ("Peca",))
        self.assertEqual(cursor.lastrowid, 42)

    def test_sqlite_fallback(self):
        with patch.dict("os.environ", {}, clear=True):
            con = db.open_connection(":memory:")
            try:
                self.assertEqual(con.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            finally:
                con.close()

if __name__ == "__main__":
    unittest.main()
