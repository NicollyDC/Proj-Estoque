import tkinter as tk
from tkinter import ttk

from login import iniciar_login
from sessao import sessao
from ui.usuarios import JanelaUsuarios


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

PERIGO = "#DC2626"


# ============================================================
# FUNÇÕES VISUAIS
# ============================================================

def desenhar_retangulo_arredondado(
    canvas,
    x1,
    y1,
    x2,
    y2,
    raio,
    preenchimento
):
    canvas.create_rectangle(
        x1 + raio,
        y1,
        x2 - raio,
        y2,
        fill=preenchimento,
        outline=""
    )

    canvas.create_rectangle(
        x1,
        y1 + raio,
        x2,
        y2 - raio,
        fill=preenchimento,
        outline=""
    )

    canvas.create_arc(
        x1,
        y1,
        x1 + raio * 2,
        y1 + raio * 2,
        start=90,
        extent=90,
        fill=preenchimento,
        outline=""
    )

    canvas.create_arc(
        x2 - raio * 2,
        y1,
        x2,
        y1 + raio * 2,
        start=0,
        extent=90,
        fill=preenchimento,
        outline=""
    )

    canvas.create_arc(
        x1,
        y2 - raio * 2,
        x1 + raio * 2,
        y2,
        start=180,
        extent=90,
        fill=preenchimento,
        outline=""
    )

    canvas.create_arc(
        x2 - raio * 2,
        y2 - raio * 2,
        x2,
        y2,
        start=270,
        extent=90,
        fill=preenchimento,
        outline=""
    )


def criar_botao_arredondado(
    parent,
    texto,
    comando,
    largura=150,
    altura=40,
    cor=PRINCIPAL,
    cor_hover=PRINCIPAL_HOVER,
    cor_texto=BRANCO,
    raio=10,
    fonte=("Segoe UI", 10, "bold"),
    fundo=FUNDO
):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=fundo,
        highlightthickness=0,
        bd=0
    )

    def desenhar(cor_atual):
        canvas.delete("all")

        desenhar_retangulo_arredondado(
            canvas,
            0,
            0,
            largura,
            altura,
            raio,
            cor_atual
        )

        canvas.create_text(
            largura / 2,
            altura / 2,
            text=texto,
            fill=cor_texto,
            font=fonte
        )

    desenhar(cor)

    canvas.bind(
        "<Enter>",
        lambda event: desenhar(cor_hover)
    )

    canvas.bind(
        "<Leave>",
        lambda event: desenhar(cor)
    )

    canvas.bind(
        "<Button-1>",
        lambda event: comando()
    )

    return canvas


def criar_card_arredondado(
    parent,
    largura,
    altura,
    raio=16
):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=FUNDO,
        highlightthickness=0,
        bd=0
    )

    desenhar_retangulo_arredondado(
        canvas,
        1,
        1,
        largura - 1,
        altura - 1,
        raio,
        BRANCO
    )

    conteudo = tk.Frame(
        canvas,
        bg=BRANCO
    )

    canvas.create_window(
        largura / 2,
        altura / 2,
        window=conteudo,
        width=largura - 4,
        height=altura - 4
    )

    return canvas, conteudo


# ============================================================
# AÇÕES
# ============================================================

def abrir_hotel():
    from estoque_hotel.main import criar_janela_hotel

    root.withdraw()

    criar_janela_hotel(
        root,
        ao_fechar=voltar_painel
    )


def abrir_restaurante():
    from estoque_restaurante.main import criar_janela_restaurante

    root.withdraw()

    criar_janela_restaurante(
        root,
        ao_fechar=voltar_painel
    )


def abrir_usuarios():
    if not sessao.tem_permissao("usuarios.visualizar"):
        return

    JanelaUsuarios(root)


def logout():
    sessao.encerrar()

    btn_usuarios.pack_forget()

    root.withdraw()

    iniciar_login(
        root,
        criar_painel
    )


def voltar_painel():
    root.deiconify()


def criar_painel(usuario):
    sessao.iniciar(usuario)

    titulo_usuario.config(
        text=sessao.nome
    )

    perfil_usuario.config(
        text=sessao.perfil.capitalize()
    )

    if sessao.tem_permissao("usuarios.visualizar"):
        btn_usuarios.pack(
            fill="x",
            pady=(0, 8)
        )
    else:
        btn_usuarios.pack_forget()

    root.deiconify()


def fechar():
    root.destroy()


# ============================================================
# JANELA PRINCIPAL
# ============================================================

root = tk.Tk()

root.title("Controle de Estoque")
root.geometry("840x570")
root.resizable(False, False)
root.configure(bg=FUNDO)


# ============================================================
# ESTILO
# ============================================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TFrame",
    background=FUNDO
)

style.configure(
    "Title.TLabel",
    background=FUNDO,
    foreground=TEXTO,
    font=("Segoe UI", 23, "bold")
)

style.configure(
    "Subtitle.TLabel",
    background=FUNDO,
    foreground=TEXTO_SECUNDARIO,
    font=("Segoe UI", 10)
)

style.configure(
    "Section.TLabel",
    background=FUNDO,
    foreground=TEXTO,
    font=("Segoe UI", 12, "bold")
)

style.configure(
    "User.TLabel",
    background=BRANCO,
    foreground=TEXTO,
    font=("Segoe UI", 11, "bold")
)

style.configure(
    "Profile.TLabel",
    background=BRANCO,
    foreground=TEXTO_SECUNDARIO,
    font=("Segoe UI", 9)
)

