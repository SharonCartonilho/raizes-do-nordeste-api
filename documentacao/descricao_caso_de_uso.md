UC01 — Realização do Pedido

Objetivo: Permitir que o cliente ou atendente registre um pedido de produtos disponíveis no cardápio de uma unidade da Rede Raízes do Nordeste.

Pessoas principais: Cliente e Atendente.

Pré-condições: A unidade precisa estar ativa, os produtos devem estar cadastrados e disponíveis no cardápio, e deve existir estoque suficiente. O usuário precisa ter autorização para realizar a operação, quando exigida pelo endpoint.

Fluxo principal:

O usuário seleciona a unidade.
O sistema apresenta os produtos disponíveis no cardápio.
O usuário escolhe os produtos e informa as quantidades.
O sistema verifica a disponibilidade dos produtos e do estoque.
O sistema calcula o valor do pedido, considerando eventuais promoções.
O usuário confirma o pedido.
O sistema registra o pedido no banco de dados.
O estoque é atualizado.
O pedido recebe o status AGUARDANDO_PAGAMENTO.
O sistema retorna a identificação e os dados do pedido.

Fluxos alternativos e exceções:

Situação	Comportamento esperado:

Produto inexistente: O sistema rejeita a solicitação.
Produto indisponível na unidade: O pedido não é registrado.
Estoque insuficiente: O sistema informa a impossibilidade de concluir o pedido.
Quantidade inválida: O sistema rejeita os dados informados.
Unidade inativa: O sistema impede a criação do pedido.
Falha durante a gravação: A transação é revertida para evitar inconsistências.
Pagamento recusado:	O pedido permanece aguardando pagamento, conforme a implementação atual.

Pós-condições: O pedido fica registrado no banco de dados, seus itens são armazenados e as quantidades correspondentes são descontadas do estoque da unidade.

Regras de negócio: O sistema aceita pedidos de diferentes canais, como aplicativo, web, totem e balcão. Os preços são calculados de acordo com os produtos e as promoções válidas. A atualização do pedido e do estoque ocorre dentro de uma transação, para preservar a consistência dos dados.