from fastapi import HTTPException
from datetime import date
from database.conexao import conectar_banco
from services.fidelidade_service import conceder_pontos_pedido


def criar_novo_pedido(pedido):
    canais_validos = ["APP", "TOTEM", "BALCAO", "PICKUP", "WEB"]

    if pedido.canal_pedido not in canais_validos:
        raise HTTPException(
            status_code=400,
            detail="Canal de pedido inválido"
        )

    if pedido.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade deve ser maior que zero"
        )

    conexao = conectar_banco()

    try:
        # Verificar se o produto existe
        produto = conexao.execute("""
            SELECT id, nome, preco
            FROM produtos
            WHERE id = ?
        """, (pedido.produto_id,)).fetchone()

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )

        # Verificar se a unidade existe e está ativa
        unidade = conexao.execute("""
            SELECT id
            FROM unidades
            WHERE id = ? AND ativa = 1
        """, (pedido.unidade_id,)).fetchone()

        if unidade is None:
            raise HTTPException(
                status_code=404,
                detail="Unidade não encontrada ou inativa"
            )

        # Verificar o cliente, quando informado
        if pedido.usuario_id is not None:
            cliente = conexao.execute("""
                SELECT id
                FROM usuarios
                WHERE id = ?
                  AND perfil = 'CLIENTE'
                  AND ativo = 1
            """, (pedido.usuario_id,)).fetchone()

            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente não encontrado ou inativo"
                )

        # Consultar o cardápio da unidade
        item_cardapio = conexao.execute("""
            SELECT preco, disponivel
            FROM cardapio_unidade
            WHERE produto_id = ?
              AND unidade_id = ?
        """, (
            pedido.produto_id,
            pedido.unidade_id
        )).fetchone()

        if item_cardapio is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado no cardápio desta unidade"
            )

        if not item_cardapio["disponivel"]:
            raise HTTPException(
                status_code=409,
                detail="Produto indisponível nesta unidade"
            )

        # Consultar estoque
        estoque = conexao.execute("""
            SELECT quantidade
            FROM estoque
            WHERE produto_id = ?
              AND unidade_id = ?
        """, (
            pedido.produto_id,
            pedido.unidade_id
        )).fetchone()

        if estoque is None:
            raise HTTPException(
                status_code=409,
                detail="Produto sem estoque cadastrado"
            )

        if pedido.quantidade > estoque["quantidade"]:
            raise HTTPException(
                status_code=409,
                detail="Estoque insuficiente"
            )

        # Calcular o valor original
        valor_original = round(
            item_cardapio["preco"] * pedido.quantidade,
            2
        )

        # Procurar promoção válida
        hoje = date.today().isoformat()

        promocao = conexao.execute("""
            SELECT id, nome, percentual_desconto
            FROM promocoes
            WHERE unidade_id = ?
              AND produto_id = ?
              AND ativa = 1
              AND data_inicio <= ?
              AND data_fim >= ?
            ORDER BY percentual_desconto DESC, id ASC
            LIMIT 1
        """, (
            pedido.unidade_id,
            pedido.produto_id,
            hoje,
            hoje
        )).fetchone()

        desconto = 0

        if promocao is not None:
            desconto = round(
                valor_original *
                promocao["percentual_desconto"] / 100,
                2
            )

        valor_total = round(valor_original - desconto, 2)

        # Registrar pedido
        cursor = conexao.execute("""
            INSERT INTO pedidos (
                produto_id,
                unidade_id,
                usuario_id,
                quantidade,
                canal_pedido,
                status,
                valor_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pedido.produto_id,
            pedido.unidade_id,
            pedido.usuario_id,
            pedido.quantidade,
            pedido.canal_pedido,
            "AGUARDANDO_PAGAMENTO",
            valor_total
        ))

        # Atualizar estoque
        conexao.execute("""
            UPDATE estoque
            SET quantidade = quantidade - ?
            WHERE produto_id = ?
              AND unidade_id = ?
        """, (
            pedido.quantidade,
            pedido.produto_id,
            pedido.unidade_id
        ))

        conexao.commit()

        novo_pedido = {
            "id": cursor.lastrowid,
            "produto_id": pedido.produto_id,
            "unidade_id": pedido.unidade_id,
            "usuario_id": pedido.usuario_id,
            "produto": produto["nome"],
            "quantidade": pedido.quantidade,
            "canal_pedido": pedido.canal_pedido,
            "status": "AGUARDANDO_PAGAMENTO",
            "valor_original": valor_original,
            "desconto": desconto,
            "promocao": promocao["nome"] if promocao else None,
            "valor_total": valor_total
        }

        return novo_pedido

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()

def alterar_status_pedido(pedido_id, dados):
    status_validos = ["EM_PREPARACAO", "PRONTO", "ENTREGUE"]

    if dados.status not in status_validos:
        raise HTTPException(
            status_code=400,
            detail="Status de pedido inválido"
        )

    conexao = conectar_banco()

    pedido = conexao.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,)
    ).fetchone()

    if pedido is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    status_atual = pedido["status"]

    transicoes_permitidas = {
        "EM_PREPARACAO": "PRONTO",
        "PRONTO": "ENTREGUE"
    }

    proximo_status = transicoes_permitidas.get(status_atual)

    if proximo_status != dados.status:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail=f"Não é permitido alterar de {status_atual} para {dados.status}"
        )

    conexao.execute("""
        UPDATE pedidos
        SET status = ?
        WHERE id = ?
    """, (dados.status, pedido_id))

    pontos_concedidos = 0

    if dados.status == "ENTREGUE":
        pontos_concedidos = conceder_pontos_pedido(
            conexao,
            pedido_id
        )

    conexao.commit()
    conexao.close()

    return {
    "id": pedido_id,
    "status_anterior": status_atual,
    "status_atual": dados.status,
    "pontos_concedidos": pontos_concedidos
}