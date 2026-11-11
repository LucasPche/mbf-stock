"""Testes estáticos de regressão para pontos críticos da interface.

Não substituem testes de navegador nem uma auditoria de segurança.
"""
from pathlib import Path
import unittest


APP_JS = Path(__file__).resolve().parent / "public" / "app.js"


class FrontendSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_JS.read_text(encoding="utf-8")

    def test_escape_html_covers_special_characters(self):
        self.assertIn("function escapeHTML(value)", self.source)
        for escaped in ("&amp;", "&lt;", "&gt;", "&quot;", "&#39;"):
            self.assertIn(escaped, self.source)

    def test_dashboard_escapes_dynamic_part_fields(self):
        for field in ("category", "part.code", "part.name", "part.quantity",
                      "part.min_quantity", "part.unit"):
            self.assertIn("${escapeHTML(" + field + ")}", self.source)
        self.assertIn('escapeHTML(part.supplier || "Não informado")', self.source)

    def test_critical_report_escapes_fields(self):
        start = self.source.index("function renderReports()")
        end = self.source.index("function updateView()", start)
        report = self.source[start:end]
        for field in ("part.code", "part.name", "part.quantity",
                      "part.min_quantity", "part.unit"):
            self.assertIn("${escapeHTML(" + field + ")}", report)

    def test_request_actions_use_validated_id(self):
        start = self.source.index("function renderRequests()")
        end = self.source.index("function renderMovements()", start)
        requests = self.source[start:end]
        self.assertIn("Number.isSafeInteger(requestId)", requests)
        self.assertIn("reviewRequest(${safeRequestId}", requests)
        self.assertNotIn("reviewRequest(${req.id}", requests)

    def test_csv_neutralizes_formula_prefixes(self):
        start = self.source.index("function csvDownload(")
        end = self.source.index("async function loadAll()", start)
        csv = self.source[start:end]
        self.assertIn("const safeCSV = value =>", csv)
        self.assertIn('text = "\'" + text', csv)
        self.assertIn("row.map(safeCSV)", csv)


if __name__ == "__main__":
    unittest.main()
