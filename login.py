import tkinter as tk
from tkinter import messagebox
import hashlib
import secrets

from dados.usuarios.database import q, run


# ============================================================
# CORES
# ============================================================

FUNDO = "#F4F6F8"
BRANCO = "#FFFFFF"

TEXTO = "#1F2937"
TEXTO_SECUNDARIO = "#6B7280"

PRINCIPAL = "#2563EB"
PRINCIPAL_HOVER = "#1D4ED8"

BORDA = "#E5E7EB"
PERIGO = "#DC2626"


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ITERACOES = 600_000


# ============================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================

def normalizar_usuario(usuario):
    return usuario.strip().lower()


def usuario_valido(usuario):
    if not usuario:
        return False

    if len(usuario) < 3:
        return False

    if len(usuario) > 30:
        return False

    permitido = usuario.replace("_", "").replace(".", "")

    return permitido.isalnum()


def gerar_senha(senha):
    salt = secrets.token_bytes(16)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES
    )

    return salt.hex(), senha_hash.hex()


def verificar_senha(senha, salt_hex, hash_hex):
    salt = bytes.fromhex(salt_hex)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES
    )

    return secrets.compare_digest(
        senha_hash.hex(),
        hash_hex
    )


def existem_usuarios():
    resultado = q(
        "SELECT COUNT(*) AS total FROM usuarios"
    )

    return resultado[0]["total"] > 0


def criar_usuario_admin(usuario, nome, senha):
    usuario = normalizar_usuario(usuario)

    salt, senha_hash = gerar_senha(senha)

    run(
        """
        INSERT INTO usuarios (
            usuario,
            nome,
            senha_hash,
            salt,
            perfil,
            ativo
        )
        VALUES (?, ?, ?, ?, 'admin', 1)
        """,
        (
            usuario,
            nome,
            senha_hash,
            salt
        )
    )


def autenticar(usuario, senha):
    usuario = normalizar_usuario(usuario)

    resultado = q(
        """
        SELECT *
        FROM usuarios
        WHERE usuario = ?
          AND ativo = 1
        """,
        (usuario,)
    )

    if not resultado:
        return None

    usuario_db = resultado[0]

    if verificar_senha(
        senha,
        usuario_db["salt"],
        usuario_db["senha_hash"]
    ):
        return usuario_db

    return None


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
    largura=300,
    altura=42,
    cor=PRINCIPAL,
    cor_hover=PRINCIPAL_HOVER,
    cor_texto=BRANCO,
    fundo=BRANCO,
    raio=10
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
            font=("Segoe UI", 10, "bold")
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


def criar_card(parent, largura, altura):
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
        18,
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
# PRIMEIRO ADMINISTRADOR
# ============================================================

