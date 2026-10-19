import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from estoque_hotel.app_state import marcar_alteracao
from dados.hotel.database import q, run, execute, commit, rollback
from dados.estoque import calcular_quantidade_estoque, calcular_valor_unitario_estoque
from estoque_hotel.utils import today, estoque_produto

from estoque_hotel.front import (
    tree,
    buttons,
    form,
    sel,
    safe,
)

from estoque_hotel.ui.notas_detalhes import nota_win

from estoque_hotel.xml_import import (
    ler_xml_nfe,
    ler_xml_nfe_bytes,
)

from estoque_hotel.consulta_nfe import (
    consultar_nfe,
    validar_chave,
)

from estoque_hotel.config import CNPJ_ESTABELECIMENTO


# ============================================================
# CAMPOS
# ============================================================

NOTA_F = [
    ("numero", "Nº da nota", "entry", None),
    ("fornecedor", "Fornecedor", "entry", None),
    ("data", "Data (AAAA-MM-DD)", "entry", None),
    ("faturada", "Faturada", "check", None),
    ("data_fat", "Data do faturamento", "entry", None),
]


# ============================================================
# ESTADO DA ABA
# ============================================================

nt = None
busca = None
root_ref = None
status_nfe = None


# ============================================================
# UTILIDADES
# ============================================================

def nota_vals(r):
    df = (
        (r["data_fat"].strip() or today())
        if r["faturada"]
        else None
    )

    return (
        r["numero"].strip(),
        r["fornecedor"].strip(),
        r["data"].strip(),
        int(r["faturada"]),
        df,
    )


def normalizar_cnpj(cnpj):
    """
    Remove máscara e deixa somente números.
    """
    if not cnpj:
        return ""

    return "".join(
        c for c in str(cnpj)
        if c.isdigit()
    )


def mensagem_erro_operacao(erro):
    if isinstance(erro, (ValueError, RuntimeError)):
        return str(erro)
    return (
        "Não foi possível concluir a operação com esta NF-e. "
        "Confira os dados e tente novamente. Se o problema continuar, contate o suporte."
    )


def validar_destinatario(nota):
    """
    Confere se o CNPJ da NF-e pertence ao Hotel.
    """

    cnpj_xml = normalizar_cnpj(
        nota.get("destinatario_cnpj")
    )

    cnpj_hotel = normalizar_cnpj(
        CNPJ_ESTABELECIMENTO
    )

    if not cnpj_xml:
        raise RuntimeError(
            "A NF-e não possui CNPJ de destinatário."
        )

    if cnpj_xml != cnpj_hotel:

        destinatario = (
            nota.get("destinatario")
            or "não identificado"
        )

        raise RuntimeError(
            "Esta NF-e não pertence ao Hotel.\n\n"
            f"Destinatário encontrado:\n"
            f"{destinatario}\n"
            f"CNPJ: {cnpj_xml}\n\n"
            f"CNPJ esperado:\n"
            f"{cnpj_hotel}"
        )


# ============================================================
# IMPORTAÇÃO DA NF-E
# ============================================================

def conferir_nota(nota, itens, estabelecimento):
    total_itens = len(itens)
    msg = (
        f"Confira os dados desta NF-e antes de importar no {estabelecimento}.\n\n"
        f"Número: {nota.get('numero') or '-'}\n"
        f"Fornecedor: {nota.get('fornecedor') or '-'}\n"
        f"Destinatário: {nota.get('destinatario') or '-'}\n"
        f"CNPJ destinatário: {normalizar_cnpj(nota.get('destinatario_cnpj'))}\n"
        f"Data: {nota.get('data') or '-'}\n"
        f"Itens: {total_itens}\n\n"
        "Deseja importar esta nota?"
    )
    return messagebox.askyesno("Conferência da NF-e", msg, parent=root_ref)


