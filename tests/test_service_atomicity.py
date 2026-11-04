"""Testes direto no serviço (sem HTTP) para as garantias mais delicadas:
atomicidade e proteção contra execuções simultâneas."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.models.transaction import Transaction
from app.repositories.memory import InMemoryAccountRepository
from app.services.account_service import AccountService
from app.services.errors import InsufficientFundsError


class FailingRepository(InMemoryAccountRepository):
    """Simula uma falha no meio da transferência (ex.: o banco caiu).

    `fail_in = 2` significa: a 2ª chamada a add_transaction a partir de agora explode.
    Em uma transferência, isso acontece DEPOIS de débito e crédito já terem sido gravados.
    """

    def __init__(self) -> None:
        super().__init__()
        self.fail_in: int | None = None

    def add_transaction(self, transaction: Transaction) -> None:
        if self.fail_in is not None:
            self.fail_in -= 1
            if self.fail_in == 0:
                raise RuntimeError("falha simulada no meio da transferência")
        super().add_transaction(transaction)


def test_transfer_is_rolled_back_if_it_fails_midway() -> None:
    repo = FailingRepository()
    service = AccountService(repo)
    ana = service.create_account("Ana")
    bruno = service.create_account("Bruno")
    service.deposit(ana.id, 10_000)

    repo.fail_in = 2  # falha ao gravar o extrato da 2ª ponta
    with pytest.raises(RuntimeError):
        service.transfer(ana.id, bruno.id, 4_000, idempotency_key="k1")

    # Nada pela metade: saldos, extratos e a chave de idempotência voltaram ao estado anterior.
    assert service.get_account(ana.id).balance_cents == 10_000
    assert service.get_account(bruno.id).balance_cents == 0
    assert len(service.get_statement(ana.id)) == 1  # só o depósito
    assert service.get_statement(bruno.id) == []

    # E a mesma chave pode ser usada de novo, porque a tentativa falha não "valeu".
    repo.fail_in = None
    service.transfer(ana.id, bruno.id, 4_000, idempotency_key="k1")
    assert service.get_account(ana.id).balance_cents == 6_000


def test_concurrent_transfers_never_overdraw_the_account() -> None:
    service = AccountService(InMemoryAccountRepository())
    ana = service.create_account("Ana")
    bruno = service.create_account("Bruno")
    service.deposit(ana.id, 1_000)  # dá para 10 transferências de 100

    def attempt(_: int) -> bool:
        try:
            service.transfer(ana.id, bruno.id, 100)
        except InsufficientFundsError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(attempt, range(40)))

    assert sum(results) == 10  # exatamente 10 passaram; as outras 30 foram recusadas
    assert service.get_account(ana.id).balance_cents == 0
    assert service.get_account(bruno.id).balance_cents == 1_000  # dinheiro conservado
