"""Auditoria somente leitura do banco MBF Stock.

Uso: python auditar_banco.py [caminho/para/banco.db]
Não modifica o banco nem imprime registros pessoais.
"""
import json
import sqlite3
import sys
from pathlib import Path

EXPECTED = {
    'parts': ['CHECK(quantity >= 0)', 'CHECK(min_quantity >= 0)', 'CHECK(unit_price >= 0)'],
    'requests': ['CHECK(quantity > 0)'],
    'movements': ['CHECK(quantity > 0)'],
}


def audit_database(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Banco não encontrado: {path}')
    # URI read-only evita criar ou alterar arquivos por engano.
    con = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        con.execute('PRAGMA foreign_keys = ON')
        integrity_result = con.execute('PRAGMA integrity_check').fetchone()[0]
        fk_errors = con.execute('PRAGMA foreign_key_check').fetchall()
        schema = dict(con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
        checks = {}
        for table, constraints in EXPECTED.items():
            definition = ' '.join((schema.get(table) or '').lower().split())
            checks[table] = {constraint: ' '.join(constraint.lower().split()) in definition for constraint in constraints}
        # Bancos legados podem conter valores inválidos mesmo quando o esquema
        # não declara CHECK. Contamos ocorrências sem revelar dados pessoais.
        anomalies = {}
        rules = {
            'parts': [('quantity', 'quantity < 0 OR quantity IS NULL'),
                      ('min_quantity', 'min_quantity < 0 OR min_quantity IS NULL'),
                      ('unit_price', 'unit_price < 0 OR unit_price IS NULL')],
            'requests': [('quantity', 'quantity <= 0 OR quantity IS NULL')],
            'movements': [('quantity', 'quantity <= 0 OR quantity IS NULL')],
        }
        for table, checks_for_table in rules.items():
            if table not in schema:
                continue
            columns = {row[1] for row in con.execute(f'PRAGMA table_info({table})')}
            for column, condition in checks_for_table:
                if column in columns:
                    anomalies[f'{table}.{column}'] = con.execute(
                        f'SELECT COUNT(*) FROM {table} WHERE {condition}'
                    ).fetchone()[0]
        return {
            'database': str(path),
            'integrity_check': integrity_result,
            'foreign_key_violations': len(fk_errors),
            'invalid_value_counts': anomalies,
            'missing_tables': sorted(set(EXPECTED) - set(schema)),
            'constraints': checks,
            'migration_required': bool(integrity_result != 'ok' or fk_errors or any(anomalies.values()) or set(EXPECTED) - set(schema) or any(not ok for values in checks.values() for ok in values.values())),
        }
    finally:
        con.close()


if __name__ == '__main__':
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('mbf_estoque.db')
    try:
        result = audit_database(target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(2 if result['migration_required'] else 0)
    except (sqlite3.DatabaseError, OSError) as exc:
        print(f'Erro na auditoria: {exc}', file=sys.stderr)
        sys.exit(1)
