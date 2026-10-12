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

    # Aceitar o formato novo ou o antigo
    if pedido.itens is not None:
        itens_recebidos = pedido.itens

        if not itens_recebidos:
            raise HTTPException(
                status_code=400,
                detail="O pedido deve conter pelo menos um item"
            )

        if pedido.produto_id is not None or pedido.quantidade is not None:
            raise HTTPException(
                status_code=400,
                detail="Informe itens ou produto_id/quantidade, não ambos"
            )

    else:
        if pedido.produto_id is None or pedido.quantidade is None:
            raise HTTPException(
                status_code=400,
                detail="Informe os produtos do pedido"
            )

        itens_recebidos = [
            {
                "produto_id": pedido.produto_id,
                "quantidade": pedido.quantidade
            }
        ]

    # Organizar os itens e somar produtos repetidos
    quantidades = {}

    for item in itens_recebidos:
        if isinstance(item, dict):
            produto_id = item["produto_id"]
            quantidade = item["quantidade"]
        else:
            produto_id = item.produto_id
            quantidade = item.quantidade

        if quantidade <= 0:
            raise HTTPException(
                status_code=400,
                detail="A quantidade deve ser maior que zero"
            )

        quantidades[produto_id] = (
            quantidades.get(produto_id, 0) + quantidade
        )

    conexao = conectar_banco()

    try:
        # Iniciar transação para proteger o estoque
        conexao.execute("BEGIN IMMEDIATE")

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

        itens_calculados = []
        valor_original = 0
        desconto_total = 0
        hoje = date.today().isoformat()

        # Verificar todos os produtos antes de registrar o pedido
        for produto_id, quantidade in quantidades.items():

            produto = conexao.execute("""
                SELECT id, nome
                FROM produtos
                WHERE id = ?
            """, (produto_id,)).fetchone()

            if produto is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produto {produto_id} não encontrado"
                )

            cardapio = conexao.execute("""
                SELECT preco, disponivel
                FROM cardapio_unidade
                WHERE produto_id = ?
                  AND unidade_id = ?
            """, (
                produto_id,
                pedido.unidade_id
            )).fetchone()

            if cardapio is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produto {produto_id} não está no cardápio da unidade"
                )

            if not cardapio["disponivel"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"Produto {produto_id} indisponível"
                )

            estoque = conexao.execute("""
                SELECT quantidade
                FROM estoque
                WHERE produto_id = ?
                  AND unidade_id = ?
            """, (
                produto_id,
                pedido.unidade_id
            )).fetchone()

            if estoque is None or quantidade > estoque["quantidade"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"Estoque insuficiente para o produto {produto_id}"
                )

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
                produto_id,
                hoje,
                hoje
            )).fetchone()

            preco = round(cardapio["preco"], 2)
            subtotal_original = round(preco * quantidade, 2)

            desconto = 0
            nome_promocao = None

            if promocao is not None:
                desconto = round(
                    subtotal_original *
                    promocao["percentual_desconto"] / 100,
                    2
                )
                nome_promocao = promocao["nome"]

            subtotal_final = round(
                subtotal_original - desconto, 2
            )

            valor_original = round(
                valor_original + subtotal_original, 2
            )

            desconto_total = round(
                desconto_total + desconto, 2
            )

            itens_calculados.append({
                "produto_id": produto_id,
                "produto": produto["nome"],
                "quantidade": quantidade,
                "preco_unitario": preco,
                "subtotal_original": subtotal_original,
                "desconto": desconto,
                "promocao": nome_promocao,
                "subtotal": subtotal_final
            })

        valor_total = round(
            valor_original - desconto_total, 2
        )

        # Compatibilidade com a estrutura antiga de pedidos
        primeiro_item = itens_calculados[0]

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
            primeiro_item["produto_id"],
            pedido.unidade_id,
            pedido.usuario_id,
            sum(quantidades.values()),
            pedido.canal_pedido,
            "AGUARDANDO_PAGAMENTO",
            valor_total
        ))

        pedido_id = cursor.lastrowid

        # Registrar cada item e atualizar seu estoque
        for item in itens_calculados:

            conexao.execute("""
                INSERT INTO itens_pedido (
                    pedido_id,
                    produto_id,
                    quantidade,
                    preco_unitario,
                    subtotal
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                pedido_id,
                item["produto_id"],
                item["quantidade"],
                item["preco_unitario"],
                item["subtotal"]
            ))

            conexao.execute("""
                UPDATE estoque
                SET quantidade = quantidade - ?
                WHERE produto_id = ?
                  AND unidade_id = ?
            """, (
                item["quantidade"],
                item["produto_id"],
                pedido.unidade_id
            ))

        conexao.commit()

        return {
            "id": pedido_id,
            "unidade_id": pedido.unidade_id,
            "usuario_id": pedido.usuario_id,
            "canal_pedido": pedido.canal_pedido,
            "status": "AGUARDANDO_PAGAMENTO",
            "itens": itens_calculados,
            "valor_original": valor_original,
            "desconto": desconto_total,
            "valor_total": valor_total
        }

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