from pydantic import BaseModel
from datetime import date
from pydantic import Field





class ProdutoNovo(BaseModel):
    nome: str
    preco: float


class PedidoNovo(BaseModel):
    produto_id: int
    unidade_id: int
    quantidade: int
    canal_pedido: str
    usuario_id: int | None = None

class PagamentoNovo(BaseModel):
    pedido_id: int
    aprovado: bool
    identificador_tentativa: str


class AtualizarStatusPedido(BaseModel):
    status: str


class EstoqueAtualizacao(BaseModel):
    produto_id: int
    unidade_id: int
    quantidade: int


class UnidadeNova(BaseModel):
    nome: str
    cidade: str
    estado: str

class UsuarioNovo(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str
    unidade_id: int | None = None


class LoginUsuario(BaseModel):
    email: str
    senha: str

class ItemCardapioNovo(BaseModel):
    unidade_id: int
    produto_id: int
    preco: float
    disponivel: bool = True


class ResgatePontos(BaseModel):
    pontos: int


class PromocaoNova(BaseModel):
    nome: str
    unidade_id: int
    produto_id: int
    percentual_desconto: float = Field(gt=0, le=100)
    data_inicio: date
    data_fim: date