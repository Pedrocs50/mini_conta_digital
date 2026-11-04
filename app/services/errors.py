class DomainError(Exception):
    """Erro de regra de negócio. O serviço levanta; a camada de API traduz para HTTP.

    Assim o serviço não sabe nada de HTTP e pode ser testado/reutilizado sem FastAPI.
    """

    code = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AccountNotFoundError(DomainError):
    code = "account_not_found"


class InsufficientFundsError(DomainError):
    code = "insufficient_funds"


class SameAccountTransferError(DomainError):
    code = "same_account_transfer"


class IdempotencyKeyConflictError(DomainError):
    code = "idempotency_key_conflict"
