import jwt

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from database.conexao import conectar_banco
from services.usuario_service import CHAVE_SECRETA, ALGORITMO


seguranca = OAuth2PasswordBearer(tokenUrl="/auth/token")


def obter_usuario_logado(
    token: str = Depends(seguranca)
):

    try:
        dados_token = jwt.decode(
            token,
            CHAVE_SECRETA,
            algorithms=[ALGORITMO]
        )

        usuario_id = int(dados_token["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )

    conexao = conectar_banco()

    usuario = conexao.execute("""
        SELECT
            id,
            nome,
            email,
            perfil,
            unidade_id,
            ativo
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    conexao.close()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    if not usuario["ativo"]:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo"
        )

    return dict(usuario)


def exigir_perfis(*perfis_permitidos):
    def verificar_perfil(
        usuario_logado: dict = Depends(obter_usuario_logado)
    ):
        if usuario_logado["perfil"] not in perfis_permitidos:
            raise HTTPException(
                status_code=403,
                detail="Usuário sem permissão para esta operação"
            )

        return usuario_logado

    return verificar_perfil