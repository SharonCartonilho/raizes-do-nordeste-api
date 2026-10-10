from fastapi import APIRouter, Depends
from services.auth_service import obter_usuario_logado
from models.schemas import UsuarioNovo, LoginUsuario
from services.usuario_service import criar_usuario_service, fazer_login_service


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post("", status_code=201)
def criar_usuario(usuario: UsuarioNovo):
    return criar_usuario_service(usuario)


@router.post("/login")
def fazer_login(dados: LoginUsuario):
    return fazer_login_service(dados)


@router.get("/me")
def meu_perfil(
    usuario_logado: dict = Depends(obter_usuario_logado)
):
    return usuario_logado