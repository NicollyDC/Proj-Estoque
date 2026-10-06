import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox
import functools
import traceback


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


# ============================================================
# ESTILO
# ============================================================

def configurar_estilo():

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # ============================================================
    # FILTROS / PAINÉIS
    # ============================================================

    style.configure(
        "Filtro.TLabelframe",
        background=BRANCO,
        bordercolor=BORDA,
        relief="solid"
    )

    style.configure(
        "Filtro.TLabelframe.Label",
        background=BRANCO,
        foreground=TEXTO,
        font=("Segoe UI", 10, "bold")
    )

    style.configure(
        "Filtro.TFrame",
        background=BRANCO
    )

    style.configure(
        "Filtro.TLabel",
        background=BRANCO,
        foreground=TEXTO
    )

    style.configure(
        "Filtro.TCheckbutton",
        background=BRANCO,
        foreground=TEXTO
    )
    
    # --------------------------------------------------------
    # LABELS
    # --------------------------------------------------------

    style.configure(
        "App.TLabel",
        background=FUNDO,
        foreground=TEXTO,
        font=("Segoe UI", 10)
    )

    style.configure(
        "AppTitle.TLabel",
        background=BRANCO,
        foreground=TEXTO,
        font=("Segoe UI", 15, "bold")
    )

    style.configure(
        "AppSubtitle.TLabel",
        background=BRANCO,
        foreground=TEXTO_SECUNDARIO,
        font=("Segoe UI", 9)
    )

    # --------------------------------------------------------
    # ENTRY
    # --------------------------------------------------------

    style.configure(
        "App.TEntry",
        fieldbackground=BRANCO,
        foreground=TEXTO,
        bordercolor=BORDA,
        lightcolor=BORDA,
        darkcolor=BORDA,
        padding=7,
        font=("Segoe UI", 10)
    )

    style.map(
        "App.TEntry",
        bordercolor=[
            ("focus", AZUL)
        ],
        lightcolor=[
            ("focus", AZUL)
        ],
        darkcolor=[
            ("focus", AZUL)
        ]
    )

    # --------------------------------------------------------
    # COMBOBOX
    # --------------------------------------------------------

    style.configure(
        "App.TCombobox",
        fieldbackground=BRANCO,
        background=BRANCO,
        foreground=TEXTO,
        bordercolor=BORDA,
        lightcolor=BORDA,
        darkcolor=BORDA,
        padding=7,
        font=("Segoe UI", 10)
    )

    style.map(
        "App.TCombobox",
        bordercolor=[
            ("focus", AZUL)
        ],
        lightcolor=[
            ("focus", AZUL)
        ],
        darkcolor=[
            ("focus", AZUL)
        ]
    )

    # --------------------------------------------------------
    # BOTÃO AZUL
    # --------------------------------------------------------

    style.configure(
        "App.TButton",
        background=AZUL,
        foreground=BRANCO,
        borderwidth=0,
        padding=(14, 8),
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "App.TButton",
        background=[
            ("active", AZUL_HOVER),
            ("pressed", AZUL_HOVER)
        ],
        foreground=[
            ("active", BRANCO),
            ("pressed", BRANCO)
        ]
    )

    # --------------------------------------------------------
    # BOTÃO VERDE
    # --------------------------------------------------------

    style.configure(
        "Success.TButton",
        background=VERDE,
        foreground=BRANCO,
        borderwidth=0,
        padding=(14, 8),
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "Success.TButton",
        background=[
            ("active", VERDE_HOVER),
            ("pressed", VERDE_HOVER)
        ],
        foreground=[
            ("active", BRANCO),
            ("pressed", BRANCO)
        ]
    )

    # --------------------------------------------------------
    # BOTÃO VERMELHO
    # --------------------------------------------------------

    style.configure(
        "Danger.TButton",
        background=VERMELHO,
        foreground=BRANCO,
        borderwidth=0,
        padding=(14, 8),
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "Danger.TButton",
        background=[
            ("active", VERMELHO_HOVER),
            ("pressed", VERMELHO_HOVER)
        ],
        foreground=[
            ("active", BRANCO),
            ("pressed", BRANCO)
        ]
    )

    # --------------------------------------------------------
    # BOTÃO AMARELO
    # --------------------------------------------------------

    style.configure(
        "Warning.TButton",
        background=AMARELO,
        foreground=BRANCO,
        borderwidth=0,
        padding=(14, 8),
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "Warning.TButton",
        background=[
            ("active", AMARELO_HOVER),
            ("pressed", AMARELO_HOVER)
        ],
        foreground=[
            ("active", BRANCO),
            ("pressed", BRANCO)
        ]
    )

    # --------------------------------------------------------
    # BOTÃO NEUTRO
    # --------------------------------------------------------

    style.configure(
        "Neutral.TButton",
        background=CINZA,
        foreground=BRANCO,
        borderwidth=0,
        padding=(14, 8),
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "Neutral.TButton",
        background=[
            ("active", CINZA_HOVER),
            ("pressed", CINZA_HOVER)
        ],
        foreground=[
            ("active", BRANCO),
            ("pressed", BRANCO)
        ]
    )

    # --------------------------------------------------------
    # CHECKBUTTON
    # --------------------------------------------------------

    style.configure(
        "App.TCheckbutton",
        background=BRANCO,
        foreground=TEXTO,
        font=("Segoe UI", 10)
    )

    # --------------------------------------------------------
    # TREEVIEW
    # --------------------------------------------------------

    style.configure(
        "App.Treeview",
        background=BRANCO,
        foreground=TEXTO,
        fieldbackground=BRANCO,
        rowheight=34,
        borderwidth=0,
        font=("Segoe UI", 9)
    )

    style.configure(
        "App.Treeview.Heading",
        background=AZUL_CLARO,
        foreground=TEXTO,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        borderwidth=0,
        padding=(8, 9)
    )

    style.map(
        "App.Treeview",
        background=[
            ("selected", "#DCEAFF")
        ],
        foreground=[
            ("selected", TEXTO)
        ]
    )

    style.map(
        "App.Treeview.Heading",
        background=[
            ("active", "#DDEAFF")
        ]
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


configurar_estilo()


# ============================================================
# FORMULÁRIO
# ============================================================

def form(parent, title, fields, values=None):

    values = values or {}

    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=BRANCO)
    win.transient(parent)
    win.grab_set()

    # --------------------------------------------------------
    # CABEÇALHO
    # --------------------------------------------------------

    cabecalho = tk.Frame(
        win,
        bg=BRANCO
    )

    cabecalho.pack(
        fill="x",
        padx=24,
        pady=(20, 8)
    )

    tk.Label(
        cabecalho,
        text=title,
        bg=BRANCO,
        fg=TEXTO,
        font=("Segoe UI", 15, "bold")
    ).pack(
        anchor="w"
    )

    tk.Label(
        cabecalho,
        text="Preencha as informações abaixo.",
        bg=BRANCO,
        fg=TEXTO_SECUNDARIO,
        font=("Segoe UI", 9)
    ).pack(
        anchor="w",
        pady=(2, 0)
    )

    # --------------------------------------------------------
    # CAMPOS
    # --------------------------------------------------------

    area = tk.Frame(
        win,
        bg=BRANCO
    )

    area.pack(
        fill="both",
        expand=True,
        padx=24,
        pady=8
    )

    variaveis = {}
    resultado = {}

    for i, (key, label, kind, options) in enumerate(fields):

        tk.Label(
            area,
            text=label,
            bg=BRANCO,
            fg=TEXTO,
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=i,
            column=0,
            sticky="w",
            padx=(0, 16),
            pady=6
        )

        valor = values.get(key)

        if kind == "check":

            var = tk.IntVar(
                value=int(valor or 0)
            )

            widget = ttk.Checkbutton(
                area,
                variable=var,
                style="App.TCheckbutton"
            )

        elif kind in ("combo", "combo_ro"):

            var = tk.StringVar(
                value=valor or ""
            )

            widget = ttk.Combobox(
                area,
                textvariable=var,
                values=options,
                width=38,
                state=(
                    "readonly"
                    if kind == "combo_ro"
                    else "normal"
                ),
                style="App.TCombobox"
            )

        else:

            var = tk.StringVar(
                value=(
                    ""
                    if valor is None
                    else str(valor)
                )
            )

            widget = ttk.Entry(
                area,
                textvariable=var,
                width=40,
                style="App.TEntry"
            )

        widget.grid(
            row=i,
            column=1,
            padx=0,
            pady=6,
            sticky="ew"
        )

        variaveis[key] = var

    area.columnconfigure(
        1,
        weight=1
    )

    # --------------------------------------------------------
    # RODAPÉ
    # --------------------------------------------------------

    rodape = tk.Frame(
        win,
        bg=FUNDO,
        highlightbackground=BORDA,
        highlightthickness=1
    )

    rodape.pack(
        fill="x",
        side="bottom"
    )

    def salvar():

        resultado.update({
            k: v.get()
            for k, v in variaveis.items()
        })

        win.destroy()

    ttk.Button(
        rodape,
        text="✓  Salvar",
        command=salvar,
        style="Success.TButton"
    ).pack(
        side="right",
        padx=20,
        pady=12
    )

    win.update_idletasks()

    largura = max(
        520,
        win.winfo_reqwidth()
    )

    altura = max(
        180 + len(fields) * 42,
        win.winfo_reqheight()
    )

    win.geometry(
        f"{largura}x{altura}"
    )

    win.resizable(
        False,
        False
    )

    win.wait_window()

    return resultado or None


