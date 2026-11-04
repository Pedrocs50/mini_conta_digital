from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import AccountFactory, get_balance


def test_deposit_increases_balance(client: TestClient, make_account: AccountFactory) -> None:
    account_id = make_account()

    response = client.post(f"/accounts/{account_id}/deposits", json={"amount_cents": 2500})

    assert response.status_code == 201
    assert response.json()["type"] == "deposit"
    assert response.json()["amount_cents"] == 2500
    assert response.json()["balance_after_cents"] == 2500
    assert get_balance(client, account_id) == 2500


def test_deposits_accumulate(client: TestClient, make_account: AccountFactory) -> None:
    account_id = make_account()

    client.post(f"/accounts/{account_id}/deposits", json={"amount_cents": 1000})
    client.post(f"/accounts/{account_id}/deposits", json={"amount_cents": 550})

    assert get_balance(client, account_id) == 1550


@pytest.mark.parametrize("amount", [0, -1, -1000, 10.5, "100", None, True])
def test_deposit_rejects_invalid_amount(
    client: TestClient,
    make_account: AccountFactory,
    amount: Any,
) -> None:
    account_id = make_account()

    response = client.post(f"/accounts/{account_id}/deposits", json={"amount_cents": amount})

    assert response.status_code == 422
    assert get_balance(client, account_id) == 0


def test_deposit_to_unknown_account_returns_404(client: TestClient) -> None:
    response = client.post(f"/accounts/{uuid4()}/deposits", json={"amount_cents": 100})

    assert response.status_code == 404
