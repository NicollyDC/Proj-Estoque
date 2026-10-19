"""
Estilos e componentes visuais (tkinter / ttk) - Hotel.
"""

import functools
import sqlite3
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from ui import design_system as design


# ============================================================
# PALETA
# ============================================================

FUNDO = design.PALETA["bg"]
BRANCO = design.PALETA["surface"]

TEXTO = design.PALETA["text"]
TEXTO_SECUNDARIO = design.PALETA["muted"]

AZUL = design.PALETA["primary"]
AZUL_HOVER = design.PALETA["primary_hover"]
AZUL_CLARO = design.PALETA["primary_soft"]

VERDE = design.PALETA["success"]
VERDE_HOVER = "#15803D"
VERDE_CLARO = "#EAF7EF"

VERMELHO = design.PALETA["danger"]
VERMELHO_HOVER = design.PALETA["danger_hover"]
VERMELHO_CLARO = "#FFF0F0"

AMARELO = design.PALETA["warning"]
AMARELO_HOVER = "#B45309"
AMARELO_CLARO = "#FFF8E5"

LILAS = design.PALETA["info"]
LILAS_HOVER = "#6D28D9"
LILAS_CLARO = "#F1EEFF"

CINZA = "#AAB4C0"
CINZA_HOVER = "#929EAB"

BORDA = design.PALETA["border"]
LINHA = design.PALETA["surface2"]

FONTE = "Segoe UI"


def mensagem_integridade(erro):
    texto = str(erro).lower()

    if "foreign key" in texto:
        return (
            "Não foi possível concluir esta operação porque existem "
            "movimentações ou vínculos relacionados."
        )

    if "unique" in texto:
        return (
            "Já existe um cadastro com essas informações. "
            "Verifique o código do produto ou a chave da nota."
        )

    return "Não foi possível gravar os dados. Confira as informações e tente novamente."


def _estilo_campo(style, nome):
    style.configure(
        nome,
        fieldbackground=BRANCO,
        foreground=TEXTO,
        bordercolor=BORDA,
        lightcolor=BORDA,
        darkcolor=BORDA,
        padding=7,
        font=(FONTE, 10)
    )
    style.map(
        nome,
        bordercolor=[("focus", AZUL)],
        lightcolor=[("focus", AZUL)],
        darkcolor=[("focus", AZUL)]
    )


def configurar():
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("App.TLabel", background=FUNDO, foreground=TEXTO, font=(FONTE, 10))
    style.configure("AppTitle.TLabel", background=FUNDO, foreground=TEXTO, font=(FONTE, 15, "bold"))
    style.configure("AppSubtitle.TLabel", background=FUNDO, foreground=TEXTO_SECUNDARIO, font=(FONTE, 9))
    style.configure("Painel.TLabel", background=BRANCO, foreground=TEXTO, font=(FONTE, 10))

    _estilo_campo(style, "App.TEntry")
    _estilo_campo(style, "App.TCombobox")
    style.configure("App.TCombobox", background=BRANCO)

    coloridos = {
        "Primario.TButton": (AZUL, AZUL_HOVER),
        "Sucesso.TButton": (VERDE, VERDE_HOVER),
        "Perigo.TButton": (VERMELHO, VERMELHO_HOVER),
        "Atencao.TButton": (AMARELO, AMARELO_HOVER),
        "Neutral.TButton": (CINZA, CINZA_HOVER),
    }

    for nome, (cor, hover) in coloridos.items():
        style.configure(
            nome,
            background=cor,
            foreground=BRANCO,
            borderwidth=0,
            padding=(14, 8),
            font=(FONTE, 9, "bold"),
            relief="flat"
        )
        style.map(nome, background=[("active", hover), ("pressed", hover)])

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

    style.configure("App.TCheckbutton", background=BRANCO, foreground=TEXTO, font=(FONTE, 10))

    style.configure(
        "App.Treeview",
        background=BRANCO,
        foreground=TEXTO,
        fieldbackground=BRANCO,
        rowheight=34,
        borderwidth=0,
        font=(FONTE, 9)
    )
    style.configure(
        "App.Treeview.Heading",
        background=AZUL_CLARO,
        foreground=TEXTO,
        font=(FONTE, 9, "bold"),
        relief="flat",
        borderwidth=0,
        padding=(8, 9)
    )
    style.map("App.Treeview", background=[("selected", "#DCEAFF")], foreground=[("selected", TEXTO)])
    style.map("App.Treeview.Heading", background=[("active", "#DDEAFF")])

    style.configure(
        "App.Vertical.TScrollbar",
        background="#DDE5EF",
        troughcolor=FUNDO,
        borderwidth=0,
        arrowsize=12
    )


