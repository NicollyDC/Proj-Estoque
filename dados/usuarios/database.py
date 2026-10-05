import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "usuarios.db"

DB.parent.mkdir(parents=True, exist_ok=True)


def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def q(sql, params=()):
    with conectar() as con:
        return con.execute(sql, params).fetchall()


def run(sql, params=()):
    with conectar() as con:
        con.execute(sql, params)
        con.commit()


def criar_tabelas():
    with conectar() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios(
                id INTEGER PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'operador',
                ativo INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        con.commit()


criar_tabelas()