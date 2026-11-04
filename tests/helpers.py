from typing import Any, Protocol

import httpx
from fastapi.testclient import TestClient


class AccountFactory(Protocol):
    """Tipo da fixture `make_account`: uma função que cria conta e devolve o id."""

    def __call__(self, owner_name: str = "Ana", balance_cents: int = 0) -> str: ...


def get_balance(client: TestClient, account_id: str) -> int:
    balance: int = client.get(f"/accounts/{account_id}").json()["balance_cents"]
    return balance


def post_transfer(
    client: TestClient,
    from_id: str,
    to_id: str,
    amount: Any,
    idempotency_key: str | None = None,
) -> httpx.Response:
    headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
    return client.post(
        "/transfers",
        json={"from_account_id": from_id, "to_account_id": to_id, "amount_cents": amount},
        headers=headers,
    )
