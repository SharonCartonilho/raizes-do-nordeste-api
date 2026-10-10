from fastapi import APIRouter, Depends

from services.auth_service import exigir_perfis
from models.schemas import EstoqueAtualizacao
from services.estoque_service import (
    listar_estoque_service,
    atualizar_estoque_service
)


router = APIRouter(
    prefix="/estoque",
    tags=["Estoque"]
)




@router.get("")
def listar_estoque():
    return listar_estoque_service()

    registros = conexao.execute("""
        SELECT
            estoque.id,
            estoque.produto_id,
            produtos.nome AS produto,
            estoque.unidade_id,
            unidades.nome AS unidade,
            estoque.quantidade
        FROM estoque
        JOIN produtos ON produtos.id = estoque.produto_id
        JOIN unidades ON unidades.id = estoque.unidade_id
        ORDER BY estoque.id
    """).fetchall()

    conexao.close()

    return [dict(registro) for registro in registros]


@router.post("", status_code=201)
def atualizar_estoque(
    dados: EstoqueAtualizacao,
    usuario_logado: dict = Depends(
        exigir_perfis("GERENTE", "ADMIN")
    )
):
    return atualizar_estoque_service(dados)

    if dados.quantidade < 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade do estoque não pode ser negativa"
        )

    conexao = conectar_banco()

    produto = conexao.execute(
        "SELECT id FROM produtos WHERE id = ?",
        (dados.produto_id,)
    ).fetchone()

    if produto is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    unidade = conexao.execute(
        "SELECT id FROM unidades WHERE id = ? AND ativa = 1",
        (dados.unidade_id,)
    ).fetchone()

    if unidade is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada ou inativa"
        )

    estoque = conexao.execute(
        """
        SELECT id
        FROM estoque
        WHERE produto_id = ? AND unidade_id = ?
        """,
        (dados.produto_id, dados.unidade_id)
    ).fetchone()

    if estoque is None:
        conexao.execute(
            """
            INSERT INTO estoque (produto_id, unidade_id, quantidade)
            VALUES (?, ?, ?)
            """,
            (
                dados.produto_id,
                dados.unidade_id,
                dados.quantidade
            )
        )
    else:
        conexao.execute(
            """
            UPDATE estoque
            SET quantidade = ?
            WHERE produto_id = ? AND unidade_id = ?
            """,
            (
                dados.quantidade,
                dados.produto_id,
                dados.unidade_id
            )
        )

    conexao.commit()
    conexao.close()

    return {
        "produto_id": dados.produto_id,
        "unidade_id": dados.unidade_id,
        "quantidade": dados.quantidade
    }