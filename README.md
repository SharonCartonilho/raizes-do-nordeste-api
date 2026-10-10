# API Raízes do Nordeste

## 1. Exposição

Este projeto envolve a criação de uma API *back-end* para a rede de alimentação Raízes do Nordeste.

O sistema foi criado para estruturar o gerenciamento de produtos, unidades, cardápios, pedidos, pagamentos, estoque, usuários, promoções e programas de fidelidade.

## 2. Tecnologias aplicadas

- Python
- FastAPI
- SQLite
- Pydantic
- JWT para fins de autenticação
- Pytest para automação de testes
- Swagger para documentação interativa

## 3. Funcionalidades

O sistema conta com as seguintes características:

- Cadastro e consulta de produtos;
- Cadastro e consulta de unidades;
- Cardápio personalizado para cada unidade;
- Registro de pedidos por diferentes canais;
- Gerenciamento de estoque por unidade;
- Simulação de pagamentos aprovados e negados;
- Atualização do status dos pedidos;
- Cadastro de usuários;
- Autenticação usando token JWT;
- Controle de permissões por perfil;
- Acúmulo e verificação de pontos de fidelidade;
- Resgate de pontos;
- Cadastro de promoções;
- Aplicação automática de descontos promocionais.

## 4. Estruturação do projeto

```text
database/       Conexão e criação das tabelas
models/         Modelos de dados
routes/         Rotas da API
services/       Regras de negócio
tests/          Testes automatizados
main.py         Inicialização da aplicação
requirements.txt Dependências do projeto
```


## 5. Instalação

É necessário ter o Python instalado.

Instale as dependências:

```bash
py -m pip install -r requirements.txt
```

## 6. Execução

Na pasta principal do projeto, execute:

```bash
py -m uvicorn main:app --reload
```

A aplicação será iniciada localmente na porta 8000.

## 7. Documentação da API

Com a aplicação em execução, abra no navegador:

http://127.0.0.1:8000/docs

O Swagger permite consultar as rotas disponíveis e executar requisições para testar as funcionalidades.

## 8. Testes automatizados

O projeto utiliza Pytest.

Para executar os testes:

```bash
py -m pytest -v
```

Até o momento, foram implementados 10 testes automatizados envolvendo consultas, validações e autenticação.

## 9. Segurança

O sistema utiliza autenticação JWT e controle de permissões para restringir operações administrativas.

As senhas dos usuários são armazenadas utilizando hash.

## 10. Limitações e melhorias futuras

Ainda há espaço para melhorias em algumas funcionalidades:

- Integração com um serviço autêntico de pagamento;
- Uso direto dos benefícios de fidelidade nos pedidos;
- Registro detalhado das promoções implementadas;
- Expansão dos testes automatizados;
- Avanços na competitividade do gerenciamento de estoque;
- Análise das diretrizes de privacidade e segurança de dados.

## 11. Considerações finais

A API Raízes do Nordeste exibe a aplicação de recursos fundamentais para a administração de uma rede de alimentação com várias unidades.

O projeto emprega uma arquitetura em camadas, que divide rotas, modelos, serviços e acesso ao banco de dados.