"""Regras de estoque independentes do transporte HTTP.

O chamador controla a transação SQLite: confirma (commit) apenas após
atualizar também o estado da solicitação.
"""


def stock_adjustment(previous_quantity, new_quantity):
    """Retorna (tipo, quantidade) ou None quando não há alteração."""
    delta = new_quantity - previous_quantity
    if delta == 0:
        return None
    return ("entrada" if delta > 0 else "saida", abs(delta))


def reserve_withdrawal(cursor, part_id, quantity):
    """Baixa saldo apenas se houver estoque; operação atômica no SQLite."""
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise ValueError("Quantidade de retirada invalida")
    cursor.execute(
        "UPDATE parts SET quantity = quantity - ? WHERE id = ? AND quantity >= ?",
        (quantity, part_id, quantity),
    )
    return cursor.rowcount == 1
