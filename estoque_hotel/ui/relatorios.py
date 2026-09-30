import tkinter as tk
from tkinter import ttk

from estoque_hotel.app_state import marcar_alteracao
from dados.hotel.database import q
from estoque_hotel.utils import fmt, TIPOS
from estoque_hotel.ui.components import tree

rt = None
per = None
tipo = None
por_prod = None


def rel_gerar():
    global rt

    formato = {
        "Semana": "%Y-S%W",
        "Mês": "%Y-%m",
        "Ano": "%Y"
    }[per.get()]

    if tipo.get() == "todos":
        where = ""
        parametros = [formato]
    else:
        where = "WHERE s.tipo=?"
        parametros = [formato, tipo.get()]

    rt.delete(*rt.get_children())

    sql = f"""
        SELECT
            strftime(?, s.data_hora) AS periodo,
            {'p.nome' if por_prod.get() else "''"} AS produto,
            s.tipo,
            SUM(isd.qtd) AS qtd,
            SUM(
                isd.qtd * COALESCE(
                    (
                        SELECT SUM(valor_total) /
                               NULLIF(SUM(qtd_estoque), 0)
                        FROM itens
                        WHERE produto_id = isd.produto_id
                    ),
                    0
                )
            ) AS custo
        FROM saidas s
        JOIN itens_saida isd ON isd.saida_id = s.id
        JOIN produtos p ON p.id = isd.produto_id
        {where}
        GROUP BY periodo, produto, s.tipo
        ORDER BY periodo DESC, s.tipo
    """

    for r in q(sql, parametros):
        rt.insert(
            "",
            "end",
            values=(
                r["periodo"],
                r["produto"],
                r["tipo"],
                fmt(round(r["qtd"], 4)),
                f"{round(r['custo'], 2):.2f}"
            )
        )


def criar_aba_relatorios(notebook, root):
    global rt, per, tipo, por_prod

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

    filtro = ttk.Frame(aba)
    filtro.pack(fill="x", padx=6, pady=6)

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

    detalhar = ttk.Checkbutton(
        filtro,
        text="Detalhar por produto"
    )

    detalhar_var = tk.IntVar(value=0)

    detalhar.config(
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
        text="Custo estimado = quantidade de saída × custo médio de entrada."
    ).pack(
        anchor="w",
        padx=8
    )

    return aba