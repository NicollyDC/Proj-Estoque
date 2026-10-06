"""
Estilos e componentes visuais (tkinter / ttk) - versão Restaurante.

Arquivo independente: não depende do módulo de UI do Hotel.
"""

import functools
import sqlite3
import traceback
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# PALETA
# ============================================================

FUNDO = "#F6F8FB"
BRANCO = "#FFFFFF"

TEXTO = "#263238"
TEXTO_SECUNDARIO = "#6B7280"

AZUL = "#7AA7E8"
AZUL_HOVER = "#6695DD"
AZUL_CLARO = "#EAF2FF"

VERDE = "#8BC9A3"
VERDE_HOVER = "#72B98D"
VERDE_CLARO = "#EAF7EF"

VERMELHO = "#E59A9A"
VERMELHO_HOVER = "#D77F7F"
VERMELHO_CLARO = "#FFF0F0"

AMARELO = "#E8C878"
AMARELO_HOVER = "#D9B65C"
AMARELO_CLARO = "#FFF8E5"

LILAS = "#B5A7E8"
LILAS_HOVER = "#A496DB"
LILAS_CLARO = "#F1EEFF"

CINZA = "#AAB4C0"
CINZA_HOVER = "#929EAB"

BORDA = "#E2E8F0"
LINHA = "#F3F5F8"

FONTE = "Segoe UI"


# ============================================================
# BOTÃO ARREDONDADO
# ============================================================

def _desenhar_fundo_arredondado(canvas, largura, altura, cor, raio=10):
    """Desenha o retângulo de cantos arredondados (polígono + 4 círculos)."""

    pontos = [
        raio, 0,
        largura - raio, 0,
        largura, raio,
        largura, altura - raio,
        largura - raio, altura,
        raio, altura,
        0, altura - raio,
        0, raio
    ]

    canvas.create_polygon(pontos, fill=cor, outline=cor, tags="botao")

    diametro = raio * 2
    cantos = (
        (0, 0),                                  # superior esquerdo
        (largura - diametro, 0),                 # superior direito
        (0, altura - diametro),                  # inferior esquerdo
        (largura - diametro, altura - diametro)  # inferior direito
    )

    for x, y in cantos:
        canvas.create_oval(
            x, y, x + diametro, y + diametro,
            fill=cor, outline=cor, tags="botao"
        )


def criar_botao_arredondado(
    parent,
    texto,
    comando,
    largura=150,
    altura=38,
    cor=AZUL,
    cor_hover=AZUL_HOVER
):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=parent.cget("bg"),
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    canvas.pack()

    _desenhar_fundo_arredondado(canvas, largura, altura, cor)

    canvas.create_text(
        largura // 2,
        altura // 2,
        text=texto,
        fill=BRANCO,
        font=(FONTE, 10, "bold")
    )

    canvas.bind(
        "<Enter>",
        lambda e: canvas.itemconfig("botao", fill=cor_hover, outline=cor_hover)
    )
    canvas.bind(
        "<Leave>",
        lambda e: canvas.itemconfig("botao", fill=cor, outline=cor)
    )
    canvas.bind("<Button-1>", lambda e: comando())

    return canvas


# ============================================================
# ESTILOS (ttk)
# ============================================================

# nome do estilo -> (cor normal, cor hover)
_BOTOES_COLORIDOS = {
    "Primario.TButton": (AZUL, AZUL_HOVER),
    "Sucesso.TButton": (VERDE, VERDE_HOVER),
    "Atencao.TButton": (AMARELO, AMARELO_HOVER),
    "Perigo.TButton": (VERMELHO, VERMELHO_HOVER),
}


def _estilo_campo(style, nome, padding):
    """Estilo comum de Entry / Combobox."""

    style.configure(
        nome,
        fieldbackground=BRANCO,
        foreground=TEXTO,
        bordercolor=BORDA,
        lightcolor=BORDA,
        darkcolor=BORDA,
        padding=padding
    )


