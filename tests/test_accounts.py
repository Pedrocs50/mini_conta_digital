from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import AccountFactory


def test_create_account_returns_201_with_zero_balance(client: TestClient) -> None:
    response = client.post("/accounts", json={"owner_name": "Ana"})

    assert response.status_code == 201
    body = response.json()
    assert body["owner_name"] == "Ana"
    assert body["balance_cents"] == 0
    UUID(body["id"])  # levanta erro se não for um UUID válido


def test_create_account_trims_owner_name(client: TestClient) -> None:
    response = client.post("/accounts", json={"owner_name": "  Ana  "})

    assert response.json()["owner_name"] == "Ana"


@pytest.mark.parametrize("payload", [{}, {"owner_name": ""}, {"owner_name": "   "}])
def test_create_account_rejects_invalid_owner_name(
    client: TestClient, payload: dict[str, str]
) -> None:
    response = client.post("/accounts", json=payload)

    assert response.status_code == 422


def test_get_account_returns_balance(client: TestClient, make_account: AccountFactory) -> None:
    account_id = make_account("Ana", balance_cents=1050)

    response = client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["id"] == account_id
    assert response.json()["balance_cents"] == 1050


def test_get_unknown_account_returns_404(client: TestClient) -> None:
    response = client.get(f"/accounts/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["code"] == "account_not_found"


def test_get_account_with_malformed_id_returns_422(client: TestClient) -> None:
    response = client.get("/accounts/nao-e-um-uuid")

    assert response.status_code == 422
