Documentação da API — Rede Raízes do Nordeste

Tecnologia: Python e FastAPI
Banco de dados: SQLite
Formato de comunicação: JSON
Autenticação: JWT
Documentação interativa: Swagger UI

A API foi desenvolvida para gerenciar as operações de uma rede de restaurantes, incluindo usuários, produtos, cardápios, pedidos, estoque, pagamentos, promoções e fidelidade.

 Módulos da API

Módulo	Funcionalidade
Autenticação	Login e controle de acesso por perfil
Usuários	Cadastro e gerenciamento de usuários
Produtos	Cadastro e consulta de produtos
Unidades	Gerenciamento das unidades
Cardápio	Produtos e preços disponíveis por unidade
Pedidos	Registro, consulta e atualização de pedidos
Estoque	Controle da quantidade de produtos
Pagamentos	Simulação de aprovação e recusa
Promoções	Cadastro e aplicação de descontos
Fidelidade	Consulta e movimentação de pontos

 Principais endpoints

Estes são os caminhos principais utilizados no desenvolvimento:

| Método | Endpoint                            | Funcionalidade                 |
| ------ | ----------------------------------- | ------------------------------ |
| GET    | `/produtos`                         | Listar produtos                |
| POST   | `/produtos`                         | Cadastrar produto              |
| GET    | `/produtos/{produto_id}`            | Buscar produto                 |
| POST   | `/pedidos`                          | Criar pedido                   |
| GET    | `/pedidos`                          | Listar pedidos                 |
| PATCH  | `/pedidos/{pedido_id}/status`       | Atualizar status do pedido     |
| POST   | `/pagamentos`                       | Realizar pagamento simulado    |
| GET    | `/estoque`                          | Listar estoque                 |
| POST   | `/estoque`                          | Atualizar estoque              |
| GET    | `/unidades`                         | Listar unidades                |
| POST   | `/unidades`                         | Criar unidade                  |
| POST   | `/usuarios`                         | Criar usuário                  |
| POST   | `/usuarios/login`                   | Fazer login                    |
| GET    | `/usuarios/me`                      | Consultar perfil autenticado   |
| GET    | `/cardapio/{unidade_id}`            | Consultar cardápio da unidade  |
| POST   | `/cardapio`                         | Adicionar item ao cardápio     |
| POST   | `/auth/token`                       | Gerar token de autenticação    |
| GET    | `/fidelidade/{usuario_id}`          | Consultar pontos de fidelidade |
| POST   | `/fidelidade/{usuario_id}/resgatar` | Resgatar pontos                |
| POST   | `/promocoes`                        | Criar promoção                 |
| GET    | `/promocoes`                        | Listar promoções               |
| GET    | `/`                                 | Página inicial                 |


Exemplo de requisição

Cadastro de pedido:

{
  "unidade_id": 1,
  "usuario_id": 3,
  "canal_pedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2
    }
  ]
}

Exemplo de resposta obtida nos testes:

{
  "id": 24,
  "unidade_id": 1,
  "usuario_id": 3,
  "canal_pedido": "APP",
  "status": "AGUARDANDO_PAGAMENTO",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2,
      "preco_unitario": 22.9,
      "subtotal": 45.8
    }
  ],
  "valor_original": 45.8,
  "desconto": 0,
  "valor_total": 45.8
}

O exemplo acima apresenta os principais campos; a resposta real pode conter campos adicionais.

Autenticação e segurança

A API utiliza autenticação baseada em JWT e diferencia as permissões dos usuários conforme seus perfis.

Os perfis previstos são CLIENTE, ATENDENTE, COZINHA, GERENTE e ADMINISTRADOR.

As senhas são armazenadas por meio de hash, evitando o armazenamento em texto simples.

Códigos de resposta

A documentação deve explicar os principais códigos HTTP utilizados:

Código	Significado
200	Requisição realizada com sucesso
201	Recurso criado
400	Dados ou operação inválidos
401	Usuário não autenticado
403	Usuário sem permissão
404	Recurso não encontrado
409	Conflito com uma regra de negócio
422	Erro de validação dos dados

Esses códigos são uma referência para conferir os retornos de cada endpoint; não significa que todos eles estejam implementados em todas as rotas.