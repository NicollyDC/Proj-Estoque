import tkinter as tk
from tkinter import ttk, messagebox

from dados.hotel.database import q, run
from estoque_hotel.ui.components import tree, sel, safe
from estoque_hotel.utils import fmt, ESTOQUE_SQL


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
    ).pack(
        anchor="w",
        padx=10,
        pady=(10, 0)
    )

    ttk.Entry(
        win,
        textvariable=busca
    ).pack(
        fill="x",
        padx=10,
        pady=5
    )

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

        for p in q(
            ESTOQUE_SQL + " WHERE ativo=1 ORDER BY p.nome"
        ):
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

    busca.trace_add(
        "write",
        carregar
    )

    tv.bind(
        "<Double-1>",
        confirmar
    )

    ttk.Button(
        win,
        text="Selecionar",
        command=confirmar
    ).pack(
        pady=8
    )

    carregar()

    win.wait_window()

    return escolhido["id"]


# ---------------- CUSTO MÉDIO ---------------- #

def obter_custo_medio(produto_id):
    """
    Calcula o custo médio atual do estoque.

    Valor do estoque =
        valor das entradas
        - valor das saídas

    Custo médio =
        valor do estoque / quantidade em estoque
    """

    dados = q("""
        SELECT
            COALESCE(
                (
                    SELECT SUM(
                        qtd_estoque * COALESCE(valor_unit, 0)
                    )
                    FROM itens
                    WHERE produto_id=?
                ),
                0
            ) AS valor_entradas,

            COALESCE(
                (
                    SELECT SUM(
                        qtd * COALESCE(valor_unit, 0)
                    )
                    FROM itens_saida
                    WHERE produto_id=?
                ),
                0
            ) AS valor_saidas,

            COALESCE(
                (
                    SELECT SUM(qtd_estoque)
                    FROM itens
                    WHERE produto_id=?
                ),
                0
            ) AS qtd_entradas,

            COALESCE(
                (
                    SELECT SUM(qtd)
                    FROM itens_saida
                    WHERE produto_id=?
                ),
                0
            ) AS qtd_saidas
    """, (
        produto_id,
        produto_id,
        produto_id,
        produto_id,
    ))

    if not dados:
        return None, 0

    r = dados[0]

    qtd_estoque = (
        (r["qtd_entradas"] or 0)
        - (r["qtd_saidas"] or 0)
    )

    valor_estoque = (
        (r["valor_entradas"] or 0)
        - (r["valor_saidas"] or 0)
    )

    if qtd_estoque <= 0:
        return None, max(qtd_estoque, 0)

    custo_medio = valor_estoque / qtd_estoque

    return custo_medio, qtd_estoque


# ---------------- JANELA PRINCIPAL ---------------- #

