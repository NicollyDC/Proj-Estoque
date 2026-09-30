import tkinter as tk
from tkinter import ttk, messagebox

from estoque_restaurante.app_state import salvar, tem_alteracoes

from estoque_restaurante.ui.notas import criar_aba_notas
from estoque_restaurante.ui.produtos import criar_aba_produtos
from estoque_restaurante.ui.saidas import criar_aba_saidas
from estoque_restaurante.ui.relatorios import criar_aba_relatorios


def salvar_com_mensagem():
    salvar()
    messagebox.showinfo("Salvar", "Alterações salvas com sucesso!")


def fechar():
    if tem_alteracoes():
        resp = messagebox.askyesnocancel(
            "Salvar alterações",
            "Deseja salvar antes de sair?"
        )

        if resp is None:
            return

        if resp:
            salvar_com_mensagem()

    root.destroy()


root = tk.Tk()

root.title("Controle de Estoque - Restaurante")
root.geometry("1100x620")

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

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

criar_aba_notas(notebook, root)
criar_aba_produtos(notebook, root)
criar_aba_saidas(notebook, root)
criar_aba_relatorios(notebook, root)

root.protocol("WM_DELETE_WINDOW", fechar)

root.mainloop()