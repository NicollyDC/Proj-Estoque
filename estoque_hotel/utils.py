from datetime import datetime

from dados.hotel.database import q
from dados.estoque import ESTOQUE_SQL

FIN = ["venda", "uso e consumo"]

TIPOS = ["perda", "uso e consumo", "venda"]


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today():
    return datetime.now().strftime("%Y-%m-%d")


def data_ok(txt, formato="%Y-%m-%d"):
    if not txt:
        return False

    try:
        datetime.strptime(txt.strip(), formato)
        return True
    except ValueError:
        return False


# Mantém o comportamento original (não engole erros)
def num(valor, default=None):
    valor = str(valor).strip().replace(",", ".")
    return float(valor) if valor else default


def fmt(valor):
    if valor is None:
        return ""

    if isinstance(valor, float):
        return f"{valor:g}"

    return str(valor)


def prod_map(incluir_id=None):
    if incluir_id is None:
        rows = q("""
            SELECT *
            FROM produtos
            WHERE ativo=1
            ORDER BY nome
        """)
    else:
        rows = q("""
            SELECT *
            FROM produtos
            WHERE ativo=1 OR id=?
            ORDER BY nome
        """, (incluir_id,))

    return {
        f"{r['codigo']} - {r['nome']}": r["id"]
        for r in rows
    }


def estoque_produto(produto_id):
    rows = q(ESTOQUE_SQL + " WHERE p.id=?", (produto_id,))
    if not rows:
        return 0.0
    return float(rows[0]["estoque"] or 0)
