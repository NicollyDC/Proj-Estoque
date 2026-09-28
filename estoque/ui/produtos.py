import tkinter as tk
from tkinter import ttk

from estoque.database import q, run
from estoque.utils import ESTOQUE_SQL, fmt, num, FIN
from estoque.ui.components import tree, buttons, form, sel, safe

# Campos do formulário
PROD_F = [
    ("codigo", "Código", "entry", None),
    ("nome", "Nome", "entry", None),
    ("unidade", "Unidade de medida", "entry", None),
    ("minimo", "Estoque mínimo", "entry", None),
    ("finalidade", "Finalidade", "combo", FIN),
    ("ativo", "Ativo", "check", None),
]

pt = None  # Treeview global da aba


def prod_refresh():
    """Atualiza a tabela de produtos."""
    global pt

    pt.delete(*pt.get_children())

    for r in q(ESTOQUE_SQL + " ORDER BY p.nome"):
        baixo = r["ativo"] and r["estoque"] <= (r["minimo"] or 0)

        pt.insert(
            "",
            "end",
            iid=str(r["id"]),
            tags=("low",) if baixo else (),
            values=(
                r["codigo"],
                r["nome"],
                r["unidade"],
                fmt(round(r["estoque"], 4)),
                fmt(r["minimo"]),
                r["finalidade"],
                "Sim" if r["ativo"] else "Não",
                "ESTOQUE MÍNIMO!" if baixo else "",
            ),
        )


@safe
def prod_edit(root, new=False):
    """Cria ou edita um produto."""
    pid = None if new else sel(pt)

    if not new and not pid:
        return

    atual = (
        dict(q("SELECT * FROM produtos WHERE id=?", (pid,))[0])
        if pid
        else {"ativo": 1, "finalidade": "uso e consumo"}
    )

    r = form(root, "Produto", PROD_F, atual)

    if not r or not r["codigo"].strip() or not r["nome"].strip():
        return

    valores = (
        r["codigo"].strip(),
        r["nome"].strip(),
        r["unidade"].strip(),
        num(r["minimo"], 0.0),
        r["finalidade"],
        int(r["ativo"]),
    )

    if pid:
        run(
            """UPDATE produtos
               SET codigo=?, nome=?, unidade=?, minimo=?, finalidade=?, ativo=?
               WHERE id=?""",
            valores + (pid,),
        )
    else:
        run(
            """INSERT INTO produtos
               (codigo,nome,unidade,minimo,finalidade,ativo)
               VALUES (?,?,?,?,?,?)""",
            valores,
        )

    prod_refresh()


@safe
def prod_del():
    pid = sel(pt)

    if not pid:
        return

    from tkinter import messagebox

    if messagebox.askyesno(
        "Excluir",
        "Excluir este produto?\n\nSe houver movimentações, prefira apenas inativá-lo.",
    ):
        run("DELETE FROM produtos WHERE id=?", (pid,))
        prod_refresh()


def criar_aba_produtos(notebook, root):
    """Cria a aba Produtos dentro do Notebook."""
    global pt

    aba = ttk.Frame(notebook)
    notebook.add(aba, text="Produtos / Estoque")

    pt = tree(
        aba,
        [
            ("cod", "Código", 100),
            ("nome", "Nome", 260),
            ("un", "Unidade", 70),
            ("est", "Estoque atual", 100),
            ("min", "Mínimo", 80),
            ("fin", "Finalidade", 110),
            ("ativo", "Ativo", 60),
            ("alerta", "Alerta", 130),
        ],
    )

    pt.tag_configure("low", background="#ffd6d6")

    buttons(
        aba,
        [
            ("Novo produto", lambda: prod_edit(root, True)),
            ("Editar produto", lambda: prod_edit(root)),
            ("Excluir produto", prod_del),
        ],
    )

    pt.bind("<Double-1>", lambda e: prod_edit(root))

    prod_refresh()

    return aba