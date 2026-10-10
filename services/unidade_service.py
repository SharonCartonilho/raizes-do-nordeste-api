from database.conexao import conectar_banco


def criar_unidade_service(unidade):
    conexao = conectar_banco()

    cursor = conexao.execute(
        """
        INSERT INTO unidades (nome, cidade, estado, ativa)
        VALUES (?, ?, ?, 1)
        """,
        (
            unidade.nome,
            unidade.cidade,
            unidade.estado
        )
    )

    conexao.commit()

    nova_unidade = {
        "id": cursor.lastrowid,
        "nome": unidade.nome,
        "cidade": unidade.cidade,
        "estado": unidade.estado,
        "ativa": True
    }

    conexao.close()

    return nova_unidade


def listar_unidades_service():
    conexao = conectar_banco()

    registros = conexao.execute(
        """
        SELECT id, nome, cidade, estado, ativa
        FROM unidades
        ORDER BY id
        """
    ).fetchall()

    conexao.close()

    return [
        {
            "id": registro["id"],
            "nome": registro["nome"],
            "cidade": registro["cidade"],
            "estado": registro["estado"],
            "ativa": bool(registro["ativa"])
        }
        for registro in registros
    ]