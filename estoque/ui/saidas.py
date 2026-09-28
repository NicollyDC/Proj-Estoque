from tkinter import ttk, messagebox

from estoque.database import q, run
from estoque.utils import now, fmt, num, TIPOS, ESTOQUE_SQL
from estoque.ui.components import tree, buttons, form, sel, safe

st = None
root_ref = None


def prod_map():
    return {
        f"{r['codigo']} - {r['nome']}": r["id"]
        for r in q("SELECT * FROM produtos ORDER BY nome")
    }


def sai_refresh():
    global st

    st.delete(*st.get_children())

    for r in q("""
        SELECT s.*,
               p.codigo || ' - ' || p.nome AS prod
        FROM saidas s
        JOIN produtos p ON p.id = s.produto_id
        ORDER BY data_hora DESC, s.id DESC
    """):

        st.insert(
            "",
            "end",
            iid=str(r["id"]),
            values=(
                r["data_hora"],
                r["prod"],
                fmt(r["qtd"]),
                r["responsavel"],
                r["tipo"],
            ),
        )


@safe
def sai_edit(new=False):
    sid = None if new else sel(st)

    if not new and not sid:
        return

    mapa = prod_map()
    reverso = {v: k for k, v in mapa.items()}

    valores = {
        "data_hora": now(),
        "tipo": "uso e consumo",
    }

    if sid:
        atual = dict(q("SELECT * FROM saidas WHERE id=?", (sid,))[0])
        atual["produto"] = reverso.get(atual["produto_id"], "")
        valores = atual

    campos = [
        ("produto", "Produto", "combo", list(mapa)),
        ("qtd", "Quantidade", "entry", None),
        ("responsavel", "Quem fez a saída", "entry", None),
        ("data_hora", "Data e hora", "entry", None),
        ("tipo", "Tipo", "combo", TIPOS),
    ]

    r = form(root_ref, "Saída", campos, valores)

    if not r:
        return

    pid = mapa.get(r["produto"])

    if not pid:
        messagebox.showerror("Erro", "Escolha um produto da lista.")
        return

    dados = (
        pid,
        num(r["qtd"], 0.0),
        r["responsavel"].strip(),
        r["data_hora"].strip(),
        r["tipo"],
    )

    if sid:
        run("""
            UPDATE saidas
            SET produto_id=?,
                qtd=?,
                responsavel=?,
                data_hora=?,
                tipo=?
            WHERE id=?
        """, dados + (sid,))
    else:
        run("""
            INSERT INTO saidas
            (produto_id, qtd, responsavel, data_hora, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, dados)

    sai_refresh()

    p = q(ESTOQUE_SQL + " WHERE p.id=?", (pid,))[0]

    if p["estoque"] < 0:
        messagebox.showwarning(
            "Estoque negativo",
            f"{p['nome']} ficou com estoque negativo ({p['estoque']:g})."
        )

    elif p["estoque"] <= (p["minimo"] or 0):
        messagebox.showwarning(
            "Estoque mínimo",
            f"{p['nome']} atingiu o estoque mínimo ({p['estoque']:g})."
        )


@safe
def sai_del():
    sid = sel(st)

    if sid and messagebox.askyesno(
        "Excluir",
        "Excluir esta saída?"
    ):
        run("DELETE FROM saidas WHERE id=?", (sid,))
        sai_refresh()


def criar_aba_saidas(notebook, root):
    global st, root_ref

    root_ref = root

    aba = ttk.Frame(notebook)
    notebook.add(aba, text="Saídas")

    st = tree(
        aba,
        [
            ("data", "Data/hora", 140),
            ("prod", "Produto", 260),
            ("qtd", "Qtd", 70),
            ("resp", "Responsável", 170),
            ("tipo", "Tipo", 120),
        ],
    )

    buttons(
        aba,
        [
            ("Nova saída", lambda: sai_edit(True)),
            ("Editar saída", lambda: sai_edit(False)),
            ("Excluir saída", sai_del),
        ],
    )

    st.bind("<Double-1>", lambda e: sai_edit(False))

    sai_refresh()

    return aba