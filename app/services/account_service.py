from uuid import UUID, uuid4

from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.transfer import Transfer
from app.repositories.base import AccountRepository, IdempotencyRecord
from app.services.errors import (
    AccountNotFoundError,
    IdempotencyKeyConflictError,
    InsufficientFundsError,
    SameAccountTransferError,
)


class AccountService:
    """Regras de negócio. Não sabe de HTTP nem de como os dados são guardados."""

    def __init__(self, repository: AccountRepository) -> None:
        self._repo = repository

    def create_account(self, owner_name: str) -> Account:
        account = Account(owner_name=owner_name)
        self._repo.add_account(account)
        return account

    def get_account(self, account_id: UUID) -> Account:
        return self._require_account(account_id)

    def deposit(self, account_id: UUID, amount_cents: int) -> Transaction:
        with self._repo.atomic():
            account = self._require_account(account_id)
            account.balance_cents += amount_cents
            transaction = Transaction(
                account_id=account.id,
                type=TransactionType.DEPOSIT,
                amount_cents=amount_cents,
                balance_after_cents=account.balance_cents,
            )
            self._repo.save_account(account)
            self._repo.add_transaction(transaction)
        return transaction

    def transfer(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount_cents: int,
        idempotency_key: str | None = None,
    ) -> Transfer:
        if from_account_id == to_account_id:
            raise SameAccountTransferError("Não é possível transferir para a mesma conta.")

        fingerprint = (from_account_id, to_account_id, amount_cents)

        # Tudo abaixo roda dentro de UM bloco atômico: validar, debitar, creditar,
        # registrar extrato e guardar a chave de idempotência. Se qualquer passo falhar,
        # nenhum deles vale.
        with self._repo.atomic():
            if idempotency_key is not None:
                record = self._repo.get_idempotency_record(idempotency_key)
                if record is not None:
                    if record.fingerprint != fingerprint:
                        raise IdempotencyKeyConflictError(
                            "Esta Idempotency-Key já foi usada com um pedido diferente."
                        )
                    return record.transfer  # repetição: devolve o resultado, não move dinheiro

            source = self._require_account(from_account_id)
            destination = self._require_account(to_account_id)

            if source.balance_cents < amount_cents:
                raise InsufficientFundsError(
                    f"Saldo insuficiente: saldo de {source.balance_cents} centavos, "
                    f"transferência de {amount_cents} centavos."
                )

            transfer = Transfer(
                id=uuid4(),
                from_account_id=source.id,
                to_account_id=destination.id,
                amount_cents=amount_cents,
            )
            source.balance_cents -= amount_cents
            destination.balance_cents += amount_cents

            self._repo.save_account(source)
            self._repo.save_account(destination)
            self._repo.add_transaction(
                Transaction(
                    account_id=source.id,
                    type=TransactionType.TRANSFER_OUT,
                    amount_cents=amount_cents,
                    balance_after_cents=source.balance_cents,
                    counterparty_account_id=destination.id,
                    transfer_id=transfer.id,
                )
            )
            self._repo.add_transaction(
                Transaction(
                    account_id=destination.id,
                    type=TransactionType.TRANSFER_IN,
                    amount_cents=amount_cents,
                    balance_after_cents=destination.balance_cents,
                    counterparty_account_id=source.id,
                    transfer_id=transfer.id,
                )
            )
            if idempotency_key is not None:
                self._repo.save_idempotency_record(
                    idempotency_key, IdempotencyRecord(fingerprint, transfer)
                )
        return transfer

    def get_statement(self, account_id: UUID) -> list[Transaction]:
        self._require_account(account_id)
        return self._repo.list_transactions(account_id)

    def _require_account(self, account_id: UUID) -> Account:
        account = self._repo.get_account(account_id)
        if account is None:
            raise AccountNotFoundError(f"Conta {account_id} não encontrada.")
        return account
