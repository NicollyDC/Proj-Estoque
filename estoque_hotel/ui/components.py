import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox
import functools
import traceback


def form(parent, title, fields, values=None):
    """
    Cria um formulário dinâmico.

    fields = (chave, rótulo, tipo, opções)
    tipo: entry | combo | check

    Retorna um dicionário ou None.
    """
    values = values or {}

    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()

    variaveis = {}
    resultado = {}

    for i, (key, label, kind, options) in enumerate(fields):
        ttk.Label(win, text=label).grid(
            row=i, column=0, sticky="w", padx=8, pady=3
        )

        valor = values.get(key)

        if kind == "check":
            var = tk.IntVar(value=int(valor or 0))
            widget = ttk.Checkbutton(win, variable=var)

        elif kind in ("combo", "combo_ro"):
            var = tk.StringVar(value=valor or "")
            widget = ttk.Combobox(
                win,
                textvariable=var,
                values=options,
                width=38,
                state="readonly" if kind == "combo_ro" else "normal"
            )

        else:
            var = tk.StringVar(
                value="" if valor is None else str(valor)
            )
            widget = ttk.Entry(
                win,
                textvariable=var,
                width=40
            )

        widget.grid(
            row=i,
            column=1,
            padx=8,
            pady=3,
            sticky="w"
        )

        variaveis[key] = var

    def salvar():
        resultado.update({
            k: v.get()
            for k, v in variaveis.items()
        })
        win.destroy()

    ttk.Button(
        win,
        text="Salvar",
        command=salvar
    ).grid(
        row=len(fields),
        column=0,
        columnspan=2,
        pady=8
    )

    win.wait_window()

    return resultado or None


def tree(parent, cols):
    """
    Cria um Treeview com scrollbar.

    cols = [(chave, título, largura)]
    """
    frame = ttk.Frame(parent)
    frame.pack(
        fill="both",
        expand=True,
        padx=6,
        pady=6
    )

    tabela = ttk.Treeview(
        frame,
        columns=[c[0] for c in cols],
        show="headings",
        selectmode="browse"
    )

    for key, title, width in cols:
        tabela.heading(
            key,
            text=title
        )
        tabela.column(
            key,
            width=width
        )

    barra = ttk.Scrollbar(
        frame,
        command=tabela.yview
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


def buttons(parent, items):
    """
    Cria uma barra de botões.

    items = [(texto, função)]
    """
    frame = ttk.Frame(parent)
    frame.pack(
        fill="x",
        padx=6,
        pady=4
    )

    for text, command in items:
        ttk.Button(
            frame,
            text=text,
            command=command
        ).pack(
            side="left",
            padx=3
        )

    return frame


def sel(treeview):
    """
    Retorna o ID da linha selecionada.
    """
    selecionado = treeview.selection()

    if not selecionado:
        messagebox.showinfo(
            "Atenção",
            "Selecione uma linha primeiro."
        )
        return None

    return int(selecionado[0])


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