def configurar_notebook_hotel():
    style = ttk.Style()
    style.configure("Hotel.TNotebook", background=FUNDO, borderwidth=0)
    style.configure(
        "Hotel.TNotebook.Tab",
        background=AZUL_CLARO,
        foreground=TEXTO_SECUNDARIO,
        padding=(20, 10),
        font=(FONTE, 10, "bold"),
        borderwidth=0
    )
    style.map(
        "Hotel.TNotebook.Tab",
        background=[("selected", BRANCO), ("active", "#DDEAFF")],
        foreground=[("selected", AZUL), ("active", TEXTO)]
    )


def _desenhar_fundo_arredondado(canvas, largura, altura, cor, raio=10):
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
    for x, y in (
        (0, 0),
        (largura - diametro, 0),
        (0, altura - diametro),
        (largura - diametro, altura - diametro),
    ):
        canvas.create_oval(x, y, x + diametro, y + diametro, fill=cor, outline=cor, tags="botao")


def criar_botao_arredondado(parent, texto, comando, largura=150, altura=38, cor=AZUL, cor_hover=AZUL_HOVER):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=parent.cget("bg"),
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )
    _desenhar_fundo_arredondado(canvas, largura, altura, cor)
    canvas.create_text(largura // 2, altura // 2, text=texto, fill=design.palette()["button_text"], font=(FONTE, 10, "bold"), tags=("button-label-primary",))
    canvas.bind("<Enter>", lambda e: canvas.itemconfig("botao", fill=design.palette()["primary_hover"], outline=design.palette()["primary_hover"]))
    canvas.bind("<Leave>", lambda e: canvas.itemconfig("botao", fill=design.palette()["primary"], outline=design.palette()["primary"]))
    canvas.bind("<Button-1>", lambda e: comando())
    return canvas


def painel(parent, **kwargs):
    kwargs.setdefault("bg", BRANCO)
    kwargs.setdefault("highlightbackground", BORDA)
    kwargs.setdefault("highlightthickness", 1)
    return tk.Frame(parent, **kwargs)


def titulo(parent, texto):
    return tk.Label(parent, text=texto, bg=BRANCO, fg=TEXTO, font=(FONTE, 15, "bold"))


def subtitulo(parent, texto):
    return tk.Label(parent, text=texto, bg=BRANCO, fg=TEXTO_SECUNDARIO, font=(FONTE, 9))


def label(parent, texto):
    return tk.Label(parent, text=texto, bg=BRANCO, fg=TEXTO, font=(FONTE, 9))


def botao(parent, texto, command, estilo="Padrao.TButton"):
    return ttk.Button(parent, text=texto, command=command, style=estilo)


def separador(parent):
    return tk.Frame(parent, bg=LINHA, height=1)


def form(parent, title, fields, values=None, extra_content=None):
    values = values or {}

    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=BRANCO)
    win.transient(parent)
    win.grab_set()

    cabecalho = tk.Frame(win, bg=BRANCO)
    cabecalho.pack(fill="x", padx=24, pady=(20, 8))

    tk.Label(cabecalho, text=title, bg=BRANCO, fg=TEXTO, font=(FONTE, 15, "bold")).pack(anchor="w")
    tk.Label(
        cabecalho,
        text="Preencha as informações e clique em Salvar. Use Cancelar para voltar sem gravar.",
        bg=BRANCO,
        fg=TEXTO_SECUNDARIO,
        font=(FONTE, 9)
    ).pack(anchor="w", pady=(2, 0))

    area = tk.Frame(win, bg=BRANCO)
    area.pack(fill="both", expand=True, padx=24, pady=8)
    area.columnconfigure(1, weight=1)

    variaveis = {}
    resultado = {}

    for i, (key, label_text, kind, options) in enumerate(fields):
        tk.Label(
            area, text=label_text, bg=BRANCO, fg=TEXTO, font=(FONTE, 9, "bold")
        ).grid(row=i, column=0, sticky="w", padx=(0, 16), pady=6)

        valor = values.get(key)

        if kind == "check":
            var = tk.IntVar(value=int(valor or 0))
            widget = ttk.Checkbutton(area, variable=var, style="App.TCheckbutton")
        elif kind in ("combo", "combo_ro"):
            var = tk.StringVar(value=valor or "")
            opcoes = tuple(options or ())
            widget = ttk.Combobox(
                area,
                textvariable=var,
                values=opcoes,
                width=38,
                state="readonly" if kind == "combo_ro" else "normal",
                style="App.TCombobox"
            )
            if kind == "combo":
                def filtrar(event, combo=widget, variable=var, all_options=opcoes):
                    if event.keysym in {"Up", "Down", "Left", "Right", "Return", "Escape", "Tab", "Shift_L", "Control_L"}:
                        return
                    termo = variable.get().strip().casefold()
                    resultados = design.filtrar_opcoes(all_options, termo)
                    combo.configure(values=resultados if termo else all_options)
                    if termo and resultados:
                        def abrir_lista():
                            try:
                                combo.tk.call("ttk::combobox::Post", combo)
                            except tk.TclError:
                                pass
                        combo.after_idle(abrir_lista)
                widget.bind("<KeyRelease>", filtrar)
                widget.bind("<<ComboboxSelected>>", lambda _event, combo=widget, all_options=opcoes: combo.configure(values=all_options))
        else:
            var = tk.StringVar(value="" if valor is None else str(valor))
            widget = ttk.Entry(area, textvariable=var, width=40, style="App.TEntry")

        widget.grid(row=i, column=1, padx=0, pady=6, sticky="ew")
        variaveis[key] = var

    if extra_content is not None:
        extra_content(area, len(fields))

    rodape = tk.Frame(win, bg=FUNDO, highlightbackground=BORDA, highlightthickness=1)
    rodape.pack(fill="x", side="bottom")

    def salvar():
        resultado.update({k: v.get() for k, v in variaveis.items()})
        win.destroy()

    def cancelar():
        win.destroy()

    ttk.Button(rodape, text="Cancelar", command=cancelar, style="Padrao.TButton").pack(
        side="right", padx=(0, 20), pady=12
    )
    ttk.Button(rodape, text="Salvar", command=salvar, style="Primario.TButton").pack(
        side="right", padx=8, pady=12
    )

    win.bind("<Return>", lambda e: salvar())
    win.bind("<Escape>", lambda e: cancelar())

    win.update_idletasks()
    largura = max(520, win.winfo_reqwidth())
    altura = max(220 + len(fields) * 42, win.winfo_reqheight())
    win.geometry(f"{largura}x{altura}")
    win.resizable(False, False)
    win.wait_window()

    return resultado or None


