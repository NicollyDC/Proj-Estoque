import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import html
import tempfile
import webbrowser
from pathlib import Path
from dados.estoque import status_estoque
from ui import design_system as design

ESTILO_RELATORIO_HTML = r"""
@page { size: A4 landscape; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2937; font-size: 11px; background: white; }
.cabecalho { border-bottom: 2px solid #1f4e79; padding-bottom: 12px; margin-bottom: 16px; }
.titulo { font-size: 22px; font-weight: bold; color: #17365d; margin-bottom: 4px; }
.subtitulo { font-size: 13px; color: #6b7280; }
.informacoes, .resumo { display: table; width: 100%; margin-bottom: 18px; }
.info-card { display: table-cell; width: 25%; padding: 8px 12px; border: 1px solid #d1d5db; background: #f8fafc; }
.info-label { display: block; font-size: 9px; color: #6b7280; text-transform: uppercase; margin-bottom: 4px; }
.info-valor { font-size: 12px; font-weight: bold; }
.resumo-card { display: table-cell; width: 33.33%; padding: 10px 14px; border: 1px solid #d1d5db; }
.resumo-card + .resumo-card { border-left: none; }
.resumo-titulo { font-size: 9px; color: #6b7280; text-transform: uppercase; }
.resumo-valor { margin-top: 5px; font-size: 16px; font-weight: bold; }
.secao { font-size: 14px; font-weight: bold; color: #17365d; margin: 18px 0 8px; }
table { width: 100%; border-collapse: collapse; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; page-break-after: auto; }
th { background: #17365d; color: white; padding: 8px; text-align: left; font-size: 10px; }
td { border-bottom: 1px solid #d9dee5; padding: 7px 8px; vertical-align: middle; }
td.numero { text-align: right; white-space: nowrap; }
tr:nth-child(even) { background: #f8fafc; }
tr.sem-movimentacao { color: #6b7280; }
tr.alerta { background: #fff4f4; }
tr.positivo { background: #f5faf6; }
.total { background: #e8eef5 !important; font-weight: bold; border-top: 2px solid #17365d; }
.total td { padding: 9px 8px; }
.rodape { margin-top: 20px; padding-top: 8px; border-top: 1px solid #d1d5db; font-size: 9px; color: #6b7280; }
.detalhes { page-break-before: always; }
@media screen { body { max-width: 1100px; margin: 30px auto; padding: 30px; box-shadow: 0 0 15px rgba(0,0,0,.12); } }
"""


def abrir_html_para_impressao(parent, documento, titulo="Relatório"):
    """Abre um documento HTML temporário para impressão pelo navegador."""
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8"
        ) as arquivo:
            arquivo.write(documento)
            caminho = Path(arquivo.name)
        webbrowser.open_new_tab(caminho.as_uri())
        messagebox.showinfo(
            titulo,
            "O relatório foi aberto no navegador.\n\n"
            "Use Ctrl + P para conferir e imprimir em papel A4.",
            parent=parent,
        )
    except Exception as ex:
        messagebox.showerror(
            "Erro ao abrir relatório",
            "Não foi possível abrir o relatório para impressão. Tente novamente. "
            "Se o problema continuar, contate o suporte.",
            parent=parent,
        )


