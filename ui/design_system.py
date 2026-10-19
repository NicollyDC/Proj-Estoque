"""Paleta e estilos compartilhados do Proj-Estoque (tema claro único)."""

import tkinter as tk
from tkinter import ttk


PALETA = {
    "bg": "#F4F7FB", "surface": "#FFFFFF", "surface2": "#F8FAFC",
    "text": "#1F2937", "muted": "#64748B", "border": "#E2E8F0",
    "primary": "#2563EB", "primary_hover": "#1D4ED8", "primary_soft": "#EAF2FF",
    "success": "#15803D", "warning": "#D97706", "danger": "#DC2626",
    "info": "#7C3AED", "selection": "#DBEAFE", "low": "#FEF2F2",
    "button_text": "#FFFFFF", "danger_action": "#DC2626", "danger_hover": "#B91C1C",
    "danger_button_text": "#FFFFFF", "focus": "#2563EB",
}
FONT = "Segoe UI"


def palette():
    return PALETA


def filtrar_opcoes(opcoes, busca):
    """Retorna resultados que correspondem ao texto digitado, sem distinção de caixa."""
    termo = (busca or "").strip().casefold()
    if not termo:
        return list(opcoes)
    return [opcao for opcao in opcoes if termo in str(opcao).casefold()]


def dinheiro(valor):
    """Formata valores em reais com separadores brasileiros."""
    texto = f"{float(valor or 0):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def configurar_treeview_responsivo(tabela, container, colunas, barra_vertical=None,
                                  barra_horizontal=None, padx=0, pady=0):
    """Centraliza cabeçalhos e células e adapta as colunas à largura disponível."""
    especificacoes = []
    for coluna in colunas:
        chave, largura = coluna[:2]
        minimo = coluna[2] if len(coluna) > 2 else min(largura, max(42, int(largura * 0.55)))
        especificacoes.append((chave, largura, min(minimo, largura)))
        tabela.heading(chave, anchor="center")
        tabela.column(chave, anchor="center", width=largura, minwidth=min(minimo, largura), stretch=False)

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    tabela.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)
    if barra_vertical is not None:
        barra_vertical.grid(row=0, column=1, sticky="ns", padx=(0, padx), pady=pady)
    if barra_horizontal is not None:
        barra_horizontal.grid(row=1, column=0, sticky="ew", padx=padx, pady=(0, pady))
        barra_horizontal.grid_remove()

    mostrar_horizontal_anterior = None

    def adaptar_larguras(_evento=None):
        nonlocal mostrar_horizontal_anterior
        largura_container = container.winfo_width()
        if largura_container <= 1:
            return

        largura_barra = barra_vertical.winfo_reqwidth() if barra_vertical is not None else 0
        disponivel = max(0, largura_container - largura_barra - (2 * padx) - 4)
        soma_base = sum(item[1] for item in especificacoes)
        soma_minima = sum(item[2] for item in especificacoes)

        if disponivel >= soma_base:
            fator = disponivel / soma_base if soma_base else 1
            larguras = [max(minimo, int(base * fator)) for _, base, minimo in especificacoes]
        elif disponivel >= soma_minima:
            inferior, superior = 0.0, 1.0
            for _ in range(24):
                meio = (inferior + superior) / 2
                total = sum(max(minimo, int(base * meio)) for _, base, minimo in especificacoes)
                if total <= disponivel:
                    inferior = meio
                else:
                    superior = meio
            larguras = [max(minimo, int(base * inferior)) for _, base, minimo in especificacoes]
            sobra = disponivel - sum(larguras)
            for indice, (_, base, _) in enumerate(especificacoes):
                acrescimo = min(sobra, base - larguras[indice])
                larguras[indice] += acrescimo
                sobra -= acrescimo
                if sobra <= 0:
                    break
        else:
            larguras = [minimo for _, _, minimo in especificacoes]

        for (chave, _, _), largura in zip(especificacoes, larguras):
            tabela.column(chave, width=largura)

        mostrar_horizontal = sum(larguras) > disponivel
        if barra_horizontal is not None and mostrar_horizontal != mostrar_horizontal_anterior:
            if mostrar_horizontal:
                barra_horizontal.grid()
            else:
                barra_horizontal.grid_remove()
            mostrar_horizontal_anterior = mostrar_horizontal
    container.bind("<Configure>", adaptar_larguras, add="+")
    container.after_idle(adaptar_larguras)
    return adaptar_larguras


