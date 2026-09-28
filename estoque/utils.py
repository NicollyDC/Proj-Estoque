from datetime import datetime

FIN = ["venda", "uso e consumo"]
TIPOS = ["perda", "uso e consumo", "venda"]

ESTOQUE_SQL = """
SELECT p.*,
COALESCE((SELECT SUM(qtd_estoque)
          FROM itens
          WHERE produto_id=p.id),0)
-
COALESCE((SELECT SUM(qtd)
          FROM saidas
          WHERE produto_id=p.id),0) AS estoque
FROM produtos p
"""

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def today():
    return datetime.now().strftime("%Y-%m-%d")

def num(valor, default=None):
    valor = str(valor).strip().replace(",", ".")
    return float(valor) if valor else default

def fmt(valor):
    if valor is None:
        return ""
    if isinstance(valor, float):
        return f"{valor:g}"
    return str(valor)