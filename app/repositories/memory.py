import threading
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from app.models.account import Account
from app.models.transaction import Transaction
from app.repositories.base import AccountRepository, IdempotencyRecord


class InMemoryAccountRepository(AccountRepository):
    """Armazenamento em memória: some quando o processo reinicia. Serve para estudo e testes."""

    def __init__(self) -> None:
        self._accounts: dict[UUID, Account] = {}
        self._transactions: list[Transaction] = []  # só cresce (append-only)
        self._idempotency: dict[str, IdempotencyRecord] = {}
        # O FastAPI executa rotas `def` em várias threads. O lock garante que só uma
        # operação "ler saldo -> alterar -> gravar" aconteça por vez (neste processo).
        self._lock = threading.RLock()

    @contextmanager
    def atomic(self) -> Iterator[None]:
        with self._lock:
            # "Foto" do estado antes de começar. Copiar os dicionários é barato para um
            # projeto de estudo; os objetos dentro deles nunca são alterados no lugar
            # (get_account devolve cópias), então a foto continua válida.
            accounts = dict(self._accounts)
            transaction_count = len(self._transactions)
            idempotency = dict(self._idempotency)
            try:
                yield
            except BaseException:
                # Deu erro no meio: volta tudo como estava e propaga o erro.
                self._accounts = accounts
                del self._transactions[transaction_count:]
                self._idempotency = idempotency
                raise

    def add_account(self, account: Account) -> None:
        with self._lock:
            self._accounts[account.id] = account.model_copy()

    def get_account(self, account_id: UUID) -> Account | None:
        with self._lock:
            account = self._accounts.get(account_id)
            # Devolve uma CÓPIA: quem recebe pode mexer à vontade, e nada muda aqui
            # até chamar save_account(). Isso é o que torna o rollback simples.
            return account.model_copy() if account else None

    def save_account(self, account: Account) -> None:
        with self._lock:
            self._accounts[account.id] = account.model_copy()

    def add_transaction(self, transaction: Transaction) -> None:
        with self._lock:
            self._transactions.append(transaction)

    def list_transactions(self, account_id: UUID) -> list[Transaction]:
        with self._lock:
            return [t for t in self._transactions if t.account_id == account_id]

    def get_idempotency_record(self, key: str) -> IdempotencyRecord | None:
        with self._lock:
            return self._idempotency.get(key)

    def save_idempotency_record(self, key: str, record: IdempotencyRecord) -> None:
        with self._lock:
            self._idempotency[key] = record
