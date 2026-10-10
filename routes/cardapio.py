from fastapi import APIRouter, Depends

from models.schemas import ItemCardapioNovo

from services.cardapio_service import (
    listar_cardapio_service,
    adicionar_item_cardapio_service
)

from services.auth_service import exigir_perfis


router = APIRouter(
    prefix="/cardapio",
    tags=["Cardápio"]
)


@router.get("/{unidade_id}")
def listar_cardapio(unidade_id: int):
    return listar_cardapio_service(unidade_id)


@router.post("", status_code=201)
def adicionar_item_cardapio(
    dados: ItemCardapioNovo,
    usuario_logado: dict = Depends(exigir_perfis("ADMIN"))
):
    return adicionar_item_cardapio_service(dados)
