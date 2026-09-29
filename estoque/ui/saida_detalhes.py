
import tkinter as tk
from tkinter import ttk, messagebox

from estoque.database import q, run
from estoque.ui.components import tree, sel, safe
from estoque.utils import fmt, ESTOQUE_SQL


# ---------------- PESQUISA DE PRODUTO ---------------- #

def selecionar_produto(root):
    win = tk.Toplevel(root)
    win.title("Selecionar produto")
    win.geometry("650x420")
    win.transient(root)
    win.grab_set()

    busca = tk.StringVar()

    ttk.Label(
        win,
        text="Pesquisar por código ou nome:"
    ).pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Entry(
        win,
        textvariable=busca
    ).pack(fill="x", padx=10, pady=5)

    tv = tree(
        win,
        [
            ("cod", "Código", 90),
            ("nome", "Produto", 270),
            ("est", "Estoque", 80),
            ("un", "Un", 60),
        ],
    )

    escolhido = {"id": None}

    def carregar(*_):
        termo = busca.get().lower()

        tv.delete(*tv.get_children())

        for p in q(ESTOQUE_SQL + " WHERE ativo=1 ORDER BY p.nome"):
            texto = f"{p['codigo']} {p['nome']}".lower()

            if termo in texto:
                tv.insert(
                    "",
                    "end",
                    iid=str(p["id"]),
                    values=(
                        p["codigo"],
                        p["nome"],
                        fmt(round(p["estoque"], 4)),
                        p["unidade"],
                    ),
                )

    def confirmar(event=None):
        pid = sel(tv)

        if not pid:
            return

        escolhido["id"] = int(pid)
        win.destroy()

    busca.trace_add("write", carregar)

    tv.bind("<Double-1>", confirmar)

    ttk.Button(
        win,
        text="Selecionar",
        command=confirmar
    ).pack(pady=8)

    carregar()
    win.wait_window()

    return escolhido["id"]


# ---------------- JANELA PRINCIPAL ---------------- #

def saida_win(root, sid):
    w = tk.Toplevel(root)
    w.title(f"Saída #{sid}")
    w.geometry("850x560")

    # Cabeçalho
    cab = q(
        "SELECT * FROM saidas WHERE id=?",
        (sid,)
    )[0]

    topo = ttk.Frame(w)
    topo.pack(fill="x", padx=10, pady=8)

    ttk.Label(
        topo,
        text=f"Responsável: {cab['responsavel']}",
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w")

    ttk.Label(
        topo,
        text=f"Tipo: {cab['tipo']}"
    ).grid(row=0, column=1, padx=20)

    ttk.Label(
        topo,
        text=f"Data: {cab['data_hora']}"
    ).grid(row=0, column=2)

    # Tabela
    tv = tree(
        w,
        [
            ("cod", "Código", 90),
            ("prod", "Produto", 260),
            ("qtd", "Qtd", 70),
            ("vu", "Valor Unit.", 100),
            ("sub", "Subtotal", 110),
        ],
    )

    total_var = tk.StringVar(value="R$ 0,00")

    def refresh():
        tv.delete(*tv.get_children())

        total = 0

        for i in q("""
            SELECT i.*,
                   p.codigo,
                   p.nome
            FROM itens_saida i
            JOIN produtos p
                ON p.id=i.produto_id
            WHERE saida_id=?
        """, (sid,)):
            total += i["subtotal"] or 0

            tv.insert(
                "",
                "end",
                iid=str(i["id"]),
                values=(
                    i["codigo"],
                    i["nome"],
                    fmt(i["qtd"]),
                    f"R$ {i['valor_unit']:.2f}",
                    f"R$ {i['subtotal']:.2f}",
                ),
            )

        total_var.set(f"R$ {total:.2f}")

    @safe
    def adicionar():
        pid = selecionar_produto(w)

        if not pid:
            return

        prod = q("""
            SELECT *
            FROM produtos
            WHERE id=?
        """, (pid,))[0]

        valor = q("""
            SELECT valor_unit
            FROM itens
            WHERE produto_id=?
            ORDER BY id DESC
            LIMIT 1
        """, (pid,))

        if not valor:
            messagebox.showwarning(
                "Sem custo",
                "Esse produto ainda não possui valor de entrada."
            )
            return

        valor_unit = valor[0]["valor_unit"]

        pop = tk.Toplevel(w)
        pop.title("Quantidade")
        pop.transient(w)
        pop.grab_set()

        ttk.Label(
            pop,
            text=f"{prod['codigo']} - {prod['nome']}"
        ).pack(padx=10, pady=(10, 5))

        ttk.Label(
            pop,
            text=f"Valor unitário: R$ {valor_unit:.2f}"
        ).pack()

        qtd = tk.StringVar()

        ttk.Entry(
            pop,
            textvariable=qtd,
            width=12
        ).pack(pady=8)

        def salvar():
            try:
                qv = float(qtd.get().replace(",", "."))

                if qv <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Quantidade inválida."
                )
                return

            subtotal = round(qv * valor_unit, 2)

            run("""
                INSERT INTO itens_saida(
                    saida_id,
                    produto_id,
                    qtd,
                    valor_unit,
                    subtotal
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                sid,
                pid,
                qv,
                valor_unit,
                subtotal,
            ))

            pop.destroy()
            refresh()

        ttk.Button(
            pop,
            text="Adicionar",
            command=salvar
        ).pack(pady=(0, 10))

    @safe
    def excluir_item():
        iid = sel(tv)

        if not iid:
            return

        if messagebox.askyesno(
            "Excluir",
            "Remover este item da saída?"
        ):
            run(
                "DELETE FROM itens_saida WHERE id=?",
                (iid,)
            )
            refresh()

    botoes = ttk.Frame(w)
    botoes.pack(fill="x", padx=10, pady=6)

    ttk.Button(
        botoes,
        text="+ Adicionar produto",
        command=adicionar
    ).pack(side="left")

    ttk.Button(
        botoes,
        text="Excluir item",
        command=excluir_item
    ).pack(side="left", padx=6)

    rodape = ttk.Frame(w)
    rodape.pack(fill="x", padx=10, pady=10)

    ttk.Label(
        rodape,
        text="Valor total:",
        font=("Segoe UI", 10, "bold")
    ).pack(side="left")

    ttk.Label(
        rodape,
        textvariable=total_var,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=8)

    refresh()