def configurar():

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # --------------------------------------------------------
    # FRAME / LABELS
    # --------------------------------------------------------

    style.configure("App.TFrame", background=FUNDO)

    style.configure(
        "App.TLabel",
        background=FUNDO,
        foreground=TEXTO,
        font=(FONTE, 10)
    )

    style.configure(
        "AppTitle.TLabel",
        background=FUNDO,
        foreground=TEXTO,
        font=(FONTE, 18, "bold")
    )

    style.configure(
        "AppSubtitle.TLabel",
        background=FUNDO,
        foreground=TEXTO_SECUNDARIO,
        font=(FONTE, 9)
    )

    # --------------------------------------------------------
    # LABEL FRAME
    # --------------------------------------------------------

    style.configure(
        "App.TLabelframe",
        background=BRANCO,
        foreground=TEXTO,
        bordercolor=BORDA,
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "App.TLabelframe.Label",
        background=BRANCO,
        foreground=TEXTO,
        font=(FONTE, 10, "bold")
    )

    # --------------------------------------------------------
    # ENTRY / COMBOBOX
    # --------------------------------------------------------

    _estilo_campo(style, "App.TEntry", padding=6)
    _estilo_campo(style, "App.TCombobox", padding=5)
    style.configure("App.TCombobox", background=BRANCO)

    # --------------------------------------------------------
    # BOTÕES COLORIDOS
    # --------------------------------------------------------

    for nome, (cor, hover) in _BOTOES_COLORIDOS.items():

        style.configure(
            nome,
            background=cor,
            foreground=BRANCO,
            borderwidth=0,
            padding=(12, 7),
            font=(FONTE, 9, "bold")
        )

        style.map(
            nome,
            background=[("active", hover), ("pressed", hover)],
            foreground=[("active", BRANCO), ("pressed", BRANCO)]
        )

    # --------------------------------------------------------
    # BOTÃO PADRÃO (branco com borda)
    # --------------------------------------------------------

    style.configure(
        "Padrao.TButton",
        background=BRANCO,
        foreground=TEXTO,
        borderwidth=1,
        relief="solid",
        padding=(12, 7),
        font=(FONTE, 9, "bold")
    )

    style.map(
        "Padrao.TButton",
        background=[("active", "#F3F5F8"), ("pressed", "#E9EDF2")],
        foreground=[("active", TEXTO), ("pressed", TEXTO)]
    )

    # --------------------------------------------------------
    # CHECKBUTTON
    # --------------------------------------------------------

    style.configure(
        "App.TCheckbutton",
        background=BRANCO,
        foreground=TEXTO,
        font=(FONTE, 9)
    )

    # --------------------------------------------------------
    # TREEVIEW
    # --------------------------------------------------------

    style.configure(
        "App.Treeview",
        background=BRANCO,
        foreground=TEXTO,
        fieldbackground=BRANCO,
        rowheight=30,
        font=(FONTE, 10),
        borderwidth=0
    )

    style.configure(
        "App.Treeview.Heading",
        background="#F8FAFC",
        foreground=TEXTO,
        font=(FONTE, 10, "bold"),
        relief="flat",
        padding=(8, 8)
    )

    style.map(
        "App.Treeview",
        background=[("selected", AZUL_CLARO)],
        foreground=[("selected", TEXTO)]
    )

    # --------------------------------------------------------
    # SCROLLBAR
    # --------------------------------------------------------

    style.configure(
        "App.Vertical.TScrollbar",
        background="#DDE5EF",
        troughcolor=FUNDO,
        borderwidth=0,
        arrowsize=12
    )


def configurar_notebook_restaurante():

    style = ttk.Style()

    style.configure(
        "Restaurante.TNotebook",
        background=FUNDO,
        borderwidth=0
    )

    style.configure(
        "Restaurante.TNotebook.Tab",
        background=AZUL_CLARO,
        foreground=TEXTO_SECUNDARIO,
        padding=(20, 10),
        font=(FONTE, 10, "bold"),
        borderwidth=0
    )

    style.map(
        "Restaurante.TNotebook.Tab",
        background=[("selected", BRANCO), ("active", "#DDEAFF")],
        foreground=[("selected", AZUL), ("active", TEXTO)]
    )


# ============================================================
# COMPONENTES VISUAIS
# ============================================================

def painel(parent, **kwargs):

    kwargs.setdefault("bg", BRANCO)
    kwargs.setdefault("highlightbackground", BORDA)
    kwargs.setdefault("highlightthickness", 1)

    return tk.Frame(parent, **kwargs)


def titulo(parent, texto):

    return tk.Label(
        parent,
        text=texto,
        bg=BRANCO,
        fg=TEXTO,
        font=(FONTE, 15, "bold")
    )


def subtitulo(parent, texto):

    return tk.Label(
        parent,
        text=texto,
        bg=BRANCO,
        fg=TEXTO_SECUNDARIO,
        font=(FONTE, 9)
    )


def label(parent, texto):

    return tk.Label(
        parent,
        text=texto,
        bg=BRANCO,
        fg=TEXTO,
        font=(FONTE, 9)
    )


def botao(parent, texto, command, estilo="Padrao.TButton"):

    return ttk.Button(
        parent,
        text=texto,
        command=command,
        style=estilo
    )


def separador(parent):

    return tk.Frame(parent, bg=LINHA, height=1)


# ============================================================
# FORMULÁRIO
# ============================================================

