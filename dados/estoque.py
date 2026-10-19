"""Consultas e regras compartilhadas para posição atual do estoque."""


def calcular_quantidade_estoque(quantidade, fator=1):
    """Converte a quantidade informada para a unidade-base do estoque."""
    return float(quantidade or 0) * float(fator)


def calcular_valor_unitario_estoque(valor_total, quantidade_estoque):
    """Converte o custo total informado para custo por unidade-base do estoque."""
    quantidade_estoque = float(quantidade_estoque or 0)
    return round(float(valor_total or 0) / quantidade_estoque, 4) if quantidade_estoque > 0 else 0


def numero_brasileiro(valor, padrao=None):
    """Converte números em formato brasileiro, incluindo valores em reais."""
    texto = "" if valor is None else str(valor)
    texto = texto.strip().replace("R$", "").replace(" ", "").replace("\u00a0", "")
    if not texto:
        return padrao
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")
    elif "." in texto:
        inteiro, fracao = texto.rsplit(".", 1)
        if len(fracao) == 3 and inteiro.lstrip("+-").isdigit():
            texto = inteiro + fracao
    return float(texto)

ESTOQUE_SQL = """
SELECT p.*,
COALESCE(
    (SELECT SUM(qtd_estoque) FROM itens WHERE produto_id=p.id), 0
) - COALESCE(
    (SELECT SUM(isd.qtd) FROM itens_saida isd
     JOIN saidas s ON s.id=isd.saida_id WHERE isd.produto_id=p.id), 0
) + COALESCE(
    (SELECT SUM(a.diferenca) FROM ajustes_estoque a
     WHERE a.produto_id=p.id), 0
) AS estoque,
CASE WHEN (
    COALESCE((SELECT SUM(qtd_estoque) FROM itens WHERE produto_id=p.id), 0)
    - COALESCE((SELECT SUM(isd.qtd) FROM itens_saida isd JOIN saidas s ON s.id=isd.saida_id WHERE isd.produto_id=p.id), 0)
    + COALESCE((SELECT SUM(a.diferenca) FROM ajustes_estoque a WHERE a.produto_id=p.id), 0)
) > 0 THEN (
    -- Legacy rows may have a stored total but no usable unit price.
    COALESCE((SELECT SUM(COALESCE(NULLIF(valor_unit, 0) * qtd_estoque, CASE WHEN qtd_estoque > 0 THEN valor_total END, 0)) FROM itens WHERE produto_id=p.id), 0)
    - COALESCE((SELECT SUM(COALESCE(NULLIF(valor_unit, 0) * qtd, CASE WHEN qtd > 0 THEN subtotal END, 0)) FROM itens_saida WHERE produto_id=p.id), 0)
    + COALESCE((SELECT SUM(a.diferenca * a.valor_unit) FROM ajustes_estoque a WHERE a.produto_id=p.id), 0)
) / (
    COALESCE((SELECT SUM(qtd_estoque) FROM itens WHERE produto_id=p.id), 0)
    - COALESCE((SELECT SUM(isd.qtd) FROM itens_saida isd JOIN saidas s ON s.id=isd.saida_id WHERE isd.produto_id=p.id), 0)
    + COALESCE((SELECT SUM(a.diferenca) FROM ajustes_estoque a WHERE a.produto_id=p.id), 0)
) ELSE 0 END AS valor_unitario
FROM produtos p
"""


def status_estoque(quantidade, minimo):
    quantidade = float(quantidade or 0)
    minimo = float(minimo or 0)
    if quantidade <= 0:
        return "✕ Sem estoque", "zerado"
    if quantidade <= minimo:
        return "⚠ Estoque baixo", "baixo"
    return "✓ Normal", "normal"
