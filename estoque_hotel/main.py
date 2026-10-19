import tkinter as tk
from tkinter import ttk, messagebox
from ui import design_system as design

from estoque_hotel.app_state import salvar
from estoque_hotel.utils import ESTOQUE_SQL, fmt
from ui.design_system import dinheiro
from dados.hotel.database import q, sync_tracker
from ui.dashboard import criar_aba_dashboard
from ui.sidebar import criar_sidebar
from ui.usuarios import JanelaUsuarios
from sessao import sessao

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

    def fechar():
        salvar()
        root.destroy()
        if ao_fechar:
            ao_fechar()

    def voltar_painel():
        if not messagebox.askyesno(
            "Voltar ao painel",
            "Deseja voltar à tela inicial?\n\n"
            "As informações já gravadas no estoque do Hotel permanecem salvas.",
            parent=root
        ):
            return

        salvar()
        root.destroy()
        if ao_fechar:
            ao_fechar()

    area = tk.Frame(root, bg=FUNDO)
    area.pack(fill="both", expand=True)

    # ========================================================
    # ABAS
    # ========================================================

    notebook = ttk.Notebook(
        area,
        style="Hotel.TNotebook"
    )

    criar_sidebar(
        area, notebook, "Hotel", sessao.nome, sessao.perfil, voltar_painel,
        (lambda: JanelaUsuarios(root)) if sessao.tem_permissao("usuarios.visualizar") else None,
        "Hotel.TNotebook",
        sync_tracker,
    )

    notebook.pack(side="left", fill="both", expand=True, padx=18, pady=16)

    # ========================================================
    # VISÃO GERAL
    # ========================================================
    criar_aba_dashboard(notebook, q, ESTOQUE_SQL, dinheiro, fmt)

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

    design.configure_styles()
    return root
