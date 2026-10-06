
import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime, date, timedelta
from calendar import monthrange

import html
import tempfile
import webbrowser
from pathlib import Path

from dados.restaurante.database import q
from estoque_restaurante.utils import TIPOS
from estoque_restaurante.front import tree


# ============================================================
# PALETA ESPECÍFICA DO RELATÓRIO
# ============================================================

COR_FUNDO_CABECALHO = "#eef4ff"
COR_TEXTO_TITULO = "#1e3a8a"
COR_TEXTO_SUB = "#64748b"

COR_CARD_COMPRAS = "#e0f2fe"
COR_CARD_SAIDAS = "#fde8e8"
COR_CARD_DIFERENCA = "#e6f6ea"

COR_LINHA_POSITIVO = "#eaf7ee"
COR_LINHA_ALERTA = "#fdecec"
COR_LINHA_VAZIA = "#f3f4f6"
COR_LINHA_NEUTRA = "#ffffff"


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

rt = None

per = None
tipo = None

data_de = None
data_ate = None

por_prod = None
aviso = None

root_ref = None

resumo_compras = None
resumo_saidas = None
resumo_diferenca = None


# ============================================================
# UTILIDADES
# ============================================================

def hoje():
    return date.today()


def data_valida(txt):
    try:
        return datetime.strptime(
            txt.strip(),
            "%Y-%m-%d"
        ).date()

    except (ValueError, AttributeError):
        return None


def formatar_data_br(txt):
    data = data_valida(txt)

    if not data:
        return txt

    return data.strftime("%d/%m/%Y")