def tree(parent, cols):
    frame = tk.Frame(parent, bg=BRANCO)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tabela = ttk.Treeview(
        frame,
        columns=[c[0] for c in cols],
        show="headings",
        selectmode="browse",
        style="App.Treeview"
    )

    barra = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview, style="App.Vertical.TScrollbar")
    barra_horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tabela.xview)
    tabela.configure(yscrollcommand=barra.set, xscrollcommand=barra_horizontal.set)
    for key, title, _width in cols:
        tabela.heading(key, text=title)
    design.configurar_treeview_responsivo(
        tabela,
        frame,
        [(key, width) for key, _title, width in cols],
        barra,
        barra_horizontal,
    )
    return tabela


_PALAVRAS_POR_ESTILO = (
    ("Perigo.TButton", ("excluir", "remover", "apagar", "deletar")),
    ("Primario.TButton", ("salvar", "adicionar", "nova", "novo", "criar", "confirmar", "importar")),
    ("Primario.TButton", ("abrir", "editar", "selecionar", "visualizar", "detalhes", "consultar")),
    ("Atencao.TButton", ("atualizar", "recarregar", "refresh")),
    ("Padrao.TButton", ("limpar", "cancelar", "voltar", "fechar")),
)


def estilo_botao(texto):
    texto_lower = texto.lower().strip()
    for estilo, palavras in _PALAVRAS_POR_ESTILO:
        if any(palavra in texto_lower for palavra in palavras):
            return estilo
    return "Padrao.TButton"


def buttons(parent, items):
    frame = tk.Frame(parent, bg=FUNDO)
    frame.pack(fill="x", padx=10, pady=(0, 10))

    for texto, command in items:
        ttk.Button(frame, text=texto, command=command, style=estilo_botao(texto)).pack(
            side="left", padx=(0, 6)
        )
    return frame


def sel(treeview, parent=None):
    selecionado = treeview.selection()
    if not selecionado:
        messagebox.showinfo(
            "Atenção",
            "Selecione uma linha da lista primeiro.",
            parent=parent
        )
        return None
    return int(selecionado[0])


def safe(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            messagebox.showerror("Dados inválidos", str(e))
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Não foi possível salvar", mensagem_integridade(e))
        except Exception:
            traceback.print_exc()
            messagebox.showerror(
                "Algo deu errado",
                "Não foi possível concluir esta ação. Tente novamente."
            )
    return wrapper


configurar()
configurar_notebook_hotel()
design.configure_styles()
