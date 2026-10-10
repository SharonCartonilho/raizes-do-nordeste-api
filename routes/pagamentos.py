from fastapi import APIRouter

from models.schemas import PagamentoNovo
from services.pagamento_service import processar_pagamento


router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)


@router.post("", status_code=201)
def realizar_pagamento(pagamento: PagamentoNovo):
    return processar_pagamento(pagamento)