def dinheiro(valor):
    valor = valor or 0

    texto = f"{valor:,.2f}"

    return (
        "R$ "
        + texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def numero_br(valor):
    valor = valor or 0

    texto = f"{valor:,.4f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    texto = texto.rstrip("0").rstrip(",")

    return texto


def primeiro_dia_mes(data):
    return date(
        data.year,
        data.month,
        1
    )


def ultimo_dia_mes(data):
    ultimo = monthrange(
        data.year,
        data.month
    )[1]

    return date(
        data.year,
        data.month,
        ultimo
    )


def voltar_mes(data):
    if data.month == 1:
        return date(
            data.year - 1,
            12,
            1
        )

    return date(
        data.year,
        data.month - 1,
        1
    )


# ============================================================
# PERÍODOS
# ============================================================

def gerar_periodos():

    atual = hoje()
    modo = per.get()

    periodos = []

    # --------------------------------------------------------
    # DIA
    # --------------------------------------------------------

    if modo == "Dia":

        inicio = data_valida(
            data_de.get()
        )

        fim = data_valida(
            data_ate.get()
        )

        if not inicio or not fim:
            return []

        if inicio > fim:
            return []

        data = inicio

        while data <= fim:

            periodos.append({
                "chave": data.strftime("%Y-%m-%d"),
                "inicio": data,
                "fim": data,
                "exibicao": data.strftime("%d/%m/%Y")
            })

            data += timedelta(days=1)

        return periodos

    # --------------------------------------------------------
    # MÊS
    # --------------------------------------------------------

    if modo == "Mês":

        data = primeiro_dia_mes(atual)

        for _ in range(24):

            periodos.append({
                "chave": data.strftime("%Y-%m"),
                "inicio": primeiro_dia_mes(data),
                "fim": ultimo_dia_mes(data),
                "exibicao": data.strftime("%m/%Y")
            })

            data = voltar_mes(data)

        return periodos

    # --------------------------------------------------------
    # ANO
    # --------------------------------------------------------

    if modo == "Ano":

        for i in range(10):

            ano = atual.year - i

            periodos.append({
                "chave": str(ano),
                "inicio": date(ano, 1, 1),
                "fim": date(ano, 12, 31),
                "exibicao": str(ano)
            })

        return periodos

    return []


# ============================================================
# FILTRO POR TIPO
# ============================================================

def tipo_valido():

    valor = tipo.get()

    if valor == "todos":
        return None

    return valor


# ============================================================
# BUSCA DE COMPRAS
# ============================================================

def buscar_compras(inicio, fim):

    rows = q("""
        SELECT
            COALESCE(SUM(i.valor_total), 0) AS total
        FROM itens i
        JOIN notas n
            ON n.id = i.nota_id
        WHERE date(n.data)
              BETWEEN date(?) AND date(?)
    """, (
        inicio.strftime("%Y-%m-%d"),
        fim.strftime("%Y-%m-%d"),
    ))

    if not rows:
        return 0

    return rows[0]["total"] or 0


# ============================================================
# BUSCA DE SAÍDAS
# ============================================================

def buscar_saidas(
    inicio,
    fim,
    tipo_filtro
):

    inicio_txt = inicio.strftime(
        "%Y-%m-%d"
    )

    fim_txt = fim.strftime(
        "%Y-%m-%d"
    )

    if tipo_filtro is None:

        rows = q("""
            SELECT
                COALESCE(SUM(isd.subtotal), 0) AS total
            FROM itens_saida isd
            JOIN saidas s
                ON s.id = isd.saida_id
            WHERE date(s.data_hora)
                  BETWEEN date(?) AND date(?)
        """, (
            inicio_txt,
            fim_txt,
        ))

    else:

        rows = q("""
            SELECT
                COALESCE(SUM(isd.subtotal), 0) AS total
            FROM itens_saida isd
            JOIN saidas s
                ON s.id = isd.saida_id
            WHERE date(s.data_hora)
                  BETWEEN date(?) AND date(?)
              AND s.tipo=?
        """, (
            inicio_txt,
            fim_txt,
            tipo_filtro,
        ))

    if not rows:
        return 0

    return rows[0]["total"] or 0


# ============================================================
# DETALHAMENTO POR PRODUTO
# ============================================================

def buscar_detalhes(
    inicio,
    fim,
    tipo_filtro
):

    inicio_txt = inicio.strftime(
        "%Y-%m-%d"
    )

    fim_txt = fim.strftime(
        "%Y-%m-%d"
    )

    # --------------------------------------------------------
    # COMPRAS
    # --------------------------------------------------------

    compras = q("""
        SELECT
            n.data AS data,
            i.descricao AS produto,
            n.fornecedor AS fornecedor,
            COALESCE(i.qtd_estoque, 0) AS quantidade,
            COALESCE(i.valor_total, 0) AS valor
        FROM itens i
        JOIN notas n
            ON n.id = i.nota_id
        WHERE date(n.data)
              BETWEEN date(?) AND date(?)
        ORDER BY n.data DESC, i.descricao
    """, (
        inicio_txt,
        fim_txt,
    ))

    # --------------------------------------------------------
    # SAÍDAS
    # --------------------------------------------------------

    if tipo_filtro is None:

        saidas = q("""
            SELECT
                date(s.data_hora) AS data,
                p.nome AS produto,
                s.tipo AS tipo,
                isd.qtd AS quantidade,
                COALESCE(
                    isd.subtotal,
                    isd.qtd * isd.valor_unit
                ) AS valor
            FROM itens_saida isd
            JOIN saidas s
                ON s.id = isd.saida_id
            JOIN produtos p
                ON p.id = isd.produto_id
            WHERE date(s.data_hora)
                  BETWEEN date(?) AND date(?)
            ORDER BY s.data_hora DESC, p.nome
        """, (
            inicio_txt,
            fim_txt,
        ))

    else:

        saidas = q("""
            SELECT
                date(s.data_hora) AS data,
                p.nome AS produto,
                s.tipo AS tipo,
                isd.qtd AS quantidade,
                COALESCE(
                    isd.subtotal,
                    isd.qtd * isd.valor_unit
                ) AS valor
            FROM itens_saida isd
            JOIN saidas s
                ON s.id = isd.saida_id
            JOIN produtos p
                ON p.id = isd.produto_id
            WHERE date(s.data_hora)
                  BETWEEN date(?) AND date(?)
              AND s.tipo=?
            ORDER BY s.data_hora DESC, p.nome
        """, (
            inicio_txt,
            fim_txt,
            tipo_filtro,
        ))

    detalhes = []

    for r in compras:

        detalhes.append({
            "data": r["data"],
            "produto": (
                r["produto"]
                or "Produto não identificado"
            ),
            "origem": r["fornecedor"] or "-",
            "tipo": "Compra",
            "quantidade": r["quantidade"] or 0,
            "valor": r["valor"] or 0,
        })

    for r in saidas:

        detalhes.append({
            "data": r["data"],
            "produto": (
                r["produto"]
                or "Produto não identificado"
            ),
            "origem": "-",
            "tipo": r["tipo"],
            "quantidade": r["quantidade"] or 0,
            "valor": r["valor"] or 0,
        })

    detalhes.sort(
        key=lambda x: (
            x["data"] or "",
            x["produto"] or ""
        ),
        reverse=True
    )

    return detalhes


# ============================================================
# SITUAÇÃO
# ============================================================

def situacao(
    compras,
    saidas
):

    compras = compras or 0
    saidas = saidas or 0

    if compras == 0 and saidas == 0:
        return "Sem movimentação"

    if compras > 0 and saidas == 0:
        return "Somente compra"

    if compras == 0 and saidas > 0:
        return "Somente saída"

    if saidas > compras:
        return "Saídas maiores que compras"

    if compras > saidas:
        return "Compras maiores que saídas"

    return "Compras e saídas equilibradas"


def tag_da_linha(
    compras,
    saidas
):

    if not compras and not saidas:
        return "vazia"

    if saidas > compras:
        return "alerta"

    if compras > saidas:
        return "positivo"

    return "neutra"


def icone_situacao(txt):

    icones = {
        "Sem movimentação": "⚪",
        "Somente compra": "🟢",
        "Somente saída": "🔴",
        "Saídas maiores que compras": "🔴",
        "Compras maiores que saídas": "🟢",
        "Compras e saídas equilibradas": "🟡",
    }

    return f"{icones.get(txt, '')} {txt}"


# ============================================================
# ATUALIZAÇÃO DA TABELA
# ============================================================

def atualizar_relatorio(*_):

    global rt, aviso

    if rt is None:
        return

    rt.delete(
        *rt.get_children()
    )

    periodos = gerar_periodos()

    if not periodos:

        aviso.config(
            text=(
                "⚠️ Informe um intervalo de "
                "datas válido (AAAA-MM-DD)."
            )
        )

        atualizar_resumo(
            0,
            0
        )

        return

    tipo_filtro = tipo_valido()

    total_compras = 0
    total_saidas = 0

    quantidade_periodos = len(
        periodos
    )

    for periodo in periodos:

        compras = buscar_compras(
            periodo["inicio"],
            periodo["fim"]
        )

        saidas = buscar_saidas(
            periodo["inicio"],
            periodo["fim"],
            tipo_filtro
        )

        diferenca = compras - saidas

        situacao_txt = situacao(
            compras,
            saidas
        )

        total_compras += compras
        total_saidas += saidas

        rt.insert(
            "",
            "end",
            values=(
                periodo["exibicao"],
                dinheiro(compras),
                dinheiro(saidas),
                dinheiro(diferenca),
                icone_situacao(
                    situacao_txt
                ),
            ),
            tags=(
                tag_da_linha(
                    compras,
                    saidas
                ),
            )
        )

    aviso.config(
        text=(
            f"ℹ️ {quantidade_periodos} período(s) analisado(s). "
            "Períodos sem movimentação também são exibidos."
        )
    )

    atualizar_resumo(
        total_compras,
        total_saidas
    )


# ============================================================
# RESUMO FINANCEIRO
# ============================================================

def atualizar_resumo(
    compras,
    saidas
):

    if resumo_compras is None:
        return

    diferenca = compras - saidas

    resumo_compras.config(
        text=dinheiro(compras)
    )

    resumo_saidas.config(
        text=dinheiro(saidas)
    )

    resumo_diferenca.config(
        text=dinheiro(diferenca)
    )


# ============================================================
# CONTROLE DOS CAMPOS DE DATA
# ============================================================

def atualizar_campos_data(*_):

    modo = per.get()

    if modo == "Dia":

        data_de.config(
            state="normal"
        )

        data_ate.config(
            state="normal"
        )

    else:

        data_de.config(
            state="disabled"
        )

        data_ate.config(
            state="disabled"
        )

    atualizar_relatorio()


# ============================================================
# AJUDA
# ============================================================

def mostrar_ajuda():

    messagebox.showinfo(
        "Como usar os relatórios",
        (
            "📊 Esta tela compara o que foi COMPRADO com o que "
            "SAIU do estoque.\n\n"

            "1. Escolha o período:\n"
            "   • Dia: informe as datas 'De' e 'Até'\n"
            "   • Mês: mostra os últimos 24 meses\n"
            "   • Ano: mostra os últimos 10 anos\n\n"

            "2. Escolha o tipo de saída (perda, uso e consumo, "
            "venda) ou deixe em 'todos'.\n\n"

            "3. Marque 'Detalhar por produto' para ver cada item "
            "no relatório impresso.\n\n"

            "4. Clique em 'Gerar relatório' para visualizar e "
            "imprimir.\n\n"

            "Cores da tabela:\n"
            "🟢 compras maiores que saídas\n"
            "🔴 saídas maiores que compras\n"
            "⚪ sem movimentação"
        ),
        parent=root_ref
    )


# ============================================================
# MONTAGEM DO TEXTO
# ============================================================

def montar_texto_relatorio():

    periodos = gerar_periodos()

    if not periodos:
        return "", []

    tipo_filtro = tipo_valido()

    linhas = []

    total_compras = 0
    total_saidas = 0

    linhas.append(
        "RELATÓRIO DE MOVIMENTAÇÃO DE ESTOQUE"
    )

    linhas.append(
        "RESTAURANTE"
    )

    linhas.append("")

    linhas.append(
        f"Período: {per.get()}"
    )

    if per.get() == "Dia":

        linhas.append(
            f"De: {formatar_data_br(data_de.get())}"
        )

        linhas.append(
            f"Até: {formatar_data_br(data_ate.get())}"
        )

    elif per.get() == "Mês":

        linhas.append(
            "Intervalo: últimos 24 meses"
        )

    else:

        linhas.append(
            "Intervalo: últimos 10 anos"
        )

    linhas.append(
        f"Tipo de saída: {tipo.get()}"
    )

    linhas.append("")

    linhas.append(
        "=" * 100
    )

    linhas.append(
        f"{'PERÍODO':<18}"
        f"{'COMPRAS':>18}"
        f"{'SAÍDAS':>18}"
        f"{'DIFERENÇA':>18}"
        f"  SITUAÇÃO"
    )

    linhas.append(
        "-" * 100
    )

    for periodo in periodos:

        compras = buscar_compras(
            periodo["inicio"],
            periodo["fim"]
        )

        saidas = buscar_saidas(
            periodo["inicio"],
            periodo["fim"],
            tipo_filtro
        )

        diferenca = compras - saidas

        total_compras += compras
        total_saidas += saidas

        linhas.append(
            f"{periodo['exibicao']:<18}"
            f"{dinheiro(compras):>18}"
            f"{dinheiro(saidas):>18}"
            f"{dinheiro(diferenca):>18}"
            f"  {situacao(compras, saidas)}"
        )

    total_diferenca = (
        total_compras
        - total_saidas
    )

    linhas.append(
        "-" * 100
    )

    linhas.append(
        f"{'TOTAL':<18}"
        f"{dinheiro(total_compras):>18}"
        f"{dinheiro(total_saidas):>18}"
        f"{dinheiro(total_diferenca):>18}"
    )

    detalhes = []

    if por_prod.get():

        for periodo in periodos:

            dados = buscar_detalhes(
                periodo["inicio"],
                periodo["fim"],
                tipo_filtro
            )

            if not dados:
                continue

            detalhes.extend(
                [
                    (
                        periodo["exibicao"],
                        item
                    )
                    for item in dados
                ]
            )

        if detalhes:

            linhas.append("")
            linhas.append("")

            linhas.append(
                "DETALHAMENTO POR PRODUTO"
            )

            linhas.append(
                "=" * 100
            )

            linhas.append(
                f"{'PERÍODO':<14}"
                f"{'TIPO':<20}"
                f"{'PRODUTO':<35}"
                f"{'QUANTIDADE':>12}"
                f"{'VALOR':>15}"
            )

            linhas.append(
                "-" * 100
            )

            for periodo_txt, item in detalhes:

                linhas.append(
                    f"{periodo_txt:<14}"
                    f"{item['tipo']:<20}"
                    f"{item['produto'][:33]:<35}"
                    f"{numero_br(item['quantidade']):>12}"
                    f"{dinheiro(item['valor']):>15}"
                )

    return "\n".join(linhas), detalhes


# ============================================================
# HTML DO RELATÓRIO
# ============================================================

def gerar_html_relatorio(
    periodos,
    tipo_filtro,
    detalhes
):

    linhas_html = []

    total_compras = 0
    total_saidas = 0

    for periodo in periodos:

        compras = buscar_compras(
            periodo["inicio"],
            periodo["fim"]
        )

        saidas = buscar_saidas(
            periodo["inicio"],
            periodo["fim"],
            tipo_filtro
        )

        diferenca = compras - saidas

        total_compras += compras
        total_saidas += saidas

        situacao_txt = situacao(
            compras,
            saidas
        )

        classe = ""

        if situacao_txt == "Sem movimentação":
            classe = "sem-movimentacao"

        elif saidas > compras:
            classe = "alerta"

        elif compras > saidas:
            classe = "positivo"

        linhas_html.append(
            f"""
            <tr class="{classe}">
                <td>{html.escape(periodo['exibicao'])}</td>
                <td class="numero">{dinheiro(compras)}</td>
                <td class="numero">{dinheiro(saidas)}</td>
                <td class="numero">{dinheiro(diferenca)}</td>
                <td>{html.escape(situacao_txt)}</td>
            </tr>
            """
        )

    total_diferenca = (
        total_compras
        - total_saidas
    )

    # --------------------------------------------------------
    # INTERVALO
    # --------------------------------------------------------

    if per.get() == "Dia":

        intervalo = (
            f"{formatar_data_br(data_de.get())} "
            f"até "
            f"{formatar_data_br(data_ate.get())}"
        )

    elif per.get() == "Mês":

        intervalo = "Últimos 24 meses"

    else:

        intervalo = "Últimos 10 anos"

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    html_texto = f"""
<!DOCTYPE html>

<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<title>Relatório de Movimentação de Estoque</title>

<style>

@page {{
    size: A4 landscape;
    margin: 12mm;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: Arial, Helvetica, sans-serif;
    color: #1f2937;
    font-size: 11px;
    background: white;
}}

.cabecalho {{
    border-bottom: 2px solid #1f4e79;
    padding-bottom: 12px;
    margin-bottom: 16px;
}}

.titulo {{
    font-size: 22px;
    font-weight: bold;
    color: #17365d;
    margin-bottom: 4px;
}}

.subtitulo {{
    font-size: 13px;
    color: #6b7280;
}}

.informacoes {{
    display: table;
    width: 100%;
    margin-bottom: 18px;
}}

.info-card {{
    display: table-cell;
    width: 25%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    background: #f8fafc;
}}

.info-label {{
    display: block;
    font-size: 9px;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

.info-valor {{
    font-size: 12px;
    font-weight: bold;
}}

.resumo {{
    display: table;
    width: 100%;
    margin-bottom: 18px;
}}

.resumo-card {{
    display: table-cell;
    width: 33.33%;
    padding: 10px 14px;
    border: 1px solid #d1d5db;
}}

.resumo-card + .resumo-card {{
    border-left: none;
}}

.resumo-titulo {{
    font-size: 9px;
    color: #6b7280;
    text-transform: uppercase;
}}

.resumo-valor {{
    margin-top: 5px;
    font-size: 16px;
    font-weight: bold;
}}

.secao {{
    font-size: 14px;
    font-weight: bold;
    color: #17365d;
    margin: 18px 0 8px 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    page-break-inside: auto;
}}

thead {{
    display: table-header-group;
}}

tr {{
    page-break-inside: avoid;
    page-break-after: auto;
}}

th {{
    background: #17365d;
    color: white;
    padding: 8px;
    text-align: left;
    font-size: 10px;
}}

td {{
    border-bottom: 1px solid #d9dee5;
    padding: 7px 8px;
    vertical-align: middle;
}}

td.numero {{
    text-align: right;
}}

tr:nth-child(even) {{
    background: #f8fafc;
}}

tr.sem-movimentacao {{
    color: #6b7280;
}}

tr.alerta {{
    background: #fff4f4;
}}

tr.positivo {{
    background: #f5faf6;
}}

.total {{
    background: #e8eef5 !important;
    font-weight: bold;
    border-top: 2px solid #17365d;
}}

.total td {{
    padding: 9px 8px;
}}

.rodape {{
    margin-top: 20px;
    padding-top: 8px;
    border-top: 1px solid #d1d5db;
    font-size: 9px;
    color: #6b7280;
}}

.detalhes {{
    page-break-before: always;
}}

@media screen {{

    body {{
        max-width: 1100px;
        margin: 30px auto;
        padding: 30px;
        box-shadow: 0 0 15px rgba(0,0,0,.12);
    }}

}}

</style>

</head>

<body>

<div class="cabecalho">

    <div class="titulo">
        RELATÓRIO DE MOVIMENTAÇÃO DE ESTOQUE
    </div>

    <div class="subtitulo">
        Controle de Estoque - Restaurante
    </div>

</div>


<div class="informacoes">

    <div class="info-card">

        <span class="info-label">
            Agrupamento
        </span>

        <span class="info-valor">
            {html.escape(per.get())}
        </span>

    </div>


    <div class="info-card">

        <span class="info-label">
            Intervalo
        </span>

        <span class="info-valor">
            {html.escape(intervalo)}
        </span>

    </div>


    <div class="info-card">

        <span class="info-label">
            Tipo de saída
        </span>

        <span class="info-valor">
            {html.escape(tipo.get())}
        </span>

    </div>


    <div class="info-card">

        <span class="info-label">
            Detalhamento
        </span>

        <span class="info-valor">
            {"Por produto" if por_prod.get() else "Resumo"}
        </span>

    </div>

</div>


<div class="resumo">

    <div class="resumo-card">

        <div class="resumo-titulo">
            Total de compras
        </div>

        <div class="resumo-valor">
            {dinheiro(total_compras)}
        </div>

    </div>


    <div class="resumo-card">

        <div class="resumo-titulo">
            Total de saídas / consumo
        </div>

        <div class="resumo-valor">
            {dinheiro(total_saidas)}
        </div>

    </div>


    <div class="resumo-card">

        <div class="resumo-titulo">
            Diferença
        </div>

        <div class="resumo-valor">
            {dinheiro(total_diferenca)}
        </div>

    </div>

</div>


<div class="secao">
    Movimentação por período
</div>


<table>

<thead>

<tr>

    <th>Período</th>
    <th>Compras</th>
    <th>Saídas / Consumo</th>
    <th>Diferença</th>
    <th>Situação</th>

</tr>

</thead>


<tbody>

{''.join(linhas_html)}


<tr class="total">

    <td>TOTAL</td>

    <td class="numero">
        {dinheiro(total_compras)}
    </td>

    <td class="numero">
        {dinheiro(total_saidas)}
    </td>

    <td class="numero">
        {dinheiro(total_diferenca)}
    </td>

    <td>
        {html.escape(
            situacao(
                total_compras,
                total_saidas
            )
        )}
    </td>

</tr>

</tbody>

</table>
"""

    # --------------------------------------------------------
    # DETALHAMENTO
    # --------------------------------------------------------

    if detalhes:

        html_texto += """
<div class="detalhes">

<div class="secao">
    Detalhamento por produto
</div>

<table>

<thead>

<tr>

    <th>Período</th>
    <th>Tipo</th>
    <th>Produto</th>
    <th>Origem / Fornecedor</th>
    <th>Quantidade</th>
    <th>Valor</th>

</tr>

</thead>

<tbody>
"""

        for periodo_txt, item in detalhes:

            html_texto += f"""
<tr>

    <td>
        {html.escape(periodo_txt)}
    </td>

    <td>
        {html.escape(item['tipo'])}
    </td>

    <td>
        {html.escape(item['produto'])}
    </td>

    <td>
        {html.escape(item['origem'])}
    </td>

    <td class="numero">
        {html.escape(
            numero_br(item['quantidade'])
        )}
    </td>

    <td class="numero">
        {dinheiro(item['valor'])}
    </td>

</tr>
"""

        html_texto += """
</tbody>

</table>

</div>
"""

    html_texto += """

<div class="rodape">

    Relatório gerado pelo Controle de Estoque - Restaurante.

    <br>

    Compras representam valores incorporados ao estoque.
    Saídas representam o custo registrado no momento da retirada.

</div>

</body>

</html>
"""

    return html_texto


# ============================================================
# IMPRESSÃO
# ============================================================

def imprimir_relatorio(
    periodos,
    tipo_filtro,
    detalhes
):

    try:

        html_texto = gerar_html_relatorio(
            periodos,
            tipo_filtro,
            detalhes
        )

        arquivo = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".html",
            mode="w",
            encoding="utf-8"
        )

        arquivo.write(
            html_texto
        )

        arquivo.close()

        caminho = Path(
            arquivo.name
        )

        webbrowser.open_new_tab(
            caminho.as_uri()
        )

        messagebox.showinfo(
            "Relatório aberto",
            (
                "O relatório foi aberto no navegador.\n\n"

                "Para imprimir:\n"
                "1. Pressione Ctrl + P\n"
                "2. Escolha a impressora conectada ao computador\n"
                "3. Confira a visualização\n"
                "4. Clique em Imprimir"
            ),
            parent=root_ref
        )

    except Exception as ex:

        messagebox.showerror(
            "Erro ao abrir relatório",
            (
                "Não foi possível abrir o relatório "
                "para impressão.\n\n"
                f"{ex}"
            ),
            parent=root_ref
        )


