import sqlite3
from pathlib import Path


# ---------------- BANCO DE DADOS ---------------- #

BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "estoque.db"

DB.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys = ON")


# ---------------- TABELAS ---------------- #

con.executescript("""
CREATE TABLE IF NOT EXISTS produtos(
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    unidade TEXT,
    minimo REAL DEFAULT 0,
    finalidade TEXT DEFAULT 'uso e consumo',
    ativo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS notas(
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    fornecedor TEXT,
    data TEXT,
    faturada INTEGER DEFAULT 0,
    data_faturamento TEXT,
    chave TEXT
);

CREATE TABLE IF NOT EXISTS itens(
    id INTEGER PRIMARY KEY,
    nota_id INTEGER REFERENCES notas(id) ON DELETE CASCADE,
    cod_forn TEXT,
    descricao TEXT,
    qtd REAL,
    unidade TEXT,
    produto_id INTEGER REFERENCES produtos(id),
    fator REAL DEFAULT 1,
    qtd_estoque REAL,
    valor_total REAL,
    valor_unit REAL
);

CREATE TABLE IF NOT EXISTS vinculos(
    fornecedor TEXT,
    cod_forn TEXT,
    produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    fator REAL,
    PRIMARY KEY(fornecedor, cod_forn)
);

-- Cabeçalho da saída
CREATE TABLE IF NOT EXISTS saidas(
    id INTEGER PRIMARY KEY,
    responsavel TEXT,
    tipo TEXT,
    data_hora TEXT
);

-- Itens da saída
CREATE TABLE IF NOT EXISTS itens_saida(
    id INTEGER PRIMARY KEY,
    saida_id INTEGER REFERENCES saidas(id) ON DELETE CASCADE,
    produto_id INTEGER REFERENCES produtos(id),
    qtd REAL,
    valor_unit REAL,
    subtotal REAL
);
""")


# ---------------- MIGRAÇÕES ---------------- #

# Adiciona a chave da NF-e caso o banco seja antigo
try:
    con.execute("ALTER TABLE notas ADD COLUMN chave TEXT")
except sqlite3.OperationalError:
    pass


# Adiciona o valor unitário caso o banco seja antigo
try:
    con.execute("ALTER TABLE itens ADD COLUMN valor_unit REAL")
except sqlite3.OperationalError:
    pass


# Caso alguém tenha um banco antigo sem itens_saida
try:
    con.execute("""
        CREATE TABLE IF NOT EXISTS itens_saida(
            id INTEGER PRIMARY KEY,
            saida_id INTEGER REFERENCES saidas(id) ON DELETE CASCADE,
            produto_id INTEGER REFERENCES produtos(id),
            qtd REAL,
            valor_unit REAL,
            subtotal REAL
        )
    """)
except sqlite3.OperationalError:
    pass


con.commit()


# ---------------- FUNÇÕES ---------------- #

def q(sql, parametros=()):
    return con.execute(sql, parametros).fetchall()


def run(sql, parametros=()):
    cur = con.execute(sql, parametros)
    con.commit()
    return cur