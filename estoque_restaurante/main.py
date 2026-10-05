import tkinter as tk
from tkinter import ttk, messagebox

from estoque_restaurante.app_state import salvar, tem_alteracoes

from estoque_restaurante.ui.notas import criar_aba_notas
from estoque_restaurante.ui.produtos import criar_aba_produtos
from estoque_restaurante.ui.saidas import criar_aba_saidas
from estoque_restaurante.ui.relatorios import criar_aba_relatorios


# ============================================================
# CORES
# ============================================================

FUNDO = "#F4F6F8"
BRANCO = "#FFFFFF"
TEXTO = "#1F2937"
TEXTO_SECUNDARIO = "#6B7280"
BORDA = "#E5E7EB"
PRINCIPAL = "#2563EB"
PRINCIPAL_HOVER = "#1D4ED8"


# ============================================================
# BOTÃO ARREDONDADO
# ============================================================

def criar_botao_arredondado(
    parent,
    texto,
    comando,
    largura=150,
    altura=38,
    cor=PRINCIPAL,
    cor_hover=PRINCIPAL_HOVER
):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=parent.cget("bg"),
        highlightthickness=0
    )

    canvas.pack()

    raio = 10

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

    canvas.create_polygon(
        pontos,
        fill=cor,
        outline=cor
    )

    canvas.create_oval(
        0,
        0,
        raio * 2,
        raio * 2,
        fill=cor,
        outline=cor
    )

    canvas.create_oval(
        largura - raio * 2,
        0,
        largura,
        raio * 2,
        fill=cor,
        outline=cor
    )

    canvas.create_oval(
        0,
        altura - raio * 2,
        raio * 2,
        altura,
        fill=cor,
        outline=cor
    )

    canvas.create_oval(
        largura - raio * 2,
        altura - raio * 2,
        largura,
        altura,
        fill=cor,
        outline=cor
    )

    texto_id = canvas.create_text(
        largura // 2,
        altura // 2,
        text=texto,
        fill=BRANCO,
        font=("Segoe UI", 10, "bold")
    )

    def entrar(event):
        canvas.itemconfig(
            "all",
            fill=cor_hover
        )

        canvas.itemconfig(
            texto_id,
            fill=BRANCO
        )

    def sair(event):
        canvas.itemconfig(
            "all",
            fill=cor
        )

        canvas.itemconfig(
            texto_id,
            fill=BRANCO
        )

    def clicar(event):
        comando()

    canvas.bind("<Enter>", entrar)
    canvas.bind("<Leave>", sair)
    canvas.bind("<Button-1>", clicar)

    return canvas


# ============================================================
# JANELA DO RESTAURANTE
# ============================================================

def criar_janela_restaurante(painel, ao_fechar=None):

    root = tk.Toplevel(painel)

    root.title("Controle de Estoque - Restaurante")
    root.geometry("1150x680")
    root.minsize(1000, 600)

    root.configure(
        bg=FUNDO
    )

    # ========================================================
    # SALVAR
    # ========================================================

    def salvar_com_mensagem():

        salvar()

        messagebox.showinfo(
            "Salvar",
            "Alterações salvas com sucesso!",
            parent=root
        )

    # ========================================================
    # FECHAR
    # ========================================================

    def fechar():

        if tem_alteracoes():

            resp = messagebox.askyesnocancel(
                "Salvar alterações",
                "Deseja salvar antes de sair?",
                parent=root
            )

            if resp is None:
                return

            if resp:
                salvar_com_mensagem()

        root.destroy()

        if ao_fechar:
            ao_fechar()

    # ========================================================
    # VOLTAR AO PAINEL
    # ========================================================

    def voltar_painel():

        if tem_alteracoes():

            resp = messagebox.askyesnocancel(
                "Salvar alterações",
                "Existem alterações não salvas.\n\n"
                "Deseja salvar antes de voltar ao painel?",
                parent=root
            )

            if resp is None:
                return

            if resp:
                salvar_com_mensagem()

        root.destroy()

        if ao_fechar:
            ao_fechar()

    # ========================================================
    # ESTILO
    # ========================================================

    style = ttk.Style()

    style.theme_use("clam")

    style.configure(
        "Restaurante.TFrame",
        background=FUNDO
    )

    style.configure(
        "RestauranteCard.TFrame",
        background=BRANCO
    )

    style.configure(
        "Restaurante.TLabel",
        background=FUNDO,
        foreground=TEXTO,
        font=("Segoe UI", 10)
    )

    style.configure(
        "RestauranteTitle.TLabel",
        background=FUNDO,
        foreground=TEXTO,
        font=("Segoe UI", 18, "bold")
    )

    style.configure(
        "RestauranteSubtitle.TLabel",
        background=FUNDO,
        foreground=TEXTO_SECUNDARIO,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Restaurante.TNotebook",
        background=FUNDO,
        borderwidth=0
    )

    style.configure(
        "Restaurante.TNotebook.Tab",
        background="#E5E7EB",
        foreground=TEXTO_SECUNDARIO,
        padding=(20, 10),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0
    )

    style.map(
        "Restaurante.TNotebook.Tab",
        background=[
            ("selected", BRANCO),
            ("active", "#DCE5F5")
        ],
        foreground=[
            ("selected", PRINCIPAL),
            ("active", TEXTO)
        ]
    )

    style.configure(
        "Treeview",
        background=BRANCO,
        foreground=TEXTO,
        fieldbackground=BRANCO,
        rowheight=30,
        font=("Segoe UI", 10),
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background="#F8FAFC",
        foreground=TEXTO,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padding=(8, 8)
    )

    style.map(
        "Treeview",
        background=[
            ("selected", "#DBEAFE")
        ],
        foreground=[
            ("selected", TEXTO)
        ]
    )

    # ========================================================
    # CABEÇALHO
    # ========================================================

    cabecalho = tk.Frame(
        root,
        bg=FUNDO
    )

    cabecalho.pack(
        fill="x",
        padx=28,
        pady=(24, 12)
    )

    esquerda = tk.Frame(
        cabecalho,
        bg=FUNDO
    )

    esquerda.pack(
        side="left",
        fill="x",
        expand=True
    )

    tk.Label(
        esquerda,
        text="Controle de Estoque",
        bg=FUNDO,
        fg=TEXTO,
        font=("Segoe UI", 20, "bold")
    ).pack(
        anchor="w"
    )

    tk.Label(
        esquerda,
        text="Restaurante",
        bg=FUNDO,
        fg=TEXTO_SECUNDARIO,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(2, 0)
    )

    direita = tk.Frame(
        cabecalho,
        bg=FUNDO
    )

    direita.pack(
        side="right"
    )

    criar_botao_arredondado(
        direita,
        "← Voltar ao painel",
        voltar_painel,
        largura=170,
        altura=40
    )

    # ========================================================
    # ÁREA PRINCIPAL
    # ========================================================

    area = tk.Frame(
        root,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1
    )

    area.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=(4, 24)
    )

    notebook = ttk.Notebook(
        area,
        style="Restaurante.TNotebook"
    )

    notebook.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=12
    )

    # ========================================================
    # ABAS
    # ========================================================

    criar_aba_notas(
        notebook,
        root
    )

    criar_aba_produtos(
        notebook,
        root
    )

    criar_aba_saidas(
        notebook,
        root
    )

    criar_aba_relatorios(
        notebook,
        root
    )

    # ========================================================
    # FECHAMENTO
    # ========================================================

    root.protocol(
        "WM_DELETE_WINDOW",
        fechar
    )

    return root