# ============================================================
# JANELA DE VISUALIZAÇÃO
# ============================================================

def abrir_visualizacao():

    periodos = gerar_periodos()

    if not periodos:

        messagebox.showwarning(
            "Relatório",
            "Informe um período válido antes de gerar o relatório.",
            parent=root_ref
        )

        return

    tipo_filtro = tipo_valido()

    texto, detalhes = montar_texto_relatorio()

    win = tk.Toplevel(
        root_ref
    )

    win.title(
        "Visualização do relatório"
    )

    win.geometry(
        "1050x700"
    )

    win.minsize(
        800,
        500
    )

    win.transient(
        root_ref
    )

    win.grab_set()

    # --------------------------------------------------------
    # CABEÇALHO
    # --------------------------------------------------------

    topo = ttk.Frame(
        win
    )

    topo.pack(
        fill="x",
        padx=12,
        pady=10
    )

    ttk.Label(
        topo,
        text="📄 Visualização do relatório",
        style="AppTitle.TLabel"
    ).pack(
        side="left"
    )

    ttk.Label(
        topo,
        text=f"  •  {per.get()}",
        style="AppSubtitle.TLabel"
    ).pack(
        side="left",
        padx=8
    )

    # --------------------------------------------------------
    # ÁREA DE TEXTO
    # --------------------------------------------------------

    area = ttk.Frame(
        win
    )

    area.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 8)
    )

    barra_y = ttk.Scrollbar(
        area,
        orient="vertical"
    )

    barra_x = ttk.Scrollbar(
        area,
        orient="horizontal"
    )

    texto_widget = tk.Text(
        area,
        wrap="none",
        font=("Consolas", 10),
        yscrollcommand=barra_y.set,
        xscrollcommand=barra_x.set,
        bg="#ffffff",
        fg="#1f2937",
        relief="solid",
        borderwidth=1,
        padx=10,
        pady=10
    )

    barra_y.config(
        command=texto_widget.yview
    )

    barra_x.config(
        command=texto_widget.xview
    )

    texto_widget.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    barra_y.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    barra_x.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    area.rowconfigure(
        0,
        weight=1
    )

    area.columnconfigure(
        0,
        weight=1
    )

    texto_widget.insert(
        "1.0",
        texto
    )

    texto_widget.config(
        state="disabled"
    )

    # --------------------------------------------------------
    # RODAPÉ
    # --------------------------------------------------------

    rodape = ttk.Frame(
        win
    )

    rodape.pack(
        fill="x",
        padx=12,
        pady=10
    )

    ttk.Label(
        rodape,
        text=(
            "💡 A impressão será aberta no navegador "
            "para utilizar a impressora do computador."
        ),
        style="App.TLabel"
    ).pack(
        side="left"
    )

    ttk.Button(
        rodape,
        text="🖨️ Imprimir",
        style="Sucesso.TButton",
        command=lambda: imprimir_relatorio(
            periodos,
            tipo_filtro,
            detalhes
        )
    ).pack(
        side="right"
    )

    ttk.Button(
        rodape,
        text="Fechar",
        style="Padrao.TButton",
        command=win.destroy
    ).pack(
        side="right",
        padx=6
    )


