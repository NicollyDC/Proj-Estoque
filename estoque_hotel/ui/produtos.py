import tkinter as tk
import math
import sqlite3
from tkinter import ttk, messagebox

from dados.hotel.database import q, run, execute, commit, rollback
from dados.estoque import status_estoque, calcular_quantidade_estoque, calcular_valor_unitario_estoque, numero_brasileiro
from estoque_hotel.utils import ESTOQUE_SQL, fmt, num, FIN, now
from estoque_hotel.config import CNPJ_ESTABELECIMENTO
from ui.design_system import dinheiro, configurar_treeview_responsivo
from ui.dashboard import abrir_conferencia_relatorio, gerar_html_estoque, texto_previa_estoque
from sessao import sessao

from estoque_hotel.front import (
    tree,
    buttons,
    form,
    sel,
    safe,
)


# ============================================================
# CAMPOS DO FORMULÁRIO
# ============================================================

PROD_F = [
    ("codigo", "Código", "entry", None),
    ("nome", "Nome", "entry", None),
    ("unidade", "Unidade de medida", "entry", None),
    ("minimo", "Estoque mínimo", "entry", None),
    ("finalidade", "Finalidade", "combo_ro", FIN),
    ("ativo", "Ativo", "check", None),
]


pt = None
busca_produto = None
estado_vazio = None


# ============================================================
# ATUALIZAR PRODUTOS
# ============================================================

def prod_refresh():
    """Atualiza a tabela de produtos, respeitando a pesquisa."""

    global pt, busca_produto

    pt.delete(
        *pt.get_children()
    )

    termo = ""

    if busca_produto is not None:
        termo = busca_produto.get().strip().lower()

    for r in q(
        ESTOQUE_SQL + " ORDER BY p.nome"
    ):

        texto = (
            f"{r['codigo']} "
            f"{r['nome']}"
        ).lower()

        if termo and termo not in texto:
            continue

        status, _ = status_estoque(r["estoque"], r["minimo"])

        pt.insert(
            "",
            "end",
            iid=str(r["id"]),
            values=(
                r["codigo"],
                r["nome"],
                r["unidade"],
                fmt(round(r["estoque"], 4)),
                fmt(r["minimo"]),
                dinheiro(r["valor_unitario"]),
                "Sim" if r["ativo"] else "Não",
                status,
            ),
        )

    if estado_vazio is not None:
        if pt.get_children():
            estado_vazio.place_forget()
        else:
            estado_vazio.place(relx=0.5, rely=0.5, anchor="center")


# ============================================================
# CRIAR / EDITAR PRODUTO
# ============================================================

