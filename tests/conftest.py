from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.helpers import AccountFactory


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente HTTP de teste com um app NOVO: cada teste começa com zero contas."""
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def make_account(client: TestClient) -> AccountFactory:
    """Fábrica de contas: cria a conta e, se pedido, já deposita um saldo inicial."""

    def _make(owner_name: str = "Ana", balance_cents: int = 0) -> str:
        response = client.post("/accounts", json={"owner_name": owner_name})
        account_id: str = response.json()["id"]
        if balance_cents:
            client.post(f"/accounts/{account_id}/deposits", json={"amount_cents": balance_cents})
        return account_id

    return _make
