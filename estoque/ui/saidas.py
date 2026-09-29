import tkinter as tk
from tkinter import ttk, messagebox

from estoque.database import q, run
from estoque.utils import fmt, now
from estoque.ui.components import tree, buttons, sel, safe
from estoque.ui.saida_detalhes import saida_win

st = None
root_ref = None


# ---------------- REFRESH ---------------- #

def sai_refresh():
    """Atualiza a lista de saídas."""

    st.delete(*st.get_children())

    for s in q("""
        SELECT s.*,
               COUNT(i.id) AS itens,
               COALESCE(SUM(i.subtotal), 0) AS total
        FROM saidas s
        LEFT JOIN itens_saida i
            ON i.saida_id = s.id
        GROUP BY s.id
        ORDER BY s.data_hora DESC, s.id DESC
    """):

        st.insert(
            "",
            "end",
            iid=str(s["id"]),
            values=(
                s["data_hora"],
                s["responsavel"] or "-",
                s["tipo"],
                s["itens"],
                f"R$ {s['total']:.2f}",
            ),
        )


# ---------------- CRUD ---------------- #

@safe
def nova_saida():
    """Cria o cabeçalho da saída e abre os detalhes."""

    cur = run("""
        INSERT INTO saidas(
            responsavel,
            tipo,
            data_hora
        )
        VALUES (?, ?, ?)
    """, (
        "",
        "uso e consumo",
        now(),
    ))

    sai_refresh()
    saida_win(root_ref, cur.lastrowid)
    sai_refresh()


@safe
def editar_saida():
    sid = sel(st)

    if not sid:
        messagebox.showwarning(
            "Atenção",
            "Selecione uma saída."
        )
        return

    saida_win(root_ref, int(sid))
    sai_refresh()


@safe
def excluir_saida():
    sid = sel(st)

    if not sid:
        return

    if messagebox.askyesno(
        "Excluir",
        "Excluir esta saída e todos os seus itens?"
    ):
        run("DELETE FROM saidas WHERE id=?", (sid,))
        sai_refresh()


# ---------------- ABA ---------------- #

def criar_aba_saidas(notebook, root):
    global st, root_ref

    root_ref = root

    aba = ttk.Frame(notebook)
    notebook.add(aba, text="Saídas")

    st = tree(
        aba,
        [
            ("data", "Data/Hora", 150),
            ("resp", "Responsável", 180),
            ("tipo", "Tipo", 120),
            ("itens", "Itens", 70),
            ("total", "Valor Total", 120),
        ],
    )

    buttons(
        aba,
        [
            ("Nova saída", nova_saida),
            ("Abrir saída", editar_saida),
            ("Excluir saída", excluir_saida),
            ("Atualizar", sai_refresh),
        ],
    )

    st.bind("<Double-1>", lambda e: editar_saida())

    sai_refresh()

    return aba