style.configure(
    "CardTitle.TLabel",
    background=BRANCO,
    foreground=TEXTO,
    font=("Segoe UI", 15, "bold")
)

style.configure(
    "CardSubtitle.TLabel",
    background=BRANCO,
    foreground=TEXTO_SECUNDARIO,
    font=("Segoe UI", 9)
)


# ============================================================
# CABEÇALHO
# ============================================================

header = ttk.Frame(root)

header.pack(
    fill="x",
    padx=45,
    pady=(28, 0)
)

titulo = ttk.Label(
    header,
    text="Controle de Estoque",
    style="Title.TLabel"
)

titulo.pack(anchor="w")

subtitulo = ttk.Label(
    header,
    text="Selecione o estabelecimento para continuar",
    style="Subtitle.TLabel"
)

subtitulo.pack(
    anchor="w",
    pady=(3, 0)
)


# ============================================================
# USUÁRIO
# ============================================================

usuario_card, usuario_conteudo = criar_card_arredondado(
    root,
    largura=750,
    altura=72,
    raio=14
)

usuario_card.pack(
    padx=45,
    pady=(20, 20)
)

usuario_interno = tk.Frame(
    usuario_conteudo,
    bg=BRANCO
)

usuario_interno.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=12
)

titulo_usuario = ttk.Label(
    usuario_interno,
    text="",
    style="User.TLabel"
)

titulo_usuario.pack(
    anchor="w"
)

perfil_usuario = ttk.Label(
    usuario_interno,
    text="",
    style="Profile.TLabel"
)

perfil_usuario.pack(
    anchor="w",
    pady=(2, 0)
)


# ============================================================
# ESTABELECIMENTOS
# ============================================================

ttk.Label(
    root,
    text="Estabelecimentos",
    style="Section.TLabel"
).pack(
    anchor="w",
    padx=45
)

frame_estabelecimentos = ttk.Frame(root)

frame_estabelecimentos.pack(
    fill="x",
    padx=45,
    pady=(10, 0)
)


# ============================================================
# HOTEL
# ============================================================

card_hotel, conteudo_hotel = criar_card_arredondado(
    frame_estabelecimentos,
    largura=365,
    altura=170,
    raio=16
)

card_hotel.grid(
    row=0,
    column=0,
    padx=(0, 8)
)

titulo_hotel = ttk.Label(
    conteudo_hotel,
    text="🏨  Hotel",
    style="CardTitle.TLabel"
)

titulo_hotel.pack(
    anchor="w",
    padx=20,
    pady=(19, 3)
)

descricao_hotel = ttk.Label(
    conteudo_hotel,
    text="Controle de estoque do hotel",
    style="CardSubtitle.TLabel"
)

descricao_hotel.pack(
    anchor="w",
    padx=20
)

btn_hotel = criar_botao_arredondado(
    conteudo_hotel,
    "Acessar hotel",
    abrir_hotel,
    largura=325,
    altura=42,
    fundo=BRANCO
)

btn_hotel.pack(
    padx=20,
    pady=(16, 0)
)


# ============================================================
# RESTAURANTE
# ============================================================

card_restaurante, conteudo_restaurante = criar_card_arredondado(
    frame_estabelecimentos,
    largura=365,
    altura=170,
    raio=16
)

card_restaurante.grid(
    row=0,
    column=1,
    padx=(8, 0)
)

titulo_restaurante = ttk.Label(
    conteudo_restaurante,
    text="🍽️  Restaurante",
    style="CardTitle.TLabel"
)

titulo_restaurante.pack(
    anchor="w",
    padx=20,
    pady=(19, 3)
)

descricao_restaurante = ttk.Label(
    conteudo_restaurante,
    text="Controle de estoque do restaurante",
    style="CardSubtitle.TLabel"
)

descricao_restaurante.pack(
    anchor="w",
    padx=20
)

btn_restaurante = criar_botao_arredondado(
    conteudo_restaurante,
    "Acessar restaurante",
    abrir_restaurante,
    largura=325,
    altura=42,
    fundo=BRANCO
)

btn_restaurante.pack(
    padx=20,
    pady=(16, 0)
)


# ============================================================
# ÁREA ADMINISTRATIVA
# ============================================================

frame_admin = ttk.Frame(root)

frame_admin.pack(
    fill="x",
    padx=45,
    pady=(16, 0)
)

btn_usuarios = criar_botao_arredondado(
    frame_admin,
    "👥  Gerenciar usuários",
    abrir_usuarios,
    largura=750,
    altura=42,
    cor=BRANCO,
    cor_hover="#F3F4F6",
    cor_texto=TEXTO,
    raio=10,
    fonte=("Segoe UI", 9, "bold"),
    fundo=FUNDO
)


# ============================================================
# RODAPÉ
# ============================================================

footer = ttk.Frame(root)

footer.pack(
    fill="x",
    side="bottom",
    padx=45,
    pady=14
)

btn_sair = criar_botao_arredondado(
    footer,
    "Sair",
    logout,
    largura=82,
    altura=36,
    cor=BRANCO,
    cor_hover="#FEF2F2",
    cor_texto=PERIGO,
    raio=9,
    fonte=("Segoe UI", 9, "bold"),
    fundo=FUNDO
)

btn_sair.pack(
    side="right"
)


# ============================================================
# EVENTOS
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    fechar
)


# ============================================================
# LOGIN
# ============================================================

root.withdraw()

iniciar_login(
    root,
    criar_painel
)

root.mainloop()