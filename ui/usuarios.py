import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from dados.usuarios.database import q, run
from login import gerar_senha, usuario_valido, normalizar_usuario
from sessao import sessao


# ============================================================
# CORES
# ============================================================

FUNDO = "#F4F6F8"
BRANCO = "#FFFFFF"

TEXTO = "#1F2937"
SECUNDARIO = "#6B7280"

BORDA = "#E5E7EB"

AZUL = "#2563EB"
AZUL_HOVER = "#1D4ED8"

VERMELHO = "#DC2626"

CINZA = "#F3F4F6"
CINZA_HOVER = "#E5E7EB"


# ============================================================
# ELEMENTOS VISUAIS
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


def criar_botao(
    parent,
    texto,
    comando,
    largura=150,
    altura=40,
    cor=AZUL,
    hover=AZUL_HOVER,
    texto_cor=BRANCO,
    fundo=FUNDO
):
    canvas = tk.Canvas(
        parent,
        width=largura,
        height=altura,
        bg=fundo,
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    raio = 9

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
            fill=texto_cor,
            font=("Segoe UI", 9, "bold")
        )

    desenhar(cor)

    canvas.bind(
        "<Enter>",
        lambda event: desenhar(hover)
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


def criar_card(parent, largura, altura, raio=14):

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
# GERENCIAR USUÁRIOS
# ============================================================

class JanelaUsuarios:

    def __init__(self, parent):

        self.janela = tk.Toplevel(parent)

        self.janela.title("Gerenciar usuários")
        self.janela.geometry("780x520")
        self.janela.resizable(False, False)

        self.janela.configure(
            bg=FUNDO
        )

        self.janela.transient(parent)
        self.janela.grab_set()

        self.criar_interface()
        self.carregar_usuarios()

        self.centralizar()

    # --------------------------------------------------------
    # CENTRALIZAR
    # --------------------------------------------------------

    def centralizar(self):

        self.janela.update_idletasks()

        largura = 780
        altura = 520

        tela_largura = self.janela.winfo_screenwidth()
        tela_altura = self.janela.winfo_screenheight()

        x = (tela_largura - largura) // 2
        y = (tela_altura - altura) // 2

        self.janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------

    def criar_interface(self):

        # Cabeçalho
        header = tk.Frame(
            self.janela,
            bg=FUNDO
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 0)
        )

        tk.Label(
            header,
            text="Gerenciar usuários",
            bg=FUNDO,
            fg=TEXTO,
            font=("Segoe UI", 21, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Gerencie os acessos ao sistema.",
            bg=FUNDO,
            fg=SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

        # Card da tabela
        card, conteudo = criar_card(
            self.janela,
            710,
            300,
            raio=14
        )

        card.pack(
            padx=35,
            pady=(20, 15)
        )

        # Estilo da tabela
        style = ttk.Style(self.janela)

        style.configure(
            "Usuarios.Treeview",
            background=BRANCO,
            fieldbackground=BRANCO,
            foreground=TEXTO,
            rowheight=34,
            font=("Segoe UI", 9),
            borderwidth=0
        )

        style.configure(
            "Usuarios.Treeview.Heading",
            background="#F9FAFB",
            foreground=SECUNDARIO,
            font=("Segoe UI", 9, "bold"),
            padding=7,
            relief="flat"
        )

        style.map(
            "Usuarios.Treeview",
            background=[
                ("selected", "#DBEAFE")
            ],
            foreground=[
                ("selected", TEXTO)
            ]
        )

        colunas = (
            "id",
            "nome",
            "usuario",
            "perfil",
            "status"
        )

        tabela_frame = tk.Frame(
            conteudo,
            bg=BRANCO
        )

        tabela_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        self.tabela = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            style="Usuarios.Treeview",
            selectmode="browse"
        )

        configuracoes = {
            "id": ("ID", 45, "center"),
            "nome": ("Nome", 245, "w"),
            "usuario": ("Usuário", 165, "w"),
            "perfil": ("Perfil", 105, "center"),
            "status": ("Status", 90, "center")
        }

        for coluna, (
            titulo,
            largura,
            ancora
        ) in configuracoes.items():

            self.tabela.heading(
                coluna,
                text=titulo
            )

            self.tabela.column(
                coluna,
                width=largura,
                anchor=ancora
            )

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            tabela_frame,
            command=self.tabela.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tabela.configure(
            yscrollcommand=scrollbar.set
        )

        # Botões
        botoes = tk.Frame(
            self.janela,
            bg=FUNDO
        )

        botoes.pack(
            fill="x",
            padx=35
        )

        criar_botao(
            botoes,
            "+ Novo usuário",
            self.novo_usuario,
            largura=140,
            altura=40,
            fundo=FUNDO
        ).pack(
            side="left"
        )

        criar_botao(
            botoes,
            "Ativar",
            self.ativar_usuario,
            largura=82,
            altura=40,
            cor=CINZA,
            hover=CINZA_HOVER,
            texto_cor=TEXTO,
            fundo=FUNDO
        ).pack(
            side="left",
            padx=(7, 0)
        )

        criar_botao(
            botoes,
            "Desativar",
            self.desativar_usuario,
            largura=98,
            altura=40,
            cor=CINZA,
            hover="#FEE2E2",
            texto_cor=VERMELHO,
            fundo=FUNDO
        ).pack(
            side="left",
            padx=(7, 0)
        )

        criar_botao(
            botoes,
            "Redefinir senha",
            self.redefinir_senha,
            largura=125,
            altura=40,
            cor=CINZA,
            hover=CINZA_HOVER,
            texto_cor=TEXTO,
            fundo=FUNDO
        ).pack(
            side="left",
            padx=(7, 0)
        )

        criar_botao(
            botoes,
            "Fechar",
            self.janela.destroy,
            largura=78,
            altura=40,
            cor=BRANCO,
            hover=CINZA_HOVER,
            texto_cor=TEXTO,
            fundo=FUNDO
        ).pack(
            side="right"
        )

    # --------------------------------------------------------
    # SELEÇÃO
    # --------------------------------------------------------

    def usuario_selecionado(self):

        selecionado = self.tabela.selection()

        if not selecionado:

            messagebox.showwarning(
                "Usuário",
                "Selecione um usuário.",
                parent=self.janela
            )

            return None

        return self.tabela.item(
            selecionado[0]
        )["values"]

    # --------------------------------------------------------
    # LISTAGEM
    # --------------------------------------------------------

    def carregar_usuarios(self):

        self.tabela.delete(
            *self.tabela.get_children()
        )

        for usuario in q(
            """
            SELECT id, nome, usuario, perfil, ativo
            FROM usuarios
            ORDER BY nome
            """
        ):

            self.tabela.insert(
                "",
                "end",
                values=(
                    usuario["id"],
                    usuario["nome"],
                    usuario["usuario"],
                    usuario["perfil"].capitalize(),
                    "Ativo"
                    if usuario["ativo"]
                    else "Inativo"
                )
            )

    # --------------------------------------------------------
    # NOVO
    # --------------------------------------------------------

    def novo_usuario(self):

        if not sessao.tem_permissao(
            "usuarios.criar"
        ):

            messagebox.showwarning(
                "Acesso negado",
                "Você não tem permissão para criar usuários.",
                parent=self.janela
            )

            return

        JanelaNovoUsuario(
            self,
            self.carregar_usuarios
        )

    # --------------------------------------------------------
    # DESATIVAR
    # --------------------------------------------------------

    def desativar_usuario(self):

        if not sessao.tem_permissao(
            "usuarios.desativar"
        ):

            messagebox.showwarning(
                "Acesso negado",
                "Você não tem permissão para desativar usuários.",
                parent=self.janela
            )

            return

        dados = self.usuario_selecionado()

        if not dados:
            return

        usuario_id = int(dados[0])
        usuario = dados[2]
        perfil = dados[3].lower()
        status = dados[4]

        if usuario_id == sessao.usuario_id:

            messagebox.showwarning(
                "Operação não permitida",
                "Você não pode desativar o próprio usuário.",
                parent=self.janela
            )

            return

        if status == "Inativo":

            messagebox.showinfo(
                "Usuário",
                "Esse usuário já está inativo.",
                parent=self.janela
            )

            return

        if perfil == "admin":

            total = q(
                """
                SELECT COUNT(*) AS total
                FROM usuarios
                WHERE perfil = 'admin'
                AND ativo = 1
                """
            )[0]["total"]

            if total <= 1:

                messagebox.showwarning(
                    "Operação não permitida",
                    "O sistema precisa possuir pelo menos "
                    "um administrador ativo.",
                    parent=self.janela
                )

                return

        if not messagebox.askyesno(
            "Desativar usuário",
            f"Deseja desativar '{usuario}'?",
            parent=self.janela
        ):
            return

        run(
            "UPDATE usuarios SET ativo = 0 WHERE id = ?",
            (usuario_id,)
        )

        self.carregar_usuarios()

    # --------------------------------------------------------
    # ATIVAR
    # --------------------------------------------------------

    def ativar_usuario(self):

        if not sessao.tem_permissao(
            "usuarios.ativar"
        ):

            messagebox.showwarning(
                "Acesso negado",
                "Você não tem permissão para ativar usuários.",
                parent=self.janela
            )

            return

        dados = self.usuario_selecionado()

        if not dados:
            return

        usuario_id = int(dados[0])
        usuario = dados[2]

        if dados[4] == "Ativo":

            messagebox.showinfo(
                "Usuário",
                "Esse usuário já está ativo.",
                parent=self.janela
            )

            return

        if not messagebox.askyesno(
            "Ativar usuário",
            f"Deseja ativar '{usuario}'?",
            parent=self.janela
        ):
            return

        run(
            "UPDATE usuarios SET ativo = 1 WHERE id = ?",
            (usuario_id,)
        )

        self.carregar_usuarios()

    # --------------------------------------------------------
    # REDEFINIR SENHA
    # --------------------------------------------------------

    def redefinir_senha(self):

        if not sessao.tem_permissao(
            "usuarios.redefinir_senha"
        ):

            messagebox.showwarning(
                "Acesso negado",
                "Você não tem permissão para redefinir senhas.",
                parent=self.janela
            )

            return

        dados = self.usuario_selecionado()

        if not dados:
            return

        usuario_id = int(dados[0])
        usuario = dados[2]

        if dados[4] == "Inativo":

            messagebox.showwarning(
                "Usuário",
                "Não é possível redefinir a senha "
                "de um usuário inativo.",
                parent=self.janela
            )

            return

        senha = simpledialog.askstring(
            "Redefinir senha",
            f"Nova senha para '{usuario}':",
            show="*",
            parent=self.janela
        )

        if senha is None:
            return

        if len(senha) < 6:

            messagebox.showwarning(
                "Senha",
                "A senha deve possuir pelo menos 6 caracteres.",
                parent=self.janela
            )

            return

        confirmar = simpledialog.askstring(
            "Redefinir senha",
            "Confirme a nova senha:",
            show="*",
            parent=self.janela
        )

        if confirmar != senha:

            messagebox.showwarning(
                "Senha",
                "As senhas não coincidem.",
                parent=self.janela
            )

            return

        salt, senha_hash = gerar_senha(senha)

        run(
            """
            UPDATE usuarios
            SET senha_hash = ?, salt = ?
            WHERE id = ?
            """,
            (
                senha_hash,
                salt,
                usuario_id
            )
        )

        messagebox.showinfo(
            "Senha",
            "Senha redefinida com sucesso.",
            parent=self.janela
        )


# ============================================================
# NOVO USUÁRIO
# ============================================================

class JanelaNovoUsuario:

    def __init__(self, parent, ao_salvar):

        self.ao_salvar = ao_salvar

        self.janela = tk.Toplevel(
            parent.janela
        )

        self.janela.title("Novo usuário")
        self.janela.geometry("440x470")
        self.janela.resizable(False, False)

        self.janela.configure(
            bg=FUNDO
        )

        self.janela.transient(
            parent.janela
        )

        self.janela.grab_set()

        self.criar_interface()

        self.centralizar()

    # --------------------------------------------------------
    # CENTRALIZAR
    # --------------------------------------------------------

    def centralizar(self):

        self.janela.update_idletasks()

        largura = 440
        altura = 470

        tela_largura = self.janela.winfo_screenwidth()
        tela_altura = self.janela.winfo_screenheight()

        x = (tela_largura - largura) // 2
        y = (tela_altura - altura) // 2

        self.janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------

    def criar_interface(self):

        header = tk.Frame(
            self.janela,
            bg=FUNDO
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 0)
        )

        tk.Label(
            header,
            text="Novo usuário",
            bg=FUNDO,
            fg=TEXTO,
            font=("Segoe UI", 21, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Crie um novo acesso ao sistema.",
            bg=FUNDO,
            fg=SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

        card, conteudo = criar_card(
            self.janela,
            370,
            335,
            raio=14
        )

        card.pack(
            padx=35,
            pady=(18, 0)
        )

        form = tk.Frame(
            conteudo,
            bg=BRANCO
        )

        form.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20
        )

        self.nome = self.campo(
            form,
            "Nome completo"
        )

        self.usuario = self.campo(
            form,
            "Nome de usuário"
        )

        self.usuario.bind(
            "<KeyRelease>",
            self.normalizar_usuario
        )

        tk.Label(
            form,
            text="Letras, números, ponto ou _",
            bg=BRANCO,
            fg=SECUNDARIO,
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.senha = self.campo(
            form,
            "Senha",
            show="*"
        )

        tk.Label(
            form,
            text="Perfil de acesso",
            bg=BRANCO,
            fg=TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.perfil = ttk.Combobox(
            form,
            state="readonly",
            values=("operador", "admin"),
            font=("Segoe UI", 9)
        )

        self.perfil.set("operador")

        self.perfil.pack(
            fill="x",
            ipady=3
        )

        criar_botao(
            self.janela,
            "Criar usuário",
            self.salvar,
            largura=370,
            altura=42,
            fundo=FUNDO
        ).pack(
            pady=(12, 0)
        )

    # --------------------------------------------------------
    # CAMPO
    # --------------------------------------------------------

    def campo(
        self,
        parent,
        titulo,
        show=None
    ):

        tk.Label(
            parent,
            text=titulo,
            bg=BRANCO,
            fg=TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )

        entrada = tk.Entry(
            parent,
            bg=BRANCO,
            fg=TEXTO,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Segoe UI", 10),
            show=show or ""
        )

        entrada.pack(
            fill="x",
            ipady=6,
            pady=(5, 10)
        )

        return entrada

    # --------------------------------------------------------
    # NORMALIZAR USUÁRIO
    # --------------------------------------------------------

    def normalizar_usuario(self, event=None):

        valor = self.usuario.get()

        normalizado = normalizar_usuario(
            valor
        )

        if valor == normalizado:
            return

        posicao = self.usuario.index(
            tk.INSERT
        )

        self.usuario.delete(
            0,
            tk.END
        )

        self.usuario.insert(
            0,
            normalizado
        )

        self.usuario.icursor(
            min(
                posicao,
                len(normalizado)
            )
        )

    # --------------------------------------------------------
    # SALVAR
    # --------------------------------------------------------

    def salvar(self):

        nome = self.nome.get().strip()

        usuario = normalizar_usuario(
            self.usuario.get()
        )

        senha = self.senha.get()

        perfil = self.perfil.get()

        if not nome or not usuario or not senha:

            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha todos os campos.",
                parent=self.janela
            )

            return

        if not usuario_valido(usuario):

            messagebox.showwarning(
                "Usuário inválido",
                "Use de 3 a 30 caracteres, apenas letras, "
                "números, ponto ou _.",
                parent=self.janela
            )

            return

        if len(senha) < 6:

            messagebox.showwarning(
                "Senha",
                "A senha deve possuir pelo menos 6 caracteres.",
                parent=self.janela
            )

            return

        if perfil not in (
            "admin",
            "operador"
        ):
            return

        if q(
            "SELECT id FROM usuarios WHERE usuario = ?",
            (usuario,)
        ):

            messagebox.showerror(
                "Usuário existente",
                "Esse usuário já está cadastrado.",
                parent=self.janela
            )

            return

        salt, senha_hash = gerar_senha(
            senha
        )

        run(
            """
            INSERT INTO usuarios
            (usuario, nome, senha_hash, salt, perfil, ativo)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                usuario,
                nome,
                senha_hash,
                salt,
                perfil
            )
        )

        messagebox.showinfo(
            "Usuário criado",
            "Usuário criado com sucesso!",
            parent=self.janela
        )

        self.janela.destroy()

        self.ao_salvar()