def abrir_conferencia_relatorio(parent, documento, texto, estabelecimento, titulo):
    """Tela de conferência anterior à impressão, no padrão do relatório de comparação."""
    win = tk.Toplevel(parent)
    win.title(f"Visualização do relatório - {estabelecimento}")
    win.geometry("1050x700")
    win.minsize(800, 500)
    win.transient(parent)

    topo = ttk.Frame(win)
    topo.pack(fill="x", padx=12, pady=10)
    ttk.Label(topo, text=f"📄 Relatório do {estabelecimento}", font=("Segoe UI", 13, "bold")).pack(side="left")
    ttk.Label(topo, text=f"• {titulo}", font=("Segoe UI", 10)).pack(side="left", padx=10)

    area = ttk.Frame(win)
    area.pack(fill="both", expand=True, padx=12, pady=(0, 8))
    barra_y = ttk.Scrollbar(area, orient="vertical")
    barra_x = ttk.Scrollbar(area, orient="horizontal")
    visualizacao = tk.Text(
        area, wrap="none", font=("Consolas", 10),
        yscrollcommand=barra_y.set, xscrollcommand=barra_x.set,
        bg="#ffffff", fg="#1f2937", relief="solid", borderwidth=1,
    )
    barra_y.config(command=visualizacao.yview)
    barra_x.config(command=visualizacao.xview)
    visualizacao.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")
    barra_x.grid(row=1, column=0, sticky="ew")
    area.rowconfigure(0, weight=1)
    area.columnconfigure(0, weight=1)
    visualizacao.insert("1.0", texto)
    visualizacao.config(state="disabled")

    rodape = ttk.Frame(win)
    rodape.pack(fill="x", padx=12, pady=10)
    ttk.Label(rodape, text="A impressão será aberta no navegador.").pack(side="left")
    ttk.Button(
        rodape, text="🖨️ Imprimir", style="Sucesso.TButton",
        command=lambda: abrir_html_para_impressao(parent, documento, titulo),
    ).pack(side="right")
    ttk.Button(rodape, text="Fechar", command=win.destroy).pack(side="right", padx=6)
    return win


