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
    conexao = conectar_banco()

    if canalPedido:
        canais_validos = ["APP", "TOTEM", "BALCAO", "PICKUP", "WEB"]

        if canalPedido not in canais_validos:
            conexao.close()
            raise HTTPException(
                status_code=400,
                detail="Canal de pedido inválido"
            )

        registros = conexao.execute("""
            SELECT
                pedidos.id,
                pedidos.produto_id,
                produtos.nome AS produto,
                pedidos.unidade_id,
                unidades.nome AS unidade,
                pedidos.quantidade,
                pedidos.canal_pedido,
                pedidos.status,
                pedidos.valor_total
            FROM pedidos
            JOIN produtos ON produtos.id = pedidos.produto_id
            JOIN unidades ON unidades.id = pedidos.unidade_id
            WHERE pedidos.canal_pedido = ?
            ORDER BY pedidos.id
        """, (canalPedido,)).fetchall()

    else:
        registros = conexao.execute("""
            SELECT
                pedidos.id,
                pedidos.produto_id,
                produtos.nome AS produto,
                pedidos.unidade_id,
                unidades.nome AS unidade,
                pedidos.quantidade,
                pedidos.canal_pedido,
                pedidos.status,
                pedidos.valor_total
            FROM pedidos
            JOIN produtos ON produtos.id = pedidos.produto_id
            JOIN unidades ON unidades.id = pedidos.unidade_id
            ORDER BY pedidos.id
        """).fetchall()

    conexao.close()

    return [dict(pedido) for pedido in registros]


@router.patch("/{pedido_id}/status")
def atualizar_status_pedido(
    pedido_id: int,
    dados: AtualizarStatusPedido
):
    return alterar_status_pedido(pedido_id, dados)

    