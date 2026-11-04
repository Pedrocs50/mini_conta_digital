from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass
from uuid import UUID

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.transfer import Transfer


@dataclass(frozen=True)
class IdempotencyRecord:
    """O que guardamos de uma transferência já feita com certa Idempotency-Key."""

    fingerprint: tuple[UUID, UUID, int]  # (origem, destino, valor) do pedido original
    transfer: Transfer  # resultado devolvido na primeira vez


class AccountRepository(ABC):
    """Contrato de armazenamento.

    O serviço só conhece esta interface. Trocar a memória por SQLite/Postgres significa
    escrever OUTRA classe que a implemente, sem mexer em rotas nem em regras de negócio.
    """

    @abstractmethod
    def atomic(self) -> AbstractContextManager[None]:
        """Bloco "tudo ou nada": se algo levantar exceção lá dentro, nada fica gravado.

        Em um banco SQL isso seria uma transação (BEGIN ... COMMIT/ROLLBACK).
        """

    @abstractmethod
    def add_account(self, account: Account) -> None: ...

    @abstractmethod
    def get_account(self, account_id: UUID) -> Account | None: ...

    @abstractmethod
    def save_account(self, account: Account) -> None: ...

    @abstractmethod
    def add_transaction(self, transaction: Transaction) -> None: ...

    @abstractmethod
    def list_transactions(self, account_id: UUID) -> list[Transaction]: ...

    @abstractmethod
    def get_idempotency_record(self, key: str) -> IdempotencyRecord | None: ...

    @abstractmethod
    def save_idempotency_record(self, key: str, record: IdempotencyRecord) -> None: ...
