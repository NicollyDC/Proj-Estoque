class Sessao:
    def __init__(self):
        self.usuario_id = None
        self.usuario = None
        self.nome = None
        self.perfil = None

    def iniciar(self, usuario):
        self.usuario_id = usuario["id"]
        self.usuario = usuario["usuario"]
        self.nome = usuario["nome"]
        self.perfil = usuario["perfil"]

    def encerrar(self):
        self.usuario_id = None
        self.usuario = None
        self.nome = None
        self.perfil = None

    def esta_logado(self):
        return self.usuario_id is not None

    def tem_permissao(self, permissao):
        permissoes = {
            "admin": {
                "usuarios.visualizar",
                "usuarios.criar",
                "usuarios.ativar",
                "usuarios.desativar",
                "usuarios.redefinir_senha",
            },

            "operador": {
            },
        }

        return (
            self.esta_logado()
            and permissao in permissoes.get(self.perfil, set())
        )


sessao = Sessao()