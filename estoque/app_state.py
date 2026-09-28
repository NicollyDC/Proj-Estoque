alterado = False

def marcar_alteracao():
    global alterado
    alterado = True

def salvar():
    global alterado
    alterado = False

def tem_alteracoes():
    return alterado