def saida_win(root, sid):
    w = tk.Toplevel(root)

    w.title(f"Saída #{sid}")
    w.geometry("850x600")

    cab = q(
        "SELECT * FROM saidas WHERE id=?",
        (sid,)
    )[0]

    # ========================================================
    # CABEÇALHO
    # ========================================================

    topo = ttk.Frame(w)

    topo.pack(
        fill="x",
        padx=10,
        pady=8
    )

    # --------------------------------------------------------
    # RESPONSÁVEL
    # --------------------------------------------------------

    ttk.Label(
        topo,
        text="Responsável pela retirada:"
    ).grid(
        row=0,
        column=0,
        sticky="w"
    )

    responsavel_var = tk.StringVar(
        value=cab["responsavel"] or ""
    )

    entrada_responsavel = ttk.Entry(
        topo,
        textvariable=responsavel_var,
        width=35
    )

    entrada_responsavel.grid(
        row=0,
        column=1,
        padx=(8, 6),
        sticky="w"
    )

    def salvar_responsavel():

        responsavel = responsavel_var.get().strip()

        if not responsavel:
            messagebox.showwarning(
                "Responsável",
                "Informe quem foi o responsável pela retirada.",
                parent=w
            )
            entrada_responsavel.focus()
            return

        run(
            """
            UPDATE saidas
            SET responsavel=?
            WHERE id=?
            """,
            (
                responsavel,
                sid,
            )
        )

        messagebox.showinfo(
            "Responsável",
            "Responsável salvo com sucesso.",
            parent=w
        )

    ttk.Button(
        topo,
        text="Salvar",
        command=salvar_responsavel
    ).grid(
        row=0,
        column=2,
        padx=(0, 15)
    )

    # --------------------------------------------------------
    # INFORMAÇÕES
    # --------------------------------------------------------

    ttk.Label(
        topo,
        text=f"Tipo: {cab['tipo']}"
    ).grid(
        row=0,
        column=3,
        padx=10
    )

    ttk.Label(
        topo,
        text=f"Data: {cab['data_hora']}"
    ).grid(
        row=0,
        column=4,
        padx=10
    )

    # ========================================================
    # TABELA
    # ========================================================

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

    total_var = tk.StringVar(
        value="R$ 0,00"
    )

    def refresh():
        tv.delete(
            *tv.get_children()
        )

        total = 0

        for i in q("""
            SELECT i.*,
                   p.codigo,
                   p.nome
            FROM itens_saida i
            JOIN produtos p
                ON p.id=i.produto_id
            WHERE saida_id=?
            ORDER BY i.id
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

        total_var.set(
            f"R$ {total:.2f}"
        )

    # ========================================================
    # ADICIONAR PRODUTO
    # ========================================================

    @safe
    def adicionar():

        pid = selecionar_produto(w)

        if not pid:
            return

        prod = q("""
            SELECT *
            FROM produtos
            WHERE id=?
        """, (pid,))

        if not prod:
            messagebox.showerror(
                "Erro",
                "Produto não encontrado."
            )
            return

        prod = prod[0]

        custo_medio, estoque = obter_custo_medio(pid)

        if estoque <= 0:
            messagebox.showwarning(
                "Estoque insuficiente",
                "Esse produto não possui estoque disponível."
            )
            return

        if custo_medio is None:
            messagebox.showwarning(
                "Sem custo",
                "Não foi possível calcular o custo médio deste produto."
            )
            return

        pop = tk.Toplevel(w)

        pop.title("Quantidade")
        pop.transient(w)
        pop.grab_set()

        ttk.Label(
            pop,
            text=f"{prod['codigo']} - {prod['nome']}"
        ).pack(
            padx=10,
            pady=(10, 5)
        )

        ttk.Label(
            pop,
            text=(
                f"Estoque disponível: "
                f"{fmt(round(estoque, 4))} "
                f"{prod['unidade'] or ''}"
            )
        ).pack()

        ttk.Label(
            pop,
            text=f"Custo médio: R$ {custo_medio:.2f}"
        ).pack(
            pady=(4, 0)
        )

        qtd = tk.StringVar()

        ttk.Entry(
            pop,
            textvariable=qtd,
            width=12
        ).pack(
            pady=8
        )

        def salvar():

            try:
                qv = float(
                    qtd.get().replace(",", ".")
                )

                if qv <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Quantidade inválida."
                )
                return

            if qv > estoque:
                messagebox.showwarning(
                    "Estoque insuficiente",
                    (
                        f"A quantidade informada é maior que "
                        f"o estoque disponível.\n\n"
                        f"Estoque disponível: "
                        f"{fmt(round(estoque, 4))}\n"
                        f"Quantidade solicitada: {fmt(qv)}"
                    )
                )
                return

            subtotal = round(
                qv * custo_medio,
                2
            )

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
                custo_medio,
                subtotal,
            ))

            pop.destroy()

            refresh()

        ttk.Button(
            pop,
            text="Adicionar",
            command=salvar
        ).pack(
            pady=(0, 10)
        )

    # ========================================================
    # EXCLUIR ITEM
    # ========================================================

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

    # ========================================================
    # BOTÕES
    # ========================================================

    botoes = ttk.Frame(w)

    botoes.pack(
        fill="x",
        padx=10,
        pady=6
    )

    ttk.Button(
        botoes,
        text="+ Adicionar produto",
        command=adicionar
    ).pack(
        side="left"
    )

    ttk.Button(
        botoes,
        text="Excluir item",
        command=excluir_item
    ).pack(
        side="left",
        padx=6
    )

    # ========================================================
    # RODAPÉ
    # ========================================================

    rodape = ttk.Frame(w)

    rodape.pack(
        fill="x",
        padx=10,
        pady=10
    )

    ttk.Label(
        rodape,
        text="Valor total:",
        font=("Segoe UI", 10, "bold")
    ).pack(
        side="left"
    )

    ttk.Label(
        rodape,
        textvariable=total_var,
        font=("Segoe UI", 10, "bold")
    ).pack(
        side="left",
        padx=8
    )

    refresh()