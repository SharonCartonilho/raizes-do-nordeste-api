from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from models.schemas import LoginUsuario
from services.usuario_service import fazer_login_service


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/token")
def gerar_token(
    formulario: OAuth2PasswordRequestForm = Depends()
):
    dados = LoginUsuario(
        email=formulario.username,
        senha=formulario.password
    )

    resultado = fazer_login_service(dados)

    return {
        "access_token": resultado["access_token"],
        "token_type": "bearer"
    }