# ============================================================
# CARD DO RESUMO
# ============================================================

def criar_card_resumo(
    pai,
    titulo,
    cor
):

    card = tk.Frame(
        pai,
        bg=cor,
        padx=16,
        pady=10,
        highlightthickness=1,
        highlightbackground="#d1d5db"
    )

    tk.Label(
        card,
        text=titulo,
        bg=cor,
        fg=COR_TEXTO_SUB,
        font=("Segoe UI", 9)
    ).pack(
        anchor="w"
    )

    valor = tk.Label(
        card,
        text="R$ 0,00",
        bg=cor,
        fg="#1f2937",
        font=("Segoe UI", 15, "bold")
    )

    valor.pack(
        anchor="w"
    )

    return card, valor


# ============================================================
# CRIAÇÃO DA ABA
# ============================================================

def criar_aba_relatorios(
    notebook,
    root
):

    global rt
    global per
    global tipo
    global data_de
    global data_ate
    global por_prod
    global aviso
    global root_ref

    global resumo_compras
    global resumo_saidas
    global resumo_diferenca

    root_ref = root

    aba = ttk.Frame(
        notebook
    )

    notebook.add(
        aba,
        text="📊 Relatórios"
    )

    # ========================================================
    # CABEÇALHO
    # ========================================================

    cabecalho = tk.Frame(
        aba,
        bg=COR_FUNDO_CABECALHO
    )

    cabecalho.pack(
        fill="x",
        padx=10,
        pady=(10, 4)
    )

    textos = tk.Frame(
        cabecalho,
        bg=COR_FUNDO_CABECALHO
    )

    textos.pack(
        side="left",
        padx=12,
        pady=8
    )

    tk.Label(
        textos,
        text="📊 Relatórios",
        bg=COR_FUNDO_CABECALHO,
        fg=COR_TEXTO_TITULO,
        font=("Segoe UI", 15, "bold")
    ).pack(
        anchor="w"
    )

    tk.Label(
        textos,
        text=(
            "Compare o que foi comprado com o que "
            "saiu do estoque"
        ),
        bg=COR_FUNDO_CABECALHO,
        fg=COR_TEXTO_SUB,
        font=("Segoe UI", 9)
    ).pack(
        anchor="w"
    )

    ttk.Button(
        cabecalho,
        text="❓ Ajuda",
        style="Padrao.TButton",
        command=mostrar_ajuda
    ).pack(
        side="right",
        padx=12
    )

        # ========================================================
    # FILTROS
    # ========================================================

    grupo = ttk.LabelFrame(
        aba,
        text="🔎 Filtros do relatório",
        style="App.TLabelframe"
    )

    grupo.pack(
        fill="x",
        padx=10,
        pady=8
    )

    # ========================================================
    # LINHA 1
    # ========================================================

    linha1 = ttk.Frame(
        grupo,
        style="App.TFrame"
    )

    linha1.pack(
        fill="x",
        padx=10,
        pady=(8, 4)
    )

    # AGRUPAMENTO

    ttk.Label(
        linha1,
        text="📅 Agrupar por:",
        style="App.TLabel"
    ).pack(
        side="left",
        padx=(0, 5)
    )

    per = ttk.Combobox(
        linha1,
        values=[
            "Dia",
            "Mês",
            "Ano"
        ],
        state="readonly",
        width=10,
        style="App.TCombobox"
    )

    per.set(
        "Mês"
    )

    per.pack(
        side="left"
    )

    # TIPO

    ttk.Label(
        linha1,
        text="🏷️ Tipo de saída:",
        style="App.TLabel"
    ).pack(
        side="left",
        padx=(20, 5)
    )

    tipo = ttk.Combobox(
        linha1,
        values=[
            "todos"
        ] + TIPOS,
        state="readonly",
        width=20,
        style="App.TCombobox"
    )

    tipo.set(
        "todos"
    )

    tipo.pack(
        side="left"
    )

    # ========================================================
    # LINHA 2
    # ========================================================

    linha2 = ttk.Frame(
        grupo,
        style="App.TFrame"
    )

    linha2.pack(
        fill="x",
        padx=10,
        pady=(4, 8)
    )

    # DATA INICIAL

    ttk.Label(
        linha2,
        text="📆 De:",
        style="App.TLabel"
    ).pack(
        side="left",
        padx=(0, 5)
    )

    data_de = ttk.Entry(
        linha2,
        width=13,
        style="App.TEntry"
    )

    data_de.insert(
        0,
        hoje().strftime("%Y-%m-%d")
    )

    data_de.pack(
        side="left"
    )

    # DATA FINAL

    ttk.Label(
        linha2,
        text="Até:",
        style="App.TLabel"
    ).pack(
        side="left",
        padx=(8, 5)
    )

    data_ate = ttk.Entry(
        linha2,
        width=13,
        style="App.TEntry"
    )

    data_ate.insert(
        0,
        hoje().strftime("%Y-%m-%d")
    )

    data_ate.pack(
        side="left"
    )

    # ========================================================
    # DETALHAMENTO
    # ========================================================

    detalhar_var = tk.IntVar(
        value=0
    )

    ttk.Checkbutton(
        linha2,
        text="Detalhar por produto",
        variable=detalhar_var,
        command=atualizar_relatorio,
        style="App.TCheckbutton"
    ).pack(
        side="left",
        padx=(20, 0)
    )

    class Wrapper:

        def get(self):
            return detalhar_var.get()

    por_prod = Wrapper()

    # ========================================================
    # BOTÕES
    # ========================================================

    botoes = ttk.Frame(
        linha2,
        style="App.TFrame"
    )

    botoes.pack(
        side="right"
    )

    ttk.Button(
        botoes,
        text="🔄 Atualizar",
        style="Atencao.TButton",
        command=atualizar_relatorio
    ).pack(
        side="left",
        padx=(0, 6)
    )

    ttk.Button(
        botoes,
        text="📄 Gerar relatório",
        style="Primario.TButton",
        command=abrir_visualizacao
    ).pack(
        side="left"
    )

    # ========================================================
    # AVISO
    # ========================================================

    aviso = ttk.Label(
        aba,
        text="",
        anchor="w",
        style="App.TLabel"
    )

    aviso.pack(
        fill="x",
        padx=10,
        pady=(4, 5)
    )

    # ========================================================
    # TABELA
    # ========================================================

    tabela_frame = ttk.Frame(
        aba
    )

    tabela_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=4
    )

    rt = tree(
        tabela_frame,
        [
            ("per", "Período", 130),
            ("compras", "Compras (R$)", 180),
            ("saidas", "Saídas (R$)", 180),
            ("dif", "Diferença (R$)", 180),
            ("situacao", "Situação", 260),
        ]
    )

    rt.tag_configure(
        "positivo",
        background=COR_LINHA_POSITIVO
    )

    rt.tag_configure(
        "alerta",
        background=COR_LINHA_ALERTA
    )

    rt.tag_configure(
        "vazia",
        background=COR_LINHA_VAZIA,
        foreground="#6b7280"
    )

    rt.tag_configure(
        "neutra",
        background=COR_LINHA_NEUTRA
    )

    # ========================================================
    # RESUMO
    # ========================================================

    resumo = ttk.LabelFrame(
        aba,
        text="💰 Resumo financeiro"
    )

    resumo.pack(
        fill="x",
        padx=10,
        pady=(4, 10)
    )

    card1, resumo_compras = criar_card_resumo(
        resumo,
        "🛒 Total de compras",
        COR_CARD_COMPRAS
    )

    card2, resumo_saidas = criar_card_resumo(
        resumo,
        "📤 Total de saídas",
        COR_CARD_SAIDAS
    )

    card3, resumo_diferenca = criar_card_resumo(
        resumo,
        "⚖️ Diferença",
        COR_CARD_DIFERENCA
    )

    for card in (
        card1,
        card2,
        card3
    ):

        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6,
            pady=6
        )

    # ========================================================
    # EVENTOS
    # ========================================================

    per.bind(
        "<<ComboboxSelected>>",
        atualizar_campos_data
    )

    tipo.bind(
        "<<ComboboxSelected>>",
        atualizar_relatorio
    )

    data_de.bind(
        "<KeyRelease>",
        atualizar_relatorio
    )

    data_ate.bind(
        "<KeyRelease>",
        atualizar_relatorio
    )

    # ========================================================
    # ESTADO INICIAL
    # ========================================================

    atualizar_campos_data()

    return aba

