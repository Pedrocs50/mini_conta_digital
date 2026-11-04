from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header

from app.api.deps import ServiceDep
from app.models.account import Account, CreateAccountRequest, DepositRequest
from app.models.transaction import Transaction
from app.models.transfer import Transfer, TransferRequest

router = APIRouter()

# Rotas `def` (e não `async def`): o armazenamento é bloqueante, então o FastAPI as
# roda em um pool de threads em vez de travar o loop de eventos.


@router.post("/accounts", status_code=201, tags=["accounts"])
def create_account(body: CreateAccountRequest, service: ServiceDep) -> Account:
    return service.create_account(body.owner_name)


@router.get("/accounts/{account_id}", tags=["accounts"])
def get_account(account_id: UUID, service: ServiceDep) -> Account:
    return service.get_account(account_id)


@router.post("/accounts/{account_id}/deposits", status_code=201, tags=["accounts"])
def deposit(account_id: UUID, body: DepositRequest, service: ServiceDep) -> Transaction:
    return service.deposit(account_id, body.amount_cents)


@router.get("/accounts/{account_id}/statement", tags=["accounts"])
def get_statement(account_id: UUID, service: ServiceDep) -> list[Transaction]:
    """Extrato em ordem cronológica (mais antigo primeiro)."""
    return service.get_statement(account_id)


@router.post("/transfers", status_code=201, tags=["transfers"])
def create_transfer(
    body: TransferRequest,
    service: ServiceDep,
    idempotency_key: Annotated[
        str | None,
        Header(
            min_length=1,
            max_length=255,
            description="Opcional. Mesma chave + mesmo pedido = não duplica a transferência.",
        ),
    ] = None,
) -> Transfer:
    return service.transfer(
        body.from_account_id,
        body.to_account_id,
        body.amount_cents,
        idempotency_key=idempotency_key,
    )
