import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox, filedialog
from estoque.app_state import marcar_alteracao
from estoque.database import q, run
from estoque.utils import today
from estoque.ui.components import tree, buttons, form, sel, safe
from estoque.ui.notas_detalhes import nota_win

# ---------------- CAMPOS ---------------- #

NOTA_F = [
    ("numero", "Nº da nota", "entry", None),
    ("fornecedor", "Fornecedor", "entry", None),
    ("data", "Data (AAAA-MM-DD)", "entry", None),
    ("faturada", "Faturada?", "check", None),
    ("data_fat", "Data do faturamento", "entry", None),
]

nt = None
busca = None
root_ref = None


# ---------------- UTILIDADES ---------------- #

def nota_vals(r):
    df = (r["data_fat"].strip() or today()) if r["faturada"] else None

    return (
        r["numero"].strip(),
        r["fornecedor"].strip(),
        r["data"].strip(),
        int(r["faturada"]),
        df,
    )


def xml_nfe(path):
    raiz = ET.parse(path).getroot()

    for el in raiz.iter():
        el.tag = el.tag.split("}")[-1]

    inf = raiz.find(".//infNFe")

    if inf is None:
        raise RuntimeError("O arquivo não parece ser um XML de NF-e.")

    def g(base, tag):
        return (base.findtext(tag) or "").strip() if base is not None else ""

    ide = inf.find("ide")
    emit = inf.find("emit")

    nota = {
        "numero": g(ide, "nNF"),
        "fornecedor": g(emit, "xNome"),
        "data": (g(ide, "dhEmi") or g(ide, "dEmi"))[:10],
        "chave": (inf.get("Id") or "").replace("NFe", ""),
    }

    itens = []

    for det in inf.findall("det"):
        prod = det.find("prod")

        itens.append((
            g(prod, "cProd"),
            g(prod, "xProd"),
            float(g(prod, "qCom") or 0),
            g(prod, "uCom"),
            float(g(prod, "vProd") or 0),
        ))

    return nota, itens


# ---------------- REFRESH ---------------- #

def nota_refresh():
    nt.delete(*nt.get_children())

    for r in q("""
        SELECT n.*,
        (SELECT COUNT(*) FROM itens WHERE nota_id=n.id) AS qi,
        (SELECT COUNT(*) FROM itens
            WHERE nota_id=n.id AND produto_id IS NULL) AS sv
        FROM notas n
        WHERE numero LIKE ?
        ORDER BY data DESC, id DESC
    """, (f"%{busca.get().strip()}%",)):

        fat = (
            "Sim - " + (r["data_faturamento"] or "")
            if r["faturada"]
            else "Não"
        )

        nt.insert(
            "",
            "end",
            iid=str(r["id"]),
            values=(
                r["numero"],
                r["fornecedor"],
                r["data"],
                fat,
                r["qi"],
                r["sv"],
            ),
        )


# ---------------- CRUD ---------------- #

@safe
def nota_nova():
    r = form(root_ref, "Nova nota", NOTA_F, {"data": today()})

    if r and r["numero"].strip():

        cur = run("""
            INSERT INTO notas
            (numero, fornecedor, data, faturada, data_faturamento)
            VALUES (?, ?, ?, ?, ?)
        """, nota_vals(r))

        nota_refresh()
        marcar_alteracao()
        nota_win(root_ref, cur.lastrowid)






def nota_abrir(event=None):
    nid = sel(nt)

    if nid:
        nota_win(root_ref, nid)


@safe
def nota_excluir():
    nid = sel(nt)

    if nid and messagebox.askyesno(
        "Excluir",
        "Excluir a nota e todos os itens dela?"
    ):
        run("DELETE FROM notas WHERE id=?", (nid,))
        nota_refresh()
        marcar_alteracao()


# ---------------- IMPORTAÇÃO XML ---------------- #

@safe
def nota_importar_xml():
    path = filedialog.askopenfilename(
        title="Escolha o XML da NF-e",
        filetypes=[("XML", "*.xml")]
    )

    if not path:
        return

    try:
        nota, itens = xml_nfe(path)

    except (ET.ParseError, RuntimeError) as ex:
        messagebox.showerror("Erro", f"Não consegui ler o XML:\n{ex}")
        return

    # Evita importar a mesma NF duas vezes
    if nota["chave"] and q(
        "SELECT 1 FROM notas WHERE chave=?",
        (nota["chave"],)
    ):
        messagebox.showwarning(
            "Nota já importada",
            "Esta nota fiscal já foi importada."
        )
        return

    # Cabeçalho da nota
    cur = run("""
        INSERT INTO notas(numero, fornecedor, data, chave)
        VALUES (?, ?, ?, ?)
    """, (
        nota["numero"],
        nota["fornecedor"],
        nota["data"],
        nota["chave"],
    ))

    nid = cur.lastrowid
    ok = 0

    # Itens da nota
    for cod, desc, qtd, un, val in itens:

        vinc = q("""
            SELECT *
            FROM vinculos
            WHERE fornecedor=? AND cod_forn=?
        """, (nota["fornecedor"], cod))

        if vinc:
            pid = vinc[0]["produto_id"]
            fator = vinc[0]["fator"]
            ok += 1
        else:
            pid = None
            fator = 1

        # Conversão para unidade de estoque
        qtd_estoque = qtd * fator

        # Valor unitário automático
        valor_unit = (
            round(val / qtd_estoque, 4)
            if qtd_estoque > 0 else 0
        )

        run("""
            INSERT INTO itens(
                nota_id,
                cod_forn,
                descricao,
                qtd,
                unidade,
                produto_id,
                fator,
                qtd_estoque,
                valor_total,
                valor_unit
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nid,
            cod,
            desc,
            qtd,
            un,
            pid,
            fator,
            qtd_estoque,
            val,
            valor_unit,
        ))

    nota_refresh()

    messagebox.showinfo(
        "Importação concluída",
        f"{len(itens)} itens importados.\n"
        f"{ok} vinculados automaticamente.\n"
        f"{len(itens)-ok} precisam de vínculo."
    )

    def _refresh():
        try:
            nota_refresh()
        except tk.TclError:
            pass

    nota_win(root_ref, nid, on_close=_refresh)

# ---------------- ABA ---------------- #

def criar_aba_notas(notebook, root):
    global nt, busca, root_ref

    root_ref = root

    aba = ttk.Frame(notebook)
    notebook.add(aba, text="Notas")

    busca = tk.StringVar()

    barra = ttk.Frame(aba)
    barra.pack(fill="x", padx=6, pady=4)

    ttk.Label(barra, text="Buscar nº da nota:").pack(side="left")

    e = ttk.Entry(barra, textvariable=busca, width=20)
    e.pack(side="left", padx=4)

    ttk.Button(
        barra,
        text="Buscar",
        command=nota_refresh
    ).pack(side="left")

    ttk.Button(
        barra,
        text="Limpar",
        command=lambda: (busca.set(""), nota_refresh())
    ).pack(side="left", padx=3)

    e.bind("<Return>", lambda ev: nota_refresh())

    nt = tree(aba, [
        ("numero", "Nº nota", 120),
        ("forn", "Fornecedor", 250),
        ("data", "Data", 100),
        ("fat", "Faturada", 160),
        ("itens", "Itens", 60),
        ("sem", "Sem vínculo", 90),
    ])

    buttons(aba, [
        ("Importar XML", nota_importar_xml),
        ("Nova nota", nota_nova),
        ("Abrir", nota_abrir),
        ("Excluir", nota_excluir),
    ])

    nt.bind("<Double-1>", nota_abrir)

    nota_refresh()

    return aba