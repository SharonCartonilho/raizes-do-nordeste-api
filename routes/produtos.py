from fastapi import APIRouter, HTTPException

from database.conexao import conectar_banco
from models.schemas import ProdutoNovo


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

@router.get("")
def listar_produtos():
    conexao = conectar_banco()

    registros = conexao.execute(
        "SELECT id, nome, preco FROM produtos"
    ).fetchall()

    conexao.close()

    return [dict(produto) for produto in registros]

@router.get("/{produto_id}")
def buscar_produto(produto_id: int):
    conexao =conectar_banco()

    produto = conexao.execute(
        "SELECT id, nome, preco FROM produtos WHERE id = ?",
        (produto_id,)
    ).fetchone()

    conexao.close()

    if produto is None:
        conexao.close()
        raise HTTPException(
        status_code=404,
        detail="Produto não encontrado"
    )

    return dict(produto)

@router.post("", status_code=201)
def cadastrar_produto(produto: ProdutoNovo):
    conexao = conectar_banco()

    cursor = conexao.execute(
        "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
        (produto.nome, produto.preco)
    )

    conexao.commit()

    novo_produto = {
        "id": cursor.lastrowid,
        "nome": produto.nome,
        "preco": produto.preco
    }

    conexao.close()

    return novo_produto