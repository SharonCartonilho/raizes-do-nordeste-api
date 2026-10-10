import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import HTTPException
from pwdlib import PasswordHash

from database.conexao import conectar_banco
import jwt
from datetime import datetime, timedelta, timezone


password_hash = PasswordHash.recommended()

CHAVE_SECRETA = os.environ["CHAVE_SECRETA"]
ALGORITMO = os.getenv("ALGORITMO", "HS256")
TEMPO_TOKEN_MINUTOS = int(os.getenv("TEMPO_TOKEN_MINUTOS", "60"))

def criar_usuario_service(usuario):
    perfis_validos = [
        "CLIENTE",
        "ATENDENTE",
        "COZINHA",
        "GERENTE",
        "ADMIN"
    ]

    perfil = usuario.perfil.upper()

    if perfil not in perfis_validos:
        raise HTTPException(
            status_code=400,
            detail="Perfil de usuário inválido"
        )

    conexao = conectar_banco()

    usuario_existente = conexao.execute(
        "SELECT id FROM usuarios WHERE email = ?",
        (usuario.email,)
    ).fetchone()

    if usuario_existente:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado"
        )

    if usuario.unidade_id is not None:
        unidade = conexao.execute(
            "SELECT id FROM unidades WHERE id = ? AND ativa = 1",
            (usuario.unidade_id,)
        ).fetchone()

        if unidade is None:
            conexao.close()
            raise HTTPException(
                status_code=404,
                detail="Unidade não encontrada ou inativa"
            )

    senha_protegida = password_hash.hash(usuario.senha)

    cursor = conexao.execute("""
        INSERT INTO usuarios (
            nome,
            email,
            senha_hash,
            perfil,
            unidade_id,
            ativo
        )
        VALUES (?, ?, ?, ?, ?, 1)
    """, (
        usuario.nome,
        usuario.email,
        senha_protegida,
        perfil,
        usuario.unidade_id
    ))

    conexao.commit()
    usuario_id = cursor.lastrowid
    conexao.close()

    return {
        "id": usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": perfil,
        "unidade_id": usuario.unidade_id,
        "ativo": True
    }

def fazer_login_service(dados):
    conexao = conectar_banco()

    usuario = conexao.execute("""
        SELECT
            id,
            nome,
            email,
            senha_hash,
            perfil,
            unidade_id,
            ativo
        FROM usuarios
        WHERE email = ?
    """, (dados.email,)).fetchone()

    conexao.close()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    if not usuario["ativo"]:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo"
        )

    senha_correta = password_hash.verify(
        dados.senha,
        usuario["senha_hash"]
    )

    if not senha_correta:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=TEMPO_TOKEN_MINUTOS
    )

    conteudo_token = {
        "sub": str(usuario["id"]),
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "unidade_id": usuario["unidade_id"],
        "exp": expiracao
    }

    token = jwt.encode(
        conteudo_token,
        CHAVE_SECRETA,
        algorithm=ALGORITMO
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": usuario["perfil"],
            "unidade_id": usuario["unidade_id"]
        }
    }