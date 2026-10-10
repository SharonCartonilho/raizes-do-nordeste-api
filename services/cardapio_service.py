from fastapi import HTTPException
from database.conexao import conectar_banco


def listar_cardapio_service(unidade_id):
    conexao = conectar_banco()

    unidade = conexao.execute(
        "SELECT id FROM unidades WHERE id = ? AND ativa = 1",
        (unidade_id,)
    ).fetchone()

    if unidade is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada ou inativa"
        )

    registros = conexao.execute("""
        SELECT
            cardapio_unidade.id,
            cardapio_unidade.unidade_id,
            produtos.id AS produto_id,
            produtos.nome AS produto,
            cardapio_unidade.preco,
            cardapio_unidade.disponivel
        FROM cardapio_unidade
        JOIN produtos
            ON produtos.id = cardapio_unidade.produto_id
        WHERE cardapio_unidade.unidade_id = ?
        ORDER BY produtos.nome
    """, (unidade_id,)).fetchall()

    conexao.close()

    return [
        {
            **dict(item),
            "disponivel": bool(item["disponivel"])
        }
        for item in registros
    ]


def adicionar_item_cardapio_service(dados):
    if dados.preco <= 0:
        raise HTTPException(
            status_code=400,
            detail="O preço deve ser maior que zero"
        )

    conexao = conectar_banco()

    unidade = conexao.execute(
        "SELECT id FROM unidades WHERE id = ? AND ativa = 1",
        (dados.unidade_id,)
    ).fetchone()

    produto = conexao.execute(
        "SELECT id FROM produtos WHERE id = ?",
        (dados.produto_id,)
    ).fetchone()

    if unidade is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada ou inativa"
        )

    if produto is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    existente = conexao.execute("""
        SELECT id FROM cardapio_unidade
        WHERE unidade_id = ? AND produto_id = ?
    """, (dados.unidade_id, dados.produto_id)).fetchone()

    if existente:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado no cardápio desta unidade"
        )

    cursor = conexao.execute("""
        INSERT INTO cardapio_unidade (
            unidade_id,
            produto_id,
            preco,
            disponivel
        )
        VALUES (?, ?, ?, ?)
    """, (
        dados.unidade_id,
        dados.produto_id,
        dados.preco,
        int(dados.disponivel)
    ))

    conexao.commit()
    item_id = cursor.lastrowid
    conexao.close()

    return {
        "id": item_id,
        "unidade_id": dados.unidade_id,
        "produto_id": dados.produto_id,
        "preco": dados.preco,
        "disponivel": dados.disponivel
    }