import os
import sqlite3


def conectar_banco():
    caminho_banco = os.getenv("RAIZES_DB", "raizes.db")

    conexao = sqlite3.connect(caminho_banco)
    conexao.row_factory = sqlite3.Row

    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao