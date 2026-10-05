import tkinter as tk
from tkinter import ttk, messagebox


# --------------------------------------------------
# ABRIR SISTEMAS
# --------------------------------------------------
def abrir_hotel():
    from estoque_hotel.main import criar_janela_hotel
    root.withdraw()
    criar_janela_hotel(root, ao_fechar=voltar_painel)


def abrir_restaurante():
    from estoque_restaurante.main import criar_janela_restaurante
    root.withdraw()
    criar_janela_restaurante(root, ao_fechar=voltar_painel)

def voltar_painel():
    root.deiconify()


def fechar():
    root.destroy()


# --------------------------------------------------
# JANELA PRINCIPAL
# --------------------------------------------------

root = tk.Tk()

root.title("Controle de Estoque")
root.geometry("500x300")
root.resizable(False, False)


# --------------------------------------------------
# ESTILO
# --------------------------------------------------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Title.TLabel",
    font=("Segoe UI", 20, "bold")
)

style.configure(
    "Subtitle.TLabel",
    font=("Segoe UI", 11)
)

style.configure(
    "System.TButton",
    font=("Segoe UI", 11, "bold"),
    padding=12
)


# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

titulo = ttk.Label(
    root,
    text="Controle de Estoque",
    style="Title.TLabel"
)

titulo.pack(pady=(35, 5))


subtitulo = ttk.Label(
    root,
    text="Selecione o estabelecimento",
    style="Subtitle.TLabel"
)

subtitulo.pack(pady=(0, 25))


# --------------------------------------------------
# BOTÕES
# --------------------------------------------------

frame = ttk.Frame(root)
frame.pack()


btn_hotel = ttk.Button(
    frame,
    text="🏨  Hotel",
    style="System.TButton",
    command=abrir_hotel
)

btn_hotel.grid(
    row=0,
    column=0,
    padx=10,
    ipadx=20
)


btn_restaurante = ttk.Button(
    frame,
    text="🍽️  Restaurante",
    style="System.TButton",
    command=abrir_restaurante
)

btn_restaurante.grid(
    row=0,
    column=1,
    padx=10,
    ipadx=20
)


# --------------------------------------------------
# FECHAR
# --------------------------------------------------

root.protocol(
    "WM_DELETE_WINDOW",
    fechar
)


root.mainloop()