def salvar_nota_importada(nota, itens):
    chave = (nota.get("chave") or "").strip()

    if chave:
        existente = q(
            "SELECT id, numero FROM notas WHERE chave=?",
            (chave,)
        )
        if existente:
            raise RuntimeError(
                "Esta nota fiscal já foi importada.\n\n"
                f"Nº da nota: {existente[0]['numero']}\n"
                f"Chave: {chave}"
            )

    try:
        cur = execute(
            """
            INSERT INTO notas(numero, fornecedor, data, chave)
            VALUES (?, ?, ?, ?)
            """,
            (
                nota["numero"],
                nota["fornecedor"],
                nota["data"],
                chave or None,
            )
        )
        nid = cur.lastrowid
        ok = 0

        for item in itens:
            cod = item["codigo"]
            desc = item["descricao"]
            qtd = item["qtd"]
            un = item["unidade"]
            val = item["valor"]

            vinc = q(
                """
                SELECT * FROM vinculos
                WHERE fornecedor=? AND cod_forn=?
                """,
                (nota["fornecedor"], cod)
            )

            if vinc:
                pid = vinc[0]["produto_id"]
                fator = vinc[0]["fator"] or 1
                ok += 1
            else:
                pid = None
                fator = 1

            qtd_estoque = calcular_quantidade_estoque(qtd, fator)
            valor_unit = calcular_valor_unitario_estoque(val, qtd_estoque)

            execute(
                """
                INSERT INTO itens(
                    nota_id, cod_forn, descricao, qtd, unidade,
                    produto_id, fator, qtd_estoque, valor_total, valor_unit
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (nid, cod, desc, qtd, un, pid, fator, qtd_estoque, val, valor_unit)
            )

        commit()
        return nid, len(itens), ok

    except Exception:
        rollback()
        raise


# ============================================================
# REFRESH
# ============================================================

def nota_refresh():

    if nt is None or busca is None:
        return

    nt.delete(
        *nt.get_children()
    )

    for r in q(
        """
        SELECT n.*,

        (SELECT COUNT(*)
         FROM itens
         WHERE nota_id=n.id) AS qi,

        (SELECT COUNT(*)
         FROM itens
         WHERE nota_id=n.id
           AND produto_id IS NULL) AS sv

        FROM notas n

        WHERE numero LIKE ?

        ORDER BY data DESC, id DESC
        """,
        (
            f"%{busca.get().strip()}%",
        )
    ):

        fat = (
            f"Faturada em {r['data_faturamento'] or '-'}"
            if r["faturada"]
            else "Não faturada"
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


# ============================================================
# CRUD
# ============================================================

@safe
def nota_nova():

    r = form(
        root_ref,
        "Nova nota",
        NOTA_F,
        {
            "data": today()
        }
    )

    if r and r["numero"].strip():

        cur = run(
            """
            INSERT INTO notas(
                numero,
                fornecedor,
                data,
                faturada,
                data_faturamento
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            nota_vals(r)
        )

        nota_refresh()

        marcar_alteracao()

        nota_win(
            root_ref,
            cur.lastrowid
        )


def nota_abrir(event=None):

    nid = sel(nt)

    if nid:

        nota_win(
            root_ref,
            nid
        )


@safe
def nota_excluir():

    nid = sel(nt)

    if nid and messagebox.askyesno(
        "Excluir nota",
        "Excluir esta nota e todos os itens dela?\n\n"
        "O estoque dos produtos vinculados será reduzido.",
        parent=root_ref
    ):
        itens = q(
            """
            SELECT produto_id, SUM(COALESCE(qtd_estoque, 0)) AS qtd_estoque
            FROM itens
            WHERE nota_id=? AND produto_id IS NOT NULL
            GROUP BY produto_id
            """,
            (nid,)
        )
        for item in itens:
            atual = estoque_produto(item["produto_id"])
            if atual - (item["qtd_estoque"] or 0) < -0.0001:
                messagebox.showerror(
                    "Não é possível excluir",
                    "Esta nota não pode ser excluída porque o estoque "
                    "ficaria negativo. Existem saídas que usam esses produtos.",
                    parent=root_ref
                )
                return

        run("DELETE FROM notas WHERE id=?", (nid,))
        nota_refresh()
        marcar_alteracao()


# ============================================================
# IMPORTAÇÃO XML
# ============================================================

@safe
def nota_importar_xml():

    path = filedialog.askopenfilename(
        title="Escolha o XML da NF-e",
        filetypes=[
            ("XML", "*.xml")
        ]
    )

    if not path:
        return

    try:

        if status_nfe is not None:
            status_nfe.set("Lendo os dados da NF-e…")
            root_ref.update_idletasks()

        nota, itens = ler_xml_nfe(
            path
        )

        validar_destinatario(
            nota
        )

        if status_nfe is not None:
            status_nfe.set("NF-e encontrada. Confira os dados antes de importar.")

        if not conferir_nota(nota, itens, "Hotel"):
            return

        nid, total, ok = salvar_nota_importada(
            nota,
            itens
        )

    except Exception as ex:

        if status_nfe is not None:
            status_nfe.set("Não foi possível ler esta NF-e.")

        messagebox.showerror(
            "Erro na importação",
            mensagem_erro_operacao(ex)
        )

        return

    marcar_alteracao()

    nota_refresh()

    messagebox.showinfo(
        "Importação concluída",
        f"{total} itens foram importados.\n"
        f"Itens vinculados automaticamente: {ok}.\n"
        f"Itens que precisam de vínculo: {total - ok}."
    )

    nota_win(
        root_ref,
        nid,
        on_close=nota_refresh
    )


# ============================================================
# CONSULTA PELA CHAVE
# ============================================================

@safe
def nota_consultar_chave():

    chave = simpledialog.askstring(
        "Consultar NF-e",
        "Digite a chave de acesso da NF-e:\n"
        "(44 dígitos)",
        parent=root_ref
    )

    if chave is None:
        return

    try:

        chave = validar_chave(
            chave
        )

    except ValueError as ex:

        messagebox.showerror(
            "Chave inválida",
            str(ex)
        )

        return

    # --------------------------------------------------------
    # DUPLICIDADE ANTES DA API
    # --------------------------------------------------------

    existente = q(
        """
        SELECT id, numero
        FROM notas
        WHERE chave=?
        """,
        (chave,)
    )

    if existente:

        messagebox.showwarning(
            "Nota já importada",
            "Esta NF-e já está cadastrada no estoque.\n\n"
            f"Nº da nota: {existente[0]['numero']}"
        )

        return

    try:

        if status_nfe is not None:
            status_nfe.set("Consultando NF-e…")
            root_ref.update_idletasks()

        # ----------------------------------------------------
        # CONSULTA A API
        # ----------------------------------------------------

        xml_bytes = consultar_nfe(
            chave
        )

        # ----------------------------------------------------
        # INTERPRETA O XML EM MEMÓRIA
        # ----------------------------------------------------

        nota, itens = ler_xml_nfe_bytes(
            xml_bytes
        )

        # ----------------------------------------------------
        # CONFERE A CHAVE RETORNADA
        # ----------------------------------------------------

        chave_xml = (
            nota.get("chave") or ""
        ).strip()

        if chave_xml != chave:

            raise RuntimeError(
                "A chave retornada pela consulta "
                "não corresponde à chave informada."
            )

        # ----------------------------------------------------
        # CONFERE DESTINATÁRIO
        # ----------------------------------------------------

        validar_destinatario(
            nota
        )

        if status_nfe is not None:
            status_nfe.set("NF-e encontrada. Confira os dados antes de importar.")

        if not conferir_nota(nota, itens, "Hotel"):
            return

        nid, total, ok = salvar_nota_importada(
            nota,
            itens
        )

    except Exception as ex:

        if status_nfe is not None:
            status_nfe.set("Não foi possível consultar esta NF-e.")

        messagebox.showerror(
            "Erro na consulta",
            mensagem_erro_operacao(ex)
        )

        return

    marcar_alteracao()

    nota_refresh()

    messagebox.showinfo(
        "NF-e importada",
        f"Nota nº {nota['numero']} importada com sucesso.\n\n"
        f"Fornecedor: {nota['fornecedor']}\n"
        f"Data: {nota['data']}\n"
        f"Itens: {total}\n"
        f"Itens vinculados automaticamente: {ok}\n"
        f"Itens sem vínculo: {total - ok}"
    )

    nota_win(
        root_ref,
        nid,
        on_close=nota_refresh
    )


# ============================================================
# ABA
# ============================================================

def criar_aba_notas(notebook, root):

    global nt, busca, root_ref, status_nfe

    root_ref = root

    aba = ttk.Frame(
        notebook
    )

    notebook.add(
        aba,
        text="▤  Notas"
    )

    # --------------------------------------------------------
    # BUSCA
    # --------------------------------------------------------

    busca = tk.StringVar()

    barra = ttk.Frame(
        aba
    )

    barra.pack(
        fill="x",
        padx=6,
        pady=4
    )

    status_nfe = tk.StringVar(value="Consulte pela chave ou importe um arquivo XML.")
    ttk.Label(barra, textvariable=status_nfe, style="AppSubtitle.TLabel").pack(side="right", padx=8)

    ttk.Label(
        barra,
        text="Buscar nº da nota:"
    ).pack(
        side="left"
    )

    e = ttk.Entry(
        barra,
        textvariable=busca,
        width=20
    )

    e.pack(
        side="left",
        padx=4
    )

    ttk.Button(
        barra,
        text="Buscar",
        command=nota_refresh
    ).pack(
        side="left"
    )

    ttk.Button(
        barra,
        text="Limpar",
        command=lambda: (
            busca.set(""),
            nota_refresh()
        )
    ).pack(
        side="left",
        padx=3
    )

    e.bind(
        "<Return>",
        lambda ev: nota_refresh()
    )

    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

    nt = tree(
        aba,
        [
            ("numero", "Nº da nota", 120),
            ("forn", "Fornecedor", 250),
            ("data", "Data", 100),
            ("fat", "Faturamento", 160),
            ("itens", "Itens", 60),
            ("sem", "Sem vínculo", 90),
        ]
    )

    # --------------------------------------------------------
    # BOTÕES
    # --------------------------------------------------------

    buttons(
        aba,
        [
            (
                "Consultar NF-e",
                nota_consultar_chave
            ),
            (
                "Importar XML",
                nota_importar_xml
            ),
            (
                "Nova nota",
                nota_nova
            ),
            (
                "Abrir",
                nota_abrir
            ),
            (
                "Excluir",
                nota_excluir
            ),
        ]
    )

    nt.bind(
        "<Double-1>",
        nota_abrir
    )

    nota_refresh()

    return aba
