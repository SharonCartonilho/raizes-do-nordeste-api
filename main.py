from fastapi import FastAPI

from database.tabelas import (
    criar_tabela_produtos,
    criar_tabela_pedidos,
    criar_tabela_pagamentos,
    criar_tabela_estoque,
    criar_tabela_unidades,
    criar_tabela_usuarios,
    criar_tabela_cardapio,
    criar_tabela_fidelidade,
    criar_tabela_promocoes
)

from routes.produtos import router as produtos_router
from routes.pedidos import router as pedidos_router
from routes.pagamentos import router as pagamentos_router
from routes.estoque import router as estoque_router
from routes.unidades import router as unidades_router
from routes import produtos, pedidos, pagamentos, estoque, unidades, usuarios
from routes import cardapio
from routes import auth
from routes import fidelidade
from routes import promocoes



app = FastAPI(
    title="API Raízes do Nordeste",
    description="API para gerenciamento de produtos, pedidos...",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

criar_tabela_produtos()
criar_tabela_unidades()
criar_tabela_usuarios()
criar_tabela_pedidos()
criar_tabela_pagamentos()
criar_tabela_estoque()
criar_tabela_cardapio()
criar_tabela_fidelidade()
criar_tabela_promocoes()


app.include_router(produtos_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)
app.include_router(estoque_router)
app.include_router(unidades_router)
app.include_router(usuarios.router)
app.include_router(cardapio.router)
app.include_router(auth.router)
app.include_router(fidelidade.router)
app.include_router(promocoes.router)

@app.get("/", tags=["Sistema"])
def pagina_inicial():
    return {
        "mensagem": "Bem-vinda à API Raízes do Nordeste!"
    }