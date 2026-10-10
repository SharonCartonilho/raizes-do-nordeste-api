from fastapi import HTTPException

from database.conexao import conectar_banco


def processar_pagamento(pagamento):
    conexao = conectar_banco()

    pedido = conexao.execute(
        "SELECT id, valor_total, status FROM pedidos WHERE id = ?",
        (pagamento.pedido_id,)
    ).fetchone()

    if pedido is None:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    tentativa_existente = conexao.execute(
        "SELECT * FROM pagamentos WHERE identificador_tentativa = ?",
        (pagamento.identificador_tentativa,)
    ).fetchone()

    if tentativa_existente is not None:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail="Esta tentativa de pagamento já foi processada"
        )

    status_pagamento = "APROVADO" if pagamento.aprovado else "NEGADO"

    cursor = conexao.execute(
        """
        INSERT INTO pagamentos
        (pedido_id, valor, status, identificador_tentativa)
        VALUES (?, ?, ?, ?)
        """,
        (
            pagamento.pedido_id,
            pedido["valor_total"],
            status_pagamento,
            pagamento.identificador_tentativa
        )
    )

    if pagamento.aprovado:
        conexao.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            ("EM_PREPARACAO", pagamento.pedido_id)
        )

    conexao.commit()
    conexao.close()

    return {
        "id": cursor.lastrowid,
        "pedido_id": pagamento.pedido_id,
        "valor": pedido["valor_total"],
        "status_pagamento": status_pagamento,
        "status_pedido": (
            "EM_PREPARACAO"
            if pagamento.aprovado
            else pedido["status"]
        )
    }