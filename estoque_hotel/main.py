import tkinter as tk
from tkinter import ttk, messagebox

from estoque_hotel.app_state import salvar, tem_alteracoes

from estoque_hotel.ui.notas import criar_aba_notas
from estoque_hotel.ui.produtos import criar_aba_produtos
from estoque_hotel.ui.saidas import criar_aba_saidas
from estoque_hotel.ui.relatorios import criar_aba_relatorios


def criar_janela_hotel(painel, ao_fechar=None):
    root = tk.Toplevel(painel)

    root.title("Controle de Estoque - Hotel")
    root.geometry("1100x620")

    # --------------------------------------------------
    # SALVAR
    # --------------------------------------------------

    def salvar_com_mensagem():
        salvar()

        messagebox.showinfo(
            "Salvar",
            "Alterações salvas com sucesso!",
            parent=root
        )

    # --------------------------------------------------
    # FECHAR / VOLTAR
    # --------------------------------------------------

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

    # --------------------------------------------------
    # ESTILO
    # --------------------------------------------------

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        rowheight=26,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold")
    )

    style.configure(
        "TButton",
        padding=6
    )

    style.configure(
        "TNotebook.Tab",
        padding=(16, 8),
        font=("Segoe UI", 10, "bold")
    )

    # --------------------------------------------------
    # TOPO
    # --------------------------------------------------

    topo = ttk.Frame(root)
    topo.pack(
        fill="x",
        padx=10,
        pady=8
    )

    btn_voltar = ttk.Button(
        topo,
        text="← Voltar ao painel inicial",
        command=voltar_painel
    )

    btn_voltar.pack(
        side="left"
    )

    # --------------------------------------------------
    # ABAS
    # --------------------------------------------------

    notebook = ttk.Notebook(root)

    notebook.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 10)
    )

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

    # --------------------------------------------------
    # FECHAMENTO
    # --------------------------------------------------

    root.protocol(
        "WM_DELETE_WINDOW",
        fechar
    )

    return root