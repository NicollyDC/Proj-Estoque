import tkinter as tk
from tkinter import ttk, messagebox

from dados.restaurante.database import q, run
from estoque_restaurante.front import tree, sel, safe
from estoque_restaurante.utils import fmt, ESTOQUE_SQL, TIPOS


def selecionar_produto(root):
    win = tk.Toplevel(root)
    win.title("Selecionar produto")
    win.geometry("650x420")
    win.transient(root)
    win.grab_set()

    busca = tk.StringVar()

    ttk.Label(
        win,
        text="Pesquise pelo código ou pelo nome do produto:",
        style="App.TLabel"
    ).pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Entry(win, textvariable=busca, style="App.TEntry").pack(fill="x", padx=10, pady=5)

    tv = tree(
        win,
        [
            ("cod", "Código", 90),
            ("nome", "Produto", 270),
            ("est", "Saldo disponível (unidade-base)", 180),
            ("un", "Unidade-base", 100),
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
        pid = sel(tv, win)
        if not pid:
            return
        escolhido["id"] = int(pid)
        win.destroy()

    busca.trace_add("write", carregar)
    tv.bind("<Double-1>", confirmar)

    ttk.Button(win, text="Selecionar", command=confirmar, style="Primario.TButton").pack(pady=8)
    ttk.Button(win, text="Cancelar", command=win.destroy, style="Padrao.TButton").pack(pady=(0, 8))

    carregar()
    win.wait_window()
    return escolhido["id"]


def obter_custo_medio(produto_id):
    dados = q(ESTOQUE_SQL + " WHERE p.id=?", (produto_id,))
    if not dados:
        return None, 0
    quantidade = float(dados[0]["estoque"] or 0)
    if quantidade <= 0:
        return None, max(quantidade, 0)
    return float(dados[0]["valor_unitario"] or 0), quantidade


def saida_win(root, sid):
    w = tk.Toplevel(root)
    w.title(f"Saída #{sid}")
    w.geometry("900x620")
    w.minsize(760, 520)
    w.transient(root)

    cab = q("SELECT * FROM saidas WHERE id=?", (sid,))
    if not cab:
        messagebox.showerror("Saída", "Esta saída não foi encontrada.", parent=root)
        w.destroy()
        return

    cab = cab[0]

    topo = ttk.Frame(w)
    topo.pack(fill="x", padx=12, pady=10)
    topo.columnconfigure(1, weight=1)

    ttk.Label(topo, text="Responsável pela retirada:", style="App.TLabel").grid(
        row=0, column=0, sticky="w"
    )

    responsavel_var = tk.StringVar(value=cab["responsavel"] or "")
    entrada_responsavel = ttk.Entry(
        topo, textvariable=responsavel_var, width=32, style="App.TEntry"
    )
    entrada_responsavel.grid(row=0, column=1, padx=(8, 6), sticky="ew")

    ttk.Label(topo, text="Tipo:", style="App.TLabel").grid(row=0, column=2, padx=(12, 4))
    tipo_var = tk.StringVar(value=cab["tipo"] or "uso e consumo")
    tipo_combo = ttk.Combobox(
        topo,
        textvariable=tipo_var,
        values=TIPOS,
        state="readonly",
        width=16,
        style="App.TCombobox"
    )
    tipo_combo.grid(row=0, column=3, padx=(0, 8))

    def salvar_cabecalho():
        responsavel = responsavel_var.get().strip()
        tipo = tipo_var.get().strip()

        if not responsavel:
            messagebox.showwarning(
                "Responsável",
                "Informe quem retirou os produtos.",
                parent=w
            )
            entrada_responsavel.focus()
            return False

        if tipo not in TIPOS:
            messagebox.showwarning("Tipo", "Selecione o tipo da saída.", parent=w)
            return False

        run(
            "UPDATE saidas SET responsavel=?, tipo=? WHERE id=?",
            (responsavel, tipo, sid)
        )
        return True

    ttk.Button(
        topo,
        text="Salvar dados",
        command=lambda: (
            salvar_cabecalho() and messagebox.showinfo(
                "Saída", "Responsável e tipo salvos.", parent=w
            )
        ),
        style="Primario.TButton"
    ).grid(row=0, column=4, padx=(0, 10))

    ttk.Label(topo, text=f"Data: {cab['data_hora']}").grid(row=0, column=5, padx=6)

    rodape = ttk.Frame(w)
    rodape.pack(fill="x", side="bottom", padx=12, pady=10)

    botoes = ttk.Frame(w)
    botoes.pack(fill="x", padx=12, pady=(0, 6))

    tv = tree(
        w,
        [
            ("cod", "Código", 90),
            ("prod", "Produto", 260),
            ("qtd", "Quantidade (unidade-base)", 180),
            ("vu", "Valor unitário (unidade-base)", 190),
            ("sub", "Subtotal", 110),
        ],
    )

    total_var = tk.StringVar(value="R$ 0,00")

    def refresh():
        tv.delete(*tv.get_children())
        total = 0
        for i in q("""
            SELECT i.*, p.codigo, p.nome, p.unidade
            FROM itens_saida i
            JOIN produtos p ON p.id=i.produto_id
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
                    f"{fmt(i['qtd'])} {i['unidade'] or 'unidade-base'}",
                    f"R$ {(i['valor_unit'] or 0):.2f}",
                    f"R$ {(i['subtotal'] or 0):.2f}",
                ),
            )
        total_var.set(f"R$ {total:.2f}")

    @safe
    def adicionar():
        if not salvar_cabecalho():
            return

        pid = selecionar_produto(w)
        if not pid:
            return

        prod = q("SELECT * FROM produtos WHERE id=?", (pid,))
        if not prod:
            messagebox.showerror("Produto", "Produto não encontrado.", parent=w)
            return

        prod = prod[0]
        custo_medio, estoque = obter_custo_medio(pid)

        if estoque <= 0:
            messagebox.showwarning(
                "Estoque insuficiente",
                "Este produto não possui quantidade disponível no estoque.",
                parent=w
            )
            return

        if custo_medio is None:
            messagebox.showwarning(
                "Sem custo",
                "Não foi possível calcular o valor deste produto. "
                "Confira se ele está vinculado a uma nota com valor.",
                parent=w
            )
            return

        pop = tk.Toplevel(w)
        pop.title("Quantidade")
        pop.transient(w)
        pop.grab_set()

        ttk.Label(pop, text=f"{prod['codigo']} - {prod['nome']}").pack(padx=12, pady=(12, 6))
        ttk.Label(
            pop,
            text=f"Disponível na unidade-base: {fmt(round(estoque, 4))} {prod['unidade'] or 'unidades'}"
        ).pack()
        ttk.Label(pop, text=f"Valor unitário (unidade-base): R$ {custo_medio:.2f}").pack(pady=(4, 0))
        ttk.Label(pop, text="Informe a quantidade efetivamente retirada na unidade-base.").pack(pady=(8, 0))
        ttk.Label(pop, text="Embalagens não são convertidas automaticamente.").pack(pady=(2, 0))
        ttk.Label(pop, text=f"Quantidade a retirar ({prod['unidade'] or 'unidades-base'}):").pack(pady=(8, 0))

        qtd = tk.StringVar()
        entrada = ttk.Entry(pop, textvariable=qtd, width=14, style="App.TEntry")
        entrada.pack(pady=8)
        entrada.focus_set()

        def salvar_item():
            try:
                qv = float(qtd.get().replace(",", "."))
                if qv <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Quantidade", "Informe uma quantidade maior que zero.", parent=pop)
                return

            _, estoque_atual = obter_custo_medio(pid)
            if qv > estoque_atual:
                messagebox.showwarning(
                    "Estoque insuficiente",
                    "A quantidade informada é maior que o estoque disponível.\n\n"
                    f"Disponível na unidade-base: {fmt(round(estoque_atual, 4))} {prod['unidade'] or 'unidades'}\n"
                    f"Informado na unidade-base: {fmt(qv)} {prod['unidade'] or 'unidades'}",
                    parent=pop
                )
                return

            subtotal = round(qv * custo_medio, 2)
            run(
                """
                INSERT INTO itens_saida(
                    saida_id, produto_id, qtd, valor_unit, subtotal
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (sid, pid, qv, custo_medio, subtotal)
            )
            pop.destroy()
            refresh()

        ttk.Button(pop, text="Adicionar", command=salvar_item, style="Primario.TButton").pack(pady=(0, 4))
        ttk.Button(pop, text="Cancelar", command=pop.destroy, style="Padrao.TButton").pack(pady=(0, 10))
        pop.bind("<Return>", lambda e: salvar_item())

    @safe
    def excluir_item():
        iid = sel(tv, w)
        if not iid:
            return

        if messagebox.askyesno("Excluir item", "Remover este produto da saída?", parent=w):
            run("DELETE FROM itens_saida WHERE id=?", (iid,))
            refresh()

    def fechar():
        if not salvar_cabecalho():
            return

        itens = q("SELECT COUNT(*) AS n FROM itens_saida WHERE saida_id=?", (sid,))
        if itens and itens[0]["n"] == 0:
            if messagebox.askyesno(
                "Saída vazia",
                "Esta saída não possui produtos.\n\nDeseja apagá-la?",
                parent=w
            ):
                run("DELETE FROM saidas WHERE id=?", (sid,))
        w.destroy()

    ttk.Button(
        botoes, text="+ Adicionar produto", command=adicionar, style="Primario.TButton"
    ).pack(side="left")
    ttk.Button(
        botoes, text="Excluir item", command=excluir_item, style="Perigo.TButton"
    ).pack(side="left", padx=6)

    ttk.Label(rodape, text="Valor total:", font=("Segoe UI", 10, "bold")).pack(side="left")
    ttk.Label(rodape, textvariable=total_var, font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
    ttk.Button(rodape, text="Fechar", command=fechar, style="Padrao.TButton").pack(side="right")

    w.protocol("WM_DELETE_WINDOW", fechar)
    refresh()
