from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.errors import (
    AccountNotFoundError,
    DomainError,
    IdempotencyKeyConflictError,
    InsufficientFundsError,
    SameAccountTransferError,
)

# Tradução "erro de negócio -> código HTTP". Fica na camada de API de propósito.
_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    AccountNotFoundError: 404,
    InsufficientFundsError: 409,  # conflito com o estado atual da conta
    SameAccountTransferError: 422,
    IdempotencyKeyConflictError: 422,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status_code = _STATUS_BY_ERROR.get(type(exc), 400)
        return JSONResponse(
            status_code=status_code,
            content={"detail": exc.message, "code": exc.code},
        )
