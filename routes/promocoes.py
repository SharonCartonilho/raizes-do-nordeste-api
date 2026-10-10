from fastapi import APIRouter, Depends

from models.schemas import PromocaoNova

from services.promocao_service import (
    criar_promocao_service,
    listar_promocoes_service
)

from services.auth_service import exigir_perfis


router = APIRouter(
    prefix="/promocoes",
    tags=["Promoções"]
)


@router.post("", status_code=201)
def criar_promocao(
    dados: PromocaoNova,
    usuario_logado: dict = Depends(exigir_perfis("ADMIN"))
):
    return criar_promocao_service(dados)


@router.get("")
def listar_promocoes(unidade_id: int | None = None):
    return listar_promocoes_service(unidade_id)