def form(parent, title, fields, values=None):
    """
    Abre um formulário modal e retorna um dict com os valores,
    ou None se a janela for fechada sem salvar.

    fields: lista de tuplas (chave, rótulo, tipo, opções)
            tipo: "check", "combo", "combo_ro" ou qualquer outro (Entry)
    """

    values = values or {}

    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=BRANCO)
    win.transient(parent)
    win.grab_set()

    # ---------------- cabeçalho ----------------

    cabecalho = tk.Frame(win, bg=BRANCO)
    cabecalho.pack(fill="x", padx=24, pady=(20, 8))

    tk.Label(
        cabecalho,
        text=title,
        bg=BRANCO,
        fg=TEXTO,
        font=(FONTE, 15, "bold")
    ).pack(anchor="w")

    tk.Label(
        cabecalho,
        text="Preencha as informações abaixo.",
        bg=BRANCO,
        fg=TEXTO_SECUNDARIO,
        font=(FONTE, 9)
    ).pack(anchor="w", pady=(2, 0))

    # ---------------- campos ----------------

    area = tk.Frame(win, bg=BRANCO)
    area.pack(fill="both", expand=True, padx=24, pady=8)
    area.columnconfigure(1, weight=1)

    variaveis = {}
    resultado = {}

    for i, (key, label_text, kind, options) in enumerate(fields):

        tk.Label(
            area,
            text=label_text,
            bg=BRANCO,
            fg=TEXTO,
            font=(FONTE, 9, "bold")
        ).grid(row=i, column=0, sticky="w", padx=(0, 16), pady=6)

        valor = values.get(key)

        if kind == "check":

            var = tk.IntVar(value=int(valor or 0))

            widget = ttk.Checkbutton(
                area,
                variable=var,
                style="App.TCheckbutton"
            )

        elif kind in ("combo", "combo_ro"):

            var = tk.StringVar(value=valor or "")

            widget = ttk.Combobox(
                area,
                textvariable=var,
                values=options,
                width=38,
                state="readonly" if kind == "combo_ro" else "normal",
                style="App.TCombobox"
            )

        else:

            var = tk.StringVar(value="" if valor is None else str(valor))

            widget = ttk.Entry(
                area,
                textvariable=var,
                width=40,
                style="App.TEntry"
            )

        widget.grid(row=i, column=1, padx=0, pady=6, sticky="ew")

        variaveis[key] = var

    # ---------------- rodapé ----------------

    rodape = tk.Frame(
        win,
        bg=FUNDO,
        highlightbackground=BORDA,
        highlightthickness=1
    )

    rodape.pack(fill="x", side="bottom")

    def salvar():

        resultado.update({k: v.get() for k, v in variaveis.items()})
        win.destroy()

    ttk.Button(
        rodape,
        text="✓  Salvar",
        command=salvar,
        style="Sucesso.TButton"
    ).pack(side="right", padx=20, pady=12)

    # ---------------- tamanho da janela ----------------

    win.update_idletasks()

    largura = max(520, win.winfo_reqwidth())
    altura = max(180 + len(fields) * 42, win.winfo_reqheight())

    win.geometry(f"{largura}x{altura}")
    win.resizable(False, False)

    win.wait_window()

    return resultado or None


# ============================================================
# TABELA
# ============================================================

def tree(parent, cols):
    """cols: lista de tuplas (chave, título, largura)."""

    frame = tk.Frame(parent, bg=BRANCO)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tabela = ttk.Treeview(
        frame,
        columns=[c[0] for c in cols],
        show="headings",
        selectmode="browse",
        style="App.Treeview"
    )

    for key, title, width in cols:

        tabela.heading(key, text=title)
        tabela.column(key, width=width, minwidth=50, anchor="w")

    barra = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tabela.yview,
        style="App.Vertical.TScrollbar"
    )

    tabela.configure(yscrollcommand=barra.set)

    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    return tabela


# ============================================================
# BOTÕES
# ============================================================

# A ordem importa: a primeira categoria que casar define o estilo.
_PALAVRAS_POR_ESTILO = (
    ("Perigo.TButton", ("excluir", "remover", "apagar", "deletar", "cancelar")),
    ("Sucesso.TButton", ("salvar", "adicionar", "nova", "novo", "criar",
                         "confirmar", "importar")),
    ("Primario.TButton", ("abrir", "editar", "selecionar", "visualizar",
                          "detalhes")),
    ("Atencao.TButton", ("atualizar", "recarregar", "refresh")),
)


def estilo_botao(texto):

    texto_lower = texto.lower().strip()

    for estilo, palavras in _PALAVRAS_POR_ESTILO:

        if any(palavra in texto_lower for palavra in palavras):
            return estilo

    return "Padrao.TButton"


def buttons(parent, items):
    """items: lista de tuplas (texto, comando)."""

    frame = tk.Frame(parent, bg=FUNDO)
    frame.pack(fill="x", padx=10, pady=(0, 10))

    for texto, command in items:

        ttk.Button(
            frame,
            text=texto,
            command=command,
            style=estilo_botao(texto)
        ).pack(side="left", padx=(0, 6))

    return frame


# ============================================================
# SELEÇÃO
# ============================================================

def sel(treeview):

    selecionado = treeview.selection()

    if not selecionado:

        messagebox.showinfo("Atenção", "Selecione uma linha primeiro.")
        return None

    return int(selecionado[0])


# ============================================================
# TRATAMENTO DE ERROS
# ============================================================

def safe(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

        except sqlite3.IntegrityError as e:
            messagebox.showerror("Banco de Dados", str(e))

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erro inesperado", str(e))

    return wrapper


# ============================================================
# INICIALIZAÇÃO
# ============================================================

configurar()
configurar_notebook_restaurante()