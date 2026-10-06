import tkinter as tk
from tkinter import ttk, messagebox

from estoque_hotel.app_state import (
    salvar,
    tem_alteracoes
)

from estoque_hotel.ui.notas import (
    criar_aba_notas
)

from estoque_hotel.ui.produtos import (
    criar_aba_produtos
)

from estoque_hotel.ui.saidas import (
    criar_aba_saidas
)

from estoque_hotel.ui.relatorios import (
    criar_aba_relatorios
)

from estoque_hotel.front import (
    FUNDO,
    BRANCO,
    BORDA,
    criar_botao_arredondado
)


# ============================================================
# JANELA DO HOTEL
# ============================================================

def criar_janela_hotel(painel, ao_fechar=None):

    root = tk.Toplevel(painel)

    root.title(
        "Controle de Estoque - Hotel"
    )

    root.geometry(
        "1150x680"
    )

    root.minsize(
        1000,
        600
    )

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

    # --------------------------------------------------------
    # LADO ESQUERDO
    # --------------------------------------------------------

    esquerda = tk.Frame(
        cabecalho,
        bg=FUNDO
    )

    esquerda.pack(
        side="left",
        fill="x",
        expand=True
    )

    ttk.Label(
        esquerda,
        text="Controle de Estoque",
        style="AppTitle.TLabel"
    ).pack(
        anchor="w"
    )

    ttk.Label(
        esquerda,
        text="Hotel",
        style="AppSubtitle.TLabel"
    ).pack(
        anchor="w"
    )

    # --------------------------------------------------------
    # LADO DIREITO
    # --------------------------------------------------------

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
    ).pack()

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

    # ========================================================
    # ABAS
    # ========================================================

    notebook = ttk.Notebook(
        area,
        style="Hotel.TNotebook"
    )

    notebook.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=12
    )

    # ========================================================
    # NOTAS
    # ========================================================

    criar_aba_notas(
        notebook,
        root
    )

    # ========================================================
    # PRODUTOS
    # ========================================================

    criar_aba_produtos(
        notebook,
        root
    )

    # ========================================================
    # SAÍDAS
    # ========================================================

    criar_aba_saidas(
        notebook,
        root
    )

    # ========================================================
    # RELATÓRIOS
    # ========================================================

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