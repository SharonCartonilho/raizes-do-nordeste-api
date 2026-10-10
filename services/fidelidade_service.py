from database.conexao import conectar_banco


def conceder_pontos_pedido(conexao, pedido_id):
    pedido = conexao.execute("""
        SELECT id, usuario_id, valor_total, status
        FROM pedidos
        WHERE id = ?
    """, (pedido_id,)).fetchone()

    if pedido is None:
        return 0

    if pedido["status"] != "ENTREGUE":
        return 0

    if pedido["usuario_id"] is None:
        return 0

    movimento_existente = conexao.execute("""
        SELECT id
        FROM movimentos_fidelidade
        WHERE pedido_id = ?
          AND tipo = 'CREDITO'
    """, (pedido_id,)).fetchone()

    if movimento_existente:
        return 0

    pontos = int(round(pedido["valor_total"] * 100) // 1000)

    if pontos <= 0:
        return 0

    conexao.execute("""
        INSERT INTO fidelidade (usuario_id, pontos)
        VALUES (?, 0)
        ON CONFLICT(usuario_id) DO NOTHING
    """, (pedido["usuario_id"],))

    conexao.execute("""
        UPDATE fidelidade
        SET pontos = pontos + ?
        WHERE usuario_id = ?
    """, (pontos, pedido["usuario_id"]))

    conexao.execute("""
        INSERT INTO movimentos_fidelidade (
            usuario_id,
            pedido_id,
            tipo,
            pontos
        )
        VALUES (?, ?, 'CREDITO', ?)
    """, (
        pedido["usuario_id"],
        pedido_id,
        pontos
    ))

    return pontos

from fastapi import HTTPException


def consultar_fidelidade_service(usuario_id):
    conexao = conectar_banco()

    usuario = conexao.execute("""
        SELECT id, nome
        FROM usuarios
        WHERE id = ?
          AND perfil = 'CLIENTE'
    """, (usuario_id,)).fetchone()

    if usuario is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    saldo = conexao.execute("""
        SELECT pontos
        FROM fidelidade
        WHERE usuario_id = ?
    """, (usuario_id,)).fetchone()

    movimentos = conexao.execute("""
        SELECT
            id,
            pedido_id,
            tipo,
            pontos,
            data_movimento
        FROM movimentos_fidelidade
        WHERE usuario_id = ?
        ORDER BY id DESC
    """, (usuario_id,)).fetchall()

    conexao.close()

    return {
        "usuario_id": usuario_id,
        "cliente": usuario["nome"],
        "saldo_pontos": saldo["pontos"] if saldo else 0,
        "historico": [dict(movimento) for movimento in movimentos]
    }


def resgatar_pontos_service(usuario_id, dados):
    if dados.pontos <= 0 or dados.pontos % 10 != 0:
        raise HTTPException(
            status_code=400,
            detail="O resgate deve ser feito em múltiplos de 10 pontos"
        )

    conexao = conectar_banco()

    try:
        conexao.execute("BEGIN IMMEDIATE")

        usuario = conexao.execute("""
            SELECT id
            FROM usuarios
            WHERE id = ?
              AND perfil = 'CLIENTE'
              AND ativo = 1
        """, (usuario_id,)).fetchone()

        if usuario is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente não encontrado ou inativo"
            )

        saldo = conexao.execute("""
            SELECT pontos
            FROM fidelidade
            WHERE usuario_id = ?
        """, (usuario_id,)).fetchone()

        pontos_disponiveis = saldo["pontos"] if saldo else 0

        if pontos_disponiveis < dados.pontos:
            raise HTTPException(
                status_code=409,
                detail="Saldo de pontos insuficiente"
            )

        desconto = (dados.pontos // 10) * 5

        conexao.execute("""
            UPDATE fidelidade
            SET pontos = pontos - ?
            WHERE usuario_id = ?
        """, (dados.pontos, usuario_id))

        conexao.execute("""
            INSERT INTO movimentos_fidelidade (
                usuario_id,
                pedido_id,
                tipo,
                pontos
            )
            VALUES (?, NULL, 'DEBITO', ?)
        """, (usuario_id, dados.pontos))

        conexao.commit()

        return {
            "usuario_id": usuario_id,
            "pontos_resgatados": dados.pontos,
            "desconto_gerado": desconto,
            "saldo_restante": pontos_disponiveis - dados.pontos
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()