class TelaPrimeiroAdmin:

    def __init__(self, root, ao_concluir):

        self.root = root
        self.ao_concluir = ao_concluir

        self.janela = tk.Toplevel(root)

        self.janela.title("Configuração inicial")
        self.janela.geometry("480x570")
        self.janela.resizable(False, False)

        self.janela.configure(bg=FUNDO)

        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.fechar
        )

        self.criar_interface()

        self.centralizar()


    def centralizar(self):

        self.janela.update_idletasks()

        largura = 480
        altura = 570

        tela_largura = self.janela.winfo_screenwidth()
        tela_altura = self.janela.winfo_screenheight()

        x = (tela_largura - largura) // 2
        y = (tela_altura - altura) // 2

        self.janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )


    def criar_interface(self):

        header = tk.Frame(
            self.janela,
            bg=FUNDO
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(32, 0)
        )

        tk.Label(
            header,
            text="Configuração inicial",
            bg=FUNDO,
            fg=TEXTO,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Crie o primeiro administrador do sistema",
            bg=FUNDO,
            fg=TEXTO_SECUNDARIO,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        card, conteudo = criar_card(
            self.janela,
            400,
            410
        )

        card.pack(
            padx=40,
            pady=(25, 0)
        )

        formulario = tk.Frame(
            conteudo,
            bg=BRANCO
        )

        formulario.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=25
        )

        self.criar_campo(
            formulario,
            "Nome",
            "Digite o nome do usuário"
        )

        self.nome = self.entrada

        self.criar_campo(
            formulario,
            "Usuário",
            "Digite o usuário"
        )

        self.usuario = self.entrada

        tk.Label(
            formulario,
            text="Use apenas letras, números, . ou _",
            bg=BRANCO,
            fg=TEXTO_SECUNDARIO,
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(3, 12)
        )

        self.usuario.bind(
            "<KeyRelease>",
            self.atualizar_usuario
        )

        self.criar_campo(
            formulario,
            "Senha",
            "Digite a senha",
            senha=True
        )

        self.senha = self.entrada

        self.criar_campo(
            formulario,
            "Confirmar senha",
            "Digite novamente a senha",
            senha=True
        )

        self.confirmar = self.entrada

        btn = criar_botao(
            formulario,
            "Criar administrador",
            self.criar,
            largura=344,
            altura=42,
            fundo=BRANCO
        )

        btn.pack(
            fill="x",
            pady=(16, 0)
        )


    def criar_campo(
        self,
        parent,
        titulo,
        placeholder,
        senha=False
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
            bg="#FFFFFF",
            fg=TEXTO,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Segoe UI", 10),
            show="*" if senha else ""
        )

        entrada.pack(
            fill="x",
            ipady=7,
            pady=(5, 0)
        )

        return_value = entrada

        self.entrada = return_value


    def atualizar_usuario(self, event=None):

        valor = self.usuario.get()

        normalizado = normalizar_usuario(valor)

        if valor != normalizado:

            posicao = self.usuario.index(tk.INSERT)

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


    def criar(self):

        nome = self.nome.get().strip()

        usuario = normalizar_usuario(
            self.usuario.get()
        )

        senha = self.senha.get()

        confirmar = self.confirmar.get()

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
                "O usuário deve possuir entre 3 e 30 caracteres e pode conter apenas letras, números, ponto (.) ou sublinhado (_).",
                parent=self.janela
            )

            self.usuario.focus()

            return

        if senha != confirmar:

            messagebox.showwarning(
                "Senha",
                "As senhas não coincidem.",
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

        try:

            criar_usuario_admin(
                usuario,
                nome,
                senha
            )

        except Exception as erro:

            if "UNIQUE" in str(erro).upper():

                messagebox.showerror(
                    "Usuário existente",
                    "Esse usuário já existe.",
                    parent=self.janela
                )

            else:

                messagebox.showerror(
                    "Erro",
                    f"Não foi possível criar o administrador.\n\n{erro}",
                    parent=self.janela
                )

            return

        messagebox.showinfo(
            "Administrador criado",
            "Administrador criado com sucesso!",
            parent=self.janela
        )

        self.janela.destroy()

        self.ao_concluir()


    def fechar(self):

        resposta = messagebox.askyesno(
            "Sair",
            "A configuração inicial ainda não foi concluída.\n\nDeseja fechar o programa?",
            parent=self.janela
        )

        if resposta:
            self.root.destroy()


# ============================================================
# TELA DE LOGIN
# ============================================================

class TelaLogin:

    def __init__(self, root, ao_logar):

        self.root = root
        self.ao_logar = ao_logar

        self.janela = tk.Toplevel(root)

        self.janela.title("Login")
        self.janela.geometry("460x430")
        self.janela.resizable(False, False)

        self.janela.configure(bg=FUNDO)

        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.fechar
        )

        self.criar_interface()

        self.centralizar()


    def centralizar(self):

        self.janela.update_idletasks()

        largura = 460
        altura = 430

        tela_largura = self.janela.winfo_screenwidth()
        tela_altura = self.janela.winfo_screenheight()

        x = (tela_largura - largura) // 2
        y = (tela_altura - altura) // 2

        self.janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )


    def criar_interface(self):

        header = tk.Frame(
            self.janela,
            bg=FUNDO
        )

        header.pack(
            fill="x",
            padx=45,
            pady=(38, 0)
        )

        tk.Label(
            header,
            text="Controle de Estoque",
            bg=FUNDO,
            fg=TEXTO,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Entre com seu usuário para continuar",
            bg=FUNDO,
            fg=TEXTO_SECUNDARIO,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        card, conteudo = criar_card(
            self.janela,
            370,
            270
        )

        card.pack(
            padx=45,
            pady=(25, 0)
        )

        formulario = tk.Frame(
            conteudo,
            bg=BRANCO
        )

        formulario.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=27
        )

        tk.Label(
            formulario,
            text="Usuário",
            bg=BRANCO,
            fg=TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )

        self.usuario = tk.Entry(
            formulario,
            bg=BRANCO,
            fg=TEXTO,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Segoe UI", 10)
        )

        self.usuario.pack(
            fill="x",
            ipady=7,
            pady=(5, 16)
        )

        self.usuario.bind(
            "<KeyRelease>",
            self.atualizar_usuario
        )

        tk.Label(
            formulario,
            text="Senha",
            bg=BRANCO,
            fg=TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )

        self.senha = tk.Entry(
            formulario,
            bg=BRANCO,
            fg=TEXTO,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Segoe UI", 10),
            show="*"
        )

        self.senha.pack(
            fill="x",
            ipady=7,
            pady=(5, 20)
        )

        btn = criar_botao(
            formulario,
            "Entrar",
            self.entrar,
            largura=314,
            altura=42,
            fundo=BRANCO
        )

        btn.pack(
            fill="x"
        )

        self.usuario.focus_set()

        self.janela.bind(
            "<Return>",
            lambda event: self.entrar()
        )


    def atualizar_usuario(self, event=None):

        valor = self.usuario.get()

        normalizado = normalizar_usuario(valor)

        if valor != normalizado:

            posicao = self.usuario.index(tk.INSERT)

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


    def entrar(self):

        usuario = normalizar_usuario(
            self.usuario.get()
        )

        senha = self.senha.get()

        if not usuario or not senha:

            messagebox.showwarning(
                "Login",
                "Informe usuário e senha.",
                parent=self.janela
            )

            return

        usuario_db = autenticar(
            usuario,
            senha
        )

        if usuario_db is None:

            messagebox.showerror(
                "Login",
                "Usuário ou senha inválidos.",
                parent=self.janela
            )

            self.senha.delete(
                0,
                tk.END
            )

            self.senha.focus()

            return

        self.janela.destroy()

        self.ao_logar(usuario_db)   

    def fechar(self):

        self.root.destroy()

# ============================================================
# INICIAR LOGIN
# ============================================================

def iniciar_login(root, ao_logar):

    if existem_usuarios():

        TelaLogin(
            root,
            ao_logar
        )
    else:

        TelaPrimeiroAdmin(
            root,
            lambda: TelaLogin(
                root,
                ao_logar
            )
        )