def configure_styles():
    c = PALETA
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=c["bg"])
    style.configure("TLabel", background=c["bg"], foreground=c["text"], font=(FONT, 10))
    style.configure("App.TLabel", background=c["bg"], foreground=c["text"], font=(FONT, 10))
    style.configure("AppTitle.TLabel", background=c["bg"], foreground=c["text"], font=(FONT, 17, "bold"))
    style.configure("AppSubtitle.TLabel", background=c["bg"], foreground=c["muted"], font=(FONT, 10))
    style.configure("Painel.TLabel", background=c["surface"], foreground=c["text"], font=(FONT, 10))
    for name, size, weight in (("Title.TLabel", 23, "bold"), ("Section.TLabel", 12, "bold"), ("CardTitle.TLabel", 15, "bold"), ("User.TLabel", 11, "bold")):
        style.configure(name, background=c["bg"] if name != "User.TLabel" else c["surface"], foreground=c["text"], font=(FONT, size, weight))
    for name in ("Subtitle.TLabel", "CardSubtitle.TLabel"):
        style.configure(name, background=c["bg"] if name == "Subtitle.TLabel" else c["surface"], foreground=c["muted"], font=(FONT, 10))
    style.configure("Profile.TLabel", background=c["surface"], foreground=c["muted"], font=(FONT, 9))
    for name in ("TEntry", "App.TEntry"):
        style.configure(name, fieldbackground=c["surface"], foreground=c["text"], insertcolor=c["text"], bordercolor=c["border"], padding=7, font=(FONT, 10))
        style.map(name, bordercolor=[("focus", c["focus"])], lightcolor=[("focus", c["focus"])], darkcolor=[("focus", c["focus"])])
    for name in ("TCombobox", "App.TCombobox"):
        style.configure(name, fieldbackground=c["surface"], background=c["surface"], foreground=c["text"], arrowcolor=c["text"], padding=7, font=(FONT, 10))
        style.map(name, fieldbackground=[("readonly", c["surface"])], foreground=[("readonly", c["text"])], bordercolor=[("focus", c["focus"])])
    style.configure("TButton", background=c["surface"], foreground=c["text"], bordercolor=c["border"], padding=(12, 8), font=(FONT, 9, "bold"))
    style.map("TButton", background=[("active", c["surface2"]), ("pressed", c["border"]), ("disabled", c["surface2"])], foreground=[("disabled", c["muted"])])
    actions = (("Primario", c["primary"], c["primary_hover"], "#FFFFFF"), ("Sucesso", c["success"], "#166534", "#FFFFFF"), ("Perigo", c["danger_action"], c["danger_hover"], "#FFFFFF"), ("Atencao", "#FDE68A", "#FCD34D", c["text"]))
    for name, color, hover, foreground in actions:
        style.configure(f"{name}.TButton", background=color, foreground=foreground, borderwidth=0, padding=(13, 8), font=(FONT, 9, "bold"))
        style.map(f"{name}.TButton", background=[("active", hover), ("disabled", c["surface2"])], foreground=[("disabled", c["muted"])])
    style.configure("Padrao.TButton", background=c["surface"], foreground=c["text"], bordercolor=c["border"], padding=(12, 8), font=(FONT, 9, "bold"))
    style.map("Padrao.TButton", background=[("active", c["surface2"]), ("pressed", c["border"]), ("disabled", c["surface2"])], foreground=[("disabled", c["muted"])])
    style.configure("App.TCheckbutton", background=c["surface"], foreground=c["text"], font=(FONT, 10))
    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=c["bg"], foreground=c["muted"], padding=(18, 10), font=(FONT, 10, "bold"), borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", c["surface"]), ("active", c["primary_soft"])], foreground=[("selected", c["primary"]), ("active", c["text"])])
    for name in ("Hotel.TNotebook", "Restaurante.TNotebook"):
        style.configure(name, background=c["bg"], borderwidth=0)
        style.configure(f"{name}.Tab", background=c["bg"], foreground=c["muted"], padding=(18, 10), font=(FONT, 10, "bold"), borderwidth=0)
        style.map(f"{name}.Tab", background=[("selected", c["surface"]), ("active", c["primary_soft"])], foreground=[("selected", c["primary"]), ("active", c["text"])])
    for name in ("App.Treeview", "Usuarios.Treeview"):
        style.configure(name, background=c["surface"], foreground=c["text"], fieldbackground=c["surface"], rowheight=34, borderwidth=0, font=(FONT, 10))
        style.map(name, background=[("selected", c["selection"])], foreground=[("selected", c["text"])])
        style.configure(f"{name}.Heading", background=c["surface2"], foreground=c["text"], font=(FONT, 9, "bold"), relief="flat", borderwidth=0, padding=(9, 9))
    style.map("App.Treeview.Heading", background=[("active", c["primary_soft"])])
    style.configure("App.Vertical.TScrollbar", background=c["border"], troughcolor=c["bg"], borderwidth=0, arrowsize=12)
    style.configure("TScrollbar", background=c["border"], troughcolor=c["bg"], borderwidth=0, arrowsize=12)
    style.configure("Filtro.TLabelframe", background=c["surface"], bordercolor=c["border"])
    style.configure("Filtro.TLabelframe.Label", background=c["surface"], foreground=c["text"], font=(FONT, 10, "bold"))
    style.configure("Filtro.TFrame", background=c["surface"])
    style.configure("Filtro.TLabel", background=c["surface"], foreground=c["text"])
    style.configure("Filtro.TCheckbutton", background=c["surface"], foreground=c["text"])
    return c