def gerar_html_estoque(rows, estabelecimento, cnpj, dinheiro, numero):
    """Monta uma posição de estoque A4 com os dados já consultados pelo chamador."""
    linhas = []
    estados = [status_estoque(row["estoque"], row["minimo"])[0] for row in rows]
    baixos = estados.count("⚠ Estoque baixo")
    zerados = estados.count("✕ Sem estoque")
    valor_total = sum(float(row["estoque"] or 0) * float(row["valor_unitario"] or 0) for row in rows)
    for row, status in zip(rows, estados):
        qtd = float(row["estoque"] or 0)
        linhas.append(
            "<tr>"
            f"<td>{html.escape(str(row['codigo'] or ''))}</td>"
            f"<td>{html.escape(str(row['nome'] or ''))}</td>"
            f"<td>{html.escape(str(row['unidade'] or ''))}</td>"
            f"<td class='numero'>{html.escape(numero(qtd))}</td>"
            f"<td class='numero'>{html.escape(numero(row['minimo']))}</td>"
            f"<td class='numero'>{html.escape(dinheiro(row['valor_unitario']))}</td>"
            f"<td class='numero'>{html.escape(dinheiro(qtd * float(row['valor_unitario'] or 0)))}</td>"
            f"<td>{html.escape(status)}</td></tr>"
        )
    gerado = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas_info = (
        ("Estabelecimento", estabelecimento),
        ("CNPJ", cnpj),
        ("Período", "Posição atual"),
        ("Gerado em", gerado),
    )
    info_html = "".join(
        f"<div class='info-card'><span class='info-label'>{html.escape(chave)}</span><span class='info-valor'>{html.escape(str(valor))}</span></div>"
        for chave, valor in linhas_info
    )
    resumo_html = (
        ("Produtos", str(len(rows))),
        ("Baixo / sem estoque", f"{baixos} / {zerados}"),
        ("Valor total", dinheiro(valor_total)),
    )
    resumo_cards = "".join(
        f"<div class='resumo-card'><div class='resumo-titulo'>{html.escape(chave)}</div><div class='resumo-valor'>{html.escape(valor)}</div></div>"
        for chave, valor in resumo_html
    )
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<title>Relatório de Estoque - {html.escape(estabelecimento)}</title><style>{ESTILO_RELATORIO_HTML}</style></head><body>
<div class="cabecalho"><div class="titulo">RELATÓRIO DE ESTOQUE</div><div class="subtitulo">Controle de Estoque - {html.escape(estabelecimento)}</div></div>
<div class="informacoes">{info_html}</div><div class="resumo">{resumo_cards}</div>
<div class="secao">Posição por produto</div><table><thead><tr><th>Código</th><th>Produto</th><th>Unidade</th><th>Estoque atual</th><th>Estoque mínimo</th><th>Valor unitário</th><th>Valor total</th><th>Status</th></tr></thead>
<tbody>{''.join(linhas) if linhas else '<tr class="sem-movimentacao"><td colspan="8">Nenhum produto cadastrado.</td></tr>'}</tbody></table>
<div class="rodape">Relatório gerado pelo Controle de Estoque - {html.escape(estabelecimento)}.</div></body></html>"""


def texto_previa_estoque(rows, estabelecimento, cnpj, dinheiro, numero):
    estados = [status_estoque(row["estoque"], row["minimo"])[0] for row in rows]
    baixos = estados.count("⚠ Estoque baixo")
    zerados = estados.count("✕ Sem estoque")
    valor_total = sum(float(row["estoque"] or 0) * float(row["valor_unitario"] or 0) for row in rows)
    linhas = [
        "RELATÓRIO DE ESTOQUE",
        f"Controle de Estoque - {estabelecimento}",
        f"CNPJ: {cnpj}",
        f"Período: Posição atual    Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        f"Produtos: {len(rows)}    Estoque baixo: {baixos}    Sem estoque: {zerados}    Valor total: {dinheiro(valor_total)}",
        "",
        f"{'Código':<14}{'Produto':<30}{'Unidade':<10}{'Estoque atual':>15}{'Estoque mínimo':>16}{'Valor unitário':>18}{'Valor total':>16}  Status",
        "-" * 140,
    ]
    for row, status in zip(rows, estados):
        qtd = float(row["estoque"] or 0)
        linhas.append(
            f"{str(row['codigo'] or '')[:13]:<14}{str(row['nome'] or '')[:29]:<30}"
            f"{str(row['unidade'] or '')[:9]:<10}{numero(qtd):>15}{numero(row['minimo']):>16}"
            f"{dinheiro(row['valor_unitario']):>18}{dinheiro(qtd * float(row['valor_unitario'] or 0)):>16}  {status}"
        )
    if not rows:
        linhas.append("Nenhum produto cadastrado.")
    return "\n".join(linhas)


def criar_aba_dashboard(notebook, consultar, estoque_sql, dinheiro, numero):
    """Dashboard com indicadores e produtos reais do banco ativo."""
    aba = ttk.Frame(notebook, padding=18)
    notebook.add(aba, text="⌂  Visão Geral")
    ttk.Label(aba, text="Visão Geral", style="AppTitle.TLabel").pack(anchor="w")
    ttk.Label(aba, text="Confira rapidamente a situação do seu estoque e as movimentações recentes.", style="AppSubtitle.TLabel").pack(anchor="w", pady=(2, 14))

    produtos = consultar(estoque_sql + " ORDER BY p.nome")
    total = len(produtos)
    estados = [status_estoque(p["estoque"], p["minimo"])[0] for p in produtos]
    baixos = estados.count("⚠ Estoque baixo")
    zerados = estados.count("✕ Sem estoque")
    valor = sum(float(p["estoque"] or 0) * float(p["valor_unitario"] or 0) for p in produtos)
    notas = consultar("SELECT COUNT(*) AS total FROM notas")[0]["total"]

    cards = ttk.Frame(aba)
    cards.pack(fill="x", pady=(0, 14))
    for col in range(4):
        cards.columnconfigure(col, weight=1, uniform="metric")
    indicadores = (("📦 Total de Produtos", str(total)), ("⚠ Estoque Baixo", str(baixos)), ("💰 Valor do Estoque", dinheiro(valor)), ("📄 Notas Recebidas", str(notas)))
    for col, (titulo, valor_card) in enumerate(indicadores):
        card = tk.Frame(cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=15, pady=13)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 7, 0 if col == 3 else 7))
        tk.Label(card, text=titulo, bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(card, text=valor_card, bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(7, 0))

    body = ttk.Frame(aba)
    body.pack(fill="both", expand=True)
    left = tk.Frame(body, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    right = tk.Frame(body, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, width=250)
    right.pack(side="right", fill="y", padx=(8, 0))
    right.pack_propagate(False)

    tk.Label(left, text="Status do estoque", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
    table_frame = tk.Frame(left, bg="#FFFFFF")
    table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    cols = ("produto", "codigo", "unidade", "estoque", "minimo", "unitario", "status")
    table = ttk.Treeview(table_frame, columns=cols, show="headings", style="App.Treeview")
    colunas = (("produto", "Produto", 180), ("codigo", "Código", 90), ("unidade", "Unidade", 75), ("estoque", "Estoque", 85), ("minimo", "Mínimo", 75), ("unitario", "Valor Unitário", 105), ("status", "Status", 125))
    for key, title, _width in colunas:
        table.heading(key, text=title)
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    xscrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    table.configure(yscrollcommand=scrollbar.set, xscrollcommand=xscrollbar.set)
    design.configurar_treeview_responsivo(
        table, table_frame, [(key, width) for key, _title, width in colunas],
        scrollbar, xscrollbar,
    )
    table.tag_configure("normal", foreground="#15803D")
    table.tag_configure("baixo", foreground="#A16207")
    table.tag_configure("zerado", foreground="#B91C1C")
    for p in produtos:
        qtd = float(p["estoque"] or 0)
        minimo = float(p["minimo"] or 0)
        status, tag = status_estoque(qtd, p["minimo"])
        table.insert("", "end", values=(p["nome"], p["codigo"], p["unidade"] or "", numero(qtd), numero(minimo), dinheiro(p["valor_unitario"]), status), tags=(tag,))
    if not produtos:
        ttk.Label(left, text="Não há produtos cadastrados neste estabelecimento.", style="AppSubtitle.TLabel").pack(anchor="w", padx=14, pady=10)

    tk.Label(right, text="Situação do estoque", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 10))
    for texto, quantidade, cor in (("🟢 Estoque normal", total - baixos - zerados, "#15803D"), ("🟡 Estoque baixo", baixos, "#A16207"), ("🔴 Sem estoque", zerados, "#B91C1C")):
        linha = tk.Frame(right, bg="#FFFFFF")
        linha.pack(fill="x", padx=14, pady=7)
        tk.Label(linha, text=texto, bg="#FFFFFF", fg=cor, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(linha, text=str(quantidade), bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 10, "bold")).pack(side="right")

    tk.Label(right, text="Atividades recentes", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(20, 8))
    eventos = consultar("SELECT 'Nota recebida' AS atividade, numero AS detalhe, data AS data FROM notas ORDER BY id DESC LIMIT 4")
    saidas = consultar("SELECT 'Saída registrada' AS atividade, COALESCE(tipo, '') AS detalhe, data_hora AS data FROM saidas ORDER BY id DESC LIMIT 4")
    atividades = sorted(list(eventos) + list(saidas), key=lambda item: str(item["data"] or ""), reverse=True)[:5]
    if atividades:
        for item in atividades:
            texto = f"{item['atividade']} · {item['detalhe'] or ''}\n{item['data'] or ''}"
            tk.Label(right, text=texto, bg="#FFFFFF", fg="#475569", justify="left", anchor="w", font=("Segoe UI", 8), wraplength=215).pack(fill="x", padx=14, pady=5)
    else:
        tk.Label(right, text="Não há atividades recentes.", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9), wraplength=210, justify="left").pack(anchor="w", padx=14)
    return aba


def abrir_relatorio_saidas(parent, consultar, dinheiro, numero, estabelecimento="Estabelecimento", cnpj=""):
    """Relatório filtrável das saídas gravadas no banco atualmente aberto."""
    win = tk.Toplevel(parent)
    win.title("Relatório de Saídas")
    win.geometry("1120x640")
    win.minsize(820, 460)
    win.configure(bg="#F5F7FB")
    header = ttk.Frame(win)
    header.pack(fill="x", padx=20, pady=(18, 12))
    header_text = ttk.Frame(header)
    header_text.pack(side="left", fill="x", expand=True)
    ttk.Label(header_text, text="Controle de Saídas", style="AppTitle.TLabel").pack(anchor="w")
    ttk.Label(header_text, text="Filtre as movimentações e confira os resultados antes de imprimir.", style="AppSubtitle.TLabel").pack(anchor="w", pady=(2, 0))

    filters = tk.Frame(win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=10, pady=10)
    filters.pack(fill="x", padx=20, pady=(0, 10))
    fields = {}
    for col, (key, label) in enumerate((("de", "Data inicial (AAAA-MM-DD)"), ("ate", "Data final (AAAA-MM-DD)"), ("produto", "Produto"), ("tipo", "Tipo de saída"), ("responsavel", "Responsável"))):
        cell = tk.Frame(filters, bg="#FFFFFF")
        cell.grid(row=0, column=col, sticky="ew", padx=4)
        filters.columnconfigure(col, weight=1)
        tk.Label(cell, text=label, bg="#FFFFFF", fg="#475569", font=("Segoe UI", 8)).pack(anchor="w")
        entry = ttk.Entry(cell, style="App.TEntry")
        entry.pack(fill="x", pady=(4, 0))
        fields[key] = entry
    fields["tipo"].insert(0, "todos")
    rows_cache = []

    summary = tk.Label(win, text="", bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 10, "bold"), padx=12, pady=11, anchor="w")
    summary.pack(fill="x", padx=20, pady=(0, 10))
    frame = tk.Frame(win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))
    cols = ("data", "hora", "produto", "codigo", "qtd", "un", "tipo", "resp", "unit", "total")
    table = ttk.Treeview(frame, columns=cols, show="headings", style="App.Treeview")
    colunas = (("data", "Data", 90), ("hora", "Horário", 70), ("produto", "Produto", 180), ("codigo", "Código", 80), ("qtd", "Quantidade (unidade-base)", 180), ("un", "Unidade-base", 100), ("tipo", "Tipo de saída", 110), ("resp", "Responsável", 120), ("unit", "Valor unitário (unidade-base)", 190), ("total", "Valor total", 110))
    for key, title, _width in colunas:
        table.heading(key, text=title)
    xbar = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
    ybar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
    design.configurar_treeview_responsivo(
        table, frame, [(key, width) for key, _title, width in colunas],
        ybar, xbar, padx=8, pady=8,
    )

    def atualizar(*_):
        nonlocal rows_cache
        conditions, params = [], []
        start, end = fields["de"].get().strip(), fields["ate"].get().strip()
        if start:
            conditions.append("date(s.data_hora) >= date(?)")
            params.append(start)
        if end:
            conditions.append("date(s.data_hora) <= date(?)")
            params.append(end)
        for key, expr in (("produto", "p.nome"), ("responsavel", "s.responsavel")):
            value = fields[key].get().strip()
            if value:
                conditions.append(f"{expr} LIKE ?")
                params.append(f"%{value}%")
        tipo = fields["tipo"].get().strip()
        if tipo and tipo.casefold() != "todos":
            conditions.append("s.tipo LIKE ?")
            params.append(f"%{tipo}%")
        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = consultar(f"""SELECT s.id AS saida_id, s.data_hora, p.nome AS produto, p.codigo, p.unidade, s.tipo, s.responsavel,
            isd.qtd, isd.valor_unit, COALESCE(isd.subtotal, isd.qtd * isd.valor_unit) AS total
            FROM itens_saida isd JOIN saidas s ON s.id=isd.saida_id
            JOIN produtos p ON p.id=isd.produto_id{where}
            ORDER BY s.data_hora DESC, s.id DESC, p.nome""", tuple(params))
        rows_cache = list(rows)
        table.delete(*table.get_children())
        for row in rows:
            data_hora = str(row["data_hora"] or "")
            data, _, hora = data_hora.partition(" ")
            table.insert("", "end", values=(data, hora, row["produto"], row["codigo"], numero(row["qtd"]), row["unidade"] or "", row["tipo"] or "", row["responsavel"] or "", dinheiro(row["valor_unit"]), dinheiro(row["total"])))
        movimentos = len({row["saida_id"] for row in rows})
        itens = sum(float(row["qtd"] or 0) for row in rows)
        total = sum(float(row["total"] or 0) for row in rows)
        summary.configure(text=f"Saídas: {movimentos}    ·    Quantidade total (unidade-base): {numero(itens)}    ·    Valor total: {dinheiro(total)}")
        if not rows:
            summary.configure(text="Nenhuma movimentação encontrada para os filtros selecionados.")

    def gerar_impressao():
        atualizar()

        def filtro(chave, padrao="Todos"):
            valor = fields[chave].get().strip()
            return valor or padrao

        filtros = (
            ("Data inicial", filtro("de", "Não informada")),
            ("Data final", filtro("ate", "Não informada")),
            ("Produto", filtro("produto")),
            ("Tipo", filtro("tipo")),
            ("Responsável", filtro("responsavel")),
        )
        total_qtd = sum(float(row["qtd"] or 0) for row in rows_cache)
        total_valor = sum(float(row["total"] or 0) for row in rows_cache)
        movimentos = len({row["saida_id"] for row in rows_cache})
        gerado = datetime.now().strftime("%d/%m/%Y %H:%M")

        linhas = []
        linhas_texto = []
        for row in rows_cache:
            data_hora = str(row["data_hora"] or "")
            data, _, hora = data_hora.partition(" ")
            valores = (
                data, hora, str(row["produto"] or ""), numero(row["qtd"]),
                str(row["unidade"] or ""), str(row["tipo"] or ""),
                str(row["responsavel"] or ""), dinheiro(row["valor_unit"]),
                dinheiro(row["total"]),
            )
            linhas.append(
                "<tr>"
                f"<td>{html.escape(data)}</td><td>{html.escape(hora)}</td>"
                f"<td>{html.escape(valores[2])}</td><td class='numero'>{html.escape(valores[3])}</td>"
                f"<td>{html.escape(valores[4])}</td><td>{html.escape(valores[5])}</td>"
                f"<td>{html.escape(valores[6])}</td><td class='numero'>{html.escape(valores[7])}</td>"
                f"<td class='numero'>{html.escape(valores[8])}</td></tr>"
            )
            linhas_texto.append(
                f"{data:<12}{hora:<9}{valores[2][:24]:<25}{valores[3]:>12}"
                f"{valores[4][:8]:<9}{valores[5][:18]:<19}{valores[6][:18]:<19}"
                f"{valores[7]:>14}{valores[8]:>14}"
            )

        info = (
            ("Estabelecimento", f"{estabelecimento}" + (f" · CNPJ {cnpj}" if cnpj else "")),
            ("Período", f"{filtro('de', 'Início não informado')} até {filtro('ate', 'Fim não informado')}"),
            ("Filtros", f"Produto: {filtro('produto')} · Tipo: {filtro('tipo')} · Responsável: {filtro('responsavel')}"),
            ("Gerado em", gerado),
        )
        info_html = "".join(
            f"<div class='info-card'><span class='info-label'>{html.escape(chave)}</span><span class='info-valor'>{html.escape(valor)}</span></div>"
            for chave, valor in info
        )
        resumos = (
            ("Saídas", str(movimentos)),
            ("Quantidade total (unidade-base)", numero(total_qtd)),
            ("Valor total", dinheiro(total_valor)),
        )
        resumo_html = "".join(
            f"<div class='resumo-card'><div class='resumo-titulo'>{html.escape(chave)}</div><div class='resumo-valor'>{html.escape(valor)}</div></div>"
            for chave, valor in resumos
        )
        tabela_total = (
            f"<tr class='total'><td colspan='3'>TOTAL · {movimentos} saídas</td>"
            f"<td class='numero'>{html.escape(numero(total_qtd))}</td><td colspan='4'></td>"
            f"<td class='numero'>{html.escape(dinheiro(total_valor))}</td></tr>"
        )
        documento = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<title>Relatório de Saídas - {html.escape(estabelecimento)}</title><style>{ESTILO_RELATORIO_HTML}</style></head><body>
<div class="cabecalho"><div class="titulo">RELATÓRIO DE SAÍDAS</div><div class="subtitulo">Controle de Estoque - {html.escape(estabelecimento)}</div></div>
<div class="informacoes">{info_html}</div><div class="resumo">{resumo_html}</div>
<div class="secao">Saídas registradas</div><p>As quantidades são registradas na unidade-base de cada produto; embalagens não são convertidas automaticamente.</p><table><thead><tr><th>Data</th><th>Hora</th><th>Produto</th><th>Quantidade (unidade-base)</th><th>Unidade-base</th><th>Tipo de saída</th><th>Responsável</th><th>Valor unitário (unidade-base)</th><th>Valor total</th></tr></thead>
<tbody>{''.join(linhas) if linhas else '<tr class="sem-movimentacao"><td colspan="9">Nenhuma saída encontrada para os filtros utilizados.</td></tr>'}{tabela_total}</tbody></table>
<div class="rodape">Relatório gerado pelo Controle de Estoque - {html.escape(estabelecimento)}.</div></body></html>"""

        texto = [
            "RELATÓRIO DE SAÍDAS",
            f"Controle de Estoque - {estabelecimento}",
            f"CNPJ: {cnpj}" if cnpj else "",
            f"Período: {filtro('de', 'Início não informado')} até {filtro('ate', 'Fim não informado')}",
            f"Filtros: Produto: {filtro('produto')} | Tipo: {filtro('tipo')} | Responsável: {filtro('responsavel')}",
            f"Gerado em: {gerado}",
            "",
            f"Saídas: {movimentos}    Quantidade total (unidade-base): {numero(total_qtd)}    Valor total: {dinheiro(total_valor)}",
            "",
            f"{'Data':<12}{'Hora':<9}{'Produto':<25}{'Quantidade (unidade-base)':>27}{'Unidade-base':<15}{'Tipo':<19}{'Responsável':<19}{'Valor unitário (unidade-base)':>30}{'Valor total':>14}",
            "-" * 170,
            *(linhas_texto or ["Nenhuma saída encontrada para os filtros utilizados."]),
        ]
        abrir_conferencia_relatorio(
            parent, documento, "\n".join(texto), estabelecimento, "Relatório de Saídas"
        )

    def limpar_filtros():
        for entry in fields.values():
            entry.delete(0, tk.END)
        fields["tipo"].insert(0, "todos")
        atualizar()

    ttk.Button(filters, text="Aplicar filtros", command=atualizar, style="Primario.TButton").grid(row=1, column=0, sticky="w", padx=4, pady=(8, 0))
    ttk.Button(filters, text="Limpar filtros", command=limpar_filtros, style="Padrao.TButton").grid(row=1, column=1, sticky="w", padx=4, pady=(8, 0))
    ttk.Button(
        header,
        text="📋 Gerar Relatório de Saídas",
        command=gerar_impressao,
        style="Primario.TButton",
    ).pack(side="right", padx=(12, 0))
    for entry in fields.values():
        entry.bind("<Return>", atualizar)
    atualizar()
