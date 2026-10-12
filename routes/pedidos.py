from fastapi import APIRouter, HTTPException

from database.conexao import conectar_banco
from models.schemas import PedidoNovo, AtualizarStatusPedido
from services.pedido_service import criar_novo_pedido, alterar_status_pedido

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

@router.post("", status_code=201)
def criar_pedido(pedido: PedidoNovo):
    return criar_novo_pedido(pedido)



@router.get("")
def listar_pedidos(canalPedido: str = None):
    canais_validos = ["APP", "TOTEM", "BALCAO", "PICKUP", "WEB"]
    if canalPedido is not None and canalPedido not in canais_validos:
        raise HTTPException(status_code=400, detail="Canal de pedido inválido")

    conexao = conectar_banco()
    try:
        sql = """
            SELECT pedidos.id, pedidos.produto_id, produtos.nome AS produto,
                   pedidos.unidade_id, unidades.nome AS unidade,
                   pedidos.quantidade, pedidos.canal_pedido, pedidos.status,
                   pedidos.valor_total, pedidos.usuario_id
            FROM pedidos
            JOIN produtos ON produtos.id = pedidos.produto_id
            JOIN unidades ON unidades.id = pedidos.unidade_id
        """
        parametros = ()
        if canalPedido is not None:
            sql += " WHERE pedidos.canal_pedido = ?"
            parametros = (canalPedido,)
        sql += " ORDER BY pedidos.id"
        registros = conexao.execute(sql, parametros).fetchall()
        resultado = []
        for registro in registros:
            dados = dict(registro)
            itens = conexao.execute("""
                SELECT ip.id, ip.produto_id, p.nome AS produto, ip.quantidade,
                       ip.preco_unitario, ip.subtotal
                FROM itens_pedido ip
                JOIN produtos p ON p.id = ip.produto_id
                WHERE ip.pedido_id = ? ORDER BY ip.id
            """, (dados["id"],)).fetchall()
            dados["itens"] = [dict(item) for item in itens]
            # Pedidos anteriores à tabela itens_pedido continuam legíveis.
            if not dados["itens"]:
                dados["itens"] = [{
                    "produto_id": dados["produto_id"],
                    "produto": dados["produto"],
                    "quantidade": dados["quantidade"],
                    "preco_unitario": round(dados["valor_total"] / dados["quantidade"], 2) if dados["quantidade"] else 0,
                    "subtotal": dados["valor_total"]
                }]
            resultado.append(dados)
        return resultado
    finally:
        conexao.close()


@router.patch("/{pedido_id}/status")
def atualizar_status_pedido(
    pedido_id: int,
    dados: AtualizarStatusPedido
):
    return alterar_status_pedido(pedido_id, dados)

    