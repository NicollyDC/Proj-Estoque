import sqlite3
from pathlib import Path
from dados.sync import SyncTracker


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

CREATE TABLE IF NOT EXISTS ajustes_estoque(
    id INTEGER PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    estoque_anterior REAL NOT NULL,
    estoque_novo REAL NOT NULL,
    diferenca REAL NOT NULL,
    valor_unit REAL NOT NULL DEFAULT 0,
    data_hora TEXT NOT NULL,
    responsavel TEXT NOT NULL,
    motivo TEXT NOT NULL,
    observacao TEXT
);
""")


# ---------------- MIGRAÇÕES ---------------- #

# ---------------- MIGRAÇÕES ---------------- #

# Adiciona a chave da NF-e caso o banco seja antigo
try:
    con.execute(
        "ALTER TABLE notas ADD COLUMN chave TEXT"
    )
except sqlite3.OperationalError:
    pass


# Adiciona o valor unitário caso o banco seja antigo
try:
    con.execute(
        "ALTER TABLE itens ADD COLUMN valor_unit REAL"
    )
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


# Índice para localizar rapidamente NF-e pela chave
con.execute("""
    CREATE INDEX IF NOT EXISTS idx_notas_chave
    ON notas(chave)
""")

con.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_notas_chave_unica
    ON notas(chave)
    WHERE chave IS NOT NULL AND chave != ''
""")

con.execute("""
    CREATE INDEX IF NOT EXISTS idx_ajustes_estoque_produto_data
    ON ajustes_estoque(produto_id, data_hora)
""")

con.commit()
sync_tracker = SyncTracker(con)


# ---------------- FUNÇÕES ---------------- #

def q(sql, parametros=()):
    return con.execute(sql, parametros).fetchall()


def execute(sql, parametros=()):
    cur = con.execute(sql, parametros)
    if cur.rowcount > 0:
        sync_tracker.record_sql(sql, parametros, cur.lastrowid)
    return cur


def commit():
    con.commit()


def rollback():
    con.rollback()


def run(sql, parametros=()):
    cur = con.execute(sql, parametros)
    if cur.rowcount > 0:
        sync_tracker.record_sql(sql, parametros, cur.lastrowid)
    con.commit()
    return cur
