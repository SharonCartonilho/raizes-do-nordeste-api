from fastapi import APIRouter, Depends

from services.auth_service import exigir_perfis
from models.schemas import UnidadeNova
from services.unidade_service import (
    criar_unidade_service,
    listar_unidades_service
)


router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"]
)




@router.post("", status_code=201)
def criar_unidade(
    unidade: UnidadeNova,
    usuario_logado: dict = Depends(exigir_perfis("ADMIN"))
):
    return criar_unidade_service(unidade)

    cursor = conexao.execute(
        """
        INSERT INTO unidades (nome, cidade, estado, ativa)
        VALUES (?, ?, ?, 1)
        """,
        (
            unidade.nome,
            unidade.cidade,
            unidade.estado
        )
    )

    conexao.commit()

    nova_unidade = {
        "id": cursor.lastrowid,
        "nome": unidade.nome,
        "cidade": unidade.cidade,
        "estado": unidade.estado,
        "ativa": True
    }

    conexao.close()

    return nova_unidade


@router.get("")
def listar_unidades():
    return listar_unidades_service()

    registros = conexao.execute(
        """
        SELECT id, nome, cidade, estado, ativa
        FROM unidades
        ORDER BY id
        """
    ).fetchall()

    conexao.close()

    return [
        {
            "id": registro["id"],
            "nome": registro["nome"],
            "cidade": registro["cidade"],
            "estado": registro["estado"],
            "ativa": bool(registro["ativa"])
        }
        for registro in registros
    ]