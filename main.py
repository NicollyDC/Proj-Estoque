import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


def abrir_hotel():
    abrir_sistema("estoque_hotel.main")


def abrir_restaurante():
    abrir_sistema("estoque_restaurante.main")


def abrir_sistema(modulo):
    try:
        subprocess.Popen([
            sys.executable,
            "-m",
            modulo
        ])

        root.destroy()

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Não foi possível abrir o sistema.\n\n{e}"
        )


root = tk.Tk()

root.title("Controle de Estoque")
root.geometry("500x300")
root.resizable(False, False)


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


# ---------------- TÍTULO ---------------- #

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


# ---------------- BOTÕES ---------------- #

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


# ---------------- FECHAR ---------------- #

root.mainloop()