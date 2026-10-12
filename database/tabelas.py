from database.conexao import conectar_banco


def criar_tabela_produtos():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


def criar_tabela_pedidos():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            canal_pedido TEXT NOT NULL,
            status TEXT NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)
    
    
    colunas = conexao.execute(
        "PRAGMA table_info(pedidos)"
    ).fetchall()

    nomes_colunas = [coluna["name"] for coluna in colunas]

    if "unidade_id" not in nomes_colunas:
        conexao.execute(
            "ALTER TABLE pedidos ADD COLUMN unidade_id INTEGER"
        )

        conexao.execute(
            """
            UPDATE pedidos
            SET unidade_id = 1
            WHERE unidade_id IS NULL
            """
        )
    colunas = conexao.execute(
        "PRAGMA table_info(pedidos)"
    ).fetchall()

    nomes_colunas = [coluna["name"] for coluna in colunas]

    if "usuario_id" not in nomes_colunas:
        conexao.execute("""
            ALTER TABLE pedidos
            ADD COLUMN usuario_id INTEGER
            REFERENCES usuarios(id)
        """)
        
    conexao.commit()
    conexao.close()

def criar_tabela_pagamentos():
        conexao = conectar_banco()

        conexao.execute("""
             CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                status TEXT NOT NULL,
                identificador_tentativa TEXT NOT NULL UNIQUE,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        )
    """)

        conexao.commit()
        conexao.close()


def criar_tabela_estoque():
    conexao = conectar_banco()
    # A tabela correta contém apenas os dados de estoque por unidade.
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            unidade_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (unidade_id) REFERENCES unidades(id),
            UNIQUE (produto_id, unidade_id)
        )
    """)
    # Compatibilidade com bases antigas, sem apagar registros.
    colunas = [coluna["name"] for coluna in conexao.execute("PRAGMA table_info(estoque)")]
    if "unidade_id" not in colunas:
        conexao.execute("ALTER TABLE estoque ADD COLUMN unidade_id INTEGER")
        conexao.execute("UPDATE estoque SET unidade_id = 1 WHERE unidade_id IS NULL")
    conexao.commit()
    conexao.close()


def criar_tabela_unidades():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS unidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            ativa INTEGER NOT NULL DEFAULT 1
        )
    """)

    conexao.commit()
    conexao.close()

def criar_tabela_usuarios():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            perfil TEXT NOT NULL,
            unidade_id INTEGER,
            ativo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (unidade_id) REFERENCES unidades(id)
        )
    """)

    conexao.commit()
    conexao.close()

def criar_tabela_cardapio():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS cardapio_unidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            preco REAL NOT NULL,
            disponivel INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (unidade_id) REFERENCES unidades(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            UNIQUE (unidade_id, produto_id)
        )
    """)

    conexao.commit()
    conexao.close()

def criar_tabela_fidelidade():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS fidelidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            pontos INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS movimentos_fidelidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            pedido_id INTEGER,
            tipo TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            data_movimento TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        )
    """)

    conexao.commit()
    conexao.close()

def criar_tabela_promocoes():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS promocoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            unidade_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            percentual_desconto REAL NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            ativa INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (unidade_id) REFERENCES unidades(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            CHECK (percentual_desconto > 0 AND percentual_desconto <= 100),
            CHECK (data_fim >= data_inicio)
        )
    """)

    conexao.commit()
    conexao.close()
def criar_tabela_itens_pedido():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0),

            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conexao.commit()
    conexao.close()
   