# ============================================================
# TABELA
# ============================================================

def tree(parent, cols):

    frame = tk.Frame(
        parent,
        bg=BRANCO
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    tabela = ttk.Treeview(
        frame,
        columns=[c[0] for c in cols],
        show="headings",
        selectmode="browse",
        style="App.Treeview"
    )

    for key, title, width in cols:

        tabela.heading(
            key,
            text=title
        )

        tabela.column(
            key,
            width=width,
            minwidth=50,
            anchor="w"
        )

    barra = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tabela.yview,
        style="App.Vertical.TScrollbar"
    )

    tabela.configure(
        yscrollcommand=barra.set
    )

    tabela.pack(
        side="left",
        fill="both",
        expand=True
    )

    barra.pack(
        side="right",
        fill="y"
    )

    return tabela


# ============================================================
# IDENTIFICAR TIPO DO BOTÃO
# ============================================================

def _estilo_botao(texto):

    texto_lower = texto.lower().strip()

    # --------------------------------------------------------
    # PERIGO
    # --------------------------------------------------------

    palavras_perigo = [
        "excluir",
        "remover",
        "apagar",
        "deletar",
        "cancelar"
    ]

    if any(
        palavra in texto_lower
        for palavra in palavras_perigo
    ):
        return "Danger.TButton"

    # --------------------------------------------------------
    # SUCESSO / CRIAÇÃO
    # --------------------------------------------------------

    palavras_sucesso = [
        "salvar",
        "nova ",
        "novo ",
        "adicionar",
        "criar",
        "importar"
    ]

    if any(
        palavra in texto_lower
        for palavra in palavras_sucesso
    ):
        return "Success.TButton"

    # --------------------------------------------------------
    # ATENÇÃO
    # --------------------------------------------------------

    palavras_atencao = [
        "redefinir",
        "desativar",
        "ativar"
    ]

    if any(
        palavra in texto_lower
        for palavra in palavras_atencao
    ):
        return "Warning.TButton"

    # --------------------------------------------------------
    # NEUTRO
    # --------------------------------------------------------

    palavras_neutro = [
        "atualizar",
        "limpar"
    ]

    if any(
        palavra in texto_lower
        for palavra in palavras_neutro
    ):
        return "Neutral.TButton"

    # --------------------------------------------------------
    # PADRÃO
    # --------------------------------------------------------

    return "App.TButton"


# ============================================================
# BOTÕES
# ============================================================

def buttons(parent, items):

    frame = tk.Frame(
        parent,
        bg=FUNDO
    )

    frame.pack(
        fill="x",
        padx=10,
        pady=(0, 10)
    )

    for text, command in items:

        estilo = _estilo_botao(text)

        ttk.Button(
            frame,
            text=text,
            command=command,
            style=estilo
        ).pack(
            side="left",
            padx=(0, 6)
        )

    return frame


# ============================================================
# BOTÃO DE AJUDA
# ============================================================

def help_button(parent, texto):

    def mostrar():

        messagebox.showinfo(
            "Ajuda",
            texto,
            parent=parent
        )

    botao = tk.Button(
        parent,
        text="?",
        command=mostrar,
        bg=LILAS,
        fg=BRANCO,
        activebackground=LILAS_HOVER,
        activeforeground=BRANCO,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        width=3,
        height=1,
        cursor="hand2"
    )

    return botao


# ============================================================
# SELEÇÃO
# ============================================================

def sel(treeview):

    selecionado = treeview.selection()

    if not selecionado:

        messagebox.showinfo(
            "Atenção",
            "Selecione uma linha primeiro."
        )

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

            messagebox.showerror(
                "Erro",
                str(e)
            )

        except sqlite3.IntegrityError as e:

            messagebox.showerror(
                "Banco de Dados",
                str(e)
            )

        except Exception as e:

            traceback.print_exc()

            messagebox.showerror(
                "Erro inesperado",
                str(e)
            )

    return wrapper