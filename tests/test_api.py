from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_api_esta_funcionando():
    resposta = client.get("/")

    assert resposta.status_code == 200


def test_listar_produtos():
    resposta = client.get("/produtos")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_listar_unidades():
    resposta = client.get("/unidades")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_listar_cardapio():
    from database.conexao import conectar_banco

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO unidades (
            nome,
            cidade,
            estado,
            ativa
        )
        VALUES (?, ?, ?, ?)
    """, (
        "Unidade Teste",
        "Recife",
        "PE",
        1
    ))

    conexao.commit()
    conexao.close()

    resposta = client.get("/cardapio/1")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_produto_inexistente():
    resposta = client.get("/produtos/999999")

    assert resposta.status_code == 404


def test_canal_pedido_invalido():
    resposta = client.post("/pedidos", json={
        "produto_id": 1,
        "unidade_id": 1,
        "usuario_id": None,
        "quantidade": 1,
        "canal_pedido": "INVALIDO"
    })

    assert resposta.status_code == 400


def test_quantidade_negativa():
    resposta = client.post("/pedidos", json={
        "produto_id": 1,
        "unidade_id": 1,
        "usuario_id": None,
        "quantidade": -1,
        "canal_pedido": "APP"
    })

    assert resposta.status_code in [400, 422]


def test_criar_promocao_sem_login():
    resposta = client.post("/promocoes", json={
        "nome": "Promocao Teste",
        "unidade_id": 1,
        "produto_id": 1,
        "percentual_desconto": 10,
        "data_inicio": "2026-10-09",
        "data_fim": "2026-10-15"
    })

    assert resposta.status_code == 401


def test_atualizar_estoque_sem_login():
    resposta = client.post("/estoque", json={
        "produto_id": 1,
        "unidade_id": 1,
        "quantidade": 10
    })

    assert resposta.status_code == 401


def test_consultar_fidelidade_sem_login():
    resposta = client.get("/fidelidade/3")

    assert resposta.status_code == 401