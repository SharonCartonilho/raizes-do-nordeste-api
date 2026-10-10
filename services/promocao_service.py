from fastapi import HTTPException
from database.conexao import conectar_banco


def criar_promocao_service(dados):
    if dados.data_fim < dados.data_inicio:
        raise HTTPException(
            status_code=400,
            detail="A data final não pode ser anterior à inicial"
        )

    conexao = conectar_banco()

    try:
        unidade = conexao.execute("""
            SELECT id FROM unidades
            WHERE id = ? AND ativa = 1
        """, (dados.unidade_id,)).fetchone()

        if unidade is None:
            raise HTTPException(
                status_code=404,
                detail="Unidade não encontrada ou inativa"
            )

        produto = conexao.execute("""
            SELECT id FROM cardapio_unidade
            WHERE unidade_id = ?
              AND produto_id = ?
        """, (
            dados.unidade_id,
            dados.produto_id
        )).fetchone()

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado no cardápio da unidade"
            )

        cursor = conexao.execute("""
            INSERT INTO promocoes (
                nome,
                unidade_id,
                produto_id,
                percentual_desconto,
                data_inicio,
                data_fim,
                ativa
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            dados.nome,
            dados.unidade_id,
            dados.produto_id,
            dados.percentual_desconto,
            dados.data_inicio.isoformat(),
            dados.data_fim.isoformat()
        ))

        conexao.commit()

        return {
            "id": cursor.lastrowid,
            "nome": dados.nome,
            "unidade_id": dados.unidade_id,
            "produto_id": dados.produto_id,
            "percentual_desconto": dados.percentual_desconto,
            "data_inicio": dados.data_inicio,
            "data_fim": dados.data_fim,
            "ativa": True
        }

    finally:
        conexao.close()


def listar_promocoes_service(unidade_id=None):
    conexao = conectar_banco()

    try:
        consulta = """
            SELECT
                promocoes.id,
                promocoes.nome,
                promocoes.unidade_id,
                unidades.nome AS unidade,
                promocoes.produto_id,
                produtos.nome AS produto,
                promocoes.percentual_desconto,
                promocoes.data_inicio,
                promocoes.data_fim,
                promocoes.ativa
            FROM promocoes
            JOIN unidades
                ON unidades.id = promocoes.unidade_id
            JOIN produtos
                ON produtos.id = promocoes.produto_id
        """

        parametros = ()

        if unidade_id is not None:
            consulta += " WHERE promocoes.unidade_id = ?"
            parametros = (unidade_id,)

        consulta += " ORDER BY promocoes.id"

        registros = conexao.execute(
            consulta, parametros
        ).fetchall()

        return [
            {
                **dict(registro),
                "ativa": bool(registro["ativa"])
            }
            for registro in registros
        ]

    finally:
        conexao.close()