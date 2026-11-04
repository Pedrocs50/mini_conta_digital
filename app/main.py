from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes import router
from app.repositories.base import AccountRepository
from app.repositories.memory import InMemoryAccountRepository
from app.services.account_service import AccountService


def create_app(repository: AccountRepository | None = None) -> FastAPI:
    """Monta a aplicação. Ser uma função permite criar um app NOVO (e vazio) em cada teste."""
    app = FastAPI(
        title="mini-conta-digital",
        version="0.1.0",
        description="API de conta digital para estudo. Valores em centavos (inteiros).",
    )
    app.state.account_service = AccountService(repository or InMemoryAccountRepository())
    register_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()
