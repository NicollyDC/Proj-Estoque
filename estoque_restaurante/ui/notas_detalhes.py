import tkinter as tk
from tkinter import ttk, messagebox

from dados.restaurante.database import q, run
from estoque_restaurante.utils import today, fmt, num
from estoque_restaurante.front import tree, buttons, form, sel, safe


ITEM_HELP = "Qtd. no estoque (vazio = qtd × fator)"

PROD_F = [
    ("codigo", "Código", "entry", None),
    ("nome", "Nome", "entry", None),
    ("unidade", "Unidade de medida", "entry", None),
    ("minimo", "Estoque mínimo", "entry", None),
    ("finalidade", "Finalidade", "combo", ["venda", "uso e consumo"]),
    ("ativo", "Ativo", "check", None),
]


def prod_map():
    return {
        f"{r['codigo']} - {r['nome']}": r["id"]
        for r in q("SELECT * FROM produtos ORDER BY nome")
    }


def nota_win(root, nid, on_close=None):
    w = tk.Toplevel(root)
    w.title("Nota")
    w.geometry("980x420")

    head = ttk.Label(w, font=("", 11, "bold"))
    head.pack(anchor="w", padx=8, pady=6)

    t = tree(
        w,
        [
            ("cod", "Cód. fornecedor", 110),
            ("desc", "Descrição", 230),
            ("qtd", "Qtd nota", 70),
            ("un", "Un.", 60),
            ("prod", "Produto", 240),
            ("fator", "Fator", 60),
            ("est", "Qtd estoque", 80),
            ("val", "Valor", 80),
        ],
    )

    def refresh():
        n = q(
            "SELECT * FROM notas WHERE id=?",
            (nid,)
        )[0]

        fat = (
            f"FATURADA em {n['data_faturamento'] or '-'}"
            if n["faturada"]
            else "NÃO faturada"
        )

        head.config(
            text=(
                f"Nota {n['numero']} | "
                f"{n['fornecedor']} | "
                f"{n['data']} | "
                f"{fat}"
            )
        )

        t.delete(*t.get_children())

        for r in q(
            """
            SELECT i.*, p.codigo || ' - ' || p.nome AS prod
            FROM itens i
            LEFT JOIN produtos p ON p.id=i.produto_id
            WHERE nota_id=?
            """,
            (nid,),
        ):

            t.insert(
                "",
                "end",
                iid=str(r["id"]),
                values=(
                    r["cod_forn"],
                    r["descricao"],
                    fmt(r["qtd"]),
                    r["unidade"],
                    r["prod"] or "⚠ sem vínculo",
                    fmt(r["fator"]),
                    fmt(r["qtd_estoque"]),
                    fmt(r["valor_total"]),
                ),
            )

    @safe
    def edit_head():
        from estoque_restaurante.ui.notas import NOTA_F

        n = dict(
            q(
                "SELECT * FROM notas WHERE id=?",
                (nid,)
            )[0]
        )

        n["data_fat"] = n["data_faturamento"]

        r = form(
            w,
            "Cabeçalho da nota",
            NOTA_F,
            n
        )

        if not r:
            return

        data_fat = (
            (r["data_fat"].strip() or today())
            if r["faturada"]
            else None
        )

        run(
            """
            UPDATE notas
            SET numero=?, fornecedor=?, data=?,
                faturada=?, data_faturamento=?
            WHERE id=?
            """,
            (
                r["numero"].strip(),
                r["fornecedor"].strip(),
                r["data"].strip(),
                int(r["faturada"]),
                data_fat,
                nid,
            ),
        )

        refresh()

    @safe
    def item_edit(iid=None):
        fornecedor = q(
            "SELECT fornecedor FROM notas WHERE id=?",
            (nid,)
        )[0]["fornecedor"]

        mapa = prod_map()
        reverso = {v: k for k, v in mapa.items()}

        valores = {}

        if iid:
            it = q(
                "SELECT * FROM itens WHERE id=?",
                (iid,)
            )[0]

            valores = dict(it)
            valores["produto"] = reverso.get(
                it["produto_id"],
                ""
            )

            if it["qtd_estoque"] == (
                it["qtd"] or 0
            ) * (
                it["fator"] or 1
            ):
                valores["qtd_estoque"] = None

        campos = [
            ("cod_forn", "Código fornecedor", "entry", None),
            ("descricao", "Descrição", "entry", None),
            ("qtd", "Quantidade", "entry", None),
            ("unidade", "Unidade", "entry", None),
            ("produto", "Produto", "combo", list(mapa)),
            ("fator", "Fator", "entry", None),
            ("qtd_estoque", ITEM_HELP, "entry", None),
            ("valor_total", "Valor total", "entry", None),
        ]

        r = form(
            w,
            "Item da nota",
            campos,
            valores
        )

        if not r:
            return

        codigo = r["cod_forn"].strip()
        pid = mapa.get(r["produto"])

        vinc = q(
            """
            SELECT * FROM vinculos
            WHERE fornecedor=? AND cod_forn=?
            """,
            (
                fornecedor,
                codigo,
            ),
        )

        if not pid and vinc:
            pid = vinc[0]["produto_id"]

        fator = num(
            r["fator"],
            vinc[0]["fator"] if vinc else 1.0
        )

        qtd = num(
            r["qtd"],
            0.0
        )

        estoque = num(
            r["qtd_estoque"],
            qtd * fator
        )

        dados = (
            codigo,
            r["descricao"].strip(),
            qtd,
            r["unidade"].strip(),
            pid,
            fator,
            estoque,
            num(r["valor_total"]),
        )

        if iid:
            run(
                """
                UPDATE itens
                SET cod_forn=?, descricao=?, qtd=?, unidade=?,
                    produto_id=?, fator=?, qtd_estoque=?, valor_total=?
                WHERE id=?
                """,
                dados + (iid,),
            )

        else:
            run(
                """
                INSERT INTO itens
                (cod_forn,descricao,qtd,unidade,
                 produto_id,fator,qtd_estoque,valor_total,nota_id)
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                dados + (nid,),
            )

        if pid and codigo:
            run(
                """
                INSERT OR REPLACE INTO vinculos
                VALUES (?,?,?,?)
                """,
                (
                    fornecedor,
                    codigo,
                    pid,
                    fator,
                ),
            )

        refresh()

    @safe
    def criar_produto():
        iid = sel(t)

        if not iid:
            return

        it = q(
            """
            SELECT i.*, n.fornecedor forn
            FROM itens i
            JOIN notas n ON n.id=i.nota_id
            WHERE i.id=?
            """,
            (iid,),
        )[0]

        r = form(
            w,
            "Novo Produto",
            PROD_F,
            {
                "codigo": it["cod_forn"],
                "nome": it["descricao"],
                "unidade": it["unidade"],
                "finalidade": "uso e consumo",
                "ativo": 1,
            },
        )

        if not r:
            return

        cur = run(
            """
            INSERT INTO produtos
            (codigo,nome,unidade,minimo,finalidade,ativo)
            VALUES (?,?,?,?,?,?)
            """,
            (
                r["codigo"].strip(),
                r["nome"].strip(),
                r["unidade"].strip(),
                num(r["minimo"], 0.0),
                r["finalidade"],
                int(r["ativo"]),
            ),
        )

        fator = it["fator"] or 1.0

        run(
            """
            UPDATE itens
            SET produto_id=?, qtd_estoque=?
            WHERE id=?
            """,
            (
                cur.lastrowid,
                (it["qtd"] or 0) * fator,
                iid,
            ),
        )

        run(
            """
            INSERT OR REPLACE INTO vinculos
            VALUES (?,?,?,?)
            """,
            (
                it["forn"],
                it["cod_forn"],
                cur.lastrowid,
                fator,
            ),
        )

        refresh()

    @safe
    def item_del():
        iid = sel(t)

        if iid and messagebox.askyesno(
            "Excluir",
            "Excluir este item?"
        ):
            run(
                "DELETE FROM itens WHERE id=?",
                (iid,)
            )
            refresh()

    def editar_item(event=None):
        iid = sel(t)

        if iid:
            item_edit(iid)

    buttons(
        w,
        [
            ("Editar cabeçalho", edit_head),
            ("Adicionar item", lambda: item_edit()),
            ("Editar item", editar_item),
            ("Criar produto", criar_produto),
            ("Excluir item", item_del),
        ],
    )

    t.bind(
        "<Double-1>",
        editar_item
    )

    if on_close:
        w.bind(
            "<Destroy>",
            lambda e: on_close()
            if e.widget is w
            else None
        )

    refresh()