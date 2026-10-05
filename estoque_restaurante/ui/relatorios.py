import tkinter as tk
from tkinter import ttk

from dados.restaurante.database import q
from estoque_restaurante.utils import fmt, TIPOS
from estoque_restaurante.ui.components import tree


rt = None
per = None
tipo = None
por_prod = None
custo_tipo = None
aviso = None


def periodo_atual():
    formato = {
        "Semana": "%Y-S%W",
        "Mês": "%Y-%m",
        "Ano": "%Y"
    }[per.get()]

    return formato


def buscar_periodo_mais_recente(formato, tipo_filtro):
    if tipo_filtro == "todos":
        rows = q("""
            SELECT MAX(strftime(?, s.data_hora)) AS periodo
            FROM saidas s
            JOIN itens_saida isd
                ON isd.saida_id = s.id
        """, (formato,))
    else:
        rows = q("""
            SELECT MAX(strftime(?, s.data_hora)) AS periodo
            FROM saidas s
            JOIN itens_saida isd
                ON isd.saida_id = s.id
            WHERE s.tipo=?
        """, (
            formato,
            tipo_filtro,
        ))

    if not rows:
        return None

    return rows[0]["periodo"]


def rel_gerar():
    global rt, aviso

    formato = periodo_atual()
    tipo_filtro = tipo.get()

    periodo_mais_recente = buscar_periodo_mais_recente(
        formato,
        tipo_filtro
    )

    if aviso is not None:
        aviso.config(text="")

    rt.delete(*rt.get_children())

    if not periodo_mais_recente:
        aviso.config(
            text=(
                "Não há dados suficientes para gerar o relatório. "
                "Ainda não existem movimentações registradas."
            )
        )
        return

    if tipo_filtro == "todos":
        where = "WHERE strftime(?, s.data_hora)=?"
        parametros = [
            formato,
            periodo_mais_recente,
        ]
    else:
        where = """
            WHERE strftime(?, s.data_hora)=?
              AND s.tipo=?
        """
        parametros = [
            formato,
            periodo_mais_recente,
            tipo_filtro,
        ]

    sql = f"""
        SELECT
            strftime(?, s.data_hora) AS periodo,
            {'p.nome' if por_prod.get() else "''"} AS produto,
            s.tipo,
            SUM(isd.qtd) AS qtd,
            SUM(
                COALESCE(
                    isd.subtotal,
                    isd.qtd * isd.valor_unit
                )
            ) AS custo
        FROM saidas s
        JOIN itens_saida isd
            ON isd.saida_id = s.id
        JOIN produtos p
            ON p.id = isd.produto_id
        {where}
        GROUP BY periodo, produto, s.tipo
        ORDER BY periodo DESC, s.tipo, produto
    """

    parametros_sql = [formato] + parametros

    rows = q(
        sql,
        parametros_sql
    )

    for r in rows:
        rt.insert(
            "",
            "end",
            values=(
                r["periodo"],
                r["produto"],
                r["tipo"],
                fmt(round(r["qtd"], 4)),
                f"{round(r['custo'] or 0, 2):.2f}"
            )
        )

    periodo_escolhido = {
        "Semana": "semana",
        "Mês": "mês",
        "Ano": "ano"
    }[per.get()]

    aviso.config(
        text=(
            f"Não há dados suficientes para uma análise detalhada "
            f"do período selecionado. "
            f"Dados disponíveis para o {periodo_escolhido} "
            f"{periodo_mais_recente}."
        )
    )


def criar_aba_relatorios(notebook, root):
    global rt, per, tipo, por_prod, custo_tipo, aviso

    aba = ttk.Frame(notebook)
    notebook.add(aba, text="Relatórios")

    per = ttk.Combobox(
        aba,
        values=["Semana", "Mês", "Ano"],
        state="readonly",
        width=8
    )
    per.set("Mês")

    tipo = ttk.Combobox(
        aba,
        values=["todos"] + TIPOS,
        state="readonly",
        width=14
    )
    tipo.set("todos")

    custo_tipo = ttk.Combobox(
        aba,
        values=["Custo médio"],
        state="readonly",
        width=14
    )
    custo_tipo.set("Custo médio")

    filtro = ttk.Frame(aba)
    filtro.pack(
        fill="x",
        padx=6,
        pady=6
    )

    ttk.Label(
        filtro,
        text="Agrupar por:"
    ).pack(side="left")

    per.pack(
        in_=filtro,
        side="left",
        padx=4
    )

    ttk.Label(
        filtro,
        text="Tipo:"
    ).pack(side="left")

    tipo.pack(
        in_=filtro,
        side="left",
        padx=4
    )

    ttk.Label(
        filtro,
        text="Custo:"
    ).pack(side="left")

    custo_tipo.pack(
        in_=filtro,
        side="left",
        padx=4
    )

    detalhar_var = tk.IntVar(value=0)

    detalhar = ttk.Checkbutton(
        filtro,
        text="Detalhar por produto",
        variable=detalhar_var
    )

    detalhar.pack(
        side="left",
        padx=6
    )

    class Wrapper:
        def get(self):
            return detalhar_var.get()

    por_prod = Wrapper()

    ttk.Button(
        filtro,
        text="Gerar",
        command=rel_gerar
    ).pack(
        side="left",
        padx=6
    )

    aviso = ttk.Label(
        aba,
        text="",
        wraplength=900
    )
    aviso.pack(
        anchor="w",
        padx=8,
        pady=(0, 6)
    )

    rt = tree(
        aba,
        [
            ("per", "Período", 110),
            ("prod", "Produto", 240),
            ("tipo", "Tipo", 120),
            ("qtd", "Quantidade", 100),
            ("custo", "Custo (R$)", 140),
        ],
    )

    ttk.Label(
        aba,
        text=(
            "Custo = quantidade da saída × custo médio "
            "registrado no momento da saída."
        )
    ).pack(
        anchor="w",
        padx=8
    )

    return aba