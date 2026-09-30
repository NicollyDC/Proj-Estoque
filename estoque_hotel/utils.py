from datetime import datetime

from dados.hotel.database import q


FIN = ["venda", "uso e consumo"]

TIPOS = ["perda", "uso e consumo", "venda"]


ESTOQUE_SQL = """
SELECT p.*,

COALESCE(
    (
        SELECT SUM(qtd_estoque)
        FROM itens
        WHERE produto_id = p.id
    ),
    0
)

-

COALESCE(
    (
        SELECT SUM(isd.qtd)
        FROM itens_saida isd
        JOIN saidas s ON s.id = isd.saida_id
        WHERE isd.produto_id = p.id
    ),
    0
) AS estoque

FROM produtos p
"""


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