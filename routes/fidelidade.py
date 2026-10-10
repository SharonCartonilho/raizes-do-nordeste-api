from fastapi import APIRouter, Depends

from services.fidelidade_service import consultar_fidelidade_service
from services.auth_service import obter_usuario_logado
from models.schemas import ResgatePontos
from fastapi import APIRouter, Depends, HTTPException

from services.fidelidade_service import resgatar_pontos_service

router = APIRouter(
    prefix="/fidelidade",
    tags=["Fidelidade"]
)


@router.get("/{usuario_id}")
def consultar_fidelidade(
    usuario_id: int,
    usuario_logado: dict = Depends(obter_usuario_logado)
):
    if (
        usuario_logado["perfil"] not in ["ADMIN", "GERENTE"]
        and usuario_logado["id"] != usuario_id
    ):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para consultar estes pontos"
        )

    return consultar_fidelidade_service(usuario_id)


@router.post("/{usuario_id}/resgatar")
def resgatar_pontos(
    usuario_id: int,
    dados: ResgatePontos,
    usuario_logado: dict = Depends(obter_usuario_logado)
):
    if usuario_logado["id"] != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode resgatar seus próprios pontos"
        )

    return resgatar_pontos_service(usuario_id, dados)