def montar_secao_estoque_inicial(area, linha):
    """Exibe os campos opcionais e a prévia do estoque físico inicial."""
    grupo = ttk.LabelFrame(area, text="Estoque inicial")
    grupo.grid(row=linha, column=0, columnspan=2, sticky="ew", pady=(12, 2))
    grupo.columnconfigure(1, weight=1)

    quantidade_var = tk.StringVar(value="0")
    fator_var = tk.StringVar(value="1")
    valor_unitario_var = tk.StringVar(value=dinheiro(0))
    quantidade_estoque_var = tk.StringVar(value="0")
    custo_estoque_var = tk.StringVar(value=dinheiro(0))
    valor_total_var = tk.StringVar(value=dinheiro(0))

    ttk.Label(grupo, text="Quantidade inicial:").grid(row=0, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Entry(grupo, textvariable=quantidade_var, style="App.TEntry").grid(row=0, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(grupo, text="Fator de conversão:").grid(row=1, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Entry(grupo, textvariable=fator_var, style="App.TEntry").grid(row=1, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(grupo, text="Quantidade em estoque:").grid(row=2, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Label(grupo, textvariable=quantidade_estoque_var).grid(row=2, column=1, sticky="w", padx=8, pady=5)
    ttk.Label(grupo, text="Valor unitário da quantidade informada:").grid(row=3, column=0, sticky="w", padx=(10, 16), pady=5)
    valor_unitario_entry = ttk.Entry(grupo, textvariable=valor_unitario_var, style="App.TEntry")
    valor_unitario_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(grupo, text="Valor unitário (unidade-base):").grid(row=4, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Label(grupo, textvariable=custo_estoque_var).grid(row=4, column=1, sticky="w", padx=8, pady=5)
    ttk.Label(grupo, text="Valor total inicial:").grid(row=5, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Label(grupo, textvariable=valor_total_var).grid(row=5, column=1, sticky="w", padx=8, pady=5)
    ttk.Label(
        grupo,
        text="Informe o custo por unidade da quantidade informada. O custo equivalente é convertido para a unidade de estoque.",
        style="AppSubtitle.TLabel",
    ).grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(2, 7))

    def atualizar_previa(*_):
        try:
            quantidade = numero_brasileiro(quantidade_var.get(), 0)
            fator = numero_brasileiro(fator_var.get(), 1)
            valor_unitario = numero_brasileiro(valor_unitario_var.get(), 0)
            if (
                not all(math.isfinite(n) for n in (quantidade, fator, valor_unitario))
                or quantidade < 0 or fator <= 0 or valor_unitario < 0
            ):
                raise ValueError
            quantidade_estoque = calcular_quantidade_estoque(quantidade, fator)
            valor_estoque = calcular_valor_unitario_estoque(quantidade * valor_unitario, quantidade_estoque)
            valor_total = quantidade * valor_unitario
            if not math.isfinite(valor_total):
                raise ValueError
            quantidade_estoque_var.set(fmt(quantidade_estoque))
            custo_estoque_var.set(dinheiro(valor_estoque))
            valor_total_var.set(dinheiro(valor_total))
        except (TypeError, ValueError):
            quantidade_estoque_var.set("—")
            custo_estoque_var.set("—")
            valor_total_var.set("—")

    for variavel in (quantidade_var, fator_var, valor_unitario_var):
        variavel.trace_add("write", atualizar_previa)

    def preparar_edicao_valor(_event=None):
        try:
            valor = numero_brasileiro(valor_unitario_var.get(), 0)
            valor_unitario_var.set(f"{valor:.2f}".replace(".", ","))
        except (TypeError, ValueError):
            pass

    def formatar_valor(_event=None):
        try:
            valor = numero_brasileiro(valor_unitario_var.get(), 0)
            if math.isfinite(valor) and valor >= 0:
                valor_unitario_var.set(dinheiro(valor))
        except (TypeError, ValueError):
            pass

    valor_unitario_entry.bind("<FocusIn>", preparar_edicao_valor)
    valor_unitario_entry.bind("<FocusOut>", formatar_valor)
    atualizar_previa()
    return {
        "quantidade": quantidade_var,
        "fator": fator_var,
        "valor_unitario": valor_unitario_var,
        "quantidade_estoque": quantidade_estoque_var,
        "custo_estoque": custo_estoque_var,
        "valor_total": valor_total_var,
    }


def ler_estoque_inicial(campos, parent):
    try:
        quantidade = numero_brasileiro(campos["quantidade"].get(), 0)
        fator = numero_brasileiro(campos["fator"].get(), 1)
        valor_unitario = numero_brasileiro(campos["valor_unitario"].get(), 0)
    except (TypeError, ValueError):
        messagebox.showwarning("Estoque inicial", "Confira a quantidade, o fator e o valor unitário informados.", parent=parent)
        return None
    if not all(math.isfinite(n) for n in (quantidade, fator, valor_unitario)):
        messagebox.showwarning("Estoque inicial", "Informe valores numéricos válidos.", parent=parent)
        return None
    if quantidade < 0 or fator <= 0 or valor_unitario < 0:
        messagebox.showwarning(
            "Estoque inicial", "A quantidade e o valor devem ser iguais ou maiores que zero; o fator deve ser maior que zero.", parent=parent
        )
        return None
    quantidade_estoque = calcular_quantidade_estoque(quantidade, fator)
    valor_total = quantidade * valor_unitario
    if not math.isfinite(quantidade_estoque) or not math.isfinite(valor_total):
        messagebox.showwarning("Estoque inicial", "A quantidade convertida está fora do limite permitido.", parent=parent)
        return None
    valor_unitario_estoque = calcular_valor_unitario_estoque(valor_total, quantidade_estoque)
    return quantidade, fator, quantidade_estoque, valor_unitario_estoque, valor_unitario

def montar_secao_ajuste(area, linha, root, pid):
    atual_row = q(ESTOQUE_SQL + " WHERE p.id=?", (pid,))[0]
    estoque_inicial = float(atual_row["estoque"] or 0)
    saldo_referencia = [estoque_inicial]
    movimentado = q("""SELECT EXISTS(SELECT 1 FROM itens WHERE produto_id=? AND COALESCE(qtd_estoque,0)<>0)
        OR EXISTS(SELECT 1 FROM itens_saida WHERE produto_id=? AND COALESCE(qtd,0)<>0)
        OR EXISTS(SELECT 1 FROM ajustes_estoque WHERE produto_id=?) AS existe""", (pid, pid, pid))[0]["existe"]
    motivo_inicial = estoque_inicial <= 0 and not movimentado
    estoque_var = tk.StringVar(value=fmt(estoque_inicial))
    novo_var = tk.StringVar()
    motivo_var = tk.StringVar(value="Estoque inicial" if motivo_inicial else "Inventário")
    observacao_var = tk.StringVar()
    custo_var = tk.StringVar()

    grupo = ttk.LabelFrame(area, text="Ajuste de estoque")
    grupo.grid(row=linha, column=0, columnspan=2, sticky="ew", pady=(12, 2))
    grupo.columnconfigure(1, weight=1)

    ttk.Label(grupo, text="Estoque atual:").grid(row=0, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Label(grupo, textvariable=estoque_var, style="Section.TLabel").grid(row=0, column=1, sticky="w", padx=8, pady=5)
    ttk.Label(grupo, text="Definir estoque atual:").grid(row=1, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Entry(grupo, textvariable=novo_var, style="App.TEntry").grid(row=1, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(grupo, text="Motivo:").grid(row=2, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Combobox(
        grupo, textvariable=motivo_var,
        values=("Estoque inicial", "Inventário", "Correção de contagem", "Ajuste de estoque"),
        state="readonly", style="App.TCombobox"
    ).grid(row=2, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(grupo, text="Observação:").grid(row=3, column=0, sticky="w", padx=(10, 16), pady=5)
    ttk.Entry(grupo, textvariable=observacao_var, style="App.TEntry").grid(row=3, column=1, sticky="ew", padx=8, pady=5)

    custo_label = ttk.Label(grupo, text="Valor unitário (opcional):")
    custo_label.grid(row=4, column=0, sticky="w", padx=(10, 16), pady=5)
    custo_entry = ttk.Entry(grupo, textvariable=custo_var, style="App.TEntry")
    custo_entry.grid(row=4, column=1, sticky="ew", padx=8, pady=5)
    custo_info = ttk.Label(grupo, style="AppSubtitle.TLabel")
    if estoque_inicial > 0:
        custo_label.grid_remove()
        custo_entry.grid_remove()
        custo_info.configure(text=f"O ajuste usará o valor unitário atual ({dinheiro(atual_row['valor_unitario'])}).")
        custo_info.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    else:
        custo_info.configure(text="Informe somente se souber o valor unitário; sem essa informação, o ajuste não altera o valor total do estoque.")
        custo_info.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))

    status_var = tk.StringVar()
    ttk.Label(grupo, textvariable=status_var, style="AppSubtitle.TLabel").grid(
        row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(3, 0)
    )

    def aplicar_ajuste():
        if not sessao.esta_logado():
            messagebox.showwarning(
                "Ajuste de estoque", "Entre novamente no sistema para registrar o responsável pelo ajuste.", parent=root
            )
            return

        try:
            novo_estoque = float(novo_var.get().strip().replace(",", "."))
        except (TypeError, ValueError):
            messagebox.showwarning("Ajuste de estoque", "Informe um novo estoque usando apenas números.", parent=root)
            return
        if not math.isfinite(novo_estoque) or novo_estoque < 0:
            messagebox.showwarning("Ajuste de estoque", "O estoque informado deve ser um número igual ou maior que zero.", parent=root)
            return
        motivo = motivo_var.get().strip()
        if not motivo:
            messagebox.showwarning("Ajuste de estoque", "Selecione o motivo do ajuste.", parent=root)
            return

        diferenca = novo_estoque - saldo_referencia[0]
        if abs(diferenca) < 0.0000001:
            messagebox.showinfo("Ajuste de estoque", "O novo estoque é igual ao estoque atual. Nenhuma alteração foi feita.", parent=root)
            return

        sinal = "+" if diferenca > 0 else ""
        confirmacao = (
            f"Estoque atual: {fmt(saldo_referencia[0])}\n"
            f"Novo estoque: {fmt(novo_estoque)}\n"
            f"Ajuste: {sinal}{fmt(diferenca)}\n"
            f"Motivo: {motivo}\n\nDeseja aplicar este ajuste?"
        )
        if not messagebox.askyesno("Confirmar ajuste de estoque", confirmacao, parent=root):
            return

        atualizado = q(ESTOQUE_SQL + " WHERE p.id=?", (pid,))
        if not atualizado:
            messagebox.showerror("Ajuste de estoque", "Este produto não está mais disponível.", parent=root)
            return
        saldo_atual = float(atualizado[0]["estoque"] or 0)
        if abs(saldo_atual - saldo_referencia[0]) >= 0.0000001:
            estoque_var.set(fmt(saldo_atual))
            saldo_referencia[0] = saldo_atual
            messagebox.showwarning(
                "Estoque atualizado", "O saldo mudou enquanto você conferia. Confira o estoque atual e informe novamente o saldo desejado.", parent=root
            )
            return

        if saldo_atual > 0:
            valor_unitario = max(0.0, float(atualizado[0]["valor_unitario"] or 0))
        else:
            try:
                valor_unitario = float(custo_var.get().strip().replace(",", ".") or 0)
            except (TypeError, ValueError):
                messagebox.showwarning("Ajuste de estoque", "Confira o valor unitário inicial informado.", parent=root)
                return
            if not math.isfinite(valor_unitario) or valor_unitario < 0:
                messagebox.showwarning("Ajuste de estoque", "O valor unitário deve ser um número igual ou maior que zero.", parent=root)
                return

        try:
            run(
                """INSERT INTO ajustes_estoque
                   (produto_id, estoque_anterior, estoque_novo, diferenca,
                    valor_unit, data_hora, responsavel, motivo, observacao)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (pid, saldo_atual, novo_estoque, diferenca, valor_unitario,
                 now(), sessao.nome or sessao.usuario, motivo, observacao_var.get().strip() or None)
            )
        except sqlite3.Error:
            rollback()
            messagebox.showerror(
                "Ajuste não registrado", "Não foi possível salvar o ajuste. Nenhuma alteração de estoque foi registrada.", parent=root
            )
            return
        estoque_var.set(fmt(novo_estoque))
        novo_var.set("")
        saldo_referencia[0] = novo_estoque
        motivo_var.set("Inventário")
        observacao_var.set("")
        if novo_estoque > 0:
            custo_label.grid_remove()
            custo_entry.grid_remove()
            custo_info.configure(text=f"Os próximos ajustes usarão o valor unitário atual ({dinheiro(valor_unitario)}).")
            custo_info.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        else:
            custo_label.grid(row=4, column=0, sticky="w", padx=(10, 16), pady=5)
            custo_entry.grid(row=4, column=1, sticky="ew", padx=8, pady=5)
            custo_info.configure(text="Informe somente se souber o valor unitário; sem essa informação, o ajuste não altera o valor total do estoque.")
            custo_info.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        status_var.set("Ajuste registrado com sucesso.")
        prod_refresh()
        if pt.exists(str(pid)):
            pt.selection_set(str(pid))
            pt.focus(str(pid))
        messagebox.showinfo("Ajuste de estoque", f"Ajuste registrado. Estoque atual: {fmt(novo_estoque)}.", parent=root)

    ttk.Button(grupo, text="Aplicar ajuste", command=aplicar_ajuste, style="Primario.TButton").grid(
        row=7, column=1, sticky="e", padx=8, pady=(8, 10)
    )

@safe
def prod_edit(root, new=False):
    """Cria ou edita um produto."""

    pid = None if new else sel(pt)

    if not new and not pid:
        return

    atual = (
        dict(
            q(
                "SELECT * FROM produtos WHERE id=?",
                (pid,)
            )[0]
        )
        if pid
        else {
            "ativo": 1,
            "finalidade": "uso e consumo"
        }
    )

    campos_estoque_inicial = {}
    if new:
        conteudo_extra = lambda area, linha: campos_estoque_inicial.update(
            montar_secao_estoque_inicial(area, linha)
        )
    elif pid:
        conteudo_extra = lambda area, linha: montar_secao_ajuste(area, linha, root, int(pid))
    else:
        conteudo_extra = None

    r = form(
        root,
        "Produto",
        PROD_F,
        atual,
        extra_content=conteudo_extra,
    )

    if (
        not r
        or not r["codigo"].strip()
        or not r["nome"].strip()
    ):
        return

    dados_estoque_inicial = (
        ler_estoque_inicial(campos_estoque_inicial, root) if new else (0, 1, 0, 0, 0)
    )
    if dados_estoque_inicial is None:
        return
    quantidade_informada, fator_inicial, quantidade_estoque_inicial, valor_unitario_inicial, custo_informado = dados_estoque_inicial

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
            """
            UPDATE produtos
            SET codigo=?,
                nome=?,
                unidade=?,
                minimo=?,
                finalidade=?,
                ativo=?
            WHERE id=?
            """,
            valores + (pid,)
        )

    else:
        try:
            cursor = execute(
                """
                INSERT INTO produtos
                (codigo, nome, unidade, minimo, finalidade, ativo)
                VALUES (?,?,?,?,?,?)
                """,
                valores,
            )
            novo_pid = cursor.lastrowid
            if quantidade_estoque_inicial > 0:
                observacao = (
                    "Saldo informado manualmente durante o cadastro do produto. "
                    f"Quantidade informada: {fmt(quantidade_informada)}; "
                    f"fator de conversão: {fmt(fator_inicial)}; "
                    f"custo por unidade informada: {dinheiro(custo_informado)}."
                )
                execute(
                    """INSERT INTO ajustes_estoque
                       (produto_id, estoque_anterior, estoque_novo, diferenca,
                        valor_unit, data_hora, responsavel, motivo, observacao)
                       VALUES (?, 0, ?, ?, ?, ?, ?, 'Estoque inicial', ?)""",
                    (
                        novo_pid,
                        quantidade_estoque_inicial,
                        quantidade_estoque_inicial,
                        valor_unitario_inicial,
                        now(),
                        sessao.nome or sessao.usuario or "Cadastro de produto",
                        observacao,
                    ),
                )
            commit()
        except Exception:
            rollback()
            raise

    prod_refresh()


# ============================================================
# EXCLUIR / INATIVAR PRODUTO
# ============================================================

@safe
def prod_del():

    pid = sel(pt)

    if not pid:
        return

    # --------------------------------------------------------
    # PROCURA NOTA VINCULADA
    # --------------------------------------------------------

    nota = q(
        """
        SELECT
            n.numero,
            n.fornecedor
        FROM itens i
        JOIN notas n
            ON n.id = i.nota_id
        WHERE i.produto_id = ?
        LIMIT 1
        """,
        (pid,)
    )

    # --------------------------------------------------------
    # PROCURA SAÍDA VINCULADA
    # --------------------------------------------------------

    saida = q(
        """
        SELECT
            s.data_hora
        FROM itens_saida isd
        JOIN saidas s
            ON s.id = isd.saida_id
        WHERE isd.produto_id = ?
        LIMIT 1
        """,
        (pid,)
    )

    ajuste = q(
        "SELECT data_hora, motivo FROM ajustes_estoque WHERE produto_id=? LIMIT 1",
        (pid,)
    )

    # --------------------------------------------------------
    # PRODUTO COM MOVIMENTAÇÃO
    # --------------------------------------------------------

    if nota or saida or ajuste:

        if nota:

            msg = (
                f"Este produto está vinculado à NF nº "
                f"{nota[0]['numero']}\n"
                f"Fornecedor: {nota[0]['fornecedor']}\n\n"
                "Ele não pode ser excluído para preservar "
                "o histórico.\n"
                "Deseja apenas inativá-lo?"
            )

        elif saida:

            msg = (
                "Este produto possui uma saída registrada "
                f"em {saida[0]['data_hora']}.\n\n"
                "Ele não pode ser excluído.\n"
                "Deseja apenas inativá-lo?"
            )
        else:
            msg = (
                f"Este produto possui um ajuste de estoque registrado em {ajuste[0]['data_hora']} "
                f"({ajuste[0]['motivo']}).\n\n"
                "Ele não pode ser excluído para preservar o histórico.\n"
                "Deseja apenas inativá-lo?"
            )

        if messagebox.askyesno(
            "Produto em uso",
            msg
        ):

            run(
                "UPDATE produtos SET ativo = 0 WHERE id = ?",
                (pid,)
            )

            prod_refresh()

        return

    # --------------------------------------------------------
    # PRODUTO SEM MOVIMENTAÇÕES
    # --------------------------------------------------------

    if messagebox.askyesno(
        "Excluir produto",
        "Deseja excluir este produto permanentemente?"
    ):

        run(
            "DELETE FROM produtos WHERE id = ?",
            (pid,)
        )

        prod_refresh()


# ============================================================
# ABA DE PRODUTOS
# ============================================================

def criar_aba_produtos(notebook, root):
    """Cria a aba Produtos dentro do Notebook."""

    global pt, busca_produto, estado_vazio

    aba = ttk.Frame(notebook)

    notebook.add(
        aba,
        text="▦  Produtos"
    )

    cabecalho = ttk.Frame(aba)
    cabecalho.pack(fill="x", padx=18, pady=(14, 4))
    texto = ttk.Frame(cabecalho)
    texto.pack(side="left", fill="x", expand=True)
    ttk.Label(texto, text="Produtos e estoque", style="AppTitle.TLabel").pack(anchor="w")
    ttk.Label(texto, text="Consulte, cadastre e atualize os produtos deste estabelecimento.", style="AppSubtitle.TLabel").pack(anchor="w", pady=(2, 0))

    # ========================================================
    # PESQUISA
    # ========================================================

    busca_frame = ttk.Frame(aba)

    busca_frame.pack(fill="x", padx=18, pady=(8, 0))

    ttk.Label(
    busca_frame,
    text="⌕  Buscar produto:",
    style="App.TLabel"
    ).pack(
        side="left",
        padx=(0, 6)
    )

    busca_produto = tk.StringVar()

    busca_entry = ttk.Entry(
        busca_frame,
        textvariable=busca_produto,
        width=40,
        style="App.TEntry"
    )

    busca_entry.pack(
        side="left", fill="x", expand=True
    )

    ttk.Button(
        busca_frame,
        text="Limpar",
        command=lambda: busca_produto.set(""),
        style="Padrao.TButton"
    ).pack(
        side="left",
        padx=6
    )

    ttk.Button(
        busca_frame,
        text="📊 Gerar Relatório de Estoque",
        command=lambda: imprimir_relatorio_estoque(root),
        style="Padrao.TButton"
    ).pack(side="left", padx=(4, 8))

    ttk.Button(
        busca_frame,
        text="+ Novo produto",
        command=lambda: prod_edit(root, True),
        style="Primario.TButton"
    ).pack(side="left")

    # ========================================================
    # TABELA
    # ========================================================

    pt = tree(
        aba,
        [
            ("cod", "Código", 100),
            ("nome", "Produto", 230),
            ("un", "Unidade", 70),
            ("est", "Estoque", 90),
            ("min", "Mínimo", 80),
            ("valor", "Valor Unitário", 125),
            ("ativo", "Ativo", 60),
            ("status", "Status", 140),
        ],
    )

    estado_vazio = ttk.Frame(pt.master, padding=18)
    ttk.Label(estado_vazio, text="Nenhum produto encontrado", style="AppTitle.TLabel").pack(pady=(0, 4))
    ttk.Label(estado_vazio, text="Cadastre um produto ou ajuste a busca para ver resultados.", style="AppSubtitle.TLabel").pack(pady=(0, 12))
    ttk.Button(estado_vazio, text="Cadastrar primeiro produto", command=lambda: prod_edit(root, True), style="Primario.TButton").pack()

    pt.tag_configure("low", foreground="#A16207")

    # ========================================================
    # BOTÕES
    # ========================================================

    buttons(
        aba,
        [
            (
                "Editar produto",
                lambda: prod_edit(root)
            ),
            (
                "Excluir produto",
                prod_del
            ),
            (
                "↻ Atualizar",
                prod_refresh
            ),
        ],
    )

    # ========================================================
    # DUPLO CLIQUE
    # ========================================================

    pt.bind(
        "<Double-1>",
        lambda e: prod_edit(root)
    )

    # ========================================================
    # PESQUISA AUTOMÁTICA
    # ========================================================

    busca_produto.trace_add(
        "write",
        lambda *_: prod_refresh()
    )

    # ========================================================
    # CARGA INICIAL
    # ========================================================

    prod_refresh()

    return aba


def imprimir_relatorio_estoque(root):
    rows = [dict(r) for r in q(ESTOQUE_SQL + " ORDER BY p.nome")]
    documento = gerar_html_estoque(
        rows, "Hotel", CNPJ_ESTABELECIMENTO, dinheiro, fmt
    )
    previa = texto_previa_estoque(
        rows, "Hotel", CNPJ_ESTABELECIMENTO, dinheiro, fmt
    )
    abrir_conferencia_relatorio(
        root, documento, previa, "Hotel", "Relatório de Estoque"
    )


def abrir_relatorio_estoque(root):
    """Exibe o relatório usando exclusivamente o banco deste estabelecimento."""
    rows = [dict(r) for r in q(ESTOQUE_SQL + " ORDER BY p.nome")]
    win = tk.Toplevel(root)
    win.title("Relatório de Estoque")
    win.geometry("1000x560")
    win.minsize(760, 420)
    win.configure(bg="#F5F7FB")
    topo = tk.Frame(win, bg="#F5F7FB")
    topo.pack(fill="x", padx=20, pady=(18, 8))
    ttk.Label(topo, text="Relatório de Estoque", style="AppTitle.TLabel").pack(anchor="w")
    ttk.Label(topo, text="Posição atual dos produtos deste estabelecimento.", style="AppSubtitle.TLabel").pack(anchor="w", pady=(2, 0))
    estados = [status_estoque(r["estoque"], r["minimo"])[0] for r in rows]
    baixos = estados.count("⚠ Estoque baixo")
    zerados = estados.count("✕ Sem estoque")
    valor = sum(float(r["estoque"] or 0) * float(r["valor_unitario"] or 0) for r in rows)
    tk.Label(win, text=f"Produtos: {len(rows)}    ·    Estoque baixo: {baixos}    ·    Sem estoque: {zerados}    ·    Valor total: {dinheiro(valor)}", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 10, "bold"), padx=12, pady=12, anchor="w").pack(fill="x", padx=20, pady=(0, 10))
    frame = tk.Frame(win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))
    cols = ("codigo", "produto", "unidade", "qtd", "min", "unit", "total", "status")
    tabela = ttk.Treeview(frame, columns=cols, show="headings", style="App.Treeview")
    colunas = (("codigo", "Código", 85), ("produto", "Produto", 210), ("unidade", "Unidade", 75), ("qtd", "Estoque", 80), ("min", "Mínimo", 75), ("unit", "Valor Unitário", 115), ("total", "Valor Total", 115), ("status", "Status", 130))
    for key, title, _width in colunas:
        tabela.heading(key, text=title)
    barra = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    barra_horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tabela.xview)
    tabela.configure(yscrollcommand=barra.set, xscrollcommand=barra_horizontal.set)
    configurar_treeview_responsivo(
        tabela, frame, [(key, width) for key, _title, width in colunas],
        barra, barra_horizontal, padx=8, pady=8,
    )
    for r in rows:
        qtd, minimo = float(r["estoque"] or 0), float(r["minimo"] or 0)
        status, _ = status_estoque(qtd, minimo)
        tabela.insert("", "end", values=(r["codigo"], r["nome"], r["unidade"] or "", fmt(round(qtd, 4)), fmt(minimo), dinheiro(r["valor_unitario"]), dinheiro(qtd * float(r["valor_unitario"] or 0)), status))
    if not rows:
        ttk.Label(frame, text="Não há dados suficientes para exibir este relatório.", style="AppSubtitle.TLabel").place(relx=0.5, rely=0.5, anchor="center")
